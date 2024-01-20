from django.contrib import admin
from .models import ToDo, ToDoAssignee

# admin.site.register(ToDo)
# admin.site.register(ToDoAssignee)


@admin.register(ToDo)
class ToDoAdmin(admin.ModelAdmin):
    list_display = ["id", "study", "title", "status", "start_at", "end_at"]
    fields = ["study", "title", "status", "content", ("start_at", "end_at")]
    list_display_links = ["id", "title"]
    list_filter = ["study", "start_at", "status"]
    list_per_page = 25
    ordering = ["-id"]


@admin.register(ToDoAssignee)
class ToDoAssigneeAdmin(admin.ModelAdmin):
    list_display = ["id", "todo", "assignee"]
    fields = ["todo", "assignee"]
    list_display_links = ["id", "todo"]
    list_per_page = 25
    ordering = ["-id"]
