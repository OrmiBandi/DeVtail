from datetime import date, time
import factory
from factory.fuzzy import FuzzyInteger, FuzzyDate, FuzzyChoice

from accounts.models import User
from .models import Study, Category


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    카테고리 팩토리
    """

    class Meta:
        model = Category

    name = factory.Faker("word")


class StudyFactory(factory.django.DjangoModelFactory):
    """
    스터디 팩토리
    """

    class Meta:
        model = Study

    category = factory.SubFactory(CategoryFactory)
    goal = factory.Faker("word")
    start_at = FuzzyDate(date(2020, 1, 1))
    end_at = FuzzyDate(date(2020, 1, 1))
    introduce = factory.Faker("word")
    topic = factory.Faker("word")
    difficulty = FuzzyChoice(["상", "중", "하"])
    current_member = FuzzyInteger(0, 10)
    max_member = FuzzyInteger(0, 10)
