from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from .models import DevMate

User = get_user_model()


class TestDevMate(TestCase):
    """
    devmate 기능 테스트
    1. devmate를 맺을 유저들 생성(5~10명)
    2. user1이 user2에게 devmate 신청
    3. user2가 user1에게 devmate 신청 (신청 불가)
    4. user2가 user1의 신청을 수락
    5. 다수 유저들의 devmate 생성(수락)
    6. user1의 devmate 조회

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

        # 다른 유저들 생성
        self.other_users = [
            User.objects.create_user(
                email=f"test{i}@naver.com", password=f"test{i}", nickname=f"test{i}"
            )
            for i in range(3, 11)
        ]

    def test_devmate(self):
        print("devmate 기능 테스트 START")
        # 로그인한 상태로 테스트 진행
        self.client.force_login(self.user1)

        # user1이 user2에게 devmate 신청
        response = self.client.post(
            reverse("devmates:devmate_create", kwargs={"pk": self.user2.id})
        )
        self.assertEqual(response.status_code, 302)  # 신청 성공

        # user2가 user1의 신청을 수락
        self.client.force_login(self.user2, backend=None)  # user2 로그인
        devmate_instance = DevMate.objects.get(
            sent_user=self.user1, received_user=self.user2
        )
        print(devmate_instance)
        response = self.client.post(
            reverse("devmates:devmate_update", kwargs={"pk": devmate_instance.id}),
            {"_method": "put"},
        )
        self.assertEqual(response.status_code, 302)  # 수락 성공

        # 다수 유저들의 devmate 생성(수락)
        for user in self.other_users:
            DevMate.objects.create(
                sent_user=self.user1, received_user=user, is_accepted=True
            )

        self.client.force_login(self.user1)  # user1 로그인

        # user1의 devmate 조회
        response = self.client.get(reverse("devmates:devmate_list"))
        self.assertEqual(response.status_code, 200)  # 조회 성공
        print("devmate 기능 테스트 END")
