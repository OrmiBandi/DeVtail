from django.db import models


class DevMate(models.Model):
    """
    DevMate 모델
    Attributes:
        sent_user: DevMate 신청한 사용자
        received_user: DevMate 신청받은 사용자
        is_accepted: 수락 여부
    """

    sent_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="sent_users"
    )
    received_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="received_users"
    )
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return (
            self.sent_user.nickname
            + " -> "
            + self.received_user.nickname
            + " , "
            + str(self.is_accepted)
        )
