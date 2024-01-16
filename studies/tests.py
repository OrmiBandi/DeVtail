
from django.test import TestCase
from rest_framework.test import APIClient

from .factories import StudyFactory


class TestStudy(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_study_list(self):
        '''
        스터디 리스트 기능 테스트
        '''
        print('스터디 리스트 기능 테스트 BEGIN')
        StudyFactory.create_batch(6)
        response = self.client.get(
            '/study/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)
        print('스터디 리스트 기능 테스트 END')