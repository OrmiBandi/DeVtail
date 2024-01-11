from django.test import TestCase
from django.urls import reverse
from .factories import UserFactory, DevMateFactory


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
        devmate-create: devmate 신청
        devmate-list: 로그인 한 유저의 devmate 조회
        devmate-accept: devmate 수락
    """

    def setUp(self):
        # 유저 생성
        self.user1 = UserFactory()
        self.user2 = UserFactory()

        # 다른 유저들 생성
        self.other_users = [UserFactory() for _ in range(8)]

        # 로그인한 상태로 테스트 진행
        self.client.force_login(self.user1)

    def test_devmate(self):
        # user1이 user2에게 devmate 신청
        response = self.client.post(
            reverse("devmate-create"), {"received_user": self.user2.id}
        )
        self.assertEqual(response.status_code, 200)  # 신청 성공

        self.client.force_login(self.user2)  # user2 로그인

        # user2가 user1에게 devmate 신청 (신청 불가)
        response = self.client.post(
            reverse("devmate-create"), {"received_user": self.user1.id}
        )
        self.assertEqual(response.status_code, 400)  # 이미 신청이 되어있으므로 에러 반환

        # user2가 user1의 신청을 수락
        response = self.client.post(
            reverse("devmate-accept", args=[self.devmate_instance.id])
        )
        self.assertEqual(response.status_code, 200)

        # 다수 유저들의 devmate 생성(수락)
        for user in self.other_users:
            DevMateFactory(sent_user=self.user1, received_user=user, is_accepted=True)

        self.client.force_login(self.user1)  # user1 로그인

        # user1의 devmate 조회
        response = self.client.get(reverse("devmate-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)
        self.assertNotContains(
            response, self.user1.username
        )  # user1은 자신의 devmate 리스트에 미출력
