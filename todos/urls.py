from django.urls import path
from . import views

urlpatterns = [
    path("", views.ToDoList.as_view(), name="todo_list"),
    path("personal/", views.PersonalToDoList.as_view(), name="personal_todo_list"),
    path("study/", views.StudyToDoList.as_view(), name="study_todo_list"),
    path("<int:pk>/", views.ToDoDetail.as_view(), name="todo_detail"),
    path(
        "personal/create/",
        views.PersonalToDoCreate.as_view(),
        name="personal_todo_create",
    ),
    path(
        "study/<int:study_id>/create/",
        views.StudyToDoCreate.as_view(),
        name="study_todo_create",
    ),
    path(
        "personal/edit/<int:pk>/",
        views.PersonalToDoUpdate.as_view(),
        name="personal_todo_edit",
    ),
    path("delete/<int:pk>/", views.ToDoDelete.as_view(), name="todo_delete"),
]
