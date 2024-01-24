from django import forms
from .models import Study, Comment, Recomment
import datetime


class StudyForm(forms.ModelForm):
    category = forms.CharField(
        required=True,
        error_messages={"required": "카테고리를 선택해주세요."},
    )
    goal = forms.CharField(
        required=True,
        error_messages={"required": "목표를 입력해주세요."},
    )
    start_at = forms.DateField(
        initial=datetime.date.today,
        required=True,
        error_messages={"required": "시작일을 입력해주세요."},
    )
    end_at = forms.DateField(
        initial=datetime.date.today,
        required=True,
        error_messages={"required": "종료일을 입력해주세요."},
    )
    title = forms.CharField(
        required=True,
        error_messages={"required": "스터디명을 입력해주세요."},
    )
    difficulty = forms.CharField(
        required=True,
        error_messages={"required": "난이도를 선택해주세요."},
    )
    max_member = forms.IntegerField(
        required=True,
        error_messages={"required": "최대 인원을 입력해주세요."},
    )

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

    def save(self, commit=True):
        study = super().save(commit=False)
        study.thumbnail = self.cleaned_data["thumbnail"]
        study.introduce = self.cleaned_data["introduce"]
        study.save()
        return study

    def clean_start_at(self):
        start_at = self.cleaned_data["start_at"]
        if start_at < datetime.date.today():
            raise forms.ValidationError("오늘 이전의 날짜를 선택할 수 없습니다.")
        return start_at

    def clean_end_at(self):
        end_at = self.cleaned_data["end_at"]
        if end_at < datetime.date.today():
            raise forms.ValidationError("오늘 이전의 날짜를 선택할 수 없습니다.")
        return end_at

    def clean_max_member(self):
        max_member = self.cleaned_data["max_member"]
        if max_member < 2:
            raise forms.ValidationError("최대 인원은 2명 이상이어야 합니다.")
        return max_member


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        required=True,
        error_messages={"required": "댓글을 입력해주세요."},
    )

    class Meta:
        model = Comment
        fields = [
            "content",
        ]


class RecommentForm(forms.ModelForm):
    content = forms.CharField(
        required=True,
        error_messages={"required": "대댓글을 입력해주세요."},
    )

    class Meta:
        model = Recomment
        fields = [
            "content",
        ]
