from django.urls import path

from . import views

app_name = "chats"

urlpatterns = [
    path(
        "directchat/",
        views.create_or_connect_direct_chat,
        name="create_or_connect_direct_chat",
    ),
]
