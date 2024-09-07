from django.urls import path

from lexicon.auth.views.auth import LoginView, LogoutView
from lexicon.auth.views.email_signin import UserEmailSigninAPI
from lexicon.auth.views.user_signup import UserSignupAPI

urlpatterns = [
    path("api/v1/auth/signup/", UserSignupAPI.as_view(), name="auth-user-signup"),
    path("api/v1/auth/login/email/", UserEmailSigninAPI.as_view(), name="auth-user-email-login"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
