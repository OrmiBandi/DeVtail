from django import forms
from .models import (
    Study,
    Comment,
    Recomment,
    Category,
    Blacklist,
    Favorite,
    Schedule,
)
import datetime


class StudyForm(forms.ModelForm):
    thumbnail = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )
    category = forms.ModelChoiceField(
        required=True,
        queryset=Category.objects.all(),
        error_messages={"required": "카테고리를 선택해주세요."},
    )
    tags = forms.CharField(
        required=False,
        max_length=100,
    )
    ref_links = forms.CharField(
        required=False,
    )
    goal = forms.CharField(
        required=True,
        error_messages={"required": "목표를 입력해주세요."},
    )
    start_at = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=datetime.date.today,
        error_messages={"required": "시작일을 입력해주세요."},
    )
    end_at = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=datetime.date.today,
        error_messages={"required": "종료일을 입력해주세요."},
    )
    title = forms.CharField(
        required=True,
        error_messages={"required": "스터디명을 입력해주세요."},
    )
    difficulty = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect,
        choices=Study.difficulty_choices,
        error_messages={"required": "난이도를 선택해주세요."},
    )
    max_member = forms.IntegerField(
        required=True,
        error_messages={"required": "최대 인원을 입력해주세요."},
    )
    days = forms.MultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=Schedule.day_choices,
        error_messages={"required": "요일을 선택해주세요."},
    )
    start_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={"type": "time"}),
        initial=datetime.time(0, 0),
        error_messages={"required": "시작 시간을 입력해주세요."},
    )
    end_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={"type": "time"}),
        initial=datetime.time(0, 0),
        error_messages={"required": "종료 시간을 입력해주세요."},
    )

    class Meta:
        model = Study
        fields = [
            "category",
            "tags",
            "ref_links",
            "goal",
            "thumbnail",
            "start_at",
            "end_at",
            "introduce",
            "title",
            "difficulty",
            "max_member",
            "days",
            "start_time",
            "end_time",
        ]

    def __init__(self, *args, **kwargs):
        super(StudyForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = ",".join(
                [tag.name for tag in self.instance.tag.all()]
            )
            self.fields["ref_links"].initial = ",".join(
                [
                    f"{ref_link.link_type}; {ref_link.url}"
                    for ref_link in self.instance.ref_links.all()
                ]
            )
            self.fields["days"].initial = [
                schedule.day for schedule in self.instance.schedules.all()
            ]
            self.fields["start_time"].initial = self.instance.schedules.all()[
                0
            ].start_time
            self.fields["end_time"].initial = self.instance.schedules.all()[0].end_time

    def save(self, commit=True):
        study = super().save(commit=False)
        if self.cleaned_data["thumbnail"]:
            study.thumbnail = self.cleaned_data["thumbnail"]
        study.introduce = self.cleaned_data["introduce"]

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


class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = [
            "user",
            "study",
        ]


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = [
            "user",
            "study",
        ]
