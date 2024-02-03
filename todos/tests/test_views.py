from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from studies.models import Study, Category, StudyMember
from todos.models import ToDo, ToDoAssignee

User = get_user_model()


class ToDoListTest(TestCase):
    """
    모두 확인가능한 투두 리스트 테스트
    """

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

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("todo_list"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
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

    def test_logged_in_with_my_todos(self):
        """
        자신의 할 일만 볼 수 있는지 확인
        """
        login = self.client.login(
            email="testuser1@example.com", password="1X<ISRUkw+tuK"
        )
        response = self.client.get(reverse("todo_list"))

        self.assertEqual(len(response.context["todos"]), 3)

    def test_view_with_no_todos(self):
        """
        할 일이 없을 때 아무것도 없는 상태인지 확인
        """
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("todo_list"))

        self.assertEqual(len(response.context["todos"]), 0)


class PersonalToDoList(TestCase):
    """
    개인 할 일 리스트 테스트
    """

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

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("personal_todo_list"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/personal/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        self.assertEqual(str(response.context["user"]), "testuser@example.com")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "todos/todo_list.html")

    def test_logged_in_with_my_todos(self):
        """
        자신의 할 일만 볼 수 있는지 확인
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        self.assertEqual(len(response.context["todos"]), 2)

    def test_view_with_no_todos(self):
        """
        할 일이 없을 때 아무것도 없는 상태인지 확인
        """
        test_uuser = User.objects.create_user(
            nickname="testuuser",
            email="testuuser@example.com",
            password="3HJ1vRV0Z&2iD",
        )
        login = self.client.login(
            email="testuuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_list"))

        self.assertEqual(len(response.context["todos"]), 0)


class StudyToDoList(TestCase):
    """
    스터디 할 일 리스트 테스트
    """

    @classmethod
    def setUpTestData(cls):
        """
        study1 > testuser1~4
        study2 > testuser1,4~5
        todo 1~3 > study1
        todo 4~5 > study2
        todo 1-5 > testuser1-5 (1개씩 할당)
        """
        # Create users
        number_of_users = 5
        for user_id in range(1, number_of_users + 1):
            User.objects.create_user(
                nickname=f"testuser{user_id}",
                email=f"testuser{user_id}@example.com",
                password=f"{user_id}HJ1vRV0Z&2iD",
            )

        # Create a category
        category = Category.objects.create(name="TestCategory")

        # Create studies
        study1 = Study.objects.create(
            category=category,
            goal="Test Goal1",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=14),
            difficulty="상",
            max_member=4,
        )
        study2 = Study.objects.create(
            category=category,
            goal="Test Goal2",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=7),
            difficulty="하",
            max_member=20,
        )

        # Create a study_member
        # study1에 testuser1~4 추가
        for user_id in range(1, 5):
            StudyMember.objects.create(
                study=study1,
                user=User.objects.get(id=user_id),
                is_accepted=True,
            )

        # study2에 testuser1,4~5 추가
        StudyMember.objects.create(
            study=study2,
            user=User.objects.get(id=1),
            is_accepted=True,
        )
        for user_id in range(4, 6):
            StudyMember.objects.create(
                study=study2,
                user=User.objects.get(id=user_id),
                is_accepted=True,
            )

        # Create a todo
        number_of_todos = 3
        for todo_id in range(1, number_of_todos + 1):
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
                study=study1,
            )

        for todo_id in range(number_of_todos + 1, number_of_todos * 2):
            ToDo.objects.create(
                title=f"test {todo_id}",
                alert_set="없음",
                status="ToDo",
                study=study2,
            )

        # Create a todo_assignee
        for todo_id in range(1, ToDo.objects.count() + 1):
            todo = ToDo.objects.get(id=todo_id)
            assignee = User.objects.get(id=todo_id)
            ToDoAssignee.objects.create(todo=todo, assignee=assignee)

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("study_todo_list"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/study/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("study_todo_list"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "todos/todo_list.html")

    def test_logged_in_with_my_study_members(self):
        """
        해당 스터디의 멤버수 확인
        """

        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )

        response = self.client.get(reverse("study_todo_list"), {"study": 1})

        study = Study.objects.get(id=1)
        self.assertEqual(len(response.context["members"][study]), 4)

    def test_logged_in_with_my_study_todos(self):
        """
        자신이 속한 스터디의 할 일이 보이는지 확인
        """
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )

        response = self.client.get(reverse("study_todo_list"), {"study": 1})

        self.assertEqual(len(response.context["todos"]), 3)

    def test_logged_in_with_my_study_todos_by_user(self):
        """
        자신이 속한 스터디에서 유저별 할 일이 보이는지 확인
        """
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )

        response = self.client.get(reverse("study_todo_list"), {"study": 1, "user": 2})

        self.assertEqual(len(response.context["todos"]), 1)

    def test_logged_in_with_not_my_study_access_fail(self):
        """
        자신이 속한 스터디가 아닌 스터디에 접근 시 403 응답을 받는지 확인
        """
        login = self.client.login(
            email="testuser5@example.com", password="5HJ1vRV0Z&2iD"
        )

        # testuser5는 study1에 속해있지 않으므로 403 응답을 받아야 함
        response = self.client.get(reverse("study_todo_list"), {"study": 1})

        self.assertEqual(response.status_code, 403)


class PersonalToDoCreateTest(TestCase):
    """
    개인 할 일 생성 테스트
    """

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        test_user.save()

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("personal_todo_create"))
        self.assertRedirects(response, "/accounts/login/?next=/todos/personal/create/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_create"))

        self.assertTemplateUsed(response, "todos/todo_form.html")

    def test_create_todo(self):
        """
        할 일 생성 성공
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_create"))

        # start_at/end_at 필드는 date, time으로 나눠져 있으므로, 각각 입력
        response = self.client.post(
            reverse("personal_todo_create"),
            {
                "title": "test",
                "content": "test",
                "start_at_0": timezone.now().date().isoformat(),
                "start_at_1": timezone.now().time().isoformat(),
                "end_at_0": timezone.now().date().isoformat(),
                "end_at_1": timezone.now().time().isoformat(),
                "status": "ToDo",
                "alert_set": "없음",
            },
        )

        # 할 일 생성 성공, 302 응답이 오고 할 일이 생성됨
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ToDo.objects.count(), 1)
        self.assertEqual(ToDoAssignee.objects.count(), 1)

    def test_create_todo_fail(self):
        """
        할 일 생성 실패
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_create"))

        # 필수 입력값인 title이 빈 값일 때
        response = self.client.post(
            reverse("personal_todo_create"),
            {
                "title": "",
                "content": "test",
                "status": "ToDo",
                "alert_set": "없음",
            },
        )

        # 할 일 생성 실패, 200 응답이 오고 할 일이 생성되지 않음
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ToDo.objects.count(), 0)
        self.assertEqual(ToDoAssignee.objects.count(), 0)


class PersonalToDoUpdateTest(TestCase):
    """
    개인 할 일 수정 테스트
    """

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        test_user.save()

        todo = ToDo.objects.create(
            title="Test ToDo",
            content="Test Content",
            start_at=timezone.now(),
            end_at=timezone.now() + timezone.timedelta(days=1),
            status="ToDo",
            alert_set="없음",
        )

        todo.todo_assignees.create(assignee=test_user)

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("personal_todo_edit", args=[1]))
        self.assertRedirects(response, "/accounts/login/?next=/todos/personal/edit/1/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_edit", args=[1]))

        self.assertTemplateUsed(response, "todos/todo_form.html")

    def test_edit_todo(self):
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_edit", args=[1]))

        response = self.client.post(
            reverse("personal_todo_edit", args=[1]),
            {
                "title": "test2",
                "content": "test2",
                "status": "ToDo",
                "alert_set": "없음",
            },
        )

        # 할 일 수정 성공
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ToDo.objects.count(), 1)
        self.assertEqual(ToDoAssignee.objects.count(), 1)
        self.assertEqual(ToDo.objects.get().title, "test2")

    def test_edit_todo_access_fail(self):
        """
        다른 사용자가 할 일 수정에 접근할 때 403 응답을 받는지 확인
        """
        test_user2 = User.objects.create_user(
            nickname="testuser2",
            email="testuser2@example.com",
            password="3HJ1vRV0Z&2iD",
        )
        test_user2.save()

        login = self.client.login(
            email="testuser2@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("personal_todo_edit", args=[1]))

        self.assertEqual(response.status_code, 403)


class ToDoDeleteTest(TestCase):
    """
    할 일 삭제 테스트
    """

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(
            nickname="testuser", email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        test_user.save()

        todo = ToDo.objects.create(
            title="Test ToDo",
            content="Test Content",
            start_at=timezone.now(),
            end_at=timezone.now() + timezone.timedelta(days=1),
            status="ToDo",
            alert_set="없음",
        )

        todo.todo_assignees.create(assignee=test_user)

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("todo_delete", args=[1]))
        self.assertRedirects(response, "/accounts/login/?next=/todos/delete/1/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("todo_delete", args=[1]))

        self.assertTemplateUsed(response, "todos/todo_confirm_delete.html")

    def test_delete_todo(self):
        """
        할 일 삭제 성공
        """
        login = self.client.login(
            email="testuser@example.com", password="3HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("todo_delete", args=[1]))

        response = self.client.post(reverse("todo_delete", args=[1]))

        # 할 일 삭제 성공, 302 응답이 오고 할 일이 삭제됨
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ToDo.objects.count(), 0)
        self.assertEqual(ToDoAssignee.objects.count(), 0)

    def test_delete_todo_access_fail(self):
        """
        다른 사용자가 할 일 삭제에 접근할 때 403 응답을 받는지 확인
        """
        test_user2 = User.objects.create_user(
            nickname="testuser2",
            email="testuser2@example.com",
            password="3HJ1vRV0Z&2iD",
        )
        login = self.client.login(
            email="testuser2@example.com",
            password="3HJ1vRV0Z&2iD",
        )

        response = self.client.get(reverse("todo_delete", args=[1]))

        self.assertEqual(response.status_code, 403)


class StudyToDoCreateTest(TestCase):
    """
    스터디 할 일 생성 테스트
    """

    @classmethod
    def setUpTestData(cls):
        number_of_users = 5
        for user_id in range(1, number_of_users + 1):
            User.objects.create_user(
                nickname=f"testuser{user_id}",
                email=f"testuser{user_id}@example.com",
                password=f"{user_id}HJ1vRV0Z&2iD",
            )

        # Create a category
        category = Category.objects.create(name="TestCategory")

        # Create studies
        study1 = Study.objects.create(
            category=category,
            goal="Test Goal1",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=14),
            difficulty="상",
            max_member=4,
        )
        study2 = Study.objects.create(
            category=category,
            goal="Test Goal2",
            start_at=timezone.now().date(),
            end_at=timezone.now().date() + timezone.timedelta(days=7),
            difficulty="하",
            max_member=20,
        )

        # Create a study_member
        # study1에 testuser1~4 추가
        for user_id in range(1, 5):
            StudyMember.objects.create(
                study=study1,
                user=User.objects.get(id=user_id),
                is_accepted=True,
            )

        # study2에 testuser1,4~5 추가
        StudyMember.objects.create(
            study=study2,
            user=User.objects.get(id=1),
            is_accepted=True,
        )
        for user_id in range(4, 6):
            StudyMember.objects.create(
                study=study2,
                user=User.objects.get(id=user_id),
                is_accepted=True,
            )

    def test_redirect_if_not_logged_in(self):
        """
        로그인 안 했을 때 로그인 페이지로 리다이렉트 되는지 확인
        """
        response = self.client.get(reverse("study_todo_create", kwargs={"study_id": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/todos/study/1/create/")

    def test_logged_in_uses_correct_template(self):
        """
        로그인 했을 때 올바른 템플릿인지 확인
        """
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("study_todo_create", kwargs={"study_id": 1}))

        self.assertTemplateUsed(response, "todos/todo_form.html")

    def test_logged_in_with_my_study_members(self):
        """
        해당 스터디의 멤버가 아닌 경우, study_detail로 리다이렉트 되는지 확인
        """
        login = self.client.login(
            email="testuser5@example.com", password="5HJ1vRV0Z&2iD"
        )
        response = self.client.get(reverse("study_todo_create", kwargs={"study_id": 1}))

        self.assertRedirects(response, "/study/1/")

    def test_create_todo(self):
        """
        할 일 생성 성공
        """
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )

        response = self.client.post(
            reverse("study_todo_create", kwargs={"study_id": 1}),
            {
                "title": "test",
                "content": "test",
                "start_at_0": timezone.now().date().isoformat(),
                "start_at_1": timezone.now().time().isoformat(),
                "end_at_0": timezone.now().date().isoformat(),
                "end_at_1": timezone.now().time().isoformat(),
                "status": "ToDo",
                "alert_set": "없음",
                "assignees": [1, 2, 3, 4],
            },
        )

        self.assertTrue(ToDo.objects.get(study=1))
        self.assertEqual(ToDo.objects.count(), 1)
        self.assertEqual(ToDoAssignee.objects.count(), 4)

    def test_create_todo_redirect(self):
        login = self.client.login(
            email="testuser1@example.com", password="1HJ1vRV0Z&2iD"
        )

        response = self.client.post(
            reverse("study_todo_create", kwargs={"study_id": 1}),
            {
                "title": "test",
                "status": "ToDo",
                "alert_set": "없음",
                "assignees": [1, 2, 3, 4],
            },
        )

        self.assertRedirects(response, "/todos/study/?study=1")
