from django.contrib import admin

from .models import CallLog, Assessment, Conversation

# Register your models here.

admin.site.register(CallLog)
admin.site.register(Assessment)
admin.site.register(Conversation)



