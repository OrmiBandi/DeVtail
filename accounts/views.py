from django.contrib.auth.views import LoginView


class LoginView(LoginView):
    template_name = "accounts/login.html"
