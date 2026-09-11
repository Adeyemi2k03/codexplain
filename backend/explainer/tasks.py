"""
Celery Tasks layer — Single Responsibility: async execution of slow operations.

Why Celery tasks for LLM calls:

The core problem: HTTP requests have a timeout. Groq calls take 1-5 seconds.
At scale (100 concurrent users), 100 threads blocked waiting for Groq =
your server is unresponsive to everyone else.

The solution — async task queue:
1. View receives request → validates → dispatches Celery task → returns 202
2. Celery worker (separate process) picks up task → calls Groq → stores result
3. Client polls GET /api/explain/{id}/ until status = COMPLETED

This decouples your web server from your LLM calls entirely.
The web server is always fast. The workers absorb the latency.

In a FAANG interview: "we use the async worker pattern for any operation
that exceeds ~200ms. LLM calls are 1-5 seconds — they must be async."

Redis cache strategy (why hash the input):
- SHA-256(code + language) = deterministic, collision-resistant cache key
- If user A and user B paste the same code, user B gets cached result instantly
- Zero Groq API call, zero tokens consumed, zero cost
- Cache TTL = 24 hours (configurable) — explanations don't go stale quickly
"""

import hashlib
import structlog
from datetime import timezone as tz, datetime
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from groq import Groq

from .models import ExplanationRequest

logger = structlog.get_logger(__name__)


def compute_input_hash(code: str, language: str) -> str:
    """
    Compute a deterministic SHA-256 hash of code + language.

    Why SHA-256:
    - Collision resistant: two different inputs won't produce the same hash
    - Fixed length output: always 64 hex chars, safe as a cache key
    - Fast: hashing 20KB of code takes microseconds
    """
    content = f"{language}::{code.strip()}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_cache_key(input_hash: str) -> str:
    """Namespaced cache key to avoid collisions with other cache entries."""
    return f"explanation:{input_hash}"


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=3,
    name="explainer.tasks.explain_code",
)
def explain_code_task(self, explanation_id: str) -> dict:
    """
    Celery task that calls the Groq API and stores the result.

    Why bind=True:
    - Gives us access to `self` (the task instance)
    - Allows self.retry() on transient failures (network timeout, rate limit)

    Why max_retries=2:
    - Groq occasionally rate limits or has transient errors
    - Retrying twice covers most transient failures
    - We don't retry indefinitely — that would hide real bugs

    Why default_retry_delay=3:
    - Wait 3 seconds between retries
    - Gives Groq time to recover from a temporary overload

    Task flow:
    1. Load ExplanationRequest from DB
    2. Check Redis cache — return cached result if found
    3. Call Groq API
    4. Cache the result in Redis
    5. Save result to PostgreSQL
    6. Return result dict
    """
    log = logger.bind(explanation_id=explanation_id)

    try:
        # ── Load the pending request ──────────────────────────────────────────
        request = ExplanationRequest.objects.get(id=explanation_id)
        request.status = ExplanationRequest.Status.PROCESSING
        request.save(update_fields=["status"])

        log.info("task_started", language=request.language)

        # ── Cache check ───────────────────────────────────────────────────────
        # Why check cache inside the task (not the view):
        # - The task might be retried; re-checking cache avoids duplicate
        #   Groq calls if a previous retry already populated the cache
        cache_key = get_cache_key(request.input_hash)
        cached = cache.get(cache_key)

        if cached:
            log.info("cache_hit", cache_key=cache_key)
            request.explanation = cached["explanation"]
            request.tokens_used = cached.get("tokens_used")
            request.model_used = cached.get("model_used", settings.GROQ_MODEL)
            request.status = ExplanationRequest.Status.COMPLETED
            request.cache_hit = True
            request.completed_at = datetime.now(tz=tz.utc)
            request.save(update_fields=[
                "explanation", "tokens_used", "model_used",
                "status", "cache_hit", "completed_at",
            ])
            return {"status": "completed", "cache_hit": True}

        # ── Call Groq API ─────────────────────────────────────────────────────
        client = Groq(api_key=settings.GROQ_API_KEY)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer and teacher. "
                    "Explain code clearly and accurately using markdown: "
                    "headings, bullets, and inline code blocks. "
                    "Structure: 1) Overview, 2) Step-by-step breakdown, 3) Key concepts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Explain this {request.language} code:\n\n"
                    f"```{request.language}\n{request.code.strip()}\n```"
                ),
            },
        ]

        log.info("calling_groq", model=settings.GROQ_MODEL)

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )

        explanation = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else None

        # ── Store in Redis cache ──────────────────────────────────────────────
        cache_payload = {
            "explanation": explanation,
            "tokens_used": tokens_used,
            "model_used": settings.GROQ_MODEL,
        }
        cache.set(cache_key, cache_payload)  # TTL from settings (24h default)
        log.info("cached_result", cache_key=cache_key, tokens=tokens_used)

        # ── Persist to PostgreSQL ─────────────────────────────────────────────
        request.explanation = explanation
        request.tokens_used = tokens_used
        request.model_used = settings.GROQ_MODEL
        request.status = ExplanationRequest.Status.COMPLETED
        request.cache_hit = False
        request.completed_at = datetime.now(tz=tz.utc)
        request.save(update_fields=[
            "explanation", "tokens_used", "model_used",
            "status", "cache_hit", "completed_at",
        ])

        log.info("task_completed", tokens=tokens_used)
        return {"status": "completed", "cache_hit": False, "tokens": tokens_used}

    except ExplanationRequest.DoesNotExist:
        log.error("request_not_found", explanation_id=explanation_id)
        return {"status": "failed", "error": "Request not found"}

    except Exception as exc:
        log.error("task_failed", error=str(exc), exc_type=type(exc).__name__)

        # Retry on transient errors (network, rate limit)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            # All retries exhausted — mark as failed in DB
            try:
                request = ExplanationRequest.objects.get(id=explanation_id)
                request.status = ExplanationRequest.Status.FAILED
                request.error_message = str(exc)
                request.save(update_fields=["status", "error_message"])
            except ExplanationRequest.DoesNotExist:
                pass
            return {"status": "failed", "error": str(exc)}
