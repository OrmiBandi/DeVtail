from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from .models import DevMate

User = get_user_model()


class TestDevMate(TestCase):
    """
    devmate 기능 테스트

    reverse 종류:
        devmate_list: 로그인 한 유저의 devmate 조회
        devmate_recieved_list : 로그인 한 유저가 신청받은 devmate 조회
        devmate_create: devmate 신청
        devmate_update: devmate 수락
        devmate_delete: devmate 삭제
    """

    def setUp(self):
        # 유저 생성
        self.user1 = User.objects.create_user(
            email="test1@naver.com", password="test1", nickname="test1"
        )
        self.user2 = User.objects.create_user(
            email="test2@naver.com", password="test2", nickname="test2"
        )
        self.user3 = User.objects.create_user(
            email="test3@naver.com", password="test3", nickname="test3"
        )

        # 다른 유저들 생성
        self.other_users = [
            User.objects.create_user(
                email=f"test{i}@naver.com", password=f"test{i}", nickname=f"test{i}"
            )
            for i in range(4, 11)
        ]

        # devmate 생성
        # user1이 user2에게 신청, 미수락
        DevMate.objects.create(
            sent_user=self.user1, received_user=self.user2, is_accepted=False
        )
        # user1이 user3에게 신청, 수락
        DevMate.objects.create(
            sent_user=self.user1, received_user=self.user3, is_accepted=True
        )
        # user1이 다수 유저에게 신청, 수락
        for user in self.other_users:
            DevMate.objects.create(
                sent_user=self.user1, received_user=user, is_accepted=True
            )

    def test_devmate_apply_with_login(self):
        """
        로그인 후 devmate 신청
        """
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("devmates:devmate_create", kwargs={"pk": self.user2.id})
        )
        self.assertEqual(response.status_code, 302)  # 신청 성공, redirect

    def test_devmate_apply_without_login(self):
        """
        로그인 하지 않고 devmate 신청
        """
        response = self.client.post(
            reverse("devmates:devmate_create", kwargs={"pk": self.user2.id})
        )
        self.assertEqual(response.status_code, 302)  # 신청 실패, redirect

    def test_show_devmate_list_with_login(self):
        """
        로그인 후 devmate 목록 조회
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse("devmates:devmate_list"))
        self.assertEqual(response.status_code, 200)  # 조회 성공

    def test_show_devmate_list_without_login(self):
        """
        로그인 하지 않고 devmate 목록 조회
        """
        response = self.client.get(reverse("devmates:devmate_list"))
        self.assertEqual(response.status_code, 302)  # 조회 실패, redirect

    def test_show_received_devmate_list_with_login(self):
        """
        로그인 후 신청받은 devmate 목록 조회
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse("devmates:devmate_received_list"))
        self.assertEqual(response.status_code, 200)  # 조회 성공

    def test_show_received_devmate_list_without_login(self):
        """
        로그인 하지 않고 신청받은 devmate 목록 조회
        """
        response = self.client.get(reverse("devmates:devmate_received_list"))
        self.assertEqual(response.status_code, 302)  # 조회 실패, redirect

    def test_devmate_accept(self):
        """
        devmate 수락
        """
        self.client.force_login(self.user2)
        devmate_instance = DevMate.objects.get(
            sent_user=self.user1, received_user=self.user2
        )
        response = self.client.post(
            reverse("devmates:devmate_update", kwargs={"pk": devmate_instance.id}),
            {"_method": "put"},
        )
        self.assertEqual(response.status_code, 302)  # 수락 성공, redirect

    def test_devmate_delete(self):
        """
        devmate 삭제 및 거절
        """
        self.client.force_login(self.user1)
        devmate_instance = DevMate.objects.get(
            sent_user=self.user1, received_user=self.user2
        )
        response = self.client.post(
            reverse("devmates:devmate_update", kwargs={"pk": devmate_instance.id}),
            {"_method": "delete"},
        )
        self.assertEqual(response.status_code, 302)  # 삭제 성공, redirect
