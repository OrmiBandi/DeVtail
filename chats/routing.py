from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/directchat/<int:room_id>/", consumers.DirectChatConsumer.as_asgi()),
    # path("ws/studychat/<int:room_id>/", consumers.StudyChatConsumer.as_asgi()),
]
