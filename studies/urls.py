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
]
