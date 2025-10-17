from django.urls import path
from .views import LoginRequestAPIView, LoginVerificationAPIView
urlpatterns = [
    path("login-request/", LoginRequestAPIView.as_view()),
    path("login-verification/", LoginVerificationAPIView.as_view())
]
