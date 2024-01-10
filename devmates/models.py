from django.db import models


class DevMate(models.Model):
    """
    DevMate 모델
    """

    sent_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="sent_users"
    )
    received_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="received_users"
    )
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
