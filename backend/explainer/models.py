"""
Models layer — Single Responsibility: define data shape and persistence.

Why a dedicated Model layer:
- Models are the single source of truth for your data schema
- They know nothing about HTTP, serialization, or business logic
- In a FAANG interview: "our Model layer is purely about data integrity
  and relationships — it never touches request/response concerns"
"""

import uuid
from django.db import models


class ExplanationRequest(models.Model):
    """
    Persists every code explanation request and its result.

    Design decisions worth defending in an interview:

    1. UUIDField as primary key:
       - Auto-incrementing integers expose record count (security issue)
       - UUIDs are safe to expose in URLs and API responses
       - Globally unique — safe for distributed systems / sharding

    2. session_key instead of ForeignKey(User):
       - Our app doesn't require auth to explain code
       - session_key ties submissions to a browser session without login
       - Upgrade path: add optional user FK later without schema rewrite

    3. input_hash (SHA-256):
       - This is the Redis cache key
       - We hash code + language so identical submissions hit cache
       - Storing the hash in DB lets us audit cache efficiency
       - SHA-256 is collision-resistant — safe to use as a cache key

    4. status field (PENDING/PROCESSING/COMPLETED/FAILED):
       - Enables the async polling pattern
       - Client submits → gets task_id → polls GET /explain/{id}/
       - This decouples slow Groq calls from the HTTP request cycle

    5. tokens_used:
       - Tracks Groq API token consumption per request
       - Essential for cost monitoring and abuse detection
       - At FAANG: "we instrument every external API call for cost attribution"
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    SUPPORTED_LANGUAGES = [
        ("javascript", "JavaScript"),
        ("typescript", "TypeScript"),
        ("python", "Python"),
        ("java", "Java"),
        ("go", "Go"),
        ("rust", "Rust"),
        ("c", "C"),
        ("cpp", "C++"),
        ("csharp", "C#"),
        ("php", "PHP"),
        ("ruby", "Ruby"),
        ("swift", "Swift"),
        ("kotlin", "Kotlin"),
        ("sql", "SQL"),
        ("bash", "Bash"),
        ("html", "HTML"),
        ("css", "CSS"),
    ]

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)

    # Input
    code = models.TextField()
    language = models.CharField(max_length=20, choices=SUPPORTED_LANGUAGES)
    input_hash = models.CharField(max_length=64, db_index=True)  # SHA-256

    # Output
    explanation = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True)

    # Metadata
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    cache_hit = models.BooleanField(default=False)  # Was this served from Redis?
    model_used = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "explanation_requests"
        ordering = ["-created_at"]
        indexes = [
            # Composite index: fetching history for a session ordered by date
            models.Index(fields=["session_key", "-created_at"]),
            # Index for cache lookup by hash
            models.Index(fields=["input_hash", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.language} | {self.status} | {self.created_at:%Y-%m-%d %H:%M}"
