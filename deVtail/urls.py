from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("accounts/", include("accounts.urls")),
    path("study/", include("studies.urls")),
    path("devmate/", include("devmates.urls")),
    path("todo/", include("todos.urls")),
    path("chat/", include("chats.urls")),
    path("alert/", include("alerts.urls")),
]
