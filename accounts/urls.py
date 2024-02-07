from django.urls import path, include

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("email_confirm/<str:token>/", views.email_confirm, name="email_confirm"),
    path("social/signup/", views.social_signup, name="social_signup"),
    path("logout/", views.logout, name="logout"),
    path("login/", views.login, name="login"),
    path("profile/<int:pk>/", views.profile, name="profile"),
    path("edit/", views.account_update, name="account_update"),
    path("delete/", views.account_delete, name="account_delete"),
    path("password/change/", views.password_change, name="password_change"),
    path("password/reset/", views.password_reset, name="password_reset"),
    path(
        "password/reset_confirm/<str:uidb64>/<str:token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("", include("allauth.urls")),
]
