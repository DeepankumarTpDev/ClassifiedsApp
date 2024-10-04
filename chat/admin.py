from django.contrib import admin
from .models import Chat

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp', 'conversation_id')
    search_fields = ('sender__username', 'receiver__username', 'message')
    list_filter = ('timestamp', 'sender', 'receiver')
    ordering = ('-timestamp',)  

