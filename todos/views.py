from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import ToDo
from studies.models import Study, StudyMember
from .forms import PersonalToDoForm, StudyToDoForm

User = get_user_model()


class ToDoList(LoginRequiredMixin, ListView):
    """
    할 일 리스트
    """

    model = ToDo
    context_object_name = "todos"
    ordering = "-id"
    template_name = "todos/todo_board.html"

    def get_queryset(self):
        # ToDoAssignee에 연결된 ToDo 목록 가져오기
        todos = ToDo.objects.filter(todo_assignees__assignee=self.request.user)
        return todos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studies = Study.objects.filter(members__user=self.request.user)
        context["studies"] = studies

        return context


class PersonalToDoList(LoginRequiredMixin, ListView):
    """
    개인 할 일 리스트
    """

    model = ToDo
    context_object_name = "todos"
    ordering = "-id"

    def get_queryset(self):
        # ToDoAssignee에 연결된 ToDo 목록 가져오기
        todos = ToDo.objects.filter(
            todo_assignees__assignee=self.request.user, study__isnull=True
        )
        return todos


class StudyToDoList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    스터디 할 일 리스트
    """

    model = ToDo
    context_object_name = "todos"
    ordering = "-id"

    def get_queryset(self):
        study_id = self.request.GET.get("study")
        user_id = self.request.GET.get("user")

        # 사용자가 속한 스터디를 가져옴
        user_studies = StudyMember.objects.filter(user=self.request.user)

        # 스터디가 선택되지 않은 경우, 사용자가 속한 첫번째 스터디의 할 일을 가져옴
        if not study_id and user_studies.exists():
            study = user_studies.first().study.id
            todos = ToDo.objects.filter(study=study)

        # 스터디가 선택된 경우, 해당 스터디의 할 일을 가져옴
        else:
            if not user_studies.filter(study=study_id).exists():
                # 스터디에 가입되어있지 않은 경우 403 Forbidden 오류 발생
                raise PermissionDenied("스터디에 가입하거나 만들어야 사용 가능합니다.")

            todos = ToDo.objects.filter(study=study_id)

        # 사용자가 선택된 경우, 해당 사용자가 담당자인 할 일을 가져옴
        if user_id and user_id != "all":
            todos = todos.filter(todo_assignees__assignee=user_id)

        return todos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["studies"] = Study.objects.filter(members__user=self.request.user)

        study_id = self.request.GET.get("study")

        if study_id:
            selected_study = Study.objects.get(id=study_id)
            context["members"] = {
                selected_study: StudyMember.objects.filter(study=selected_study)
            }
        else:
            first_study = context["studies"].first()
            context["members"] = {
                first_study: StudyMember.objects.filter(study=first_study)
            }

        return context

    def test_func(self):
        study_id = self.request.GET.get("study")

        # 스터디가 선택되지 않은 경우, 사용자가 속한 첫 번째 스터디를 가져옴
        if not study_id:
            study_id = StudyMember.objects.filter(user=self.request.user).first()

            if study_id is not None:
                study_id = study_id.study.id

        # 현재 접근하려는 스터디에 대한 권한 확인
        return StudyMember.objects.filter(
            study=study_id, user=self.request.user
        ).exists()


class ToDoDetail(LoginRequiredMixin, DetailView):
    model = ToDo


class PersonalToDoCreate(LoginRequiredMixin, CreateView):
    """
    개인 할 일 생성
    """

    model = ToDo
    form_class = PersonalToDoForm
    success_url = reverse_lazy("personal_todo_list")

    def form_valid(self, form):
        todo = form.save(commit=False)
        todo.save()
        todo.todo_assignees.create(assignee=self.request.user)
        return super().form_valid(form)


class PersonalToDoUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    개인 할 일 수정
    """

    model = ToDo
    form_class = PersonalToDoForm
    success_url = reverse_lazy("personal_todo_list")

    def test_func(self):
        todo = self.get_object()
        return todo.todo_assignees.filter(assignee=self.request.user).exists()


class ToDoDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    할 일 삭제
    """

    model = ToDo
    success_url = reverse_lazy("todo_list")

    def test_func(self):
        todo = self.get_object()
        return todo.todo_assignees.filter(assignee=self.request.user).exists()


class StudyToDoCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    스터디 할 일 생성
    """

    model = ToDo
    form_class = StudyToDoForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["study_id"] = self.kwargs.get("study_id")
        return kwargs

    def form_valid(self, form):
        todo = form.save(commit=False)
        todo.study = Study.objects.get(id=self.kwargs.get("study_id"))
        todo.save()

        assignees = form.cleaned_data.get("assignees")
        for assignee in assignees:
            todo.todo_assignees.create(assignee=assignee.user)

        return super().form_valid(form)

    def get_success_url(self):
        return (
            reverse_lazy("study_todo_list")
            + "?study="
            + str(self.kwargs.get("study_id"))
        )

    def test_func(self):
        study_members = StudyMember.objects.filter(study=self.kwargs.get("study_id"))
        return study_members.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("studies:study_detail", pk=self.kwargs.get("study_id"))
        else:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )


class StudyToDoUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    스터디 할 일 수정
    """

    model = ToDo
    form_class = StudyToDoForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["study_id"] = self.kwargs.get("study_id")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        assignees = list(
            self.object.todo_assignees.values_list("assignee__id", flat=True)
        )
        initial["assignees"] = assignees
        return initial

    def form_valid(self, form):
        todo = form.save(commit=False)
        todo.save()

        assignees = form.cleaned_data.get("assignees")
        todo.todo_assignees.filter(todo=todo).delete()

        for assignee in assignees:
            todo.todo_assignees.create(assignee=assignee.user)

        return super().form_valid(form)

    def get_success_url(self):
        return (
            reverse_lazy("study_todo_list")
            + "?study="
            + str(self.kwargs.get("study_id"))
        )

    def test_func(self):
        study_members = StudyMember.objects.filter(study=self.kwargs.get("study_id"))
        return study_members.filter(user=self.request.user).exists()
