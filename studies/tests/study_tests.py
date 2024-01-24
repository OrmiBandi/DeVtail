import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestStudy(TestCase):
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

    def test_study_list(self):
        """
        스터디 조회 테스트
        """
        response = self.client.get("/study/list/")
        self.assertEqual(response.status_code, 200)

        # 기존 스터디 1개 조회
        self.assertEqual(len(response.context["studies"]), 1)

    def test_study_detail(self):
        """
        스터디 상세 조회 테스트
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)

        # 기존 스터디 title이 test인지 확인
        self.assertEqual(response.context["study"].title, "test")

    def test_study_create_without_login(self):
        """
        로그인 하지 않은 유저로 스터디 생성 테스트
        """
        response = self.client.post(
            reverse("studies:study_create"), self.study_create_data
        )

        # 스터디 생성은 로그인이 필요하므로 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 로그인 페이지로 리다이렉트
        self.assertIn("/accounts/login/", response.url)

    def test_study_create_with_login(self):
        """
        로그인한 유저로 스터디 생성 테스트
        """

        # user1으로 로그인 후 스터디 생성 요청
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("studies:study_create"), self.study_create_data
        )

        # 스터디 생성 성공
        self.assertEqual(response.status_code, 200)

    def test_study_create_with_login_check_required_fields_category(self):
        """
        필수 입력 필드 유효성 검사
        - 카테고리 누락 테스트
        """

        # user1으로 로그인 후 카테고리에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_category = self.study_create_data.copy()
        study_create_test_data_without_category["category"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_category
        )

        # 카테고리에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["category"][0], "카테고리를 선택해주세요."
        )

    def test_study_create_with_login_check_required_fields_goal(self):
        """
        필수 입력 필드 유효성 검사
        - 목표 누락 테스트
        """

        # user1으로 로그인 후 목표에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_goal = self.study_create_data.copy()
        study_create_test_data_without_goal["goal"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_goal
        )

        # 목표에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["goal"][0], "목표를 입력해주세요.")

    def test_study_create_with_login_check_required_fields_category_start_at_first(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 시작일 누락 테스트
        """

        # user1으로 로그인 후 시작일에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_start_at = self.study_create_data.copy()
        study_create_test_data_without_start_at["start_at"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_start_at
        )

        # 시작일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["start_at"][0], "시작일을 입력해주세요.")

    def test_study_create_with_login_check_required_fields_category_start_at_second(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 시작일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1으로 로그인 후 시작일에 오늘 이전의 날짜를 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_start_at = self.study_create_data.copy()
        study_create_test_data_without_start_at["start_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_start_at
        )

        # 시작일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )

    def test_study_create_with_login_check_required_fields_category_end_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 누락 테스트
        """

        # user1으로 로그인 후 종료일에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_end_at = self.study_create_data.copy()
        study_create_test_data_without_end_at["end_at"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_end_at
        )

        # 종료일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["end_at"][0], "종료일을 입력해주세요.")

    def test_study_create_with_login_check_required_fields_category_end_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1으로 로그인 후 종료일에 오늘 이전의 날짜를 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_end_at = self.study_create_data.copy()
        study_create_test_data_without_end_at["end_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_end_at
        )

        # 종료일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )

    def test_study_create_with_login_check_required_fields_category_difficulty(self):
        """
        필수 입력 필드 유효성 검사
        - 난이도 누락 테스트
        """

        # user1으로 로그인 후 난이도에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_difficulty = self.study_create_data.copy()
        study_create_test_data_without_difficulty["difficulty"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_difficulty
        )

        # 난이도에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["difficulty"][0], "난이도를 선택해주세요."
        )

    def test_study_create_with_login_check_required_fields_category_max_member_first(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 누락 테스트
        """

        # user1으로 로그인 후 최대 인원에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_max_member = self.study_create_data.copy()
        study_create_test_data_without_max_member["max_member"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_max_member
        )

        # 최대 인원에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원을 입력해주세요."
        )

    def test_study_create_with_login_check_required_fields_category_max_member_second(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 추가 유효성 테스트 [최대 인원은 2명 이상]
        """

        # user1으로 로그인 후 최대 인원에 1을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)
        study_create_test_data_without_max_member = self.study_create_data.copy()
        study_create_test_data_without_max_member["max_member"] = 1
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_max_member
        )

        # 최대 인원에 1이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원은 2명 이상이어야 합니다."
        )

    def test_study_update_not_author(self):
        """
        작성자가 아닌 유저로 스터디 수정 테스트
        """
        study_update_test_data = self.study_create_data.copy()

        # user2로 로그인 후 스터디 수정 요청
        self.client.force_login(self.user2)
        study_update_test_data["title"] = "test_change"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data,
        )

        # user2에게는 스터디 수정 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_study_update_author(self):
        """
        작성자인 유저로 스터디 수정 테스트
        """
        study_update_test_data = self.study_create_data.copy()

        # user1로 로그인 후 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data["title"] = "test_change"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data,
        )

        # user1에게는 스터디 수정 권한이 있으므로 200 리턴
        self.assertEqual(response.status_code, 200)

    def test_study_update_author_check_required_fields_category(self):
        """
        필수 입력 필드 유효성 검사
        - 카테고리 누락 테스트
        """

        # user1로 로그인 후 카테고리에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_category = self.study_create_data.copy()
        study_update_test_data_without_category["category"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_category,
        )

        # 카테고리에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["category"][0], "카테고리를 선택해주세요."
        )

    def test_study_update_author_check_required_fields_goal(self):
        """
        필수 입력 필드 유효성 검사
        - 목표 누락 테스트
        """

        # user1로 로그인 후 목표에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_goal = self.study_create_data.copy()
        study_update_test_data_without_goal["goal"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_goal,
        )

        # 목표에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["goal"][0], "목표를 입력해주세요.")

    def test_study_update_author_check_required_fields_start_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 시작일 누락 테스트
        """

        # user1로 로그인 후 시작일에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_start_at = self.study_create_data.copy()
        study_update_test_data_without_start_at["start_at"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_start_at,
        )

        # 시작일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["start_at"][0], "시작일을 입력해주세요.")

    def test_study_update_author_check_required_fields_start_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 시작일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1로 로그인 후 시작일에 오늘 이전의 날짜를 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_start_at = self.study_create_data.copy()
        study_update_test_data_without_start_at["start_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_start_at,
        )

        # 시작일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )

    def test_study_update_author_check_required_fields_end_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 누락 테스트
        """

        # user1로 로그인 후 종료일에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_end_at = self.study_create_data.copy()
        study_update_test_data_without_end_at["end_at"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_end_at,
        )

        # 종료일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(response.context["form"].errors["end_at"][0], "종료일을 입력해주세요.")

    def test_study_update_author_check_required_fields_end_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1로 로그인 후 종료일에 오늘 이전의 날짜를 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_end_at = self.study_create_data.copy()
        study_update_test_data_without_end_at["end_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_end_at,
        )

        # 종료일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )

    def test_study_update_author_check_required_fields_difficulty(self):
        """
        필수 입력 필드 유효성 검사
        - 난이도 누락 테스트
        """

        # user1로 로그인 후 난이도에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_difficulty = self.study_create_data.copy()
        study_update_test_data_without_difficulty["difficulty"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_difficulty,
        )

        # 난이도에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["difficulty"][0], "난이도를 선택해주세요."
        )

    def test_study_update_author_check_required_fields_max_member_first(self):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 누락 테스트
        """

        # user1로 로그인 후 최대 인원에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_max_member = self.study_create_data.copy()
        study_update_test_data_without_max_member["max_member"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_max_member,
        )

        # 최대 인원에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원을 입력해주세요."
        )

        # 최대 인원 추가 유효성 테스트 [최대 인원은 2명 이상]
        self.client.force_login(self.user1)
        study_update_test_data_without_max_member = self.study_create_data.copy()
        study_update_test_data_without_max_member["max_member"] = 1
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_max_member,
        )
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원은 2명 이상이어야 합니다."
        )

    def test_study_update_author_check_required_fields_max_member_second(self):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 추가 유효성 테스트 [최대 인원은 2명 이상]
        """

        # user1로 로그인 후 최대 인원에 1을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)
        study_update_test_data_without_max_member = self.study_create_data.copy()
        study_update_test_data_without_max_member["max_member"] = 1
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_max_member,
        )

        # 최대 인원에 1이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원은 2명 이상이어야 합니다."
        )

    def test_study_delete_not_author(self):
        """
        작성자가 아닌 유저로 스터디 삭제 테스트
        """

        # user2로 로그인 후 스터디 삭제 요청
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("studies:study_delete", kwargs={"pk": 1}),
        )

        # user2에게는 스터디 삭제 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_study_delete_author(self):
        """
        작성자인 유저로 스터디 삭제 테스트
        """

        # user1로 로그인 후 스터디 삭제 요청
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("studies:study_delete", kwargs={"pk": 1}),
        )

        # 스터디 삭제 성공 시 302 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 스터디 삭제 확인
        self.assertEqual(response.url, "/study/list/")
        self.assertEqual(Study.objects.count(), 0)
