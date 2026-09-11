"""
Centralized exception handling layer.

Why centralized exception handling:
- Without this, DRF returns inconsistent error shapes:
  validation errors look different from auth errors, which look
  different from 404s — the client has to handle 5 different shapes
- With a central handler, ALL errors follow one contract:
  { "error": "...", "code": "...", "details": {...} }
- In a FAANG interview: "our error contract is documented, consistent,
  and handled in one place — not scattered across 20 views"
"""

import structlog
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = structlog.get_logger(__name__)


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Intercepts all DRF exceptions and normalizes them into a consistent shape.

    Flow:
    1. Call DRF's default handler first (handles auth, throttle, validation)
    2. If DRF handled it, reformat the response into our shape
    3. If DRF didn't handle it (unexpected error), return a 500

    Why we call the default handler first:
    - DRF already handles ThrottledException, NotAuthenticated,
      ValidationError etc. correctly — we don't want to reimplement that
    - We just want to reformat the output, not replace the logic
    """
    response = exception_handler(exc, context)

    # Log every exception with structured context
    view = context.get("view")
    request = context.get("request")

    logger.error(
        "api_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        view=view.__class__.__name__ if view else None,
        method=request.method if request else None,
        path=request.path if request else None,
    )

    if response is not None:
        # DRF handled it — reformat to our consistent error shape
        original_data = response.data

        # Flatten DRF's nested error structure
        if isinstance(original_data, dict):
            detail = original_data.get("detail", str(original_data))
        elif isinstance(original_data, list):
            detail = original_data[0] if original_data else "An error occurred."
        else:
            detail = str(original_data)

        response.data = {
            "error": str(detail),
            "code": type(exc).__name__,
            "status_code": response.status_code,
        }

        # Add validation details if present
        if hasattr(exc, "detail") and isinstance(exc.detail, dict):
            response.data["details"] = exc.detail

        return response

    # DRF didn't handle it — this is an unexpected server error
    logger.critical(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
    )

    return Response(
        {
            "error": "An unexpected server error occurred.",
            "code": "InternalServerError",
            "status_code": 500,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
