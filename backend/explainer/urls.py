from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExplanationViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    HealthView,
)

router = DefaultRouter()
router.register(r"explanations", ExplanationViewSet, basename="explanation")

urlpatterns = [
    # Health check
    path("health/", HealthView.as_view(), name="health"),

    # Auth endpoints
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),

    # Explainer endpoints (via router)
    path("", include(router.urls)),
]