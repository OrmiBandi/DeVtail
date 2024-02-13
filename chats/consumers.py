import json
from channels.layers import get_channel_layer
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

from .models import DirectChat
from .models import ChatMessage

User = get_user_model()


class OnlineUserManager:
    """
    현재 접속자 관리자
    """

    _instance = None
    chat_rooms = {}

    def __new__(cls, chat_room_name):
        if chat_room_name not in cls.chat_rooms:
            cls.chat_rooms[chat_room_name] = super(OnlineUserManager, cls).__new__(cls)
            cls.chat_rooms[chat_room_name].online_users = set()
        return cls.chat_rooms[chat_room_name]

    def add_user(self, user):
        self.online_users.add(user)

    def remove_user(self, user):
        self.online_users.discard(user)

    def get_online_users(self):
        return list(self.online_users)


class DirectChatConsumer(JsonWebsocketConsumer):
    layer = get_channel_layer()
    room_group_name = None

    def connect(self):
        """
        웹소켓 연결 시 호출되는 함수
        """
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.chat_room = DirectChat.objects.get(id=room_id)
        user = self.get_user_from_session()
        self.scope["user"] = user
        print(self.scope)

        self.accept()
        users = self.chat_room.users.all()
        self.send(
            text_data=json.dumps(
                {
                    "type": "login",
                    "name": str(self.chat_room),
                    "message": f"{users[0].nickname}, {users[1].nickname}의 채팅",
                }
            )
        )
        return

    def get_user_from_session(self):
        session_key = self.get_session_key_from_headers()
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get("_auth_user_id")
        return User.objects.get(id=user_id)

    def get_session_key_from_headers(self):
        for name, value in self.scope["headers"]:
            if name == b"cookie":
                cookies = value.decode("utf-8").split("; ")
                for cookie in cookies:
                    if cookie.startswith("sessionid="):
                        return cookie.split("=")[1]
        return None

    def disconnect(self, close_code):
        """
        사용자의 연결이 끊겼을 때 호출되는 함수
        """

        self.remove_user_to_group()

    def authorize(self, message):
        is_login = self.login(message)
        if is_login is False:
            return

        user = self.scope["user"]
        if user.is_anonymous:
            self.close()
            return

        chat_room = self.get_chatroom()
        if chat_room is None:
            print("채팅방 없음")
            self.close()
            return

        self.room_group_name = f"chatroom_{chat_room.id}"
        self.add_user_to_group()
        self.fetch_previous_message()

    def receive_json(self, content_dict, **kwargs):
        if content_dict["type"] == "auth":
            self.authorize(message=content_dict)
            return

        if content_dict["type"] == "chat_message":
            room_id = self.scope["url_route"]["kwargs"]["room_id"]
            user_id = content_dict["user_id"]
            print("여기 receive_json")
            print(content_dict)
            print(self.scope)

            content_dict["sender"] = user_id

            chat_room = DirectChat.objects.get(id=room_id)
            user = User.objects.get(id=user_id)

            _ = ChatMessage.objects.create(
                message=content_dict["message"], direct_chat=chat_room, author=user
            )

            nickname = user.nickname
            content_dict["nickname"] = nickname
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, content_dict
            )

    def login(self, message):
        if self.scope["user"] is None:
            print("로그인 안됨")
            self.close()
            return False
        return True

    def chat_message(self, event):
        """
        그룹에서 채팅 메시지를 받았을 때 호출되는 함수
        """
        user_id = self.scope["user_id"]

        message = event["message"]
        sender = event["sender"]
        nickname = event["nickname"]

        if sender != user_id:
            self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender": sender,
                        "nickname": nickname,
                    }
                )
            )

    def get_chatroom(self):
        """
        유저 ID와 채팅방 ID로 채팅방을 가져오는 함수
        """
        try:
            user = self.scope["user"]
            room_id = self.scope["url_route"]["kwargs"]["room_id"]

            chat_room = DirectChat.objects.get(id=room_id)
            # is_member = chat_room.team.member.filter(pk=user.id).exists()
            # if is_member is True:
            #     return chat_room
            return chat_room

        except Exception as e:
            return None

    def add_user_to_group(self):
        """
        채팅방 그룹에 유저 추가
        """
        user = self.scope["user"]

        async_to_sync(self.layer.group_add)(self.room_group_name, self.channel_name)

        OnlineUserManager(self.room_group_name).add_user(user)
        self.refresh_online_users()

    def remove_user_to_group(self):
        """
        채팅방 그룹의 유저 제거
        """
        if self.room_group_name is None:
            return

        user = self.scope["user"]
        async_to_sync(self.layer.group_discard)(self.room_group_name, self.channel_name)

        OnlineUserManager(self.room_group_name).remove_user(user)
        self.refresh_online_users()

    def refresh_online_users(self):
        """
        현재 접속자 정보 제공
        """
        users = OnlineUserManager(self.room_group_name).get_online_users()
        self.publish_current_users(users)

    def fetch_previous_message(self):
        """
        이전 대화 조회
        """
        room_id = self.scope["url_route"]["kwargs"]["room_id"]

        chat_room = DirectChat.objects.get(id=room_id)

        messages = ChatMessage.objects.filter(chatroom=chat_room).order_by("-id")[:10]

        for message in reversed(messages):
            sender = User.objects.get(id=message.user.id)
            self.send_json(
                {
                    "type": "chat_message",
                    "message": message.content,
                    "sender": message.user.id,
                    "nickname": sender.nickname,
                }
            )

    def publish_current_users(self, users):
        """
        현재 접속자 정보 퍼블리시
        """
        serialized_users = [
            {"id": user.id, "nickname": user.nickname} for user in users
        ]

        async_to_sync(self.layer.group_send)(
            self.room_group_name,
            {
                "type": "current_users",
                "users": serialized_users,
            },
        )

    def current_users(self, event):
        """
        current_users 타입 메시지 처리
        """
        users = event["users"]

        self.send(
            text_data=json.dumps(
                {
                    "type": "current_users",
                    "users": users,
                }
            )
        )
