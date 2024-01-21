import datetime

from django.test import TestCase
from django.utils import timezone

from todos.forms import PersonalToDoForm


class PersonalToDoFormTest(TestCase):
    # form이 유효한 경우 테스트
    def test_valid_form(self):
        date = datetime.datetime.now()
        form = PersonalToDoForm(
            data={
                "title": "test",
                "content": "test",
                "start_at_0": date.date().isoformat(),
                "start_at_1": date.time().isoformat(),
                "end_at_0": date.date().isoformat(),
                "end_at_1": date.time().isoformat(),
                "status": "ToDo",
                "alert_set": "없음",
            }
        )

        self.assertTrue(form.is_valid())

    # start_at, end_at필드 둘 중 하나만 입력되었을 경우, 둘 다 입력되어야 한다는 테스트
    def test_both_start_at_and_end_at_should_be_filled(self):
        date = datetime.datetime.now()
        form = PersonalToDoForm(
            data={
                "title": "test",
                "content": "test",
                "start_at_0": date.date().isoformat(),
                "start_at_1": date.time().isoformat(),
                "status": "ToDo",
                "alert_set": "없음",
            }
        )
        self.assertFalse(form.is_valid())

    # start_at필드가 end_at필드보다 이전 날짜인 경우, 거부하는지 테스트
    def test_start_at_is_before_end_at(self):
        date = datetime.datetime.now()
        form = PersonalToDoForm(
            data={
                "title": "test",
                "content": "test",
                "start_at_0": (date + timezone.timedelta(days=1)).date().isoformat(),
                "start_at_1": (date + timezone.timedelta(days=1)).time().isoformat(),
                "end_at_0": date.date().isoformat(),
                "end_at_1": date.time().isoformat(),
                "status": "ToDo",
                "alert_set": "없음",
            }
        )

        self.assertFalse(form.is_valid())
