from django.contrib import admin
from .models import DirectChat, StudyChat, ChatMessage

admin.site.register(DirectChat)
admin.site.register(StudyChat)
admin.site.register(ChatMessage)
