from freezegun import freeze_time
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class TestAccount(TestCase):
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

    @freeze_time(timezone.now())
    def test_account_signup_email(self):
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
        print("이메일 회원가입 테스트 BEGIN")
        # 비밀번호 유효성 테스트 - 비밀번호가 8자리 이하일 경우
        signup_data_password_below_8 = self.signup_data.copy()
        signup_data_password_below_8["password1"] = "test1!@"
        signup_data_password_below_8["password2"] = "test1!@"
        response = self.client.post(reverse("signup"), signup_data_password_below_8)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["password1"][0], "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요."
        )

        # 비밀번호 유효성 테스트 - 비밀번호가 16자리 이상일 경우
        signup_data_password_over_16 = self.signup_data.copy()
        signup_data_password_over_16["password1"] = "testtesttest12!@"
        signup_data_password_over_16["password2"] = "testtesttest12!@"
        response = self.client.post(reverse("signup"), signup_data_password_over_16)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["password1"][0], "비밀번호는 8자리 이상, 15자리 이하로 입력해주세요."
        )

        # 비밀번호 유효성 테스트 - 비밀번호에 특수문자가 없을 경우
        signup_data_no_special = self.signup_data.copy()
        signup_data_no_special["password1"] = "testtest12"
        signup_data_no_special["password2"] = "testtest12"
        response = self.client.post(reverse("signup"), signup_data_no_special)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password1"][0], "비밀번호에 특수문자를 포함해주세요.")

        # 비밀번호 유효성 테스트 - 비밀번호에 숫자가 없을 경우
        signup_data_no_number = self.signup_data.copy()
        signup_data_no_number["password1"] = "testtest!@"
        signup_data_no_number["password2"] = "testtest!@"
        response = self.client.post(reverse("signup"), signup_data_no_number)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password1"][0], "비밀번호에 숫자를 포함해주세요.")

        # 비밀번호 유효성 테스트 - 비밀번호에 영문자가 없을 경우
        signup_data_no_alphabet = self.signup_data.copy()
        signup_data_no_alphabet["password1"] = "12!@12!@"
        signup_data_no_alphabet["password2"] = "12!@12!@"
        response = self.client.post(reverse("signup"), signup_data_no_alphabet)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password1"][0], "비밀번호에 영문자를 포함해주세요.")

        # 비밀번호 유효성 테스트 - 비밀번호가 비어있을 경우
        signup_data_empty_password = self.signup_data.copy()
        signup_data_empty_password["password1"] = ""
        response = self.client.post(reverse("signup"), signup_data_empty_password)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password1"][0], "비밀번호를 입력해주세요.")

        # 비밀번호 유효성 테스트 - 비밀번호 확인이 비어있을 경우
        signup_data_empty_password2 = self.signup_data.copy()
        signup_data_empty_password2["password2"] = ""
        response = self.client.post(reverse("signup"), signup_data_empty_password2)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password2"][0], "비밀번호 확인을 입력해주세요.")

        # 비밀번호 유효성 테스트 - 비밀번호와 비밀번호 확인이 다를 경우
        signup_data_different_password = self.signup_data.copy()
        signup_data_different_password["password2"] = "testtest12!@#"
        response = self.client.post(reverse("signup"), signup_data_different_password)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["password2"][0], "비밀번호가 일치하지 않습니다.")

        # 개발 분야 유효성 테스트 - 개발 분야가 비어있을 경우
        signup_data_empty_development_field = self.signup_data.copy()
        signup_data_empty_development_field["development_field"] = ""
        response = self.client.post(
            reverse("signup"), signup_data_empty_development_field
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["development_field"][0], "개발 분야를 선택해주세요.")

        # 개발 분야 유효성 테스트 - 개발 항목에 없는 분야일 경우
        signup_data_wrong_development_field = self.signup_data.copy()
        signup_data_wrong_development_field["development_field"] = "test"
        response = self.client.post(
            reverse("signup"), signup_data_wrong_development_field
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["development_field"][0], "항목에 포함된 개발 분야를 선택해주세요."
        )

        # 인증 URL 테스트 - 전송 성공 테스트
        response = self.client.post(
            reverse("signup"), self.signup_data, format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "인증 URL이 전송되었습니다. 메일을 확인해주세요.")

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

        # 정상적인 회원가입 테스트 - 전송된 인증 메일 확인 완료 테스트
        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "이메일 인증이 완료되었습니다. 회원가입이 완료되었습니다.")
        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.auth_code)
        self.signup_data["email"] = "test@gmail.com"
        self.signup_data["nickname"] = "test1"

        # 닉네임 유효성 테스트 - 닉네임이 1자리일 경우
        signup_data_nickname_below_1 = self.signup_data.copy()
        signup_data_nickname_below_1["nickname"] = "t"
        response = self.client.post(reverse("signup"), signup_data_nickname_below_1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["nickname"][0], "닉네임은 2자리 이상, 15자리 이하로 입력해주세요."
        )

        # 닉네임 유효성 테스트 - 닉네임이 16자리 이상일 경우
        signup_data_nickname_over_16 = self.signup_data.copy()
        signup_data_nickname_over_16["nickname"] = "testtesttesttest"
        response = self.client.post(reverse("signup"), signup_data_nickname_over_16)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["nickname"][0], "닉네임은 2자리 이상, 15자리 이하로 입력해주세요."
        )

        # 닉네임 유효성 테스트 - 닉네임에 특수문자가 있을 경우
        signup_data_nickname_special = self.signup_data.copy()
        signup_data_nickname_special["nickname"] = "test!@"
        response = self.client.post(reverse("signup"), signup_data_nickname_special)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["nickname"][0], "닉네임에 특수문자를 포함할 수 없습니다.")

        # 닉네임 유효성 테스트 - 닉네임이 비어있을 경우
        signup_data_empty_nickname = self.signup_data.copy()
        signup_data_empty_nickname["nickname"] = ""
        response = self.client.post(reverse("signup"), signup_data_empty_nickname)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["nickname"][0], "닉네임을 입력해주세요.")

        # 닉네임 유효성 테스트 - 중복된 닉네임일 경우
        signup_data_duplicate_nickname = self.signup_data.copy()
        signup_data_duplicate_nickname["nickname"] = "test"
        response = self.client.post(reverse("signup"), signup_data_duplicate_nickname)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["nickname"][0], "중복된 닉네임입니다.")

        # 이메일 유효성 테스트 - 이메일 형식이 아닐 경우
        signup_data_wrong_email = self.signup_data.copy()
        signup_data_wrong_email["email"] = "test"
        response = self.client.post(reverse("signup"), signup_data_wrong_email)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["email"][0], "이메일 형식을 확인해주세요.")

        # 이메일 유효성 테스트 - 이메일이 비어있을 경우
        signup_data_empty_email = self.signup_data.copy()
        signup_data_empty_email["email"] = ""
        response = self.client.post(reverse("signup"), signup_data_empty_email)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["email"][0], "이메일을 입력해주세요.")

        # 이메일 유효성 테스트 - 중복된 이메일일 경우
        signup_data_duplicate_email = self.signup_data.copy()
        signup_data_duplicate_email["email"] = "elwl5515@gmail.com"
        response = self.client.post(reverse("signup"), signup_data_duplicate_email)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["email"][0], "중복된 이메일입니다.")
        print("이메일 회원가입 테스트 END")

    def test_account_login(self):
        """
        로그인 테스트
        1. 정상 로그인 테스트
        2. 없는 사용자 테스트
        3. 비밀번호 불일치 테스트
        4. 이메일을 입력하지 않은 경우 테스트
        5. 비밀번호를 입력하지 않은 경우 테스트
        """
        print("-- 로그인 테스트 BEGIN --")
        self.client.post(reverse("signup"), self.signup_data, format="multipart")
        email_body = mail.outbox[0].body
        auth_url = email_body.split("인증 URL: ")[1].split("\n")[0]
        self.client.get(auth_url)

        # 정상 로그인 테스트
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.client.logout()

        # 없는 사용자 테스트
        response = self.client.post(
            reverse("login"),
            {"username": "test@test.com", "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."
        )

        # 비밀번호 불일치 테스트
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": "testtest12!@#"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode("utf-8"), "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."
        )

        # 이메일을 입력하지 않은 경우 테스트
        response = self.client.post(
            reverse("login"),
            {"username": "", "password": self.password},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "이메일을 입력해주세요.")

        # 비밀번호를 입력하지 않은 경우 테스트
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "비밀번호를 입력해주세요.")
        print("-- 로그인 테스트 END --")

    def test_account_logout(self):
        """
        로그아웃 테스트
        1. 정상 로그아웃 테스트
        2. 로그인하지 않은 사용자 테스트
        3. 로그아웃 후 로그인 테스트
        """
        print("-- 로그아웃 테스트 BEGIN --")
        # 정상 로그아웃 테스트
        self.client.post(reverse("signup"), self.signup_data, format="multipart")
        email_body = mail.outbox[0].body
        auth_url = email_body.split("인증 URL: ")[1].split("\n")[0]
        self.client.get(auth_url)
        self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
            follow=True,
        )
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

        # 로그인하지 않은 사용자 테스트
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "로그인되지 않은 사용자입니다.")

        # 로그아웃 후 로그인 테스트
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        print("-- 로그아웃 테스트 END --")

    def test_account_profile(self):
        """
        프로필 테스트
        1. 정상 프로필 응답 테스트
        2. 존재하지 않는 사용자의 프로필 요청 테스트
        3. 로그인하지 않은 사용자의 프로필 요청 테스트
        """
        print("-- 프로필 테스트 BEGIN --")
        # 정상 프로필 응답 테스트
        self.client.post(reverse("signup"), self.signup_data, format="multipart")
        email_body = mail.outbox[0].body
        auth_url = email_body.split("인증 URL: ")[1].split("\n")[0]
        self.client.get(auth_url)
        self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
            follow=True,
        )
        response = self.client.get(reverse("profile", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user_profile"].email, self.email)
        self.assertEqual(response.context["user_profile"].nickname, self.nickname)
        self.assertEqual(
            response.context["user_profile"].development_field, self.development_field
        )
        self.assertEqual(
            response.context["user_profile"].content, self.signup_data["content"]
        )

        # 존재하지 않는 사용자의 프로필 요청 테스트
        response = self.client.get(reverse("profile", kwargs={"pk": 2}), follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode("utf-8"), "존재하지 않는 사용자입니다.")

        # 로그인하지 않은 사용자의 프로필 요청 테스트
        self.client.logout()
        response = self.client.get(reverse("profile", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode("utf-8"), "로그인되지 않은 사용자입니다.")

        print("-- 프로필 테스트 END --")
