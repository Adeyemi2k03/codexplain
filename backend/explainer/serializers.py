"""
Serializers layer — Single Responsibility: validate input, shape output.

Why a dedicated Serializer layer:
- Serializers are the contract between your API and the outside world
- They validate incoming data BEFORE it touches business logic
- They control exactly what fields are exposed in responses
- In a FAANG interview: "serializers are our input validation and
  output shaping layer — business logic never touches raw request data"

Think of serializers as a two-way transformer:
  Incoming JSON → validated Python objects (deserialization)
  Python objects → outgoing JSON (serialization)
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ExplanationRequest


# ─── Auth Serializers ──────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates and creates a new user account.

    Why password write_only=True:
    - Passwords must NEVER appear in API responses
    - write_only=True means the field is accepted on input but never
      included in serialized output — a security guarantee enforced
      at the serializer layer, not the view layer
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only representation of the authenticated user.
    Only exposes safe, non-sensitive fields.
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = fields


# ─── Explainer Serializers ─────────────────────────────────────────────────────

class ExplainRequestSerializer(serializers.Serializer):
    """
    Validates the incoming explain request.

    Why Serializer not ModelSerializer here:
    - The client sends {code, language} but we compute input_hash,
      session_key, status etc. server-side
    - ModelSerializer would expose internal fields the client shouldn't set
    - Using plain Serializer gives us explicit control over the contract

    Why max_length on code:
    - Groq charges per token — unbounded input = unbounded cost
    - 20,000 chars ~= 5,000 tokens, a reasonable ceiling
    - Validation at the serializer layer means the view never receives
      invalid data — fail fast, fail early
    """
    code = serializers.CharField(
        min_length=1,
        max_length=20_000,
        trim_whitespace=False,
        error_messages={
            "blank": "Code cannot be empty.",
            "max_length": "Code exceeds the maximum length of 20,000 characters.",
        },
    )
    language = serializers.ChoiceField(
        choices=[lang[0] for lang in ExplanationRequest.SUPPORTED_LANGUAGES],
        error_messages={
            "invalid_choice": "Unsupported language. See /api/schema/ for supported values.",
        },
    )


class ExplanationResponseSerializer(serializers.ModelSerializer):
    """
    Shapes the API response for a completed explanation.

    Why explicit fields instead of fields = '__all__':
    - '__all__' is dangerous — it exposes new fields automatically
      when the model changes, potentially leaking internal data
    - Explicit fields = explicit contract = no surprises in production

    Why cache_hit is included:
    - Transparency: lets the client know if this was a cached response
    - Useful for debugging and performance monitoring dashboards
    - In a FAANG interview: "we expose cache_hit so client-side
      telemetry can track cache efficiency"
    """
    class Meta:
        model = ExplanationRequest
        fields = [
            "id",
            "language",
            "explanation",
            "status",
            "tokens_used",
            "cache_hit",
            "model_used",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class ExplanationHistorySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing past explanations.
    Excludes the full code and explanation to keep list responses small.

    Why a separate serializer for lists vs detail:
    - Listing 50 explanations with full code/explanation bodies
      would be megabytes of data — wasteful and slow
    - FAANG principle: list endpoints return summaries,
      detail endpoints return full data
    """
    code_preview = serializers.SerializerMethodField()

    class Meta:
        model = ExplanationRequest
        fields = [
            "id",
            "language",
            "code_preview",
            "status",
            "cache_hit",
            "tokens_used",
            "created_at",
        ]

    def get_code_preview(self, obj: ExplanationRequest) -> str:
        """Return first 100 chars of code as a preview."""
        return obj.code[:100] + ("..." if len(obj.code) > 100 else "")


class TaskStatusSerializer(serializers.Serializer):
    """
    Response shape for async task status polling.

    When a client submits code, they get back a task_id.
    They then poll GET /api/explain/{id}/ to check status.
    This serializer shapes that polling response.

    Why async at all:
    - Groq calls take 1-5 seconds
    - HTTP best practice: don't hold connections open for slow operations
    - The client gets an immediate 202 Accepted + task_id
    - Polls until status = COMPLETED or FAILED
    """
    task_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=ExplanationRequest.Status.choices)
    message = serializers.CharField()
