from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model


def delete_expire_account():
    """
    이메일 인증을 하지 않은 계정 삭제
    """
    now = timezone.now()
    User = get_user_model()
    expire_users = User.objects.filter(is_active=False)
    for user in expire_users:
        if now - user.created_at > timedelta(days=1):
            user.delete()
