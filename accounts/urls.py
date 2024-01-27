from django.urls import path, include

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("email_confirm/<str:token>/", views.email_confirm, name="email_confirm"),
    path("social/signup/", views.social_signup, name="social_signup"),
    path("logout/", views.logout, name="logout"),
    path("login/", views.login, name="login"),
    path("profile/<int:pk>/", views.profile, name="profile"),
    path("edit/", views.account_update, name="account_update"),
    path("delete/", views.account_delete, name="account_delete"),
    path("", include("allauth.urls")),
]
