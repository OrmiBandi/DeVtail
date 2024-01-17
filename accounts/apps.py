from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def expire_account(self):
        """
        이메일 미인증 계정 만료 메서드
        """
        from .tools import delete_expire_account

        expire_sched = BackgroundScheduler()
        expire_sched.add_job(delete_expire_account, "cron", hour=1, id="expire_account")

        expire_sched.start()

    def ready(self):
        self.expire_account()
        return super().ready()
