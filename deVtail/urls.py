from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import password_reset_confirm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path(
        "accounts/reset/<uidb64>/<token>/",
        password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("accounts/", include("accounts.urls")),
    path("study/", include("studies.urls")),
    path("devmate/", include("devmates.urls")),
    path("todos/", include("todos.urls")),
    path("chat/", include("chats.urls")),
    path("alert/", include("alerts.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
