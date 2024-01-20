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

    def clean_category(self):
        category = self.cleaned_data["category"]
        if category == "":
            raise forms.ValidationError("카테고리를 선택해주세요.")
        return category

    def clean_goal(self):
        goal = self.cleaned_data["goal"]
        if goal == "":
            raise forms.ValidationError("목표를 입력해주세요.")
        return goal

    def clean_start_at(self):
        start_at = self.cleaned_data["start_at"]
        if start_at == "":
            raise forms.ValidationError("시작일을 입력해주세요.")
        elif start_at < datetime.date.today():
            raise forms.ValidationError("오늘 이전의 날짜를 선택할 수 없습니다.")
        return start_at

    def clean_end_at(self):
        end_at = self.cleaned_data["end_at"]
        if end_at == "":
            raise forms.ValidationError("종료일을 입력해주세요.")
        elif end_at < datetime.date.today():
            raise forms.ValidationError("오늘 이전의 날짜를 선택할 수 없습니다.")
        return end_at

    def clean_title(self):
        title = self.cleaned_data["title"]
        if title == "":
            raise forms.ValidationError("스터디명을 입력해주세요.")
        return title

    def clean_difficulty(self):
        difficulty = self.cleaned_data["difficulty"]
        if difficulty == "":
            raise forms.ValidationError("난이도를 선택해주세요.")
        return difficulty

    def clean_max_member(self):
        max_member = self.cleaned_data["max_member"]
        if max_member == "":
            raise forms.ValidationError("최대 인원을 입력해주세요.")
        elif max_member < 2:
            raise forms.ValidationError("최대 인원은 2명 이상이어야 합니다.")
        return max_member


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
