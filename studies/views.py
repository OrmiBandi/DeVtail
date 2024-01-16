from .models import Study, Comment, Recomment
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .forms import StudyForm, CommentForm, RecommentForm
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404


class StudyList(ListView):
    """
    전체 스터디 리스트 조회
    스터디 새로 생성 시 생성된 스터디를 리스트에서 조회 가능
    """

    model = Study
    ordering = ["-created_at"]

    template_name = "studies/study_list.html"
    context_object_name = "studies"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(introduce__icontains=q)
            )

        return queryset


class StudyCreate(CreateView):
    """
    스터디 생성
    로그인한 유저만이 스터디를 생성할 수 있습니다.
    """

    model = Study
    form_class = StudyForm
    success_url = reverse_lazy("studies:study_list")
    template_name = "studies/form.html"


class StudyDetail(DetailView):
    """
    스터디 상세 조회
    """

    model = Study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        study = Study.objects.get(pk=pk)
        study.save()

        return super().get_object(queryset)


class StudyUpdate(UpdateView):
    """
    스터디 수정
    로그인한 유저 중 스터디 생성자만이 스터디를 수정할 수 있습니다.
    스터디 멤버의 is_manager가 True인 경우에만 스터디를 수정할 수 있습니다.
    """

    model = Study
    form_class = StudyForm
    template_name = "studies/form.html"

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.pk})


class StudyDelete(DeleteView):
    """
    스터디 삭제
    로그인한 유저 중 스터디 생성자만이 스터디를 삭제할 수 있습니다.
    스터디 멤버의 is_manager가 True인 경우에만 스터디를 삭제할 수 있습니다.
    """

    model = Study
    success_url = reverse_lazy("studies:study_list")
