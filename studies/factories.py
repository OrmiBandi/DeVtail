from datetime import date, time
import factory
from factory.fuzzy import FuzzyInteger, FuzzyDate, FuzzyChoice

from accounts.models import User
from chats.models import ChatRoom
from .models import Study, Category


class ChatRoomFactory(factory.django.DjangoModelFactory):
    """
    채팅방 목업 데이터 생성 클래스
    """

    class Meta:
        model = ChatRoom

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for user in extracted:
                self.users.add(user)


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    카테고리 목업 데이터 생성 클래스
    """

    class Meta:
        model = Category

    name = factory.Faker("word")


class UserFactory(factory.django.DjangoModelFactory):
    """
    사용자 목업 데이터 생성 클래스
    """

    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("name")
    development_field = factory.Faker("job")
    is_active = factory.Faker("boolean")
    is_staff = factory.Faker("boolean")


class StudyFactory(factory.django.DjangoModelFactory):
    """
    스터디 목업 데이터 생성 클래스
    """

    class Meta:
        model = Study

    chat_room = factory.SubFactory(ChatRoomFactory)
    category = factory.SubFactory(CategoryFactory)
    leader = factory.SubFactory(UserFactory)
    goal = factory.Faker("sentence", nb_words=4)
    startdate = FuzzyDate(date(2020, 1, 1), date(2025, 12, 31))
    enddate = FuzzyDate(date(2020, 1, 1), date(2025, 12, 31))
    cycle = FuzzyInteger(1, 7)
    day = FuzzyChoice([i for i in range(1, 8)])
    starttime = time(0, 0, 0)
    endtime = time(23, 59, 59)
    introduce = factory.Faker("paragraph")
    topic = factory.Faker("sentence", nb_words=3)
    difficulty = FuzzyChoice(["상", "중", "하"])
    max_member = FuzzyInteger(1, 20)
