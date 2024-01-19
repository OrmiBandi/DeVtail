import uuid
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.views.generic import CreateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from allauth.socialaccount.views import SignupView as BaseSignupView


# from .models import User
from .forms import SignupForm


class SignupView(CreateView):
    User = get_user_model()
    model = User
    form_class = SignupForm
    template_name = "accounts/signup.html"

    def post(self, request, *args, **kwargs):
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


signup = SignupView.as_view()
social_signup = SocialSignupView.as_view()
