from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from todos.models import ToDo, ToDoAssignee
from studies.models import Study, Category


class ToDoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="TestCategory")
        study = Study.objects.create(
            category=category,
            goal="Test Goal",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=7),
            difficulty="상",
            max_member=5,
        )
        ToDo.objects.create(title="test", alert_set="없음", status="ToDo", study=study)

    def test_study_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("study").verbose_name
        self.assertEqual(field_label, "study")

    def test_title_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_content_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("content").verbose_name
        self.assertEqual(field_label, "content")

    def test_start_at_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("start_at").verbose_name
        self.assertEqual(field_label, "start at")

    def test_end_at_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("end_at").verbose_name
        self.assertEqual(field_label, "end at")

    def test_alert_set_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("alert_set").verbose_name
        self.assertEqual(field_label, "alert set")

    def test_status_label(self):
        todo = ToDo.objects.get(id=1)
        field_label = todo._meta.get_field("status").verbose_name
        self.assertEqual(field_label, "status")

    def test_study_on_create(self):
        """
        study를 넣었을 때 todo_assignee에도 잘 들어가는지 확인
        """
        todo = ToDo.objects.get(id=1)
        assignee = get_user_model().objects.create_user(
            nickname="testuser", email="testuser@example.com", password="testpassword"
        )
        todo_assignee = ToDoAssignee.objects.create(todo=todo, assignee=assignee)
        todo_assignee = ToDoAssignee.objects.get(todo=todo)
        self.assertEqual(todo_assignee.todo, todo)
        self.assertEqual(todo_assignee.assignee, assignee)

    def test_todo_on_delete(self):
        """
        todo가 삭제되면 todo_assignee도 삭제되는지 확인
        """
        todo = ToDo.objects.get(id=1)
        todo.delete()
        todo_assignee = ToDoAssignee.objects.all()
        self.assertEqual(todo_assignee.count(), 0)

    def test_study_on_delete(self):
        """
        study를 삭제했을 때 todo도 삭제되는지 확인
        """
        study = Study.objects.get(id=1)
        study.delete()
        todo = ToDo.objects.all()
        self.assertEqual(todo.count(), 0)

    def test_title_max_length(self):
        todo = ToDo.objects.get(id=1)
        max_length = todo._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_get_absolute_url(self):
        todo = ToDo.objects.get(id=1)
        self.assertEqual(todo.get_absolute_url(), "/todos/1/")


class ToDoAssigneeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        todo = ToDo.objects.create(title="test", alert_set="없음", status="ToDo")
        assignee = get_user_model().objects.create_user(
            nickname="testuser", email="testuser@example.com", password="testpassword"
        )

        ToDoAssignee.objects.create(todo=todo, assignee=assignee)

    def test_todo_label(self):
        todo_assignee = ToDoAssignee.objects.get(id=1)
        field_label = todo_assignee._meta.get_field("todo").verbose_name
        self.assertEqual(field_label, "todo")

    def test_assignee_label(self):
        todo_assignee = ToDoAssignee.objects.get(id=1)
        field_label = todo_assignee._meta.get_field("assignee").verbose_name
        self.assertEqual(field_label, "assignee")

    def test_todo_on_delete(self):
        """
        todo가 삭제되면 todo_assignee도 삭제되는지 확인
        """
        todo = ToDo.objects.get(id=1)
        todo.delete()
        todo_assignee = ToDoAssignee.objects.filter(id=1)
        self.assertEqual(todo_assignee.count(), 0)

    def test_assignee_on_delete(self):
        """
        assignee가 삭제되면 todo_assignee도 삭제되는지 확인
        """
        assignee = get_user_model().objects.get(id=1)
        assignee.delete()
        todo_assignee = ToDoAssignee.objects.filter(id=1)
        self.assertEqual(todo_assignee.count(), 0)

    def test_assignee_multiple(self):
        """
        assignee가 여러명인 경우도 테스트
        """
        todo = ToDo.objects.get(id=1)
        assignee1 = get_user_model().objects.create_user(
            nickname="testuser1", email="testuser1@example.com", password="testpassword"
        )
        assignee2 = get_user_model().objects.create_user(
            nickname="testuser2", email="testuser2@example.com", password="testpassword"
        )
        ToDoAssignee.objects.create(todo=todo, assignee=assignee1)
        ToDoAssignee.objects.create(todo=todo, assignee=assignee2)
        todo_assignees = ToDoAssignee.objects.filter(todo=todo)
        self.assertEqual(todo_assignees.count(), 3)
