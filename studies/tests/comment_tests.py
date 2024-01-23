import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Comment, Recomment
from django.contrib.auth import get_user_model

User = get_user_model()


class TestComment(TestCase):
    def setUp(self):
        """
        1. 테스트용 데이터 생성
        1.1. 테스트용 유저 생성
        1.2. 테스트용 스터디 생성
        1.3. 테스트용 스터디 생성 데이터
        1.4. 테스트용 스터디 멤버 생성
        1.5. 테스트용 스터디 댓글 생성
        """
        self.user1 = User.objects.create_user(
            email="test1@naver.com", password="test1", nickname="test1"
        )
        self.user2 = User.objects.create_user(
            email="test2@naver.com", password="test2", nickname="test2"
        )
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
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False
        )
        self.study_create_data = Study.objects.values()[0]
        Comment.objects.create(study=self.study_object, user=self.user1, content="test")

    def test_comment_list(self):
        """
        2. 스터디의 댓글 조회 테스트
        2.1. 초기 세팅에서 댓글이 1개 생성되어 있고, 4개의 댓글을 추가 생성
        2.2. 스터디의 댓글이 5개인지 확인
        """
        print("---댓글 조회 테스트 시작---")
        for i in range(4):
            self.study_object.comments.create(user=self.user1, content=f"test{i}")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.count(), 5)
        print("---댓글 조회 테스트 종료---")

    def test_comment_create_without_login(self):
        """
        3. 스터디의 댓글 생성 테스트
        3-1. 스터디의 댓글을 생성하는 것은 로그인한 유저만 가능
        - 로그인하지 않은 유저로 댓글 생성 테스트 진행 시 302 응답을 반환
        """
        print("---로그인 하지 않은 유저로 댓글 생성 테스트 시작---")
        response = self.client.post("/study/1/comment/create/", {"content": "test"})
        self.assertEqual(response.status_code, 302)
        print("---로그인 하지 않은 유저로 댓글 생성 테스트 완료---")

    def test_comment_create_with_login(self):
        """
        3. 스터디의 댓글 생성 테스트
        3-1. 스터디의 댓글을 생성하는 것은 로그인한 유저만 가능
        - 기존 댓글이 1개 생성되어 있는지 확인
        - 테스트용 유저로 스터디 생성 테스트 진행 시 200 응답을 반환
        - 스터디 상세 페이지로 이동하여 댓글이 2개인지 확인
        """
        print("---로그인 한 유저로 댓글 생성 테스트 시작---")
        self.client.force_login(self.user1)
        self.assertEqual(self.study_object.comments.all().count(), 1)
        self.client.post("/study/1/comment/create/", {"content": "test"})
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.count(), 2)
        print("---로그인 한 유저로 댓글 생성 테스트 완료---")

    def test_comment_create_with_login_check_required_fields(self):
        """
        3. 스터디의 댓글 생성 테스트
        3-2. 스터디의 댓글 생성 유효성 검사
        - "content" 필드는 필수 입력 필드
        - "content" 필드에 값이 없을 경우 validation error 발생
        """
        print("---댓글 생성 유효성 검사 테스트 시작---")
        self.client.force_login(self.user1)
        response = self.client.post("/study/1/comment/create/", {"content": ""})
        self.assertEqual(response.context["form"].errors["content"], ["댓글을 입력해주세요."])
        print("---댓글 생성 유효성 검사 테스트 종료---")

    def test_comment_update_not_author(self):
        """
        4. 스터디의 댓글 수정 테스트
        4-1. 스터디의 댓글을 수정하는 것은 댓글을 생성한 유저만 가능
        - 기존 댓글이 "test"인지 확인
        - 댓글을 생성하지 않은 유저로 댓글 수정 테스트 진행 시 403 응답을 반환
        """

        print("---작성자가 아닌 유저로 댓글 수정 테스트 시작---")
        self.client.force_login(self.user2)
        self.assertEqual(self.study_object.comments.all()[0].content, "test")
        response = self.client.post(
            "/study/1/comment/1/update/", {"content": "update_test"}
        )
        self.assertEqual(response.status_code, 403)
        print("---작성자가 아닌 유저로 댓글 수정 테스트 완료---")

    def test_comment_update_author(self):
        """
        4. 스터디의 댓글 수정 테스트
        4-1. 스터디의 댓글을 수정하는 것은 댓글을 생성한 유저만 가능
        - 기존 댓글이 "test"인지 확인
        - 댓글을 생성한 유저로 댓글 수정 테스트 진행 시 200 응답을 반환
        - 댓글이 수정되었는지 확인하기 위해서 스터디 상세 페이지로 이동하여 댓글이 "update_test"인지 확인
        """

        print("---작성자인 유저로 댓글 수정 테스트 시작---")
        self.client.force_login(self.user1)
        self.assertEqual(self.study_object.comments.all()[0].content, "test")
        self.client.post("/study/1/comment/1/update/", {"content": "update_test"})
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].content, "update_test"
        )
        print("---로그인 한 유저로 댓글 수정 테스트 완료---")

    def test_comment_update_author_check_required_fields(self):
        """
        4. 스터디의 댓글 수정 테스트
        4-2. 스터디의 댓글 수정 유효성 검사
        - 기존 댓글이 "test"인지 확인
        - "content" 필드는 필수 입력 필드
        - "content" 필드에 값이 없을 경우 validation error 발생
        """
        print("---댓글 수정 유효성 검사 테스트 시작---")
        self.client.force_login(self.user1)
        self.assertEqual(self.study_object.comments.all()[0].content, "test")
        response = self.client.post("/study/1/comment/1/update/", {"content": ""})
        self.assertEqual(response.context["form"].errors["content"], ["댓글을 입력해주세요."])
        print("---댓글 수정 유효성 검사 테스트 종료---")

    def test_comment_delete_not_author(self):
        """
        5. 스터디의 댓글 삭제 테스트
        5-1. 스터디의 댓글을 삭제하는 것은 댓글을 생성한 유저만 가능
        - 기존 댓글이 1개 생성되어 있는지 확인
        - 댓글을 생성하지 않은 유저로 댓글 삭제 테스트 진행 시 403 응답을 반환
        """
        print("---댓글 삭제 테스트 시작---")

        print("---작성자가 아닌 유저로 댓글 삭제 테스트 시작---")
        self.client.force_login(self.user2)
        self.assertEqual(self.study_object.comments.all().count(), 1)
        response = self.client.post("/study/1/comment/1/delete/")
        self.assertEqual(response.status_code, 403)
        print("---작성자가 아닌 유저로 댓글 삭제 테스트 완료---")

    def test_comment_delete_author(self):
        """
        5. 스터디의 댓글 삭제 테스트
        5-1. 스터디의 댓글을 삭제하는 것은 댓글을 생성한 유저만 가능
        - 기존 댓글이 1개 생성되어 있는지 확인
        - 댓글을 생성한 유저로 댓글 삭제 테스트 진행 시 200 응답을 반환
        - 댓글이 삭제되었는지 확인하기 위해서 스터디 상세 페이지로 이동하여 댓글이 0개인지 확인
        """
        print("---작성자인 유저로 댓글 삭제 테스트 시작---")
        self.client.force_login(self.user1)
        self.assertEqual(self.study_object.comments.all().count(), 1)
        self.client.post("/study/1/comment/1/delete/")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.all().count(), 0)
        print("---작성자인 유저로 댓글 삭제 테스트 완료---")


class TestRecomment(TestCase):
    def setUp(self):
        """
        1. 테스트용 데이터 생성
        1.1. 테스트용 유저 생성
        1.2. 테스트용 스터디 생성
        1.3. 테스트용 스터디 생성 데이터
        1.4. 테스트용 스터디 멤버 생성
        1.5. 테스트용 스터디 댓글 생성
        1.6. 테스트용 스터디 대댓글 생성
        """
        self.user1 = User.objects.create_user(
            email="test1@naver.com", password="test1", nickname="test1"
        )
        self.user2 = User.objects.create_user(
            email="test2@naver.com", password="test2", nickname="test2"
        )
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
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False
        )
        self.study_create_data = Study.objects.values()[0]
        Comment.objects.create(study=self.study_object, user=self.user1, content="test")
        Recomment.objects.create(
            comment=Comment.objects.get(pk=1), user=self.user1, content="test"
        )

    def test_recomment_list(self):
        """
        2. 스터디의 댓글의 대댓글 조회 테스트
        2.1. 초기 세팅에서 댓글이 1개, 대댓글이 1개 생성되어 있음.
        2.2. 스터디의 댓글의 대댓글이 1개인지 확인
        """
        print("---대댓글 조회 테스트 시작---")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].comments.count(), 1)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 1
        )
        print("---대댓글 조회 테스트 종료---")

    def test_recomment_create_without_login(self):
        """
        3. 스터디의 댓글의 대댓글 생성 테스트
        3-1. 스터디의 댓글의 대댓글을 생성하는 것은 로그인한 유저만 가능
        - 기존 대댓글이 1개 생성되어 있는지 확인
        - 로그인하지 않은 유저로 대댓글 생성 테스트 진행 시 302 응답을 반환
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 1
        )

        print("---로그인 하지 않은 유저로 대댓글 생성 테스트 시작---")
        response = self.client.post(
            "/study/1/comment/1/recomment/", {"content": "test"}
        )
        self.assertEqual(response.status_code, 302)
        print("---로그인 하지 않은 유저로 대댓글 생성 테스트 완료---")

    def test_recomment_create_with_login(self):
        """
        3. 스터디의 댓글의 대댓글 생성 테스트
        3-1. 스터디의 댓글의 대댓글을 생성하는 것은 로그인한 유저만 가능
        - 기존 대댓글이 1개 생성되어 있는지 확인
        - 로그인 한 유저로 대댓글 생성 테스트 진행 시 200 응답을 반환
        - 스터디 상세 페이지로 이동하여 대댓글이 2개인지 확인
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 1
        )

        print("---로그인 한 유저로 대댓글 생성 테스트 시작---")
        self.client.force_login(self.user2)
        self.client.post("/study/1/comment/1/recomment/", {"content": "test"})
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.count(), 2
        )
        print("---로그인 한 유저로 대댓글 생성 테스트 완료---")

    def test_recomment_create_login_check_required_fields(self):
        """
        3. 스터디의 댓글의 대댓글 생성 테스트
        3-2. 스터디의 댓글의 대댓글 생성 유효성 검사
        - "content" 필드는 필수 입력 필드
        - "content" 필드에 값이 없을 경우 validation error 발생
        """
        print("---대댓글 생성 유효성 검사 테스트 시작---")
        self.client.force_login(self.user1)
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": ""}
        )
        self.assertEqual(response.context["form"].errors["content"], ["대댓글을 입력해주세요."])
        print("---대댓글 수정 유효성 검사 테스트 종료---")

    def test_recomment_update_not_author(self):
        """
        4. 스터디의 댓글의 대댓글 수정 테스트
        4-1. 스터디의 댓글의 대댓글을 수정하는 것은 대댓글을 생성한 유저만 가능
        - 기존 대댓글의 내용이 "test"인지 확인
        - 대댓글을 생성하지 않은 유저로 대댓글 수정 테스트 진행 시 403 응답을 반환
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all()[0].content,
            "test",
        )

        print("---대댓글의 작성자가 아닌 유저로 대댓글 수정 테스트 시작---")
        self.client.force_login(self.user2)
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": "update_test"}
        )
        self.assertEqual(response.status_code, 403)
        print("---대댓글의 작성자가 아닌 유저로 대댓글 수정 테스트 완료---")

    def test_recomment_update_author(self):
        """
        4. 스터디의 댓글의 대댓글 수정 테스트
        4-1. 스터디의 댓글의 대댓글을 수정하는 것은 대댓글을 생성한 유저만 가능
        - 기존 대댓글의 내용이 "test"인지 확인
        - 대댓글을 생성한 유저로 대댓글 수정 테스트 진행 시 200 응답을 반환
        - 대댓글이 수정되었는지 확인하기 위해서 스터디 상세 페이지로 이동하여 대댓글이 "update_test"인지 확인
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all()[0].content,
            "test",
        )

        print("---대댓글의 작성자로 대댓글 수정 테스트 시작---")
        self.client.force_login(self.user1)
        self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": "update_test"}
        )
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all()[0].content,
            "update_test",
        )
        print("---대댓글의 작성자로 대댓글 수정 테스트 완료---")

    def test_recomment_update_author_check_required_fields(self):
        """
        4. 스터디의 댓글의 대댓글 수정 테스트
        4-2. 스터디의 댓글의 대댓글 수정 유효성 검사
        - 기존 대댓글의 내용이 "test"인지 확인
        - "content" 필드는 필수 입력 필드
        - "content" 필드에 값이 없을 경우 validation error 발생
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all()[0].content,
            "test",
        )

        print("---대댓글 수정 유효성 검사 테스트 시작---")
        self.client.force_login(self.user1)
        response = self.client.post(
            "/study/1/comment/1/recomment/1/update/", {"content": ""}
        )
        self.assertEqual(response.context["form"].errors["content"], ["대댓글을 입력해주세요."])
        print("---대댓글 수정 유효성 검사 테스트 종료---")

    def test_recomment_delete_not_author(self):
        """
        5. 스터디의 댓글의 대댓글 삭제 테스트
        5-1. 스터디의 댓글의 대댓글을 삭제하는 것은 대댓글을 생성한 유저만 가능
        - 기존 대댓글이 1개 생성되어 있는지 확인
        - 작성자가 아닌 유저가 대댓글을 삭제하려고 할 경우 403 에러 발생
        """

        self.assertEqual(
            self.study_object.comments.all()[0].recomments.all().count(), 1
        )

        print("---대댓글의 작성자가 아닌 유저로 대댓글 삭제 테스트 시작---")
        self.client.force_login(self.user2)
        response = self.client.post("/study/1/comment/1/recomment/1/delete/")
        self.assertEqual(response.status_code, 403)
        print("---대댓글의 작성자가 아닌 유저로 대댓글 삭제 테스트 완료---")

    def test_recomment_delete_author(self):
        """
        5. 스터디의 댓글의 대댓글 삭제 테스트
        5-1. 스터디의 댓글의 대댓글을 삭제하는 것은 대댓글을 생성한 유저만 가능
        - 기존 대댓글이 1개 생성되어 있는지 확인
        - 작성자인 유저가 대댓글을 삭제하려고 할 경우 200 응답 반환
        - 대댓글이 삭제되었는지 확인하기 위해서 스터디 상세 페이지로 이동하여 대댓글이 0개인지 확인
        """

        self.assertEqual(
            self.study_object.comments.all()[0].recomments.all().count(), 1
        )

        print("---대댓글의 작성자로 대댓글 삭제 테스트 시작---")
        self.client.force_login(self.user1)
        self.client.post("/study/1/comment/1/recomment/1/delete/")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["study"].comments.all()[0].recomments.all().count(), 0
        )
        print("---대댓글의 작성자로 대댓글 삭제 테스트 완료---")
