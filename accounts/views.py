import requests
import uuid, environ
from typing import Any
from pathlib import Path
from django.http.response import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.db.models.base import Model as Model
from django.views.generic.edit import UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponseBadRequest
from allauth.account.views import LogoutView
from allauth.socialaccount.views import SignupView as BaseSignupView

from .forms import (
    SignupForm,
    CustomLoginForm,
    AccountUpdateForm,
    AccountDeleteForm,
    PasswordChangeForm,
)

User = get_user_model()
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(env_file="../../.env")


class SignupView(CreateView):
    """
    회원가입 View
    """

    model = User
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")

    def post(self, request, *args, **kwargs):
        """
        회원가입 메서드
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            token = uuid.uuid4()
            user = form.save(commit=False)
            if "profile_image" in request.FILES:
                profile_image = request.FILES["profile_image"]
                user.profile_image = profile_image
            user.auth_code = token
            user.save()
            domain = get_current_site(request).domain
            confirm_link = (
                f'http://{domain}{reverse("accounts:email_confirm", args=[token])}'
            )

            title = "deVtail 인증 메일입니다."
            message = (
                "인증을 완료하시려면 링크를 클릭해주세요.\n인증 URL: " + confirm_link
            )
            email = EmailMessage(title, message, "elwl5515@gmail.com", [user.email])
            email.send()
            messages.success(request, "인증 URL이 전송되었습니다. 메일을 확인해주세요.")
            return render(request, "accounts/signup_success.html", {"form": form})
        else:
            context = {}
            context["form"] = form
            for msg in form.errors.as_data():
                context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )


class SocialSignupView(BaseSignupView):

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def email_confirm(request, token):
    """
    이메일 인증 메서드
    """
    User = get_user_model()
    user = User.objects.get(auth_code=token)
    user.auth_code = None
    user.is_active = True
    user.save()
    messages.success(
        request, "이메일 인증이 완료되었습니다. 회원가입이 완료되었습니다."
    )
    return redirect("accounts:login")


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
            context = {}
            for msg in form.errors.as_data():
                if "이 계정은 유효하지 않습니다." in form.errors[msg][0]:
                    context[f"error_username"] = form.errors[msg][0]
                else:
                    context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )

    def get_success_url(self) -> Any:
        """
        로그인 성공시 이동할 URL
        """
        url = self.get_redirect_url()
        return url or reverse_lazy("main:home")


class CustomLogoutView(LogoutView):
    """
    로그아웃 View
    """

    def dispatch(self, request, *args, **kwargs):
        """
        로그아웃 메서드
        """
        if not request.user.is_authenticated:
            return HttpResponseBadRequest(_("로그인되지 않은 사용자입니다."))
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "user_profile"

    def handle_no_permission(self):
        """
        로그인 하지 않은 사용자의 경우
        "로그인되지 않은 사용자입니다."라는
        메시지를 에러 메시지에 담는 메서드
        """
        return HttpResponse(_("로그인되지 않은 사용자입니다."), status=401)

    def get_object(self):
        """
        입력받은 pk 값의 유저를 반환하는 메서드
        """
        pk = self.kwargs.get("pk")
        obj = User.objects.filter(pk=pk).first()
        return obj

    def get(self, request, *args, **kwargs):
        """
        프로필 요청을 처리하는 get 메서드
            - pk로 조회한 유저의 프로필이 없는 경우 404 에러 반환
        """
        obj = self.get_object()
        if not obj:
            return HttpResponse(_("존재하지 않는 사용자입니다."), status=404)
        return super().get(request, *args, **kwargs)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "accounts/account_update.html"
    form_class = AccountUpdateForm
    context_object_name = "account"

    def get_success_url(self):
        """
        수정 성공 시 프로필 페이지로 이동시키는 메서드
        """
        return reverse_lazy("accounts:profile", kwargs={"pk": self.object.pk})

    def handle_no_permission(self):
        """
        로그인 하지 않은 사용자의 경우
        "로그인되지 않은 사용자입니다."라는
        메시지를 에러 메시지에 담는 메서드
        """
        return HttpResponse(_("로그인되지 않은 사용자입니다."), status=401)

    def get_object(self, queryset=None):
        """
        현재 로그인한 유저를 반환하는 메서드
        """
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "사용자 정보가 수정되었습니다.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "사용자 정보 수정에 실패했습니다.")
        return response

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        form = self.get_form()
        if not form.is_valid():
            context = {}
            context["form"] = form
            for msg in form.errors.as_data():
                context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )
        return response


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    form_class = AccountDeleteForm
    template_name = "accounts/account_delete.html"
    context_object_name = "account"
    success_url = reverse_lazy("main:home")

    def get_object(self, queryset=None):
        return self.request.user

    def handle_no_permission(self):
        """
        로그인 하지 않은 사용자의 경우
        "로그인되지 않은 사용자입니다."라는
        메시지를 에러 메시지에 담는 메서드
        """
        return HttpResponse(_("로그인되지 않은 사용자입니다."), status=401)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        form = self.get_form()
        if not form.is_valid():
            context = {}
            for msg in form.errors.as_data():
                context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class PasswordChangeView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "accounts/password_change.html"
    form_class = PasswordChangeForm
    context_object_name = "account"

    def get_success_url(self):
        """
        수정 성공 시 프로필 페이지로 이동시키는 메서드
        """
        return reverse_lazy("accounts:profile", kwargs={"pk": self.object.pk})

    def handle_no_permission(self):
        """
        로그인 하지 않은 사용자의 경우
        "로그인되지 않은 사용자입니다."라는
        메시지를 에러 메시지에 담는 메서드
        """
        return HttpResponse(_("로그인되지 않은 사용자입니다."), status=401)

    def get_object(self, queryset=None):
        """
        현재 로그인한 유저를 반환하는 메서드
        """
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "비밀번호가 변경되었습니다.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "비밀번호 변경에 실패했습니다.")
        return response

    def post(self, request: HttpRequest, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        form = self.get_form()
        if not form.is_valid():
            context = {}
            for msg in form.errors.as_data():
                context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class PasswordResetCustomView(PasswordResetView):
    template_name = "accounts/password_find.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            return HttpResponseBadRequest("존재하지 않는 이메일입니다.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"domain": get_current_site(self.request).domain})
        return context


class PasswordResetConfirmCustomView(PasswordResetConfirmView):
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("accounts:login")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    # def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    #     uidb64 = kwargs["uidb64"]
    #     token = kwargs["token"]

    #     uid = urlsafe_base64_decode(uidb64).decode()
    #     user = User.objects.get(pk=uid)
    #     if not self.token_generator.check_token(user, token):
    #         raise ValueError("The password reset link is invalid")

    #     return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "비밀번호가 초기화되었습니다.")
        return response


class GithubSignupView(CreateView):
    """
    회원가입 View
    """

    model = User
    form_class = SignupForm
    template_name = "accounts/github_signup.html"
    success_url = reverse_lazy("accounts:login")

    def post(self, request, *args, **kwargs):
        """
        GitHub 계정 기반 회원가입 메서드
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.login_method = User.LOGIN_GITHUB
            if request.POST.get("profile_image"):
                user.profile_image = request.POST.get("profile_image")
            user.save()
            return redirect("accounts:login")
        else:
            context = {}
            context["form"] = form
            for msg in form.errors.as_data():
                context[f"error_{msg}"] = form.errors[msg][0]
            return render(
                request,
                self.template_name,
                context,
                status=HttpResponseBadRequest.status_code,
            )


def github_login(request):
    try:
        if request.user.is_authenticated:
            raise ValueError("이미 로그인되어 있습니다.")
        client_id = env("GITHUB_CLIENT_ID")
        redirect_uri = env("GITHUB_REDIRECT_URI")
        scope = "user"
        return redirect(
            f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}"
        )
    except Exception as error:
        messages.error(request, error)
        return redirect("accounts:login")


def github_callback(request):
    try:
        if request.user.is_authenticated:
            raise ValueError("이미 로그인되어 있습니다.")
        code = request.GET.get("code", None)
        client_id = env("GITHUB_CLIENT_ID")
        client_secret = env("GITHUB_CLIENT_SECRET")

        token_request = requests.post(
            f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
            headers={"Accept": "application/json"},
        )
        token_json = token_request.json()
        error = token_json.get("error", None)

        if error:
            raise Exception(error)

        access_token = token_json.get("access_token")
        profile_response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        email_response = requests.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_response.json()
        email_json = email_response.json()[0]
        email = email_json.get("email", None)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.login_method != User.LOGIN_GITHUB:
                context = {}
                context["error"] = "GitHub으로 가입한 계정이 아닙니다."
                return render(
                    request,
                    "accounts/login.html",
                    context,
                    status=HttpResponseBadRequest.status_code,
                )
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("main:home")
        else:
            context = {}
            signup_form = SignupForm(
                initial={
                    "email": email,
                    "nickname": profile_json.get("login"),
                    "profile_image": profile_json.get("avatar_url"),
                }
            )

            context["form"] = signup_form

            return render(request, "accounts/github_signup.html", context)
    except Exception as error:
        context = {}
        if "bad_verification_code" in error:
            context["error"] = "잘못된 GitHub코드입니다."
        else:
            context["error"] = error
        return render(
            request,
            "accounts/login.html",
            context,
            status=HttpResponseBadRequest.status_code,
        )


signup = SignupView.as_view()
social_signup = SocialSignupView.as_view()
login = CustomLoginView.as_view()
logout = CustomLogoutView.as_view()
profile = ProfileView.as_view()
account_update = AccountUpdateView.as_view()
account_delete = AccountDeleteView.as_view()
password_change = PasswordChangeView.as_view()
password_reset = PasswordResetCustomView.as_view()
password_reset_confirm = PasswordResetConfirmCustomView.as_view()
github_signup = GithubSignupView.as_view()
