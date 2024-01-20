from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ToDo
from .forms import PersonalToDoForm


class ToDoList(LoginRequiredMixin, ListView):
    """
    할 일 리스트
    """

    model = ToDo
    context_object_name = "todos"
    ordering = "-id"

    def get_queryset(self):
        # ToDoAssignee에 연결된 ToDo 목록 가져오기
        todos = ToDo.objects.filter(todo_assignees__assignee=self.request.user)
        return todos


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
