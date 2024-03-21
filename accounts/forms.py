from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm as BaseSignupForm
from django.contrib.auth.forms import AuthenticationForm
from .adapters import CustomAccountAdapter

User = get_user_model()


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
            "profile_image",
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
            raise forms.ValidationError(
                "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요."
            )
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
            raise forms.ValidationError(
                "닉네임은 2자리 이상, 15자리 이하로 입력해주세요."
            )
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


class CustomSignupForm(BaseSignupForm):
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
    content = forms.CharField(required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password1",
            "password2",
            "nickname",
            "development_field",
            "content",
            "auth_code",
        ]

    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop("sociallogin", None)
        super().__init__(*args, **kwargs)

        sociallogin = self.sociallogin
        user_data = sociallogin.account.extra_data

        self.fields["email"].initial = user_data.get("email")
        self.fields["nickname"].initial = user_data.get("login")

    def save(self, request):
        user = super().save(request)
        user.email = self.cleaned_data["email"]
        user.nickname = self.cleaned_data["nickname"]
        user.development_field = self.cleaned_data["development_field"]
        user.content = self.cleaned_data["content"]
        user.save()
        self.sociallogin.user = user
        self.sociallogin.save(request)
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="이메일",
        required=True,
        error_messages={
            "required": "이메일을 입력해주세요.",
            "invalid": "이메일 형식을 확인해주세요.",
        },
    )
    password = forms.CharField(
        label="비밀번호",
        required=True,
        error_messages={"required": "비밀번호를 입력해주세요."},
        widget=forms.PasswordInput,
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if not username:
            raise forms.ValidationError("이메일을 입력해주세요.")

        try:
            self.user_cache = User.objects.get(email=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."
            )
        return username

    def clean_password(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if not password:
            raise forms.ValidationError("비밀번호를 입력해주세요.")

        try:
            self.user_cache = User.objects.get(email=username)
            if not self.user_cache.check_password(password):
                raise forms.ValidationError(
                    "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        except User.DoesNotExist:
            raise forms.ValidationError(
                "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."
            )

        return password


class AccountUpdateForm(forms.ModelForm):
    nickname = forms.CharField(
        required=True,
        error_messages={
            "required": "닉네임을 입력해주세요.",
            "unique": "중복된 닉네임입니다.",
        },
    )

    development_field = forms.ChoiceField(
        required=True,
        choices=User.DEVELOPMENT_FIELD_CHOICES,
        error_messages={
            "invalid_choice": "항목에 포함된 개발 분야를 선택해주세요.",
            "required": "개발 분야를 선택해주세요.",
        },
    )

    class Meta:
        model = User
        fields = [
            "nickname",
            "development_field",
            "content",
            "profile_image",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": True}),
        }

    def clean_nickname(self):
        """
        닉네임 유효성 검사 메서드
            - 닉네임 길이가 2자리 이상, 15자리 이하인지 검사
            - 닉네임에 특수문자가 포함되어 있는지 검사
        """
        # 닉네임 길이가 2자리 이상, 15자리 이하인지 검사
        nickname = self.cleaned_data.get("nickname")
        if len(nickname) < 2 or len(nickname) > 15:
            raise forms.ValidationError(
                "닉네임은 2자리 이상, 15자리 이하로 입력해주세요."
            )
        # 닉네임에 특수문자가 포함되어 있는지 검사
        if any(char in nickname for char in "~!@#$%^&*()_+"):
            raise forms.ValidationError("닉네임에 특수문자를 포함할 수 없습니다.")

        return nickname


class AccountDeleteForm(forms.ModelForm):
    password = forms.CharField(
        required=True,
        error_messages={"required": "비밀번호를 입력해주세요."},
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ["password"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        """
        비밀번호 유효성 검사 메서드
            - 비밀번호가 일치하는지 검사
        """
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return password


class PasswordChangeForm(forms.ModelForm):
    old_password = forms.CharField(
        required=True,
        error_messages={"required": "비밀번호를 입력해주세요."},
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        required=True,
        error_messages={"required": "새 비밀번호를 입력해주세요."},
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        required=True,
        error_messages={"required": "새 비밀번호 확인을 입력해주세요."},
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        이전 비밀번호 유효성 검사 메서드
            - 이전 비밀번호가 일치하는지 검사

        """
        old_password = self.cleaned_data.get("old_password")

        if not self.user.check_password(old_password):
            raise forms.ValidationError("이전 비밀번호가 일치하지 않습니다.")
        return old_password

    def clean_new_password1(self):
        """
        새 비밀번호 유효성 검사 메서드
            - 새 비밀번호 길이가 8자리 이상, 15자리 이하인지 검사
            - 특수문자가 포함되어 있는지 검사
            - 새 비밀번호에 숫자가 포함되어 있는지 검사
            - 새 비밀번호에 영문자가 포함되어 있는지 검사
            - 새 비밀번호와 새 비밀번호 확인이 일치하는지 검사
        """
        new_password1 = self.cleaned_data.get("new_password1")
        # 새 비밀번호 길이가 8자리 이상, 15자리 이하인지 검사
        if len(new_password1) < 8 or len(new_password1) > 15:
            raise forms.ValidationError(
                "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요."
            )
        # 특수문자가 포함되어 있는지 검사
        if not any(char in new_password1 for char in "~!@#$%^&*()_+"):
            raise forms.ValidationError("비밀번호에 특수문자를 포함해주세요.")
        # 새 비밀번호에 숫자가 포함되어 있는지 검사
        if not any(char.isdigit() for char in new_password1):
            raise forms.ValidationError("비밀번호에 숫자를 포함해주세요.")
        # 새 비밀번호에 영문자가 포함되어 있는지 검사
        if not any(char.isalpha() for char in new_password1):
            raise forms.ValidationError("비밀번호에 영문을 포함해주세요.")
        return new_password1

    def clean_new_password2(self):
        """
        새 비밀번호 확인 유효성 검사 메서드
            - 새 비밀번호와 새 비밀번호 확인이 일치하는지 검사
        """
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        # 새 비밀번호와 새 비밀번호 확인이 일치하는지 검사
        if new_password1 != new_password2:
            raise forms.ValidationError("새 비밀번호가 일치하지 않습니다.")
        return new_password2
