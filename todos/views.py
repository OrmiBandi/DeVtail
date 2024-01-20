from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ToDo


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
