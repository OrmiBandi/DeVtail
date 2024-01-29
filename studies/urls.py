from django.urls import path, include

from . import views

app_name = "studies"

urlpatterns = [
    path("list/", views.StudyList.as_view(), name="study_list"),
    path("create/", views.StudyCreate.as_view(), name="study_create"),
    path("<int:pk>/", views.StudyDetail.as_view(), name="study_detail"),
    path("<int:pk>/update/", views.StudyUpdate.as_view(), name="study_update"),
    path("<int:pk>/delete/", views.StudyDelete.as_view(), name="study_delete"),
    path(
        "<int:pk>/comment/create/", views.CommentCreate.as_view(), name="comment_create"
    ),
    path(
        "<int:pk>/comment/<int:comment_pk>/update/",
        views.CommentUpdate.as_view(),
        name="comment_update",
    ),
    path(
        "<int:pk>/comment/<int:comment_pk>/delete/",
        views.CommentDelete.as_view(),
        name="comment_delete",
    ),
    path(
        "<int:pk>/comment/<int:comment_pk>/recomment/",
        views.RecommentCreate.as_view(),
        name="recomment_create",
    ),
    path(
        "<int:pk>/comment/<int:comment_pk>/recomment/<int:recomment_pk>/update/",
        views.RecommentUpdate.as_view(),
        name="recomment_update",
    ),
    path(
        "<int:pk>/comment/<int:comment_pk>/recomment/<int:recomment_pk>/delete/",
        views.RecommentDelete.as_view(),
        name="recomment_delete",
    ),
    path("<int:pk>/apply/", views.apply_study_join, name="apply_study_join"),
    path(
        "studymember/<int:studymember_id>/approve/",
        views.approve_study_join,
        name="approve_study_join",
    ),
    path(
        "studymember/<int:studymember_id>/reject/",
        views.reject_study_join,
        name="reject_study_join",
    ),
    path(
        "<int:pk>/studymember/apply/list/",
        views.ApproveStudyJoinDetail.as_view(),
        name="study_member_apply_list",
    ),
    path(
        "<int:pk>/studymember/list/",
        views.ManageStudyMemberList.as_view(),
        name="study_member_list",
    ),
    path(
        "<int:pk>/studymember/<int:studymember_id>/delete/",
        views.DeleteStudyMember.as_view(),
        name="delete_study_member",
    ),
    path(
        "<int:pk>/studymember/<int:studymember_id>/manager/",
        views.DelegateAuthorityView.as_view(),
        name="change_study_manager",
    ),
    path(
        "<int:pk>/studymember/delete/",
        views.WithdrawStudy.as_view(),
        name="withdraw_study",
    ),
    path(
        "<int:pk>/studymember/<int:studymember_id>/addblacklist/",
        views.AddBlacklistUser.as_view(),
        name="add_blacklist_user",
    ),
    path(
        "<int:pk>/blacklist/",
        views.BlacklistUserList.as_view(),
        name="blacklist_user_list",
    ),
    path(
        "<int:pk>/blacklist/<int:blacklist_id>/delete/",
        views.DeleteBlacklistUser.as_view(),
        name="delete_blacklist_user",
    ),
]
