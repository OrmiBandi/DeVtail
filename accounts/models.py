from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    사용자 모델
    """

    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=100, unique=True)
    development_field = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(
        upload_to="user/imgs/%Y/%m/%d/", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return f"/accounts/profile/{self.pk}"


class UserBlock(models.Model):
    """
    사용자 차단 모델
    """

    blocking_user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="blocking_users"
    )
    blocked_user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="blocked_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "사용자 차단"
        verbose_name_plural = "사용자 차단"


class UserReport(models.Model):
    """
    사용자 신고 모델
    """

    reporting_user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="reporting_users"
    )
    reported_user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="reported_users"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "사용자 신고"
        verbose_name_plural = "사용자 신고"
