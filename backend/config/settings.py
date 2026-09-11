"""
Django settings for CodeXplain backend.
Structured for FAANG-standard layered architecture.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ─── Applications ─────────────────────────────────────────────────────────────
# Why this order matters:
# - django.contrib.* provides core Django functionality
# - corsheaders must come before any app that handles requests
# - drf_spectacular auto-generates OpenAPI docs from our ViewSets
# - explainer is our domain layer
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "rest_framework.authtoken",
    # Local
    "explainer",
]

# ─── Middleware ───────────────────────────────────────────────────────────────
# Why CorsMiddleware is first: it must intercept OPTIONS preflight requests
# before any other middleware processes them.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─── Database — PostgreSQL ────────────────────────────────────────────────────
# Why PostgreSQL over SQLite:
# - ACID compliance for concurrent writes (multiple users submitting at once)
# - JSON field support for storing structured explanation metadata
# - Full-text search on code/explanation fields at scale
# - Production-grade: SQLite is file-based, unsuitable for multi-process servers
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "codexplain"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# ─── Redis Cache ──────────────────────────────────────────────────────────────
# Why Redis for caching:
# - In-memory = microsecond read times vs milliseconds for DB
# - Supports TTL (time-to-live) natively — cache entries auto-expire
# - Shared across multiple Django worker processes (unlike local-memory cache)
# - Same Redis instance doubles as Celery broker, reducing infrastructure cost
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,  # Degrade gracefully if Redis is down
        },
        "KEY_PREFIX": "codexplain",
        "TIMEOUT": 60 * 60 * 24,  # 24 hours default TTL
    }
}

# ─── Celery — Async Task Queue ────────────────────────────────────────────────
# Why Celery:
# - Groq API calls take 1-5 seconds — blocking the web worker for this is
#   unacceptable at scale. A blocked worker can't handle other requests.
# - Celery offloads the LLM call to a separate worker process.
# - The web server returns a task_id immediately; client polls for result.
# - This is the standard pattern at FAANG for any slow external API call.
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_BROKER_TRANSPORT = "redis"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60  # Kill tasks that run > 60 seconds

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    # Why both throttle classes:
    # - AnonRateThrottle: anonymous users get 10 requests/hour
    #   Protects the paid Groq API from public abuse
    # - UserRateThrottle: authenticated users get 100 requests/hour
    #   Gives registered users more headroom while still protecting the API
    # - In a FAANG interview: "we protect the expensive external API
    #   dependency at the DRF layer before it hits business logic"
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/hour",
        "user": "100/hour",
    },
    # Centralized exception handling — all errors go through one handler
    # so error format is consistent across every endpoint
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    # Auto-generate OpenAPI schema for drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# ─── API Documentation (drf-spectacular) ─────────────────────────────────────
# Why drf-spectacular:
# - Auto-generates OpenAPI 3.0 spec from your ViewSets and Serializers
# - Zero manual documentation — the code IS the docs
# - FAANG teams expect documented APIs; this gives you Swagger UI for free
SPECTACULAR_SETTINGS = {
    "TITLE": "CodeXplain API",
    "DESCRIPTION": "AI-powered code explanation service with Redis caching and async processing.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ─── Groq API ─────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.6-27b")
GROQ_MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "1200"))

# ─── Structured Logging ───────────────────────────────────────────────────────
# Why structlog:
# - Plain text logs are unsearchable at scale
# - structlog outputs JSON → Datadog/CloudWatch can query by field
# - e.g. filter all logs where cache_hit=true, language=python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "explainer": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
