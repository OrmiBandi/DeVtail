from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email

from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "이메일을 입력해주세요.",
            "invalid": "이메일 형식을 확인해주세요.",
            "unique": "중복된 이메일입니다.",
        },
    )
    password1 = forms.CharField(
        required=True,
        error_messages={"required": "비밀번호를 입력해주세요."},
    )
    password2 = forms.CharField(
        required=True,
        error_messages={"required": "비밀번호 확인을 입력해주세요."},
    )
    development_field = forms.ChoiceField(
        required=True,
        choices=User.DEVELOPMENT_FIELD_CHOICES,
        error_messages={
            "invalid_choice": "항목에 포함된 개발 분야를 선택해주세요.",
            "required": "개발 분야를 선택해주세요.",
        },
    )
    nickname = forms.CharField(
        required=True,
        error_messages={
            "required": "닉네임을 입력해주세요.",
            "unique": "중복된 닉네임입니다.",
        },
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password1",
            "password2",
            "nickname",
            "development_field",
            "content",
            "is_active",
            "auth_code",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nickname = self.cleaned_data["nickname"]
        user.development_field = self.cleaned_data["development_field"]
        user.content = self.cleaned_data["content"]
        user.is_active = self.cleaned_data["is_active"]
        user.save()
        return user

    def clean_password1(self):
        """
        비밀번호 유효성 검사 메서드
            - 비밀번호 길이가 8자리 이상, 15자리 이하인지 검사
            - 특수문자가 포함되어 있는지 검사
            - 비밀번호에 숫자가 포함되어 있는지 검사
            - 비밀번호에 영문자가 포함되어 있는지 검사
        """
        password1 = self.cleaned_data.get("password1")
        # 비밀번호 길이가 8자리 이상, 15자리 이하인지 검사
        if len(password1) < 8 or len(password1) > 15:
            raise forms.ValidationError("비밀번호는 8자리 이상, 15자리 이하로 입력해주세요.")
        # 특수문자가 포함되어 있는지 검사
        if not any(char in password1 for char in "~!@#$%^&*()_+"):
            raise forms.ValidationError("비밀번호에 특수문자를 포함해주세요.")
        # 비밀번호에 숫자가 포함되어 있는지 검사
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("비밀번호에 숫자를 포함해주세요.")
        # 비밀번호에 영문자가 포함되어 있는지 검사
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("비밀번호에 영문자를 포함해주세요.")
        return password1

    def clean_nickname(self):
        """
        닉네임 유효성 검사 메서드
            - 닉네임 길이가 2자리 이상, 15자리 이하인지 검사
            - 닉네임에 특수문자가 포함되어 있는지 검사
        """
        # 닉네임 길이가 2자리 이상, 15자리 이하인지 검사
        nickname = self.cleaned_data.get("nickname")
        if len(nickname) < 2 or len(nickname) > 15:
            raise forms.ValidationError("닉네임은 2자리 이상, 15자리 이하로 입력해주세요.")
        # 닉네임에 특수문자가 포함되어 있는지 검사
        if any(char in nickname for char in "~!@#$%^&*()_+"):
            raise forms.ValidationError("닉네임에 특수문자를 포함할 수 없습니다.")
        return nickname

    def clean(self):
        """
        유효성 검사 메서드
            - 비밀번호와 비밀번호 확인이 일치하는지 검사
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        # 비밀번호와 비밀번호 확인이 일치하는지 검사
        if password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return super().clean()