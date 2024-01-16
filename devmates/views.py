from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import DevMate

User = get_user_model()


class DevMateListView(LoginRequiredMixin, ListView):
    """
    DevMate 목록 보기
    Detail:
        is_accepted가 True인 경우의 목록
    """

    template_name = "devmate_list.html"
    model = DevMate
    context_object_name = "devmates"

    def get_queryset(self):
        return DevMate.objects.filter(
            Q(sent_user=self.request.user) | Q(received_user=self.request.user),
            is_accepted=True,
        )


class DevMateReceivedListView(LoginRequiredMixin, ListView):
    """
    DevMate 신청받은 목록 보기
    Detail:
        is_accepted가 False인 경우의 목록
    """

    template_name = "devmate_received_list.html"
    model = DevMate
    context_object_name = "devmates"

    def get_queryset(self):
        return DevMate.objects.filter(
            received_user=self.request.user, is_accepted=False
        )


class DevMateCreateView(LoginRequiredMixin, CreateView):
    """
    DevMate 신청
    """

    model = DevMate

    def post(self, request, *args, **kwargs):
        received_user = get_object_or_404(User, pk=self.kwargs["pk"])
        existing_devmate = DevMate.objects.filter(
            Q(sent_user=self.request.user, received_user=received_user)
            | Q(sent_user=received_user, received_user=self.request.user)
        )

        if existing_devmate.exists():
            messages.error(self.request, "이미 DevMate 신청을 보냈습니다.")
            return redirect("devmate_list")
        else:
            DevMate.objects.create(
                sent_user=self.request.user,
                received_user=received_user,
                is_accepted=False,
            )
            messages.success(self.request, "DevMate 신청이 완료되었습니다.")
            return redirect("devmate_list")


class DevMateUpdateView(LoginRequiredMixin, UpdateView):
    """
    DevMate 수락
    """

    model = DevMate
    http_method_names = ["put"]

    def put(self, request, *args, **kwargs):
        devmate = self.get_object()
        devmate.is_accepted = True
        devmate.save()
        messages.success(self.request, "DevMate 신청을 수락하였습니다.")
        return HttpResponse(status=200)


class DevMateDeleteView(LoginRequiredMixin, DeleteView):
    """
    DevMate 거절, 삭제
    """

    model = DevMate
    http_method_names = ["delete"]

    def delete(self, request, *args, **kwargs):
        devmate = self.get_object()
        devmate.delete()
        messages.success(request, "DevMate를 삭제하였습니다.")
        return HttpResponse(status=204)
