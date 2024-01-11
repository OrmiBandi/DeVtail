import factory
from .models import DevMate

from accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    사용자 목업 데이터 생성 클래스
    """

    class Meta:
        model = User

    email = factory.Faker("email")
    nickname = factory.Faker("name")
    development_field = factory.Faker("job")
    is_active = factory.Faker("boolean")
    is_staff = factory.Faker("boolean")


class DevMateFactory(factory.django.DjangoModelFactory):
    """
    DevMate 목업 데이터 생성 클래스
    추후 User 모델은 get_user_model()로 변경
    """

    class Meta:
        model = DevMate

    sent_user = factory.SubFactory(User)
    received_user = factory.SubFactory(User)
    is_accepted = factory.Faker("boolean")
