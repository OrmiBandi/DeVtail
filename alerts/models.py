from django.db import models

# Create your models here.


class Alert(models.Model):
    """
    알림 모델
    """

    ALERT_CATEGORIES = [
        ("alert_devmate", "데브메이트"),
        ("alert_chat", "채팅"),
        ("alert_todo", "할일"),
        ("alert_schedule", "일정"),
        ("alert_other", "기타"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=ALERT_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    url = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "알림"
        verbose_name_plural = "알림"
