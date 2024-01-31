import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Blacklist
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestBlacklist(TestCase):
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
        self.user3 = User.objects.create_user(
            email="test3@naver.com", password="test3", nickname="test3"
        )
        self.user4 = User.objects.create_user(
            email="test4@naver.com", password="test4", nickname="test4"
        )

        # 테스트용 스터디 생성
        self.category = Category.objects.create(name="test")
        Study.objects.create(
            category=self.category,
            goal="test",
            title="test",
            introduce="test",
            start_at=datetime.date.today(),
            end_at=datetime.date.today(),
            difficulty=Study.difficulty_choices[0][0],
            max_member=10,
        )

        self.study_object = Study.objects.get(pk=1)

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False
        )

        # 테스트용 블랙리스트 생성
        Blacklist.objects.create(user=self.user3, study=self.study_object)

    def test_blacklist_create_not_author(self):
        """
        작성자가 아닌 유저가 블랙리스트 생성 테스트
        """
        # 블랙리스트 생성
        # user2으로 로그인 후 user1를 블랙리스트에 추가
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse(
                "studies:add_blacklist_user",
                kwargs={"pk": 1, "studymember_id": self.user1.id},
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_blacklist_create_author(self):
        """
        작성한 유저로 블랙리스트 생성 테스트
        """

        # user1으로 로그인 후 user2를 블랙리스트에 추가
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse(
                "studies:add_blacklist_user",
                kwargs={"pk": 1, "studymember_id": self.user2.id},
            ),
        )
        self.assertEqual(response.status_code, 302)

        # 블랙리스트 생성 확인
        # 기존 블랙리스트에 user3이 있고, user2가 추가되었는지 확인
        self.assertEqual(Blacklist.objects.count(), 2)
        self.assertEqual(Blacklist.objects.first().user, self.user3)
        self.assertEqual(Blacklist.objects.last().user, self.user2)

        # 블랙리스트 생성 후 스터디 멤버에서 삭제되었는지 확인
        self.assertEqual(StudyMember.objects.count(), 1)
        self.assertEqual(StudyMember.objects.first().user, self.user1)

    def test_blacklist_list_not_author(self):
        """
        작성자가 아닌 유저가 블랙리스트 조회 테스트
        """

        # user2으로 로그인 후 블랙리스트 조회
        self.client.force_login(self.user2)
        response = self.client.get(
            reverse("studies:blacklist_user_list", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 403)

    def test_blacklist_list_author(self):
        """
        작성자인 유저가 블랙리스트 조회 테스트
        """

        # user1으로 로그인 후 블랙리스트 조회
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("studies:blacklist_user_list", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 200)

        # 블랙리스트 조회 확인
        # 기존 블랙리스트에 user3이 생성되어있음.
        self.assertEqual(Blacklist.objects.count(), 1)
        self.assertEqual(Blacklist.objects.first().user, self.user3)

    def test_blacklist_delete_not_author(self):
        """
        작성자가 아닌 유저가 블랙리스트 삭제 테스트
        """

        # user2으로 로그인 후 user3를 블랙리스트에서 삭제
        self.client.force_login(self.user2)
        blacklist_user = Blacklist.objects.get(user=self.user3)
        response = self.client.post(
            reverse(
                "studies:delete_blacklist_user",
                kwargs={
                    "pk": 1,
                    "blacklist_id": blacklist_user.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_blacklist_delete_author(self):
        """
        작성자인 유저가 블랙리스트 삭제 테스트
        """

        # user1으로 로그인 후 user3를 블랙리스트에서 삭제
        self.client.force_login(self.user1)
        blacklist_user = Blacklist.objects.get(user=self.user3)
        response = self.client.post(
            reverse(
                "studies:delete_blacklist_user",
                kwargs={
                    "pk": 1,
                    "blacklist_id": blacklist_user.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 302)

        # 블랙리스트 삭제 확인
        # 기존 블랙리스트에 user3이 삭제되었는지 확인
        self.assertEqual(Blacklist.objects.count(), 0)

    def test_blacklist_user_apply_study_join(self):
        """
        블랙리스트 유저가 스터디 신청 테스트
        """

        # user3으로 로그인 후 스터디 신청
        self.client.force_login(self.user3)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # 스터디 신청 확인
        # 스터디 신청 후에 스터디 가입 신청 리스트에 추가되지 않음.
        self.assertEqual(StudyMember.objects.count(), 2)
