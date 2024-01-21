from django.urls import path
from . import views

urlpatterns = [
    path("", views.ToDoList.as_view(), name="todo_list"),
    path("personal/", views.PersonalToDoList.as_view(), name="personal_todo_list"),
    path("<int:pk>/", views.ToDoDetail.as_view(), name="todo_detail"),
    path(
        "personal/create/",
        views.PersonalToDoCreate.as_view(),
        name="personal_todo_create",
    ),
]
