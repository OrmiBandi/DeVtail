from django.db import models

# Create your models here.


class ToDo(models.Model):
    """
    할 일 모델
    """

    ALERT_CATEGORY = (
        ("없음", "없음"),
        ("1시간", "1시간"),
        ("6시간", "6시간"),
        ("하루 전", "하루 전"),
    )

    study = models.ForeignKey(
        "studies.Study",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="todos",
    )
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=200, null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    alert_set = models.CharField(choices=ALERT_CATEGORY, max_length=20, null=True)
    status = models.IntegerField()

    class Meta:
        verbose_name = "할 일"
        verbose_name_plural = "할 일"


class ToDoAssignee(models.Model):
    """
    할 일 담당자 모델
    """

    todo = models.ForeignKey(
        "ToDo", on_delete=models.CASCADE, related_name="todo_assignees"
    )
    assignee = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="todo_assignees"
    )

    class Meta:
        verbose_name = "할 일 담당자"
        verbose_name_plural = "할 일 담당자"
