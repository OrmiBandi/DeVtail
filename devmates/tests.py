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
        devmate_list: 로그인 한 유저의 devmate 조회
        devmate_recieved_list : 로그인 한 유저가 신청받은 devmate 조회
        devmate_create: devmate 신청
        devmate_update: devmate 수락
        devmate_delete: devmate 삭제
    """

    def setUp(self):
        # 유저 생성
        self.user1 = UserFactory()
        self.user2 = UserFactory()

        # 다른 유저들 생성
        self.other_users = [UserFactory() for _ in range(8)]

        # 로그인한 상태로 테스트 진행
        self.client.force_login(self.user1)

        # user1이 user2에게 devmate 신청
        response = self.client.post(
            reverse("devmates:devmate_create", kwargs={"pk": self.user2.id})
        )
        self.assertEqual(response.status_code, 200)  # 신청 성공

        # user2가 user1의 신청을 수락
        self.client.force_login(self.user2)  # user2 로그인
        devmate_instance = DevMateFactory.objects.get(
            sent_user=self.user1, received_user=self.user2
        )
        response = self.client.put(
            reverse("devmates:devmate_update", kwargs={"pk": devmate_instance.id})
        )
        self.assertEqual(response.status_code, 200)

        # devmate_instance를 저장
        self.devmate_instance = devmate_instance

    def test_devmate(self):
        # 다수 유저들의 devmate 생성(수락)
        for user in self.other_users:
            DevMateFactory(sent_user=self.user1, received_user=user, is_accepted=True)

        self.client.force_login(self.user1)  # user1 로그인

        # user1의 devmate 조회
        response = self.client.get(reverse("devmates:devmate_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)
        self.assertNotContains(
            response, self.user1.username
        )  # user1은 자신의 devmate 리스트에 미출력
