import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Blacklist
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestStudyJoin(TestCase):
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

    def test_apply_study_join(self):
        """
        스터디 신청 테스트
        """

        # user4으로 로그인 후 스터디 신청
        self.client.force_login(self.user4)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # 스터디 신청 확인
        # 스터디 신청 후에 스터디 가입 신청 리스트에 추가됨.
        # 이 때 해당 유저의 is_accepted는 False로 저장됨.
        self.assertEqual(StudyMember.objects.count(), 3)
        self.assertEqual(StudyMember.objects.last().user, self.user4)
        self.assertEqual(StudyMember.objects.last().is_accepted, False)

    def test_approve_study_join_not_author(self):
        """
        작성자가 아닌 유저가 스터디 가입 승인 테스트
        """

        # user4으로 로그인 후 스터디 신청
        self.client.force_login(self.user4)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # user2으로 로그인 후 스터디 가입 승인
        self.client.force_login(self.user2)
        studymember = StudyMember.objects.get(user=self.user4)
        response = self.client.post(
            reverse(
                "studies:approve_study_join",
                kwargs={"studymember_id": studymember.id},
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_approve_study_join_author(self):
        """
        작성자가 스터디 가입 승인 테스트
        """

        # user4으로 로그인 후 스터디 신청
        self.client.force_login(self.user4)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # user1으로 로그인 후 스터디 가입 승인
        self.client.force_login(self.user1)
        studymember = StudyMember.objects.get(user=self.user4)
        response = self.client.post(
            reverse(
                "studies:approve_study_join",
                kwargs={"studymember_id": studymember.id},
            ),
        )
        self.assertEqual(response.status_code, 302)

        # 스터디 가입 승인 확인
        # 스터디 가입 승인 후 스터디 멤버에 추가되고, 스터디 가입 신청 리스트에서 삭제됨.
        self.assertEqual(StudyMember.objects.count(), 3)
        self.assertEqual(StudyMember.objects.last().user, self.user4)
        self.assertEqual(StudyMember.objects.last().is_accepted, True)

    def test_reject_study_join_not_author(self):
        """
        작성자가 아닌 유저가 스터디 가입 거절 테스트
        """

        # user4으로 로그인 후 스터디 신청
        self.client.force_login(self.user4)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # user2으로 로그인 후 스터디 가입 거절
        self.client.force_login(self.user2)
        studymember = StudyMember.objects.get(user=self.user4)
        response = self.client.post(
            reverse(
                "studies:reject_study_join",
                kwargs={"studymember_id": studymember.id},
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_reject_study_join_author(self):
        """
        작성자가 스터디 가입 거절 테스트
        """

        # user4으로 로그인 후 스터디 신청
        self.client.force_login(self.user4)
        response = self.client.post(
            reverse("studies:apply_study_join", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)

        # user1으로 로그인 후 스터디 가입 거절
        self.client.force_login(self.user1)
        studymember = StudyMember.objects.get(user=self.user4)
        response = self.client.post(
            reverse(
                "studies:reject_study_join",
                kwargs={"studymember_id": studymember.id},
            ),
        )
        self.assertEqual(response.status_code, 302)

        # 스터디 가입 거절 확인
        # 스터디 가입 거절 후 스터디 가입 신청 리스트에서 삭제됨.
        self.assertEqual(StudyMember.objects.count(), 2)
