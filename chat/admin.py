from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('ad', 'created_on')
    search_fields = ('ad__title',)
    list_filter = ('created_on',)
    ordering = ('-created_on',)  

@admin.register(Message)
class ChatMessage(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'created_on', 'chat')
    search_fields = ('sender__username', 'receiver__username', 'message')
    list_filter = ('created_on', 'sender', 'receiver')
    ordering = ('-created_on',)  

