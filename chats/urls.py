from django.urls import path, include

from . import views

app_name = "chats"

urlpatterns = [
    path(
        "directchat/",
        views.create_or_connect_direct_chat,
        name="create_or_connect_direct_chat",
    ),
    path(
        "redirect_to_chat_page/<int:room_id>/",
        views.redirect_to_chat_page,
        name="redirect_to_chat_page",
    ),
]
