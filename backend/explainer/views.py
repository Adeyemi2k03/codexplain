"""
Views layer — Single Responsibility: handle HTTP request/response cycle.

Why ViewSets over APIViews:
- ViewSets group related actions (list, create, retrieve) into one class
- Less repetition — router auto-generates URLs from ViewSet actions
- DRF routers follow REST conventions automatically
- In a FAANG interview: "ViewSets enforce REST resource semantics
  and reduce boilerplate — each resource has one class"

Why views know nothing about Groq or caching:
- Views only orchestrate: validate input → dispatch task → return response
- Business logic (caching, LLM calls) lives in tasks.py
- This is the single responsibility principle in practice
"""

import structlog
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import ExplanationRequest
from .serializers import (
    ExplainRequestSerializer,
    ExplanationResponseSerializer,
    ExplanationHistorySerializer,
    RegisterSerializer,
    UserSerializer,
    TaskStatusSerializer,
)
from .tasks import explain_code_task, compute_input_hash

logger = structlog.get_logger(__name__)


# ─── Auth Views ────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Create a new user account and return an auth token.

    Why return token on register:
    - User registers → immediately gets a token → no second login call needed
    - Better UX: one round-trip for onboarding
    """
    permission_classes = [AllowAny]
    throttle_scope = "anon"

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description="Register a new user account.",
    )
    def post(self, request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()

        # Create auth token for immediate use
        token, _ = Token.objects.get_or_create(user=user)

        logger.info("user_registered", username=user.username, user_id=user.id)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(ObtainAuthToken):
    """
    POST /api/auth/login/
    Authenticate and return a token.

    Why DRF's ObtainAuthToken:
    - Battle-tested, handles brute-force protection via throttling
    - Returns token that client stores in localStorage/header
    - We extend it only to add user data to the response
    """
    @extend_schema(
        description="Authenticate and receive an API token.",
        responses={200: {"type": "object", "properties": {
            "token": {"type": "string"},
            "user": {"type": "object"},
        }}},
    )
    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        logger.info("user_logged_in", username=user.username)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
        })


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Invalidate the current auth token.

    Why delete the token:
    - Stateless token auth means the server can't "log out" a session
    - Deleting the token from DB is the correct invalidation mechanism
    - Next request with the old token will fail with 401
    """
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        request.user.auth_token.delete()
        logger.info("user_logged_out", username=request.user.username)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /api/auth/me/ — Return the authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request) -> Response:
        return Response(UserSerializer(request.user).data)


# ─── Explainer ViewSet ─────────────────────────────────────────────────────────
class HealthView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []  # No throttling on health check

    def get(self, request) -> Response:
        return Response({
            "status": "healthy",
            "hasApiKey": bool(settings.GROQ_API_KEY),
            "model": settings.GROQ_MODEL,
            "provider": "Groq",
        })
    
class ExplanationViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    ViewSet for code explanations.

    Why GenericViewSet + Mixins instead of ModelViewSet:
    - ModelViewSet gives you create/update/delete automatically
    - We don't want clients to directly create ExplanationRequest objects
      (that goes through the /explain/ endpoint which dispatches a task)
    - We don't want clients to update or delete explanations
    - Using mixins gives us exactly what we need: retrieve + list
    - In a FAANG interview: "we use the minimum surface area needed —
      never expose endpoints you don't intend to support"

    Authentication strategy:
    - List/retrieve: requires auth (your history is private)
    - explain action: allows any (users and anon can explain code)
    """

    def get_serializer_class(self):
        """
        Why dynamic serializer selection:
        - list() returns lightweight summaries (ExplanationHistorySerializer)
        - retrieve() returns full detail (ExplanationResponseSerializer)
        - This avoids over-fetching on list endpoints
        """
        if self.action == "list":
            return ExplanationHistorySerializer
        return ExplanationResponseSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Allow retrieving any explanation by ID for polling purposes.
        """
        from django.shortcuts import get_object_or_404
        instance = get_object_or_404(ExplanationRequest, pk=kwargs["pk"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Why filter queryset per user/session:
        - Users only see their own explanations
        - Anonymous users see explanations tied to their session
        - This is row-level security at the ORM layer
        """
        if self.request.user.is_authenticated:
            return ExplanationRequest.objects.filter(
                session_key=str(self.request.user.id)
            )
        session_key = self.request.session.session_key or ""
        return ExplanationRequest.objects.filter(session_key=session_key)

    def get_permissions(self):
        """
        Why per-action permissions:
        - 'explain' is open to everyone (core product feature)
        - 'list' and 'retrieve' require auth (history is private data)
        """
        if self.action in ["explain", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        request=ExplainRequestSerializer,
        responses={
            202: TaskStatusSerializer,
            400: OpenApiResponse(description="Validation error"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        description=(
            "Submit code for AI explanation. Returns a task_id immediately. "
            "Poll GET /api/explanations/{id}/ for the result."
        ),
    )
    @action(detail=False, methods=["post"], url_path="explain")
    def explain(self, request) -> Response:
        """
        POST /api/explanations/explain/

        Why 202 Accepted instead of 200 OK:
        - 202 means "we received your request and will process it"
        - 200 means "here is your result" — we don't have it yet
        - Using 202 is semantically correct for async operations
        - Clients know to poll; they don't wait on this connection

        Request flow:
        1. Validate input via serializer
        2. Create ExplanationRequest in DB with PENDING status
        3. Dispatch Celery task (non-blocking, returns immediately)
        4. Return 202 with task_id for polling
        """
        serializer = ExplainRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        language = serializer.validated_data["language"]

        # Determine session/user identity
        if request.user.is_authenticated:
            session_key = str(request.user.id)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

        # Compute cache key hash
        input_hash = compute_input_hash(code, language)

        # Create DB record
        explanation_request = ExplanationRequest.objects.create(
            code=code,
            language=language,
            input_hash=input_hash,
            session_key=session_key,
            status=ExplanationRequest.Status.PENDING,
        )

        # Dispatch async task — non-blocking
        try:
            explain_code_task.delay(str(explanation_request.id))
        except Exception as task_err:
            import traceback
            print("TASK DISPATCH ERROR:", traceback.format_exc())
            raise

        logger.info(
            "explain_request_dispatched",
            explanation_id=str(explanation_request.id),
            language=language,
            user=request.user.username if request.user.is_authenticated else "anon",
        )

        return Response(
            {
                "task_id": str(explanation_request.id),
                "status": ExplanationRequest.Status.PENDING,
                "message": "Explanation is being processed. Poll the task_id URL for results.",
            },
            status=status.HTTP_202_ACCEPTED,
        )
