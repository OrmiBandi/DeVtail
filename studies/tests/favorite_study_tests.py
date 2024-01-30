import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Tag, Favorite
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestFavorite(TestCase):
    def setUp(self):
        """
        테스트용 데이터 생성
        """

        # 테스트용 유저 생성
        self.user1 = User.objects.create_user(
            email="test1@naver.com", password="test1", nickname="test1"
        )
        self.user2 = User.objects.create_user(
            email="test2@naver.com", password="test2", nickname="test2"
        )

        # 테스트용 스터디 생성
        self.category = Category.objects.create(name="test")
        for num in range(1, 3):
            Study.objects.create(
                category=self.category,
                goal=f"test{num}",
                title=f"test{num}",
                introduce=f"test{num}",
                start_at=datetime.date.today(),
                end_at=datetime.date.today(),
                difficulty=Study.difficulty_choices[0][0],
                max_member=10,
            )

        # 테스트용 스터디 생성 데이터
        self.study_object_first = Study.objects.get(pk=1)
        self.study_object_second = Study.objects.get(pk=2)
        tag = Tag.objects.create(name="tag_test")
        self.study_object_first.tags.add(tag)

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object_first, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object_first, user=self.user2, is_manager=False
        )
        self.study_create_data = Study.objects.values()[0]

        # 테스트용 즐겨찾기 생성
        Favorite.objects.create(user=self.user1, study=self.study_object_first)
        self.favorite_create_data = Favorite.objects.values()[0]

    def test_favorite_list_without_login(self):
        """
        로그인 하지 않은 상태로 즐겨찾기 리스트 조회 테스트
        """

        # 로그인 안한 상태에서 즐겨찾기 리스트 조회
        response = self.client.get(reverse("studies:favorite_study_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_favorite_list_with_login(self):
        """
        로그인 한 상태로 즐겨찾기 리스트 조회 테스트
        """

        # user1으로 로그인 후 즐겨찾기 리스트 조회
        self.client.force_login(self.user1)
        response = self.client.get(reverse("studies:favorite_study_list"))
        self.assertEqual(response.status_code, 200)

        # 즐겨찾기 리스트 조회 확인
        self.assertEqual(len(response.context["favorite_studies"]), 1)
        self.assertEqual(response.context["favorite_studies"][0].study.title, "test1")

    def test_favorite_create_without_login(self):
        """
        로그인 하지 않은 상태로 즐겨찾기 생성 테스트
        """

        # 로그인 안한 상태에서 즐겨찾기 생성
        study_id = self.study_create_data["id"]
        response = self.client.post(
            reverse("studies:favorite_study_create", kwargs={"pk": study_id})
        )

        # 로그인 페이지로 이동
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_favorite_create_with_login(self):
        """
        로그인 한 상태로 즐겨찾기 생성 테스트
        """

        # user1으로 로그인 후 즐겨찾기 생성
        self.client.force_login(self.user1)
        study_id = self.study_create_data["id"]
        response = self.client.post(
            reverse("studies:favorite_study_create", kwargs={"pk": study_id})
        )
        self.assertEqual(response.status_code, 302)

        # 즐겨찾기 생성 확인
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(
            Favorite.objects.filter(study=study_id)[0].study.title, "test1"
        )

    def test_facorite_create_with_login_already_exists(self):
        """
        로그인 한 상태로 즐겨찾기 생성 테스트
        이미 즐겨찾기가 존재하는 경우
        """

        # user1으로 로그인 후 즐겨찾기 생성
        self.client.force_login(self.user1)
        study_id = self.study_create_data["id"]
        response = self.client.post(
            reverse("studies:favorite_study_create", kwargs={"pk": study_id})
        )
        self.assertEqual(response.status_code, 302)

        # 즐겨찾기 생성 확인
        self.assertEqual(Favorite.objects.count(), 1)

        # 다시 동일한 즐겨찾기 생성
        response = self.client.post(
            reverse("studies:favorite_study_create", kwargs={"pk": study_id})
        )
        self.assertEqual(response.status_code, 302)

        # 즐겨찾기에 동일한 스터디가 존재하므로 즐겨찾기 생성되지 않음
        self.assertEqual(Favorite.objects.count(), 1)

    def test_favorite_delete_without_login(self):
        """
        로그인 하지 않은 상태로 즐겨찾기 삭제 테스트
        """

        # 로그인 안한 상태에서 즐겨찾기 삭제
        favorite_id = self.favorite_create_data["id"]
        response = self.client.post(
            reverse(
                "studies:favorite_study_delete", kwargs={"favorite_id": favorite_id}
            )
        )

        # 로그인 페이지로 이동
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_favorite_delete_with_login(self):
        """
        로그인 한 상태로 즐겨찾기 삭제 테스트
        """

        # user1으로 로그인 후 즐겨찾기 삭제
        self.client.force_login(self.user1)
        favorite_id = self.favorite_create_data["id"]
        response = self.client.post(
            reverse(
                "studies:favorite_study_delete", kwargs={"favorite_id": favorite_id}
            )
        )
        self.assertEqual(response.status_code, 302)

        # 즐겨찾기 삭제 확인
        self.assertEqual(Favorite.objects.count(), 0)
