from django.urls import path, include

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("email_confirm/<str:token>/", views.email_confirm, name="email_confirm"),
    path("social/signup/", views.social_signup, name="social_signup"),
    path("", include("allauth.urls")),
    path("custom_login/", views.login, name="login"),
]
