import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from studies.models import Study, Category, StudyMember
from todos.forms import PersonalToDoForm, StudyToDoForm

User = get_user_model()


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


class StudyToDoFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_users = 3
        for user_id in range(1, number_of_users + 1):
            User.objects.create_user(
                nickname=f"testuser{user_id}",
                email=f"testuser{user_id}@example.com",
                password=f"{user_id}HJ1vRV0Z&2iD",
            )

        cls.study = Study.objects.create(
            title="TestStudy",
            category=Category.objects.create(name="TestCategory"),
            goal="Test Goal",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=7),
            difficulty="상",
            max_member=5,
        )

        for user in User.objects.all():
            StudyMember.objects.create(user=user, study=cls.study)

        cls.study_member1 = StudyMember.objects.get(id=1)
        cls.study_member2 = StudyMember.objects.get(id=2)
        cls.study_member3 = StudyMember.objects.get(id=3)

    def test_assignee_multiple_study_member_selected(self):
        """
        assignees필드에 유저가 여러명 선택되었을 경우 유효한지 테스트
        """
        form = StudyToDoForm(
            data={
                "title": "test",
                "assignees": [
                    self.study_member1,
                    self.study_member2,
                    self.study_member3,
                ],
                "status": "ToDo",
                "alert_set": "없음",
            },
            study_id=self.study.id,
        )
        print(form.errors)
        self.assertTrue(form.is_valid())

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

    def test_assignees_field_should_be_loaded(self):
        """
        assignees필드 데이터가 불러와지는지 테스트
        """
        form = StudyToDoForm(study_id=self.study.id)
        self.assertEqual(
            list(form.fields["assignees"].queryset),
            list(StudyMember.objects.filter(study=self.study)),
        )
