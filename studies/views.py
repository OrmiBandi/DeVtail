from .models import (
    Study,
    Category,
    Comment,
    Recomment,
    StudyMember,
    Tag,
    Blacklist,
    Favorite,
    Schedule,
    RefLink,
)
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import StudyForm, CommentForm, RecommentForm, BlacklistForm, FavoriteForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

User = get_user_model()


class StudyList(ListView):
    """
    전체 스터디 리스트 조회
    스터디 새로 생성 시 생성된 스터디를 리스트에서 조회 가능
    """

    model = Study
    ordering = ["-created_at"]

    template_name = "studies/study_list.html"
    context_object_name = "studies"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("favorites")
        q = self.request.GET.get("q", "")
        tag = self.request.GET.get("tag", "")
        category = self.request.GET.get("category", "")
        difficulty = self.request.GET.get("difficulty", "")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(introduce__icontains=q)
            )

        if tag:
            queryset = queryset.filter(tag__name__in=[tag])

        if category:
            queryset = queryset.filter(category=category)

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["categories"] = Category.objects.all()
        context["difficulty_choices"] = Study.difficulty_choices
        return context


class MyStudyList(LoginRequiredMixin, ListView):
    """
    내 스터디 리스트 조회
    로그인한 유저가 가입한 스터디를 리스트에서 조회 가능
    스터디 생성 시 생성된 스터디를 리스트에서 조회 가능
    """

    model = StudyMember

    template_name = "studies/my_study_list.html"
    context_object_name = "mystudies"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset.select_related("study")
            .filter(user=self.request.user)
            .order_by("-study__created_at")
        )

        q = self.request.GET.get("q", "")
        tag = self.request.GET.get("tag", "")
        category = self.request.GET.get("category", "")
        difficulty = self.request.GET.get("difficulty", "")

        if q:
            queryset = queryset.filter(
                Q(study__title__icontains=q) | Q(study__introduce__icontains=q)
            )

        if tag:
            queryset = queryset.filter(study__tag__name__in=[tag])

        if category:
            queryset = queryset.filter(study__category=category)

        if difficulty:
            queryset = queryset.filter(study__difficulty=difficulty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["categories"] = Category.objects.all()
        context["difficulty_choices"] = Study.difficulty_choices
        return context


class StudyCreate(LoginRequiredMixin, CreateView):
    """
    스터디 생성
    로그인한 유저만이 스터디를 생성할 수 있습니다.
    스터디 생성시 studymember 모델의 user를 참조하여 지정하고, is_manager와 is_accepted를 True로 지정합니다.
    current_member에 1이 추가됩니다.
    """

    model = Study
    form_class = StudyForm
    success_url = reverse_lazy("studies:study_list")
    template_name = "studies/study_create_form.html"

    def form_valid(self, form):
        study = form.save(commit=False)
        study.save()
        StudyMember.objects.create(
            study=study, user=self.request.user, is_manager=True, is_accepted=True
        )

        tags_input = form.cleaned_data["tags"]
        tags_list = tags_input.strip(",").split(",")

        if len(tags_list) > 1:
            for tag in tags_list:
                tag = Tag.objects.get_or_create(name=tag.strip())[0]
                study.tag.add(tag)

        days = form.cleaned_data["days"]

        for day in days:
            Schedule.objects.create(
                study=study,
                day=day,
                start_time=form.cleaned_data["start_time"],
                end_time=form.cleaned_data["end_time"],
            )

        ref_links_input = form.cleaned_data["ref_links"]
        if ref_links_input != "":
            ref_links_list = ref_links_input.strip(",").split(",")

            for ref_link in ref_links_list:
                RefLink.objects.create(
                    link_type=ref_link.split(";")[0].strip(),
                    url=ref_link.split(";")[1].strip(),
                    study=study,
                )

        return super().form_valid(form)


class StudyDetail(DetailView):
    """
    스터디 상세 조회
    """

    model = Study
    template_name = "studies/study_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        study_members = StudyMember.objects.filter(
            study=self.object, user=self.request.user
        )
        accept_members = study_members.filter(is_accepted=True, user=self.request.user)

        context["study_members"] = {
            "accept": accept_members,
            "pending": study_members,
        }

        context["request_user"] = {
            "apply": study_members.filter(is_accepted=False, user=self.request.user),
        }

        schedules = Schedule.objects.filter(study=self.object)
        for schedule in schedules:
            schedule.day_display = dict(Schedule.day_choices).get(schedule.day, "")
        context["schedules"] = schedules
        print(context["study_members"])
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        study = Study.objects.get(pk=pk)
        study.save()

        return super().get_object(queryset)


class StudyUpdate(UserPassesTestMixin, UpdateView):
    """
    스터디 수정
    로그인한 유저 중 스터디 생성자만이 스터디를 수정할 수 있습니다.
    스터디 멤버의 is_manager가 True인 경우에만 스터디를 수정할 수 있습니다.
    """

    model = Study
    form_class = StudyForm
    template_name = "studies/study_update_form.html"

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        study = self.get_object()
        studymember = StudyMember.objects.get(study=study, user=self.request.user)
        return studymember.user == self.request.user and studymember.is_manager

    def form_valid(self, form):
        study = form.save(commit=False)
        study.tag.clear()

        tags_input = form.cleaned_data["tags"]
        tags_list = tags_input.strip(",").split(",")
        if len(tags_list) > 1:
            for tag in tags_list:
                tag = Tag.objects.get_or_create(name=tag.strip())[0]
                study.tag.add(tag)

        days = form.cleaned_data["days"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        Schedule.objects.filter(study=study).delete()

        for day in days:
            Schedule.objects.create(
                study=study, day=day, start_time=start_time, end_time=end_time
            )

        ref_links_input = form.cleaned_data["ref_links"]
        if ref_links_input != "":
            RefLink.objects.filter(study=study).delete()
            ref_links_list = ref_links_input.strip(",").split(",")

            for ref_link in ref_links_list:
                RefLink.objects.create(
                    link_type=ref_link.split(";")[0].strip(),
                    url=ref_link.split(";")[1].strip(),
                    study=study,
                )

        return super().form_valid(form)


class StudyDelete(UserPassesTestMixin, DeleteView):
    """
    스터디 삭제
    로그인한 유저 중 스터디 생성자만이 스터디를 삭제할 수 있습니다.
    스터디 멤버의 is_manager가 True인 경우에만 스터디를 삭제할 수 있습니다.
    """

    model = Study
    success_url = reverse_lazy("studies:study_list")

    def test_func(self):
        study = self.get_object()
        studymember = StudyMember.objects.get(study=study, user=self.request.user)
        return studymember.user == self.request.user and studymember.is_manager


class CommentCreate(LoginRequiredMixin, CreateView):
    """
    댓글 작성
    로그인한 유저만이 댓글을 작성할 수 있습니다.
    comment 모델의 user를 로그인한 유저 및 요청한 유저로 지정합니다.
    """

    model = Comment
    form_class = CommentForm
    template_name = "studies/form.html"

    def form_valid(self, form):
        study = get_object_or_404(Study, pk=self.kwargs["pk"])
        comment = form.save(commit=False)
        comment.study = study
        comment.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.study.pk})


class CommentUpdate(UserPassesTestMixin, UpdateView):
    """
    댓글 수정
    """

    model = Comment
    form_class = CommentForm
    template_name = "studies/form.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs["comment_pk"])

    def form_valid(self, form):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        form.instance.study = comment.study
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.study.pk})


class CommentDelete(UserPassesTestMixin, DeleteView):
    """
    댓글 삭제
    """

    model = Comment

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs["comment_pk"])

    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.study.pk})


class RecommentCreate(LoginRequiredMixin, CreateView):
    """
    대댓글 작성
    """

    model = Recomment
    form_class = RecommentForm
    template_name = "studies/form.html"

    def form_valid(self, form):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        recomment = form.save(commit=False)
        recomment.comment = comment
        recomment.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "studies:study_detail", kwargs={"pk": self.object.comment.study.pk}
        )


class RecommentUpdate(UserPassesTestMixin, UpdateView):
    """
    대댓글 수정
    """

    model = Recomment
    form_class = RecommentForm
    template_name = "studies/form.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Recomment, pk=self.kwargs["recomment_pk"])

    def form_valid(self, form):
        recomment = get_object_or_404(Recomment, pk=self.kwargs["recomment_pk"])
        form.instance.comment = recomment.comment
        return super().form_valid(form)

    def test_func(self):
        recomment = self.get_object()
        return recomment.user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "studies:study_detail", kwargs={"pk": self.object.comment.study.pk}
        )


class RecommentDelete(UserPassesTestMixin, DeleteView):
    """
    대댓글 삭제
    """

    model = Recomment

    def get_object(self, queryset=None):
        return get_object_or_404(Recomment, pk=self.kwargs["recomment_pk"])

    def test_func(self):
        recomment = self.get_object()
        return recomment.user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "studies:study_detail", kwargs={"pk": self.object.comment.study.pk}
        )


class ApproveStudyJoinDetail(UserPassesTestMixin, DetailView):
    """
    스터디 가입 승인
    스터디 생성자만이 스터디 가입을 승인할 수 있습니다.
    스터디 생성자가 스터디 가입을 승인하면 studymember 모델의 is_accept를 True로, is_manager를 False로 지정합니다.
    """

    model = StudyMember, Study
    template_name = "studies/approve_study_join.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Study, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study_leader"] = StudyMember.objects.get(
            study=self.object, is_manager=True
        )
        context["study_members"] = StudyMember.objects.filter(
            study=self.object, is_accepted=False
        )
        return context

    def test_func(self):
        study = self.get_object()
        studyleader = StudyMember.objects.get(study=study, is_manager=True)
        return studyleader.user == self.request.user


class ManageStudyMemberList(UserPassesTestMixin, DetailView):
    """
    스터디 멤버 관리 리스트 조회
    스터디 생성자만이 리스트를 조회할 수 있습니다.
    """

    model = StudyMember, Study
    template_name = "studies/manage_study_member.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Study, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study_leader"] = StudyMember.objects.get(
            study=self.object, is_manager=True
        )
        context["study_members"] = StudyMember.objects.filter(
            study=self.object, is_accepted=True
        )
        return context

    def test_func(self):
        study = self.get_object()
        studyleader = StudyMember.objects.get(study=study, is_manager=True)
        return studyleader.user == self.request.user


class DeleteStudyMember(UserPassesTestMixin, DeleteView):
    """
    스터디 멤버 삭제
    스터디 생성자만이 스터디 멤버를 삭제할 수 있습니다.
    """

    model = StudyMember

    def get_object(self, queryset=None):
        return get_object_or_404(StudyMember, pk=self.kwargs["studymember_id"])

    def test_func(self):
        studymember = self.get_object()
        studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
        return studyleader.user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "studies:study_member_list", kwargs={"pk": self.object.study.pk}
        )


class DelegateAuthorityView(UserPassesTestMixin, UpdateView):
    """
    스터디 멤버 관리자 위임
    스터디 생성자만이 스터디 멤버 관리자를 위임할 수 있습니다.
    """

    model = StudyMember
    fields = ["is_manager"]

    def get_object(self, queryset=None):
        return get_object_or_404(StudyMember, pk=self.kwargs["studymember_id"])

    def test_func(self):
        studymember = self.get_object()
        studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
        return studyleader.user == self.request.user

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.study.pk})

    def form_valid(self, form):
        studymember = self.get_object()
        studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
        studyleader.is_manager = False
        studyleader.save()

        # 폼을 통해 처리되는 특정 모델의 인스턴스를 참조하는 경우
        form.instance.is_manager = True
        return super().form_valid(form)


class WithdrawStudy(LoginRequiredMixin, DeleteView):
    """
    스터디 탈퇴
    스터디 멤버만이 스터디를 탈퇴할 수 있습니다.
    스터디 멤버가 스터디를 탈퇴하면 studymember 모델을 삭제합니다.
    """

    model = StudyMember

    def get_object(self, queryset=None):
        return get_object_or_404(
            StudyMember, study=self.kwargs["pk"], user=self.request.user
        )

    def get_success_url(self):
        return reverse_lazy("studies:study_detail", kwargs={"pk": self.object.study.pk})


class AddBlacklistUser(UserPassesTestMixin, CreateView):
    """
    스터디 블랙리스트 추가
    post 요청을 보낼 경우 스터디 블랙리스트에 유저를 추가합니다.
    스터디 생성자만이 스터디 블랙리스트에 유저를 추가할 수 있습니다.
    """

    model = Blacklist
    form_class = BlacklistForm
    template_name = "studies/form.html"

    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=self.kwargs["pk"])
        studymember = get_object_or_404(StudyMember, pk=self.kwargs["studymember_id"])
        self.object = Blacklist.objects.create(study=study, user=studymember.user)
        studymember.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        return get_object_or_404(StudyMember, pk=self.kwargs["studymember_id"])

    def test_func(self):
        studymember = self.get_object()
        studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
        return studyleader.user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "studies:study_member_list", kwargs={"pk": self.object.study.pk}
        )


class BlacklistUserList(UserPassesTestMixin, DetailView):
    """
    스터디 블랙리스트 조회
    스터디 생성자만이 스터디 블랙리스트를 조회할 수 있습니다.
    """

    model = StudyMember, Study
    template_name = "studies/blacklist_user_list.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Study, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blacklist_users"] = Blacklist.objects.filter(study=self.object)
        return context

    def test_func(self):
        study = self.get_object()
        studyleader = StudyMember.objects.get(study=study, is_manager=True)
        return studyleader.user == self.request.user


class DeleteBlacklistUser(UserPassesTestMixin, DeleteView):
    """
    스터디 블랙리스트 삭제
    스터디 생성자만이 스터디 블랙리스트내에서 취소할 수 있습니다.
    """

    model = Blacklist

    def get_object(self, queryset=None):
        return get_object_or_404(Blacklist, pk=self.kwargs["blacklist_id"])

    def test_func(self):
        studymember = self.get_object()
        studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
        return studyleader.user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "studies:blacklist_user_list", kwargs={"pk": self.object.study.pk}
        )


class FavoriteStudyCreate(LoginRequiredMixin, CreateView):
    """
    스터디 즐겨찾기 추가
    로그인한 유저만이 스터디를 즐겨찾기에 추가할 수 있습니다.
    """

    model = Favorite
    form_class = FavoriteForm
    template_name = "studies/form.html"

    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=self.kwargs["pk"])
        favorite = Favorite.objects.filter(study=study, user=request.user)
        if favorite:
            return HttpResponseRedirect(self.get_success_url())
        self.object = Favorite.objects.create(study=study, user=request.user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", reverse_lazy("studies:study_list"))


class FaveriteStudyList(LoginRequiredMixin, ListView):
    """
    스터디 즐겨찾기 조회
    로그인한 유저만이 스터디 즐겨찾기를 조회할 수 있습니다.
    """

    model = Favorite
    template_name = "studies/favorite_study_list.html"
    context_object_name = "favorite_studies"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("study").filter(user=self.request.user)

        q = self.request.GET.get("q", "")
        tag = self.request.GET.get("tag", "")
        category = self.request.GET.get("category", "")
        difficulty = self.request.GET.get("difficulty", "")

        if q:
            queryset = queryset.filter(
                Q(study__title__icontains=q) | Q(study__introduce__icontains=q)
            )

        if tag:
            queryset = queryset.filter(study__tags__name__in=[tag])

        if category:
            queryset = queryset.filter(study__category=category)

        if difficulty:
            queryset = queryset.filter(study__difficulty=difficulty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["categories"] = Category.objects.all()
        context["difficulty_choices"] = Study.difficulty_choices
        return context


class FavoriteStudyDelete(UserPassesTestMixin, DeleteView):
    """
    스터디 즐겨찾기 삭제
    로그인한 유저만이 스터디 즐겨찾기를 삭제할 수 있습니다.
    """

    model = Favorite

    def get_object(self, queryset=None):
        return get_object_or_404(Favorite, pk=self.kwargs["favorite_id"])

    def test_func(self):
        favorite = self.get_object()
        return favorite.user == self.request.user

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", reverse_lazy("studies:study_list"))


@login_required
def apply_study_join(request, pk):
    """
    스터디 가입 신청
    스터디 가입 신청 시 studymember 모델의 user를 로그인한 유저로 지정합니다.
    1번 신청이 된 스터디는 다시 승인 혹은 취소 전까지 신청할 수 없습니다.
    블랙리스트에 등록된 유저는 스터디 가입을 신청할 수 없습니다.
    """
    study = get_object_or_404(Study, pk=pk)
    studymember = StudyMember.objects.filter(study=study, user=request.user)
    blacklists = Blacklist.objects.filter(study=study, user=request.user)
    if studymember:
        return redirect("studies:study_detail", pk=pk)
    elif blacklists:
        return redirect("studies:study_detail", pk=pk)
    StudyMember.objects.create(study=study, user=request.user)

    return redirect("studies:study_detail", pk=pk)


@login_required
def approve_study_join(request, studymember_id):
    """
    스터디 가입 승인
    스터디 생성자만이 스터디 가입을 승인할 수 있습니다.
    스터디 생성자가 스터디 가입을 승인하면 studymember 모델의 is_accept를 True로, is_manager를 False로 지정합니다.
    """
    studymember = get_object_or_404(StudyMember, id=studymember_id)
    studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
    if request.user != studyleader.user:
        raise PermissionDenied("접근 권한이 없습니다.")

    studymember.is_accepted = True
    studymember.is_manager = False
    studymember.save()

    return redirect("studies:study_detail", pk=studymember.study.pk)


@login_required
def reject_study_join(request, studymember_id):
    """
    스터디 가입 거절
    스터디 생성자만이 스터디 가입을 거절할 수 있습니다.
    스터디 생성자가 스터디 가입을 거절하면 studymember 모델을 삭제합니다.
    """
    studymember = get_object_or_404(StudyMember, id=studymember_id)
    studyleader = StudyMember.objects.get(study=studymember.study, is_manager=True)
    if request.user != studyleader.user:
        raise PermissionDenied("접근 권한이 없습니다.")

    studymember.delete()

    return redirect("studies:study_detail", pk=studymember.study.pk)
