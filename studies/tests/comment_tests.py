import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Comment, Recomment
from django.contrib.auth import get_user_model

User = get_user_model()


class TestComment(TestCase):
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

        # 테스트용 스터디 생성 데이터
        self.study_object = Study.objects.get(pk=1)

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False
        )

        # 테스트용 스터디 댓글 생성
        self.study_create_data = Study.objects.values()[0]
        Comment.objects.create(study=self.study_object, user=self.user1, content="test")

    def test_comment_list(self):
        """
        댓글 조회 테스트
        """

        # 기존 댓글 1개 조회
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.count(), 1)

    def test_comment_create_without_login(self):
        """
        로그인하지 않은 유저로 댓글 생성 테스트
        """
        response = self.client.post("/study/1/comment/create/", {"content": "test"})

        # 댓글 생성은 로그인이 필요하므로 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 로그인 페이지로 리다이렉트
        self.assertIn("accounts/login", response.url)

    def test_comment_create_with_login(self):
        """
        로그인 한 유저로 댓글 생성 테스트
        """

        # user1으로 로그인 후 댓글 생성 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post("/study/1/comment/create/", {"content": "test"})

        # 댓글 생성 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 댓글 생성 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)

        # 기존 댓글 1개 + 새로운 댓글 1개 = 총 댓글 2개
        self.assertEqual(response.context["study"].comments.count(), 2)

    def test_comment_create_with_login_check_required_fields(self):
        """
        댓글 생성 유효성 검사
        """

        # user1으로 로그인 후 댓글 생성 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post("/study/1/comment/create/", {"content": ""})

        # 댓글에 빈 값이 들어오면 ValidationError 발생
        self.assertEqual(response.context["form"].errors["content"], ["댓글을 입력해주세요."])

    def test_comment_update_not_author(self):
        """
        작성자가 아닌 유저로 댓글 수정 테스트
        """

        # user2로 로그인 후 댓글 수정 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post(
            "/study/1/comment/1/update/", {"content": "update_test"}
        )

        # user2에게는 댓글 수정 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_comment_update_author(self):
        """
        작성자인 유저로 댓글 수정 테스트
        """

        # user1로 로그인 후 댓글 수정 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post(
            "/study/1/comment/1/update/", {"content": "update_test"}
        )

        # 댓글 수정 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 댓글 수정 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].content, "update_test"
        )

    def test_comment_update_author_check_required_fields(self):
        """
        댓글 수정 유효성 검사
        """

        # user1로 로그인 후 댓글 수정 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post("/study/1/comment/1/update/", {"content": ""})

        # 댓글에 빈 값이 들어오면 ValidationError 발생
        self.assertEqual(response.context["form"].errors["content"], ["댓글을 입력해주세요."])

    def test_comment_delete_not_author(self):
        """
        작성자가 아닌 유저로 댓글 삭제 테스트
        """

        # user2로 로그인 후 댓글 삭제 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post("/study/1/comment/1/delete/")

        # user2에게는 댓글 삭제 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_comment_delete_author(self):
        """
        작성자인 유저로 댓글 삭제 테스트
        """

        # user1로 로그인 후 댓글 삭제 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post("/study/1/comment/1/delete/")

        # 댓글 삭제 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 댓글 삭제 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.all().count(), 0)


class TestRecomment(TestCase):
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

        # 테스트용 스터디 생성 데이터
        self.study_object = Study.objects.get(pk=1)

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False
        )
        self.study_create_data = Study.objects.values()[0]

        # 테스트용 스터디 댓글 생성
        Comment.objects.create(study=self.study_object, user=self.user1, content="test")

        # 테스트용 스터디 대댓글 생성
        Recomment.objects.create(
            comment=Comment.objects.get(pk=1), user=self.user1, content="test"
        )
        
    def test_recomment_list(self):
        """
        대댓글 조회 테스트
        """
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)

        # 기존 대댓글 1개 조회
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 1
        )

    def test_recomment_create_without_login(self):
        """
        로그인하지 않은 유저로 대댓글 생성 테스트
        """
        response = self.client.post(
            "/study/1/comment/1/recomment/", {"content": "test"}
        )

        # 대댓글 생성은 로그인이 필요하므로 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 로그인 페이지로 리다이렉트
        self.assertIn("accounts/login", response.url)

    def test_recomment_create_with_login(self):
        """
        로그인 한 유저로 대댓글 생성 테스트
        """

        # user2로 로그인 후 대댓글 생성 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post(
            "/study/1/comment/1/recomment/", {"content": "test"}
        )

        # 대댓글 생성 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)
        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 대댓글 생성 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 2
        )

    def test_recomment_create_login_check_required_fields(self):
        """
        대댓글 생성 유효성 검사
        """

        # user2로 로그인 후 대댓글 생성 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post("/study/1/comment/1/recomment/", {"content": ""})

        # 대댓글에 빈 값이 들어오면 ValidationError 발생
        self.assertEqual(response.context["form"].errors["content"], ["대댓글을 입력해주세요."])

    def test_recomment_update_not_author(self):
        """
        작성자가 아닌 유저로 대댓글 수정 테스트
        """

        # user2로 로그인 후 대댓글 수정 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": "update_test"}
        )

        # user2에게는 대댓글 수정 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_recomment_update_author(self):
        """
        작성자인 유저로 대댓글 수정 테스트
        """

        # user1로 로그인 후 대댓글 수정 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": "update_test"}
        )

        # 대댓글 수정 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 대댓글 수정 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all()[0].content,
            "update_test",
        )

    def test_recomment_update_author_check_required_fields(self):
        """
        대댓글 수정 유효성 검사
        """

        # user1로 로그인 후 대댓글 수정 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": ""}
        )

        # 대댓글에 빈 값이 들어오면 ValidationError 발생
        self.assertEqual(response.context["form"].errors["content"], ["대댓글을 입력해주세요."])

    def test_recomment_delete_not_author(self):
        """
        작성자가 아닌 유저로 대댓글 삭제 테스트
        """

        # user2로 로그인 후 대댓글 삭제 요청
        self.client.login(email="test2@naver.com", password="test2")
        response = self.client.post("/study/1/comment/1/recomment/1/delete/")

        # user2에게는 대댓글 삭제 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_recomment_delete_author(self):
        """
        작성자인 유저로 대댓글 삭제 테스트
        """

        # user1로 로그인 후 대댓글 삭제 요청
        self.client.login(email="test1@naver.com", password="test1")
        response = self.client.post("/study/1/comment/1/recomment/1/delete/")

        # 대댓글 삭제 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 상세 페이지로 리다이렉트
        self.assertIn("study/1/", response.url)

        # 대댓글 삭제 확인
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all().count(), 0
        )
