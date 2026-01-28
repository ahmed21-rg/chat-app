from django.contrib import admin
from main.models import *



class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email"]

class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "verified"]
    list_editable = ["verified"]

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "sender", "read_by", "message"]
    list_editable = ["read_by"]

class MessageInline(admin.TabularInline):
    model = Message
    fields = ["sender", "short_message", "read_by", "created_at"]
    readonly_fields = ["short_message", "created_at"]
    extra = 0

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Message, ChatMessageAdmin)