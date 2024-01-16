import datetime
from django.test import TestCase, Client


class TestStudy(TestCase):
    def setUp(self):
        self.client = Client()

    def test_study_list(self):
        """
        스터디 리스트 기능 테스트
        """
        print("스터디 리스트 기능 테스트 BEGIN")

        data = {
            "category": "test_category",
            "goal": "목표",
            "start_at": datetime.date(2020, 1, 1),
            "end_at": datetime.date(2020, 1, 1),
            "introduce": "test_introduce",
            "topic": "test_topic",
            "difficulty": "상",
            "current_member": 1,
            "max_member": 10,
        }

        self.client.post(
            "/study/create/",
            data=data,
        )

        response = self.client.get(
            "/study/list/",
        )
        self.assertEqual(response.status_code, 200)

        print("스터디 리스트 기능 테스트 END")

    def test_study_create(self):
        """
        스터디 생성 기능 테스트
        1. 입력값 유효성 테스트
            - category는 필수 입력값
            - goal은 필수 입력값
            - start_at은 필수 입력값
            - end_at은 필수 입력값
            - difficulty는 필수 입력값
            - current_member는 필수 입력값
            - max_member는 필수 입력값
            - create_at은 필수 입력값
        2. 입력값 정상 테스트
            - 입력값이 정상적으로 들어가면 200이 반환되는지 확인
        3. 입력값 비정상 테스트
            - 입력값이 비정상적으로 들어가면 400이 반환되는지 확인
        """

        print("스터디 생성 기능 테스트 BEGIN")
        data = {
            "category": "test_category",
            "goal": "목표",
            "start_at": datetime.date(2020, 1, 1),
            "end_at": datetime.date(2020, 1, 1),
            "introduce": "test_introduce",
            "topic": "test_topic",
            "difficulty": "상",
            "current_member": 1,
            "max_member": 10,
        }

        # category 유효성 테스트
        filtered_data = {key: value for key, value in data.items() if key != "category"}
        print(filtered_data)
        response = self.client.post(
            "/study/create/",
            data=filtered_data,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["category"], "This field is required.")

        # goal 유효성 테스트
        filtered_data = {key: value for key, value in data.items() if key != "goal"}
        response = self.client.post(
            "/study/create/",
            data=filtered_data,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["goal"], "This field is required.")

        # started_at 유효성 테스트
        filtered_data = {
            key: value for key, value in data.items() if key != "started_at"
        }
        response = self.client.post(
            "/study/create/",
            data=filtered_data,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["started_at"], "This field is required.")

        # 입력값 정상 테스트
        response = self.client.post(
            "/study/create/",
            data=data,
        )
        self.assertEqual(response.status_code, 200)

        print("스터디 생성 기능 테스트 END")
