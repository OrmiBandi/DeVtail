from django.db import models


class DirectChat(models.Model):
    """
    개인 채팅방 모델
    """

    users = models.ManyToManyField("accounts.User", related_name="direct_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "개인 채팅방"
        verbose_name_plural = "개인 채팅방"


class StudyChat(models.Model):
    """
    스터디 채팅방 모델
    """

    study = models.ForeignKey(
        "studies.Study", related_name="study_chats", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "스터디 채팅방"
        verbose_name_plural = "스터디 채팅방"


class ChatMessage(models.Model):
    """
    채팅 메시지 모델
    """

    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    direct_chat = models.ForeignKey(
        "DirectChat", on_delete=models.CASCADE, related_name="chat_messages"
    )
    study_chat = models.ForeignKey(
        "StudyChat", on_delete=models.CASCADE, related_name="chat_messages"
    )

    class Meta:
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지"
