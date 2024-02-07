from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.tokens import default_token_generator


User = get_user_model()


class TestAccountSignupEmail(TestCase):
    """
    이메일 회원가입 테스트
    1. 비밀번호 유효성 테스트
        - 비밀번호가 8자리 이하일 경우
        - 비밀번호가 16자리 이상일 경우
        - 비밀번호에 특수문자가 없을 경우
        - 비밀번호에 숫자가 없을 경우
        - 비밀번호에 영문자가 없을 경우
        - 비밀번호가 비어있을 경우
        - 비밀번호 확인이 비어있을 경우
        - 비밀번호와 비밀번호 확인이 다를 경우
    2. 개발 분야 유효성 테스트
        - 개발 분야가 비어있을 경우
        - 개발 항목에 없는 분야일 경우
    3. 인증 URL 테스트
        - 전송 성공 테스트
    4. 정상적인 회원가입 테스트
        - 전송된 인증 메일 확인 완료 테스트
    5. 닉네임 유효성 테스트
        - 닉네임이 1자리일 경우
        - 닉네임이 16자리 이상일 경우
        - 닉네임에 특수문자가 있을 경우
        - 닉네임이 비어있을 경우
        - 중복된 닉네임일 경우
    6. 이메일 유효성 테스트
        - 이메일 형식이 아닐 경우
        - 이메일이 비어있을 경우
        - 중복된 이메일일 경우
    """

    @classmethod
    def setUp(self):
        self.email = "elwl5515@gmail.com"
        self.password = "testtest12!@"
        self.nickname = "test"
        self.development_field = "BE"
        self.profile_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=open("static/assets/images/test.jpg", "rb").read(),
            content_type="image/jpeg",
        )
        self.signup_data = {
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
            "nickname": self.nickname,
            "development_field": self.development_field,
            "profile_image": self.profile_image,
            "is_active": False,
            "content": "test",
        }

    def test_password_below_8(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우 BEGIN --")
        self.signup_data["password1"] = "test1!@"
        self.signup_data["password2"] = "test1!@"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"],
            "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요.",
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우 END --")

    def test_password_over_16(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우 BEGIN --")
        self.signup_data["password1"] = "testtesttest12!@"
        self.signup_data["password2"] = "testtesttest12!@"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"],
            "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요.",
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우 END --")

    def test_password_no_special(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우 BEGIN --")
        self.signup_data["password1"] = "testtest12"
        self.signup_data["password2"] = "testtest12"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"], "비밀번호에 특수문자를 포함해주세요."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우 END --")

    def test_password_no_number(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우 BEGIN --")
        self.signup_data["password1"] = "testtest!@"
        self.signup_data["password2"] = "testtest!@"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"], "비밀번호에 숫자를 포함해주세요."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우 END --")

    def test_password_no_alphabet(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 영문자가 없을 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 영문자가 없을 경우 BEGIN --")
        self.signup_data["password1"] = "12!@12!@"
        self.signup_data["password2"] = "12!@12!@"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"], "비밀번호에 영문자를 포함해주세요."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호에 영문자가 없을 경우 END --")

    def test_password_empty(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우 BEGIN --")
        self.signup_data["password1"] = ""
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password1"], "비밀번호를 입력해주세요."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우 END --")

    def test_password2_empty(self):
        """
        비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우
        """
        print("-- 비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우 BEGIN --")
        self.signup_data["password2"] = ""
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password2"], "비밀번호 확인을 입력해주세요."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우 END --")

    def test_password_different(self):
        """
        비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우
        """
        print(
            "-- 비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우 BEGIN --"
        )
        self.signup_data["password2"] = "testtest12!@#"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_password2"], "비밀번호가 일치하지 않습니다."
        )
        print("-- 비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우 END --")

    def test_development_field_empty(self):
        """
        개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우
        """
        print("-- 개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우 BEGIN --")
        self.signup_data["development_field"] = ""
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_development_field"], "개발 분야를 선택해주세요."
        )
        print("-- 개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우 END --")

    def test_development_field_wrong(self):
        """
        개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우
        """
        print("-- 개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우 BEGIN --")
        self.signup_data["development_field"] = "test"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_development_field"],
            "항목에 포함된 개발 분야를 선택해주세요.",
        )
        print("-- 개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우 END --")

    def test_auth_url_success(self):
        """
        인증 URL 테스트 - 전송 성공&전송 인증 메일 확인 완료 테스트
        """
        print("-- 인증 URL 테스트 - 전송 성공&전송 인증 메일 확인 완료 테스트 BEGIN --")
        response = self.client.post(
            reverse("accounts:signup"), self.signup_data, format="multipart"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            str(list(get_messages(response.wsgi_request))[0]),
            "인증 URL이 전송되었습니다. 메일을 확인해주세요.",
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "deVtail 인증 메일입니다.")
        self.assertEqual(mail.outbox[0].to, [self.email])

        email_body = mail.outbox[0].body
        auth_url = email_body.split("인증 URL: ")[1].split("\n")[0]
        self.assertIn("email_confirm", auth_url)
        uuid = auth_url.split("email_confirm/")[1]
        self.assertTrue(uuid)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)
        self.assertTrue(user.auth_code)

        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            str(list(get_messages(response.wsgi_request))[1]),
            "이메일 인증이 완료되었습니다. 회원가입이 완료되었습니다.",
        )
        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.auth_code)
        self.signup_data["email"] = "test@gmail.com"
        self.signup_data["nickname"] = "test1"
        print("-- 인증 URL 테스트 - 전송 성공&전송 인증 메일 확인 완료 테스트 END --")

    def test_nickname_below_2(self):
        """
        닉네임 유효성 테스트 - 닉네임이 1자리일 경우
        """
        print("-- 닉네임 유효성 테스트 - 닉네임이 1자리일 경우 BEGIN --")
        self.signup_data["nickname"] = "t"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_nickname"],
            "닉네임은 2자리 이상, 15자리 이하로 입력해주세요.",
        )
        print("-- 닉네임 유효성 테스트 - 닉네임이 1자리일 경우 END --")

    def test_nickname_over_16(self):
        """
        닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우
        """
        print("-- 닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우 BEGIN --")
        self.signup_data["nickname"] = "testtesttesttest"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_nickname"],
            "닉네임은 2자리 이상, 15자리 이하로 입력해주세요.",
        )
        print("-- 닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우 END --")

    def test_nickname_special(self):
        """
        닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우
        """
        print("-- 닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우 BEGIN --")
        self.signup_data["nickname"] = "test!@"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error_nickname"],
            "닉네임에 특수문자를 포함할 수 없습니다.",
        )
        print("-- 닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우 END --")

    def test_nickname_empty(self):
        """
        닉네임 유효성 테스트 - 닉네임이 비어있을 경우
        """
        print("-- 닉네임 유효성 테스트 - 닉네임이 비어있을 경우 BEGIN --")
        self.signup_data["nickname"] = ""
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["error_nickname"], "닉네임을 입력해주세요.")
        print("-- 닉네임 유효성 테스트 - 닉네임이 비어있을 경우 END --")

    def test_nickname_duplicate(self):
        """
        닉네임 유효성 테스트 - 중복된 닉네임일 경우
        """
        print("-- 닉네임 유효성 테스트 - 중복된 닉네임일 경우 BEGIN --")
        User.objects.create_user(
            email="test@test.com",
            password="testtest12!@",
            nickname="test",
            development_field="BE",
            is_active=True,
        )
        self.signup_data["nickname"] = "test"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["error_nickname"], "중복된 닉네임입니다.")
        print("-- 닉네임 유효성 테스트 - 중복된 닉네임일 경우 END --")

    def test_email_wrong(self):
        """
        이메일 유효성 테스트 - 이메일 형식이 아닐 경우
        """
        print("-- 이메일 유효성 테스트 - 이메일 형식이 아닐 경우 BEGIN --")
        self.signup_data["email"] = "test"
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["error_email"], "이메일 형식을 확인해주세요.")
        print("-- 이메일 유효성 테스트 - 이메일 형식이 아닐 경우 END --")

    def test_email_empty(self):
        """
        이메일 유효성 테스트 - 이메일이 비어있을 경우
        """
        print("-- 이메일 유효성 테스트 - 이메일이 비어있을 경우 BEGIN --")
        self.signup_data["email"] = ""
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["error_email"], "이메일을 입력해주세요.")
        print("-- 이메일 유효성 테스트 - 이메일이 비어있을 경우 END --")

    def test_email_duplicate(self):
        """
        이메일 유효성 테스트 - 중복된 이메일일 경우
        """
        print("-- 이메일 유효성 테스트 - 중복된 이메일일 경우 BEGIN --")
        User.objects.create_user(
            email="elwl5515@gmail.com",
            password="testtest12!@",
            nickname="test1",
            development_field="BE",
            is_active=True,
        )
        response = self.client.post(reverse("accounts:signup"), self.signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["error_email"], "중복된 이메일입니다.")
        print("-- 이메일 유효성 테스트 - 중복된 이메일일 경우 END --")


class TestAccountLogin(TestCase):
    """
    로그인 테스트
    1. 정상 로그인 테스트
    2. 없는 사용자 테스트
    3. 비밀번호 불일치 테스트
    4. 이메일을 입력하지 않은 경우 테스트
    5. 비밀번호를 입력하지 않은 경우 테스트
    """

    @classmethod
    def setUp(self):
        self.singup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
        }
        User.objects.create_user(
            email=self.singup_data["email"],
            password=self.singup_data["password1"],
            nickname=self.singup_data["nickname"],
        )

    def test_success(self):
        """
        정상 로그인 테스트
        """
        print("-- 로그인 테스트 - 정상 로그인 테스트 BEGIN --")
        response = self.client.post(
            reverse("login"),
            {
                "username": self.singup_data["email"],
                "password": self.singup_data["password1"],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        print("-- 로그인 테스트 - 정상 로그인 테스트 END --")

    def test_no_user(self):
        """
        없는 사용자 테스트
        """
        print("-- 로그인 테스트 - 없는 사용자 테스트 BEGIN --")
        response = self.client.post(
            reverse("login"),
            {"username": "test@test.com", "password": self.singup_data["password1"]},
            follow=True,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다.",
        )
        print("-- 로그인 테스트 - 없는 사용자 테스트 END --")

    def test_wrong_password(self):
        """
        비밀번호 불일치 테스트
        """
        print("-- 로그인 테스트 - 비밀번호 불일치 테스트 BEGIN --")
        response = self.client.post(
            reverse("login"),
            {"username": self.singup_data["email"], "password": "testtest12!@#"},
            follow=True,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다.",
        )
        print("-- 로그인 테스트 - 비밀번호 불일치 테스트 END --")

    def test_no_email(self):
        """
        이메일을 입력하지 않은 경우 테스트
        """
        print("-- 로그인 테스트 - 이메일을 입력하지 않은 경우 테스트 BEGIN --")
        response = self.client.post(
            reverse("login"),
            {"username": "", "password": self.singup_data["password1"]},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "이메일을 입력해주세요.")
        print("-- 로그인 테스트 - 이메일을 입력하지 않은 경우 테스트 END --")

    def test_no_password(self):
        """
        비밀번호를 입력하지 않은 경우 테스트
        """
        print("-- 로그인 테스트 - 비밀번호를 입력하지 않은 경우 테스트 BEGIN --")
        response = self.client.post(
            reverse("login"),
            {"username": self.singup_data["email"], "password": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "비밀번호를 입력해주세요.")
        print("-- 로그인 테스트 - 비밀번호를 입력하지 않은 경우 테스트 END --")


class TestAccountLogout(TestCase):
    """
    로그아웃 테스트
    1. 정상 로그아웃 테스트
    2. 로그인하지 않은 사용자 테스트
    3. 로그아웃 후 로그인 테스트
    """

    @classmethod
    def setUp(self):
        self.singup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
        }
        User.objects.create_user(
            email=self.singup_data["email"],
            password=self.singup_data["password1"],
            nickname=self.singup_data["nickname"],
        )

    def test_success(self):
        """
        정상 로그아웃 테스트
        """
        print("-- 로그아웃 테스트 - 정상 로그아웃 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.singup_data["email"]), backend=None
        )
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        print("-- 로그아웃 테스트 - 정상 로그아웃 테스트 END --")

    def test_no_user(self):
        """
        로그인하지 않은 사용자 테스트
        """
        print("-- 로그아웃 테스트 - 로그인하지 않은 사용자 테스트 BEGIN --")
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "로그인되지 않은 사용자입니다."
        )
        print("-- 로그아웃 테스트 - 로그인하지 않은 사용자 테스트 END --")

    def test_login_after_logout(self):
        """
        로그아웃 후 로그인 테스트
        """
        print("-- 로그아웃 테스트 - 로그아웃 후 로그인 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.singup_data["email"]), backend=None
        )
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

        response = self.client.post(
            reverse("login"),
            {
                "username": self.singup_data["email"],
                "password": self.singup_data["password1"],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        print("-- 로그아웃 테스트 - 로그아웃 후 로그인 테스트 END --")


class TestAccountProfile(TestCase):
    """
    프로필 테스트
    1. 정상 프로필 응답 테스트
    2. 존재하지 않는 사용자의 프로필 요청 테스트
    3. 로그인하지 않은 사용자의 프로필 요청 테스트
    """

    @classmethod
    def setUp(self):
        self.signup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
            "development_field": "BE",
        }
        User.objects.create_user(
            email=self.signup_data["email"],
            password=self.signup_data["password1"],
            nickname=self.signup_data["nickname"],
            development_field=self.signup_data["development_field"],
        )

    def test_success(self):
        """
        프로필 테스트 - 정상 프로필 응답 테스트
        """
        print("-- 프로필 테스트 - 정상 프로필 응답 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        response = self.client.get(reverse("profile", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["user_profile"].email, self.signup_data["email"]
        )
        self.assertEqual(
            response.context["user_profile"].nickname, self.signup_data["nickname"]
        )
        self.assertEqual(
            response.context["user_profile"].development_field,
            self.signup_data["development_field"],
        )
        print("-- 프로필 테스트 - 정상 프로필 응답 테스트 END --")

    def test_no_user(self):
        """
        프로필 테스트 - 존재하지 않는 사용자의 프로필 요청 테스트
        """
        print("-- 프로필 테스트 - 존재하지 않는 사용자의 프로필 요청 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        response = self.client.get(reverse("profile", kwargs={"pk": 2}), follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.content.decode("utf-8"), "존재하지 않는 사용자입니다."
        )
        print("-- 프로필 테스트 - 존재하지 않는 사용자의 프로필 요청 테스트 END --")

    def test_no_login(self):
        """
        프로필 테스트 - 로그인하지 않은 사용자의 프로필 요청 테스트
        """
        print("-- 프로필 테스트 - 로그인하지 않은 사용자의 프로필 요청 테스트 BEGIN --")
        response = self.client.get(reverse("profile", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.content.decode("utf-8"), "로그인되지 않은 사용자입니다."
        )
        print("-- 프로필 테스트 - 로그인하지 않은 사용자의 프로필 요청 테스트 END --")


class TestAccountUpdate(TestCase):
    """
    사용자 정보 수정 테스트
    1. 로그인하지 않은 사용자의 사용자 정보 수정 테스트
    2. 정상 사용자 정보 수정 테스트
    3. 닉네임 유효성 테스트
        - 닉네임이 1자리일 경우
        - 닉네임이 16자리 이상일 경우
        - 닉네임에 특수문자가 있을 경우
        - 닉네임이 비어있을 경우
        - 중복된 닉네임일 경우
    4. 개발 분야 유효성 테스트
        - 개발 분야가 비어있을 경우
        - 개발 항목에 없는 분야일 경우
    """

    @classmethod
    def setUp(self):
        self.signup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
            "development_field": "BE",
        }
        User.objects.create_user(
            email=self.signup_data["email"],
            password=self.signup_data["password1"],
            nickname=self.signup_data["nickname"],
            development_field=self.signup_data["development_field"],
        )
        self.update_data = {
            "nickname": "test1",
            "development_field": "FE",
            "content": "test",
        }

    def test_no_login(self):
        """
        로그인하지 않은 사용자의 사용자 정보 수정 테스트
        """
        print(
            "-- 사용자 정보 수정 테스트 - 로그인하지 않은 사용자의 사용자 정보 수정 테스트 BEGIN --"
        )
        response = self.client.post(reverse("account_update"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.content.decode("utf-8"), "로그인되지 않은 사용자입니다."
        )
        print(
            "-- 사용자 정보 수정 테스트 - 로그인하지 않은 사용자의 사용자 정보 수정 테스트 END --"
        )

    def test_success(self):
        """
        정상 사용자 정보 수정 테스트
        """
        print("-- 사용자 정보 수정 테스트 - 정상 사용자 정보 수정 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )

        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            str(list(get_messages(response.wsgi_request))[0]),
            "사용자 정보가 수정되었습니다.",
        )
        user = User.objects.get(pk=1)
        self.assertEqual(user.nickname, self.update_data["nickname"])
        self.assertEqual(user.development_field, self.update_data["development_field"])
        self.assertEqual(user.content, self.update_data["content"])
        print("-- 사용자 정보 수정 테스트 - 정상 사용자 정보 수정 테스트 END --")

    def test_nickname_below_2(self):
        """
        닉네임 유효성 테스트 - 닉네임이 1자리일 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 1자리일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["nickname"] = "t"
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "닉네임은 2자리 이상, 15자리 이하로 입력해주세요.",
        )
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 1자리일 경우 END --"
        )

    def test_nickname_over_16(self):
        """
        닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["nickname"] = "testtesttesttest"
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "닉네임은 2자리 이상, 15자리 이하로 입력해주세요.",
        )
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우 END --"
        )

    def test_nickname_special(self):
        """
        닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["nickname"] = "test!@"
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "닉네임에 특수문자를 포함할 수 없습니다."
        )
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우 END --"
        )

    def test_nickname_empty(self):
        """
        닉네임 유효성 테스트 - 닉네임이 비어있을 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 비어있을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["nickname"] = ""
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "닉네임을 입력해주세요.")
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 닉네임이 비어있을 경우 END --"
        )

    def test_nickname_duplicate(self):
        """
        닉네임 유효성 테스트 - 중복된 닉네임일 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 중복된 닉네임일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        User.objects.create_user(
            email="gjs5515@naver.com",
            password="testtest12!@",
            nickname="test1",
        )
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "중복된 닉네임입니다.")
        print(
            "-- 사용자 정보 수정 테스트 - 닉네임 유효성 테스트 - 중복된 닉네임일 경우 END --"
        )

    def test_development_field_empty(self):
        """
        개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["development_field"] = ""
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "개발 분야를 선택해주세요.")
        print(
            "-- 사용자 정보 수정 테스트 - 개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우 END --"
        )

    def test_development_field_wrong(self):
        """
        개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우
        """
        print(
            "-- 사용자 정보 수정 테스트 - 개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.update_data["development_field"] = "test"
        response = self.client.post(
            reverse("account_update"), self.update_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "항목에 포함된 개발 분야를 선택해주세요."
        )
        print(
            "-- 사용자 정보 수정 테스트 - 개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우 END --"
        )


class TestAccountSecession(TestCase):
    """
    회원 탈퇴 테스트
    1. 로그인하지 않은 사용자의 회원 탈퇴 테스트
    2. 비밀번호를 입력하지 않은 경우 테스트
    3. 비밀번호가 일치하지 않는 경우 테스트
    4. 정상 회원 탈퇴 테스트
    """

    def setUp(self):
        self.signup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
            "development_field": "BE",
        }
        User.objects.create_user(
            email=self.signup_data["email"],
            password=self.signup_data["password1"],
            nickname=self.signup_data["nickname"],
            development_field=self.signup_data["development_field"],
        )
        self.delete_data = {
            "password": "testtest12!@",
        }

    def test_no_login(self):
        """
        로그인하지 않은 사용자의 회원 탈퇴 테스트
        """
        print(
            "-- 회원 탈퇴 테스트 - 로그인하지 않은 사용자의 회원 탈퇴 테스트 BEGIN --"
        )
        response = self.client.post(reverse("account_delete"), data=self.delete_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.content.decode("utf-8"), "로그인되지 않은 사용자입니다."
        )
        print("-- 회원 탈퇴 테스트 - 로그인하지 않은 사용자의 회원 탈퇴 테스트 END --")

    def test_password_empty(self):
        """
        비밀번호를 입력하지 않은 경우 테스트
        """
        print("-- 회원 탈퇴 테스트 - 비밀번호를 입력하지 않은 경우 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        response = self.client.post(reverse("account_delete"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "비밀번호를 입력해주세요.")
        print("-- 회원 탈퇴 테스트 - 비밀번호를 입력하지 않은 경우 테스트 END --")

    def test_password_wrong(self):
        """
        비밀번호가 일치하지 않는 경우 테스트
        """
        print("-- 회원 탈퇴 테스트 - 비밀번호가 일치하지 않는 경우 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.delete_data["password"] = "testtest12!@#"
        response = self.client.post(reverse("account_delete"), data=self.delete_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "비밀번호가 일치하지 않습니다."
        )
        print("-- 회원 탈퇴 테스트 - 비밀번호가 일치하지 않는 경우 테스트 END --")

    def test_success(self):
        """
        정상 회원 탈퇴 테스트
        """
        print("-- 회원 탈퇴 테스트 - 정상 회원 탈퇴 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        response = self.client.post(
            reverse("account_delete"), follow=True, data=self.delete_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            str(list(get_messages(response.wsgi_request))[0]),
            "회원 탈퇴가 완료되었습니다.",
        )
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertEqual(User.objects.count(), 0)
        print("-- 회원 탈퇴 테스트 - 정상 회원 탈퇴 테스트 END --")


class TestPasswordChange(TestCase):
    """
    비밀번호 변경 테스트
    1. 로그인하지 않은 사용자의 비밀번호 변경 테스트
    2. 정상 비밀번호 변경 테스트
    3. 이전 비밀번호가 일치하지 않는 경우 테스트
    4. 비밀번호 유효성 테스트
        - 비밀번호가 8자리 이하일 경우
        - 비밀번호가 16자리 이상일 경우
        - 비밀번호에 특수문자가 없을 경우
        - 비밀번호에 숫자가 없을 경우
        - 비밀번호에 영문이 없을 경우
        - 비밀번호가 비어있을 경우
        - 비밀번호 확인이 비어있을 경우
        - 비밀번호와 비밀번호 확인이 다를 경우
    """

    def setUp(self):
        self.signup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
            "development_field": "BE",
        }
        User.objects.create_user(
            email=self.signup_data["email"],
            password=self.signup_data["password1"],
            nickname=self.signup_data["nickname"],
            development_field=self.signup_data["development_field"],
        )
        self.password_change_data = {
            "old_password": self.signup_data["password1"],
            "new_password1": "testtest12!@#",
            "new_password2": "testtest12!@#",
        }

    def test_no_login(self):
        """
        로그인하지 않은 사용자의 비밀번호 변경 테스트
        """
        print(
            "-- 비밀번호 변경 테스트 - 로그인하지 않은 사용자의 비밀번호 변경 테스트 BEGIN --"
        )
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.content.decode("utf-8"), "로그인되지 않은 사용자입니다."
        )
        print(
            "-- 비밀번호 변경 테스트 - 로그인하지 않은 사용자의 비밀번호 변경 테스트 END --"
        )

    def test_success(self):
        """
        정상 비밀번호 변경 테스트
        """
        print("-- 비밀번호 변경 테스트 - 정상 비밀번호 변경 테스트 BEGIN --")
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        response = self.client.post(
            reverse("password_change"), self.password_change_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            str(list(get_messages(response.wsgi_request))[0]),
            "비밀번호가 변경되었습니다.",
        )
        print("-- 비밀번호 변경 테스트 - 정상 비밀번호 변경 테스트 END --")

    def test_wrong_old_password(self):
        """
        이전 비밀번호가 일치하지 않는 경우 테스트
        """
        print(
            "-- 비밀번호 변경 테스트 - 이전 비밀번호가 일치하지 않는 경우 테스트 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["old_password"] = "testtest12!@#"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "이전 비밀번호가 일치하지 않습니다."
        )
        print(
            "-- 비밀번호 변경 테스트 - 이전 비밀번호가 일치하지 않는 경우 테스트 END --"
        )

    def test_password_below_8(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = "te12!@"
        self.password_change_data["new_password2"] = "te12!@"
        response = self.client.post(
            reverse("password_change"), self.password_change_data, follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요.",
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우 END --"
        )

    def test_password_over_16(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = "testtesttest12!@"
        self.password_change_data["new_password2"] = "testtesttest12!@"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"),
            "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요.",
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우 END --"
        )

    def test_password_no_special(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = "testtest12"
        self.password_change_data["new_password2"] = "testtest12"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "비밀번호에 특수문자를 포함해주세요."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우 END --"
        )

    def test_password_no_number(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = "testtest!@"
        self.password_change_data["new_password2"] = "testtest!@"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "비밀번호에 숫자를 포함해주세요."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우 END --"
        )

    def test_password_no_alphabet(self):
        """
        비밀번호 유효성 테스트 - 비밀번호에 영문이 없을 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 영문이 없을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = "12!@12!@12!@"
        self.password_change_data["new_password2"] = "12!@12!@12!@"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "비밀번호에 영문을 포함해주세요."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호에 영문이 없을 경우 END --"
        )

    def test_password_empty(self):
        """
        비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password1"] = ""
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "새 비밀번호를 입력해주세요."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우 END --"
        )

    def test_password_confirm_empty(self):
        """
        비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password2"] = ""
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "새 비밀번호 확인을 입력해주세요."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우 END --"
        )

    def test_password_not_match(self):
        """
        비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우
        """
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우 BEGIN --"
        )
        self.client.force_login(
            User.objects.get(email=self.signup_data["email"]), backend=None
        )
        self.password_change_data["new_password2"] = "testtest12!@"
        response = self.client.post(
            reverse("password_change"), self.password_change_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "새 비밀번호가 일치하지 않습니다."
        )
        print(
            "-- 비밀번호 변경 테스트 - 비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우 END --"
        )


class TestPasswordReset(TestCase):
    """
    1. 이메일 전송 테스트
        - 정상 전송
        - 존재하지 않는 이메일
    """

    def setUp(self):
        self.signup_data = {
            "email": "elwl5515@gmail.com",
            "password1": "testtest12!@",
            "password2": "testtest12!@",
            "nickname": "test",
            "development_field": "BE",
        }
        User.objects.create_user(
            email=self.signup_data["email"],
            password=self.signup_data["password1"],
            nickname=self.signup_data["nickname"],
            development_field=self.signup_data["development_field"],
        )

    def test_send_success(self):
        """
        이메일 전송 테스트 - 정상 전송
        """
        print("-- 비밀번호 찾기 테스트 - 이메일 전송 테스트 - 정상 전송 BEGIN --")
        response = self.client.post(
            reverse("password_reset"), {"email": self.signup_data["email"]}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "deVtail 비밀번호 변경 메일입니다.")
        self.assertEqual(mail.outbox[0].to, [self.signup_data["email"]])
        print("-- 비밀번호 찾기 테스트 - 이메일 전송 테스트 - 정상 전송 END --")

    def test_send_no_user(self):
        """
        이메일 전송 테스트 - 존재하지 않는 이메일
        """
        print(
            "-- 비밀번호 찾기 테스트 - 이메일 전송 테스트 - 존재하지 않는 이메일 BEGIN --"
        )
        response = self.client.post(
            reverse("password_reset"), {"email": "test@gmail.com"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "존재하지 않는 이메일입니다."
        )
        print(
            "-- 비밀번호 찾기 테스트 - 이메일 전송 테스트 - 존재하지 않는 이메일 END --"
        )

    # def test_reset_success(self):
    #     """
    #     비밀번호 초기화 테스트 - 정상 초기화
    #     """
    #     print("-- 비밀번호 찾기 테스트 - 비밀번호 초기화 테스트 - 정상 초기화 BEGIN --")
    #     user = User.objects.get(pk=1)
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     token = default_token_generator.make_token(user)
    #     url = f"/accounts/password/reset_confirm/{uid}/{token}/"
    #     print(url)
    #     response = self.client.post(
    #         url,
    #         {
    #             "new_password1": "testtest12!@#",
    #             "new_password2": "testtest12!@#",
    #         },
    #     )
    #     # self.assertRedirects(response, reverse("login"))
    #     user.refresh_from_db()
    #     self.assertTrue(user.check_password("testtest12!@#"))
    #     print("-- 비밀번호 찾기 테스트 - 비밀번호 초기화 테스트 - 정상 초기화 END --")
