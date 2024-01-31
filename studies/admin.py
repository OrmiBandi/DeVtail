from django.contrib import admin
from .models import (
    Study,
    Category,
    Tag,
    RefLink,
    Comment,
    StudyMember,
    Recomment,
    Blacklist,
    Favorite,
    Schedule,
)

admin.site.register(Study)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(RefLink)
admin.site.register(Comment)
admin.site.register(Recomment)
admin.site.register(StudyMember)
admin.site.register(Blacklist)
admin.site.register(Favorite)
admin.site.register(Schedule)
