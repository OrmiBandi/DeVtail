import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatMessage


class BaseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        room_id = text_data_json["room_id"]

        await self.save_message(room_id, message)

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                }
            )
        )

    @sync_to_async
    def save_message(self, room_id, message):
        # 메시지 저장 로직
        pass


class DirectChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"directchat_{self.room_id}"

        # 채팅방 참가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await super().connect()

    async def disconnect(self, close_code):
        # 채팅방 나가기
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await super().disconnect()


class StudyChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.study_id = self.scope["url_route"]["kwargs"]["study_id"]
        self.study_group_name = f"studychat_{self.study_id}"

        # 채팅방 참가
        await self.channel_layer.group_add(self.study_group_name, self.channel_name)

        await super().connect()

    async def disconnect(self, close_code):
        # 채팅방 나가기
        await self.channel_layer.group_discard(self.study_group_name, self.channel_name)

        await super().disconnect()
