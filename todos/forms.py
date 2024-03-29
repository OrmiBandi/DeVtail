from django import forms

from django.contrib.auth import get_user_model
from studies.models import Study, StudyMember
from todos.models import ToDo

User = get_user_model()


class PersonalToDoForm(forms.ModelForm):
    """
    개인 할 일 폼
    """

    start_at = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"}, time_attrs={"type": "time"}
        ),
        required=False,
    )
    end_at = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"}, time_attrs={"type": "time"}
        ),
        required=False,
    )

    class Meta:
        model = ToDo
        fields = (
            "status",
            "title",
            "content",
            "start_at",
            "end_at",
            "alert_set",
        )

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if bool(start_at) != bool(end_at):
            self.add_error("start_at", "시작일과 종료일 둘 다 입력되어야 합니다.")
            self.add_error("end_at", "시작일과 종료일 둘 다 입력되어야 합니다.")

        if (start_at and end_at) and (start_at > end_at):
            self.add_error("start_at", "시작일은 종료일보다 이전이어야 합니다.")
            self.add_error("end_at", "종료일은 시작일보다 이후이어야 합니다.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["data_widget_type"] = "textarea"


class StudyToDoForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=StudyMember.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    start_at = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"}, time_attrs={"type": "time"}
        ),
        required=False,
    )
    end_at = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"}, time_attrs={"type": "time"}
        ),
        required=False,
    )

    class Meta:
        model = ToDo
        fields = (
            "status",
            "title",
            "content",
            "start_at",
            "end_at",
            "alert_set",
            "assignees",
        )

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if bool(start_at) != bool(end_at):
            self.add_error("start_at", "시작일과 종료일 둘 다 입력되어야 합니다.")
            self.add_error("end_at", "시작일과 종료일 둘 다 입력되어야 합니다.")

        if (start_at and end_at) and (start_at > end_at):
            self.add_error("start_at", "시작일은 종료일보다 이전이어야 합니다.")
            self.add_error("end_at", "종료일은 시작일보다 이후이어야 합니다.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        study_id = kwargs.pop("study_id", None)
        super().__init__(*args, **kwargs)
        self.fields["assignees"].queryset = StudyMember.objects.filter(study=study_id)
        self.fields["content"].widget.attrs["data_widget_type"] = "textarea"
