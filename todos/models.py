from django.db import models
from django.urls import reverse


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

    STATUS_CATEGORY = (
        ("ToDo", "ToDo"),
        ("In Progress", "In Progress"),
        ("Done", "Done"),
    )

    study = models.ForeignKey(
        "studies.Study",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="todos",
    )
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, default="")
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    alert_set = models.CharField(choices=ALERT_CATEGORY, max_length=20, default="없음")
    status = models.CharField(choices=STATUS_CATEGORY, max_length=20, default="ToDo")

    class Meta:
        verbose_name = "할 일"
        verbose_name_plural = "할 일"

    def get_absolute_url(self):
        return reverse("todo_detail", args=[self.id])

    def __str__(self):
        return self.title


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
