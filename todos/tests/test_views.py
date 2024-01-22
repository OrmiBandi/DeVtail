from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from studies.models import Study, Category
from todos.models import ToDo, ToDoAssignee

User = get_user_model()


# ToDoList 테스트
class ToDoListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create two users
        test_user1 = User.objects.create_user(
            nickname="testuser1",
            email="testuser1@example.com",
            password="1X<ISRUkw+tuK",
        )
        test_user2 = User.objects.create_user(
            nickname="testuser2",
            email="testuser2@example.com",
            password="2HJ1vRV0Z&3iD",
        )

        test_user1.save()
        test_user2.save()

        # Create a todo
        number_of_todos = 3

        # todo 1~3번까지는 study가 있는 todo
        for todo_id in range(1, number_of_todos + 1):
            category = Category.objects.create(name="TestCategory")
            study = Study.objects.create(
                category=category,
                goal="Test Goal",
                start_at=timezone.now().date(),
                end_at=timezone.now().date() + timezone.timedelta(days=7),
                difficulty="상",
                max_member=5,
            )
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
                study=study,
            )

        # todo 4~5번까지는 study가 없는 todo
        for todo_id in range(number_of_todos + 1, number_of_todos * 2):
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
            )

        # Create a todo_assignee
        # todo 1~5번까지 testuser1, testuser2 번갈아가면서 할당
        for todo_id in range(1, ToDo.objects.count() + 1):
            todo = ToDo.objects.get(id=todo_id)
            if todo_id % 2 == 1:
                user_id = 1
            else:
                user_id = 2
            assignee = User.objects.get(id=user_id)
            ToDoAssignee.objects.create(todo=todo, assignee=assignee)

    # 로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("todo_list"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/")

    # 로그인 했을 때 올바른 템플릿인지 확인
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            email="testuser1@example.com", password="1X<ISRUkw+tuK"
        )
        response = self.client.get(reverse("todo_list"))

        # user가 로그인했는지 확인
        self.assertEqual(str(response.context["user"]), "testuser1@example.com")
        # "success" 응답을 받았는지 확인
        self.assertEqual(response.status_code, 200)

        # 올바른 템플릿인지 확인
        self.assertTemplateUsed(response, "todos/todo_list.html")

    # 자신의 할 일만 볼 수 있는지 테스트
    def test_logged_in_with_my_todos(self):
        login = self.client.login(
            email="testuser1@example.com", password="1X<ISRUkw+tuK"
        )
        response = self.client.get(reverse("todo_list"))

        # 자신의 할 일만 볼 수 있는지 확인
        self.assertTrue("todos" in response.context)
        self.assertEqual(len(response.context["todos"]), 3)

    # 할 일이 없을 때 템플릿이 올바르게 출력되는지 테스트
    def test_view_with_no_todos(self):
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("todo_list"))

        # 할 일이 없을 때 템플릿이 올바르게 출력되는지 확인
        self.assertTrue("todos" in response.context)
        self.assertEqual(len(response.context["todos"]), 0)


class PersonalToDoList(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        test_user.save()

        number_of_todos = 3
        # todo 1~3번까지는 study가 있는 todo
        for todo_id in range(1, number_of_todos + 1):
            category = Category.objects.create(name="TestCategory")
            study = Study.objects.create(
                category=category,
                goal="Test Goal",
                start_at=timezone.now().date(),
                end_at=timezone.now().date() + timezone.timedelta(days=7),
                difficulty="상",
                max_member=5,
            )
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
                study=study,
            )

        # todo 4~5번까지는 study가 없는 todo
        for todo_id in range(number_of_todos + 1, number_of_todos * 2):
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
            )

        for todo_id in range(1, ToDo.objects.count() + 1):
            todo = ToDo.objects.get(id=todo_id)
            assignee = User.objects.get(id=1)
            ToDoAssignee.objects.create(todo=todo, assignee=assignee)

    # 로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("personal_todo_list"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/personal/")

    # 로그인 했을 때 올바른 템플릿인지 확인
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        # user가 로그인했는지 확인
        self.assertEqual(str(response.context["user"]), "testuser@example.com")
        # "success" 응답을 받았는지 확인
        self.assertEqual(response.status_code, 200)

        # 올바른 템플릿인지 확인
        self.assertTemplateUsed(response, "todos/todo_list.html")

    # 자신의 할 일만 볼 수 있는지 테스트
    def test_logged_in_with_my_todos(self):
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        # 자신의 할 일만 볼 수 있는지 확인
        self.assertTrue("todos" in response.context)
        self.assertEqual(len(response.context["todos"]), 2)

    # 할 일이 없을 때 템플릿이 올바르게 출력되는지 테스트
    def test_view_with_no_todos(self):
        test_uuser = User.objects.create_user(
            nickname="testuuser",
            email="testuuser@example.com",
            password="3HJ1vRV0Z&2iD",
        )
        login = self.client.login(
            email="testuuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        # 할 일이 없을 때 템플릿이 올바르게 출력되는지 확인
        self.assertTrue("todos" in response.context)
        self.assertEqual(len(response.context["todos"]), 0)
