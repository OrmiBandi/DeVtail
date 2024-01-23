import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestStudy(TestCase):
    def setUp(self):
        """
        1. 테스트용 데이터 생성
        1.1. 테스트용 유저 생성
        1.2. 테스트용 스터디 생성
        1.3. 테스트용 스터디 생성 데이터
        1.4. 테스트용 스터디 멤버 생성
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

    def test_study_list(self):
        """
        2. 스터디 조회 테스트
        2.1. 테스트용 스터디 4개 생성
        2.2. 스터디 조회 테스트
        - 스터디 조회 테스트는 setUp에서 만든 스터디 1개와 합쳐서 총 5개의 스터디가 조회되는지 확인
        """
        # 2-1. 테스트용 스터디 4개 생성
        for i in range(4):
            category = Category.objects.create(name=f"test{i}")
            study = Study.objects.create(
                title=f"test{i}",
                category=category,
                start_at=datetime.date.today(),
                end_at=datetime.date.today(),
                difficulty=Study.difficulty_choices[0][0],
                max_member=10,
                current_member=0,
            )
            StudyMember.objects.create(study=study, user=self.user1, is_manager=True)

        # 2-2. 스터디 조회 테스트
        print("---스터디 조회 테스트 시작---")
        response = self.client.get("/study/list/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["studies"]), 5)
        print("---스터디 조회 테스트 종료---")

    def test_study_detail(self):
        """
        3. 스터디 상세 조회 테스트
        3.1. setUp에서 만든 스터디 1개의 title이 "test"인지 확인
        """
        print("---스터디 상세 조회 테스트 시작---")
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["study"].title, "test")
        print("---스터디 상세 조회 테스트 종료---")

    def test_study_create_without_login(self):
        """
        4. 스터디 생성 테스트
        4-1. 스터디를 생성하는 것은 로그인한 유저만 가능
        - 로그인하지 않은 유저로 스터디 생성 테스트 진행 시 302 응답을 반환
        """
        print("---로그인하지 않은 유저로 스터디 생성 테스트 시작---")
        study_create_test_data = self.study_create_data.copy()
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data
        )
        self.assertEqual(response.status_code, 302)
        print("---로그인하지 않은 유저로 스터디 생성 테스트 종료---")

    def test_study_create_with_login(self):
        """
        4. 스터디 생성 테스트
        4-1. 스터디를 생성하는 것은 로그인한 유저만 가능
        - 테스트용 유저로 스터디 생성 테스트 진행 시 200 응답을 반환
        """
        study_create_test_data = self.study_create_data.copy()

        print("---로그인한 유저로 스터디 생성 테스트 시작---")
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data
        )
        self.assertEqual(response.status_code, 200)
        print("---로그인한 유저로 스터디 생성 테스트 종료---")

    def test_study_create_with_login_check_required_fields(self):
        """
        4. 스터디 생성 테스트
        4-2. 스터디 생성 유효성 검사
        - 테스트용 유저로 진행 시 200 응답을 반환
        - "category", "start_at", "end_at", "difficulty", "max_member" 필드는 필수 입력 필드
        - 필수 입력 필드는 빈 값으로 들어오면 forms.ValidationError를 반환
        """

        print("---필수 입력 필드 유효성 테스트 시작---")

        print("---카테고리 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_category = self.study_create_data.copy()
        study_create_test_data_without_category["category"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_category
        )
        self.assertEqual(
            response.context["form"].errors["category"][0], "카테고리를 선택해주세요."
        )
        self.assertEqual(response.status_code, 200)
        print("---카테고리 누락 테스트 종료---")

        print("---목표 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_goal = self.study_create_data.copy()
        study_create_test_data_without_goal["goal"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_goal
        )
        self.assertEqual(response.context["form"].errors["goal"][0], "목표를 입력해주세요.")
        print("---목표 누락 테스트 종료---")

        print("---시작일 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_start_at = self.study_create_data.copy()
        study_create_test_data_without_start_at["start_at"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_start_at
        )
        self.assertEqual(response.context["form"].errors["start_at"][0], "시작일을 입력해주세요.")
        print("---시작일 누락 테스트 종료---")

        print("---시작일 추가 유효성 테스트 시작 [오늘 이전의 날짜 선택 불가능]---")
        self.client.force_login(self.user1)
        study_create_test_data_without_start_at = self.study_create_data.copy()
        study_create_test_data_without_start_at["start_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_start_at
        )
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )
        print("---시작일 추가 유효성 테스트 종료---")

        print("---종료일 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_end_at = self.study_create_data.copy()
        study_create_test_data_without_end_at["end_at"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_end_at
        )
        self.assertEqual(response.context["form"].errors["end_at"][0], "종료일을 입력해주세요.")
        print("---종료일 누락 테스트 종료---")

        print("---종료일 추가 유효성 테스트 시작 [오늘 이전의 날짜 선택 불가능]---")
        self.client.force_login(self.user1)
        study_create_test_data_without_end_at = self.study_create_data.copy()
        study_create_test_data_without_end_at["end_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_end_at
        )
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )
        print("---종료일 추가 유효성 테스트 종료---")

        print("---난이도 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_difficulty = self.study_create_data.copy()
        study_create_test_data_without_difficulty["difficulty"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_difficulty
        )
        self.assertEqual(
            response.context["form"].errors["difficulty"][0], "난이도를 선택해주세요."
        )
        print("---난이도 누락 테스트 종료---")

        print("---최대 인원 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_create_test_data_without_max_member = self.study_create_data.copy()
        study_create_test_data_without_max_member["max_member"] = ""
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_max_member
        )
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원을 입력해주세요."
        )
        print("---최대 인원 누락 테스트 종료---")

        print("---최대 인원 추가 유효성 테스트 시작 [최대 인원은 2명 이상]---")
        self.client.force_login(self.user1)
        study_create_test_data_without_max_member = self.study_create_data.copy()
        study_create_test_data_without_max_member["max_member"] = 1
        response = self.client.post(
            reverse("studies:study_create"), study_create_test_data_without_max_member
        )
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원은 2명 이상이어야 합니다."
        )
        print("---최대 인원 추가 유효성 테스트 종료---")

        print("---필수 입력 필드 유효성 테스트 종료---")

    def test_study_update_not_author(self):
        """
        5. 스터디 수정 테스트
        5-1. 스터디를 수정하는 것은 스터디를 생성한 유저만 가능
        - 스터디를 생성하지 않은 유저로 스터디 수정 테스트 진행 시 403 응답을 반환
        """
        print("---스터디 수정 테스트 시작---")
        study_update_test_data = self.study_create_data.copy()

        print("---스터디를 생성하지 않은 사용자로 스터디 수정 테스트 시작---")
        self.client.force_login(self.user2)

        study_update_test_data["title"] = "test_change"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data,
        )
        self.assertEqual(response.status_code, 403)
        print("---스터디를 생성하지 않은 사용자로 스터디 수정 테스트 종료---")

    def test_study_update_author(self):
        """
        5. 스터디 수정 테스트
        5-1. 스터디를 수정하는 것은 스터디를 생성한 유저만 가능
        - 스터디를 생성한 유저로 스터디 수정 테스트 진행 시 200 응답을 반환
        """
        print("---스터디 수정 테스트 시작---")
        study_update_test_data = self.study_create_data.copy()

        print("---스터디를 생성한 사용자로 스터디 수정 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data["title"] = "test_change"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data,
        )
        self.assertEqual(response.status_code, 200)
        print("---스터디를 생성한 사용자로 스터디 수정 테스트 종료---")

    def test_study_update_author_check_required_fields(self):
        """
        5. 스터디 수정 테스트
        5-2. 스터디 수정 유효성 검사
        - "category", "start_at", "end_at", "difficulty", "max_member" 필드는 필수 입력 필드
        - 필수 입력 필드는 빈 값으로 들어오면 forms.ValidationError를 반환
        """
        print("---필수 입력 필드 유효성 테스트 시작---")

        print("---카테고리 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_category = self.study_create_data.copy()
        study_update_test_data_without_category["category"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_category,
        )
        self.assertEqual(
            response.context["form"].errors["category"][0], "카테고리를 선택해주세요."
        )
        print("---카테고리 누락 테스트 종료---")

        print("---목표 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_goal = self.study_create_data.copy()
        study_update_test_data_without_goal["goal"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_goal,
        )
        self.assertEqual(response.context["form"].errors["goal"][0], "목표를 입력해주세요.")
        print("---목표 누락 테스트 종료---")

        print("---시작일 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_start_at = self.study_create_data.copy()
        study_update_test_data_without_start_at["start_at"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_start_at,
        )
        self.assertEqual(response.context["form"].errors["start_at"][0], "시작일을 입력해주세요.")
        print("---시작일 누락 테스트 종료---")

        print("---시작일 추가 유효성 테스트 시작 [오늘 이전의 날짜 선택 불가능]---")
        self.client.force_login(self.user1)
        study_update_test_data_without_start_at = self.study_create_data.copy()
        study_update_test_data_without_start_at["start_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_start_at,
        )
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )
        print("---시작일 추가 유효성 테스트 종료---")

        print("---종료일 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_end_at = self.study_create_data.copy()
        study_update_test_data_without_end_at["end_at"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_end_at,
        )
        self.assertEqual(response.context["form"].errors["end_at"][0], "종료일을 입력해주세요.")
        print("---종료일 누락 테스트 종료---")

        print("---종료일 추가 유효성 테스트 시작 [오늘 이전의 날짜 선택 불가능]---")
        self.client.force_login(self.user1)
        study_update_test_data_without_end_at = self.study_create_data.copy()
        study_update_test_data_without_end_at["end_at"] = "2021-01-01"
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_end_at,
        )
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "오늘 이전의 날짜를 선택할 수 없습니다."
        )
        print("---종료일 추가 유효성 테스트 종료---")

        print("---난이도 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_difficulty = self.study_create_data.copy()
        study_update_test_data_without_difficulty["difficulty"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_difficulty,
        )
        self.assertEqual(
            response.context["form"].errors["difficulty"][0], "난이도를 선택해주세요."
        )
        print("---난이도 누락 테스트 종료---")

        print("---최대 인원 누락 테스트 시작---")
        self.client.force_login(self.user1)
        study_update_test_data_without_max_member = self.study_create_data.copy()
        study_update_test_data_without_max_member["max_member"] = ""
        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_update_test_data_without_max_member,
        )
        self.assertEqual(
            response.context["form"].errors["max_member"][0], "최대 인원을 입력해주세요."
        )
        print("---최대 인원 누락 테스트 종료---")

        print("---최대 인원 추가 유효성 테스트 시작 [최대 인원은 2명 이상]---")
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
        print("---최대 인원 추가 유효성 테스트 종료---")

        print("---필수 입력 필드 유효성 테스트 종료---")

    def test_study_delete_not_author(self):
        """
        6. 스터디 삭제 테스트
        6-1. 스터디를 삭제하는 것은 스터디를 생성한 유저만 가능
        - 스터디를 생성하지 않은 유저로 스터디 삭제 테스트 진행 시 401 응답을 반환
        """
        print("---스터디를 생성하지 않은 사용자로 스터디 삭제 테스트 시작---")
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("studies:study_delete", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 403)
        print("---스터디를 생성하지 않은 사용자로 스터디 삭제 테스트 종료---")

    def test_study_delete_author(self):
        """
        6. 스터디 삭제 테스트
        6-1. 스터디를 삭제하는 것은 스터디를 생성한 유저만 가능
        - 스터디를 생성한 유저로 스터디 삭제 테스트 진행 시 200 응답을 반환
        """
        print("---스터디를 생성한 사용자로 스터디 삭제 테스트 시작---")
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("studies:study_delete", kwargs={"pk": 1}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/study/list/")
        self.assertEqual(Study.objects.count(), 0)
        print("---스터디를 생성한 사용자로 스터디 삭제 테스트 종료---")
