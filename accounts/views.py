from typing import Any
import uuid
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.views.generic import CreateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from allauth.socialaccount.views import SignupView as BaseSignupView
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _

from .forms import SignupForm, CustomLoginForm


class SignupView(CreateView):
    """
    회원가입 View
    """

    User = get_user_model()
    model = User
    form_class = SignupForm
    template_name = "accounts/signup.html"

    def post(self, request, *args, **kwargs):
        """
        회원가입 메서드
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            profile_image = request.FILES["profile_image"]
            token = uuid.uuid4()
            user = form.save(commit=False)
            if profile_image:
                user.profile_image = profile_image
            user.auth_code = token
            user.save()
            domain = get_current_site(request).domain
            confirm_link = f'http://{domain}{reverse("email_confirm", args=[token])}'

            title = "deVtail 인증 메일입니다."
            message = "인증을 완료하시려면 링크를 클릭해주세요.\n인증 URL: " + confirm_link
            email = EmailMessage(title, message, "elwl5515@gmail.com", [user.email])
            email.send()

            return JsonResponse({"message": "인증 URL이 전송되었습니다. 메일을 확인해주세요."}, status=201)
        else:
            return JsonResponse(form.errors, status=400)


class SocialSignupView(BaseSignupView):
    template_name = "accounts/signup.html"


def email_confirm(request, token):
    """
    이메일 인증 메서드
    """
    User = get_user_model()
    user = User.objects.get(auth_code=token)
    user.auth_code = None
    user.is_active = True
    user.save()

    return JsonResponse({"message": "이메일 인증이 완료되었습니다. 회원가입이 완료되었습니다."}, status=200)


class CustomLoginView(LoginView):
    """
    로그인 View
    """

    template_name = "accounts/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """
        로그인 메서드
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> Any:
        """
        로그인 성공시 이동할 URL
        """
        url = self.get_redirect_url()
        return url or reverse_lazy("home")

    def form_invalid(self, form: AuthenticationForm):
        """
        로그인 실패시 메서드
        """
        form_errors = form.errors.get("__all__", [])
        if "존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다." in form_errors:
            return HttpResponseBadRequest(_("존재하지 않는 사용자이거나 비밀번호가 일치하지 않습니다."))
        elif "이메일을 입력해주세요." in form_errors:
            return HttpResponseBadRequest(_("이메일을 입력해주세요."))
        elif "비밀번호를 입력해주세요." in form_errors:
            return HttpResponseBadRequest(_("비밀번호를 입력해주세요."))


signup = SignupView.as_view()
social_signup = SocialSignupView.as_view()
login = CustomLoginView.as_view()
