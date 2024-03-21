import datetime
from django.test import TestCase
from studies.models import Study, StudyMember, Category, Tag, Schedule, RefLink
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestStudyList(TestCase):
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
        category = Category.objects.create(name="test")
        Study.objects.create(
            category=category,
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
        Schedule.objects.create(
            study=self.study_object,
            day=Schedule.day_choices[0][0],
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        tags = Tag.objects.create(name="tag_test")
        self.study_object.tag.add(tags)

        RefLink.objects.create(
            study=self.study_object, link_type="github", url="https://github.com/"
        )

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True, is_accepted=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False, is_accepted=True
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

    def test_study_list_by_tags(self):
        """
        태그를 통한 스터디 조회 테스트
        """
        tag = Tag.objects.get(name="tag_test")
        response = self.client.get(f"/study/list/?tq={tag}")
        self.assertEqual(response.status_code, 200)

        # 태그에 해당하는 기존 스터디 1개 조회
        self.assertEqual(len(response.context["studies"]), 1)


class TestStudyDetail(TestCase):
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
        category = Category.objects.create(name="test")
        Study.objects.create(
            category=category,
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
        Schedule.objects.create(
            study=self.study_object,
            day=Schedule.day_choices[0][0],
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        tags = Tag.objects.create(name="tag_test")
        self.study_object.tag.add(tags)

        RefLink.objects.create(
            study=self.study_object, link_type="github", url="https://github.com/"
        )

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True, is_accepted=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False, is_accepted=True
        )
        self.study_create_data = Study.objects.values()[0]

    def test_study_detail(self):
        """
        스터디 상세 조회 테스트
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)

        # 기존 스터디 title이 test인지 확인
        self.assertEqual(response.context["study"].title, "test")

    def test_study_detail_schedule(self):
        """
        스터디 상세 조회 시 스케줄 조회 테스트
        """
        response = self.client.get("/study/1/")
        self.assertEqual(response.status_code, 200)

        schedule = response.context["study"].schedules.get()
        # 기존 스터디 스케줄에 저장되어있는 day와 start_time, end_time이 맞는지 확인
        self.assertEqual(schedule.get_day_display(), "월요일")
        self.assertEqual(schedule.start_time, datetime.time(10, 0))
        self.assertEqual(schedule.end_time, datetime.time(12, 0))


class TestStudyCreate(TestCase):
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
        category = Category.objects.create(name="test")
        Study.objects.create(
            category=category,
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
        Schedule.objects.create(
            study=self.study_object,
            day=Schedule.day_choices[0][0],
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        tags = Tag.objects.create(name="tag_test")
        self.study_object.tag.add(tags)

        RefLink.objects.create(
            study=self.study_object, link_type="github", url="https://github.com/"
        )

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True, is_accepted=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False, is_accepted=True
        )
        self.study_create_data = Study.objects.values()[0]

    def test_study_create_without_login(self):
        """
        로그인 하지 않은 유저로 스터디 생성 테스트
        """
        response = self.client.post(
            reverse("studies:study_create"), self.study_create_data
        )

        self.assertRedirects(response, "/accounts/login/?next=/study/create/")

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

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 스터디 생성 성공
        self.assertEqual(response.status_code, 302)

    def test_study_create_with_login_check_required_fields_category(self):
        """
        필수 입력 필드 유효성 검사
        - 카테고리 누락 테스트
        """

        # user1으로 로그인 후 카테고리에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = ""
        study_data["tags"] = "tag_test"
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

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

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["goal"] = ""
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 목표에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["goal"][0], "목표를 입력해주세요."
        )

    def test_study_create_with_login_check_required_fields_start_at_first(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 시작일 누락 테스트
        """

        # user1으로 로그인 후 시작일에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["start_at"] = ""
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 시작일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "시작일을 입력해주세요."
        )

    def test_study_create_with_login_check_required_fields_start_at_second(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 시작일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1으로 로그인 후 시작일에 오늘 이전의 날짜를 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["start_at"] = "2021-01-01"
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 시작일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0],
            "오늘 이전의 날짜를 선택할 수 없습니다.",
        )

    def test_study_create_with_login_check_required_fields_end_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 누락 테스트
        """

        # user1으로 로그인 후 종료일에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["end_at"] = ""
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 종료일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "종료일을 입력해주세요."
        )

    def test_study_create_with_login_check_required_fields_end_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1으로 로그인 후 종료일에 오늘 이전의 날짜를 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["end_at"] = "2021-01-01"
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 종료일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0],
            "오늘 이전의 날짜를 선택할 수 없습니다.",
        )

    def test_study_create_with_login_check_required_fields_difficulty(self):
        """
        필수 입력 필드 유효성 검사
        - 난이도 누락 테스트
        """

        # user1으로 로그인 후 난이도에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["difficulty"] = ""
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 난이도에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["difficulty"][0], "난이도를 선택해주세요."
        )

    def test_study_create_with_login_check_required_fields_max_member_first(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 누락 테스트
        """

        # user1으로 로그인 후 최대 인원에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["max_member"] = ""
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 최대 인원에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0],
            "최대 인원을 입력해주세요.",
        )

    def test_study_create_with_login_check_required_fields_max_member_second(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 추가 유효성 테스트 [최대 인원은 2명 이상]
        """

        # user1으로 로그인 후 최대 인원에 1을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["max_member"] = 1
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 최대 인원에 1이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0],
            "최대 인원은 2명 이상이어야 합니다.",
        )

    def test_study_create_with_login_check_required_fields_schedule_days(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 요일 누락 테스트
        """

        # user1으로 로그인 후 일정의 요일에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = []
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["max_member"] = 1
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 요일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["days"][0], "요일을 선택해주세요."
        )

    def test_study_create_with_login_check_required_fields_schedule_start_time(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 시작 시간 누락 테스트
        """

        # user1으로 로그인 후 일정의 시작 시간에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = ""
        study_data["end_time"] = datetime.time(12, 0)
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["max_member"] = 1
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 시작 시간에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_time"][0],
            "시작 시간을 입력해주세요.",
        )

    def test_study_create_with_login_check_required_fields_schedule_end_time(
        self,
    ):
        """
        필수 입력 필드 유효성 검사
        - 종료 시간 누락 테스트
        """

        # user1으로 로그인 후 일정의 종료 시간에 빈값을 넣고 스터디 생성 요청
        self.client.force_login(self.user1)

        study_data = self.study_create_data
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = datetime.time(10, 0)
        study_data["end_time"] = ""
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = "tag_test"
        study_data["max_member"] = 1
        study_data["ref_links"] = RefLink.objects.get(pk=1).url

        response = self.client.post(reverse("studies:study_create"), study_data)

        # 종료 시간에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_time"][0], "종료 시간을 입력해주세요."
        )


class TestStudyUpdate(TestCase):
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
        category = Category.objects.create(name="test")
        Study.objects.create(
            category=category,
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
        Schedule.objects.create(
            study=self.study_object,
            day=Schedule.day_choices[0][0],
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        tags = Tag.objects.create(name="tag_test")
        self.study_object.tag.add(tags)

        RefLink.objects.create(
            study=self.study_object, link_type="github", url="https://github.com/"
        )

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True, is_accepted=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False, is_accepted=True
        )
        self.study_create_data = Study.objects.values()[0]

    def test_study_update_not_author(self):
        """
        작성자가 아닌 유저로 스터디 수정 테스트
        """

        # user2로 로그인 후 스터디 수정 요청
        self.client.force_login(self.user2)

        study_data = Study.objects.values()[0]
        study_data["title"] = "test_change"

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # user2에게는 스터디 수정 권한이 없으므로 403 리턴
        self.assertEqual(response.status_code, 403)

    def test_study_update_author(self):
        """
        작성자인 유저로 스터디 수정 테스트
        """

        # user1로 로그인 후 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["ref_links"] = RefLink.objects.get(pk=1).url
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["title"] = "test_change"

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 스터디 수정 성공 시 기존 스터디 상세 페이지로 302 리다이렉트
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("studies:study_detail", kwargs={"pk": 1})
        )

    def test_study_update_author_check_required_fields_category(self):
        """
        필수 입력 필드 유효성 검사
        - 카테고리 누락 테스트
        """

        # user1로 로그인 후 카테고리에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = ""
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
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

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["goal"] = ""

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 목표에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["goal"][0], "목표를 입력해주세요."
        )

    def test_study_update_author_check_required_fields_start_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 시작일 누락 테스트
        """

        # user1로 로그인 후 시작일에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["start_at"] = ""

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 시작일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0], "시작일을 입력해주세요."
        )

    def test_study_update_author_check_required_fields_start_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 시작일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1로 로그인 후 시작일에 오늘 이전의 날짜를 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["start_at"] = "2021-01-01"

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 시작일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_at"][0],
            "오늘 이전의 날짜를 선택할 수 없습니다.",
        )

    def test_study_update_author_check_required_fields_end_at_first(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 누락 테스트
        """

        # user1로 로그인 후 종료일에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["end_at"] = ""

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 종료일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0], "종료일을 입력해주세요."
        )

    def test_study_update_author_check_required_fields_end_at_second(self):
        """
        필수 입력 필드 유효성 검사
        - 종료일 추가 유효성 테스트 [오늘 이전의 날짜 선택 불가능]
        """

        # user1로 로그인 후 종료일에 오늘 이전의 날짜를 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["end_at"] = "2021-01-01"

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 종료일에 오늘 이전의 날짜가 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_at"][0],
            "오늘 이전의 날짜를 선택할 수 없습니다.",
        )

    def test_study_update_author_check_required_fields_difficulty(self):
        """
        필수 입력 필드 유효성 검사
        - 난이도 누락 테스트
        """

        # user1로 로그인 후 난이도에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["difficulty"] = ""

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
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

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["max_member"] = ""

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 최대 인원에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0],
            "최대 인원을 입력해주세요.",
        )

    def test_study_update_author_check_required_fields_max_member_second(self):
        """
        필수 입력 필드 유효성 검사
        - 최대 인원 추가 유효성 테스트 [최대 인원은 2명 이상]
        """

        # user1로 로그인 후 최대 인원에 1을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["max_member"] = 1

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 최대 인원에 1이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["max_member"][0],
            "최대 인원은 2명 이상이어야 합니다.",
        )

    def test_study_update_author_check_required_fields_schedule_days(self):
        """
        필수 입력 필드 유효성 검사
        - 요일 누락 테스트
        """

        # user1로 로그인 후 일정의 요일에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = []
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["max_member"] = 1

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 요일에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["days"][0], "요일을 선택해주세요."
        )

    def test_study_update_author_check_required_fields_schedule_start_time(self):
        """
        필수 입력 필드 유효성 검사
        - 시작 시간 누락 테스트
        """

        # user1로 로그인 후 일정의 시작 시간에 빈값을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = ""
        study_data["end_time"] = [Schedule.objects.get(pk=1).end_time]
        study_data["max_member"] = 1

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 시작 시간에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["start_time"][0],
            "시작 시간을 입력해주세요.",
        )

    def test_study_update_author_check_required_fields_schedule_end_time(self):
        """
        필수 입력 필드 유효성 검사
        - 종료 시간 누락 테스트
        """

        # user1로 로그인 후 최대 인원에 1을 넣고 스터디 수정 요청
        self.client.force_login(self.user1)

        study_data = Study.objects.values()[0]
        study_data["category"] = Category.objects.get(name="test").pk
        study_data["tags"] = Tag.objects.get(name="tag_test")
        study_data["days"] = [Schedule.day_choices[0][0]]
        study_data["start_time"] = [Schedule.objects.get(pk=1).start_time]
        study_data["end_time"] = ""
        study_data["max_member"] = 1

        response = self.client.post(
            reverse("studies:study_update", kwargs={"pk": 1}),
            study_data,
        )

        # 종료 시간에 빈값이 들어올 경우 ValidationError 발생
        self.assertEqual(
            response.context["form"].errors["end_time"][0], "종료 시간을 입력해주세요."
        )


class TestStudyDelete(TestCase):
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
        category = Category.objects.create(name="test")
        Study.objects.create(
            category=category,
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
        Schedule.objects.create(
            study=self.study_object,
            day=Schedule.day_choices[0][0],
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        tags = Tag.objects.create(name="tag_test")
        self.study_object.tag.add(tags)

        RefLink.objects.create(
            study=self.study_object, link_type="github", url="https://github.com/"
        )

        # 테스트용 스터디 멤버 생성
        StudyMember.objects.create(
            study=self.study_object, user=self.user1, is_manager=True, is_accepted=True
        )
        StudyMember.objects.create(
            study=self.study_object, user=self.user2, is_manager=False, is_accepted=True
        )
        self.study_create_data = Study.objects.values()[0]

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
        self.assertRedirects(response, reverse("studies:study_list"))

        # 스터디 삭제 확인
        self.assertEqual(Study.objects.count(), 0)
