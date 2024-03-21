from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        print(form.cleaned_data)
        # user = super().save_user(request, user, form, commit=False)
        profile_image = form.cleaned_data.get("profile_image")
        if profile_image:
            user.profile_image = profile_image
        if commit:
            user.save()
        return user
