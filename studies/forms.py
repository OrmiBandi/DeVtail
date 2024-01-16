from django import forms
from .models import Study, Comment, Recomment
import datetime


class StudyForm(forms.ModelForm):
    start_at = forms.DateField(initial=datetime.date.today)
    end_at = forms.DateField(initial=datetime.date.today)

    class Meta:
        model = Study
        fields = [
            "category",
            "goal",
            "thumbnail",
            "start_at",
            "end_at",
            "introduce",
            "title",
            "difficulty",
            "current_member",
            "max_member",
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "content",
        ]


class RecommentForm(forms.ModelForm):
    class Meta:
        model = Recomment
        fields = [
            "content",
        ]
