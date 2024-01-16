from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("email_confirm/<str:token>/", views.email_confirm, name="email_confirm"),
]
