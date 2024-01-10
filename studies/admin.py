from django.contrib import admin
from .models import Study, Category, Tag, RefLink, Comment, StudyMember

admin.site.register(Study)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(RefLink)
admin.site.register(Comment)
admin.site.register(StudyMember)