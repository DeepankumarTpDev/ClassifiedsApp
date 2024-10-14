from django.shortcuts import render,get_list_or_404,get_object_or_404
from django.views.generic import ListView
from .models import Chat, Message
from django.shortcuts import redirect
from django.db.models import Count

class ConversationListView(ListView):
    model= Chat
    template_name = 'chat/conversationlist.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return (
            Chat.objects.filter(users=self.request.user)
            .annotate(message_count=Count('messages'))  
            .filter(message_count__gt=0)  
        )
    

class ConversationDetailView(ListView):
    model = Message
    template_name = 'chat/conversationdetail.html'
    context_object_name = 'messages'


    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        return get_list_or_404(Message.objects.filter(chat=chat).order_by('created_on'))
         
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)

        opposite_user = chat.users.exclude(id=self.request.user.id).first()
        context['opposite_user'] = opposite_user
        context['related_ad'] = chat.ad  

        return context

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs['chat_id']
        message_content = request.POST.get('message').strip()
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        opposite_user = chat.users.exclude(id=self.request.user.id).first()

        if not message_content:
            return redirect('chat:conversation_detail', chat_id=chat_id)
            
        Message.objects.create(
                sender=request.user,
                receiver= opposite_user,
                message=message_content,
                chat = chat
            )
            
         
        return redirect('chat:conversation_detail', chat_id=chat_id)

    def edit_message(self, request, chat_id, message_id):
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        message = get_object_or_404(Message, id=message_id, sender=request.user, chat=chat)

        if request.method == "POST":
            new_content = request.POST.get('editedmessage').strip()

        if not new_content:
            return redirect('chat:conversation_detail', chat_id)
        
        message.message = new_content.strip()
        message.save()

        return redirect('chat:conversation_detail', chat_id)

    def delete_message(self, request, chat_id, message_id):
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        message = get_object_or_404(Message, id=message_id, sender=request.user, chat=chat)

        if request.method == "POST":
            message.delete()

        ismessagesinCurrentConversation = Message.objects.filter(chat=chat)

        if not ismessagesinCurrentConversation:
            return redirect('chat:conversation_list')

        return redirect('chat:conversation_detail', chat_id)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            if 'edit' in request.path:
                return self.edit_message(request, kwargs['chat_id'], kwargs['message_id'])
            elif 'delete' in request.path:
                print("delete")
                return self.delete_message(request, kwargs['chat_id'], kwargs['message_id'])
        return super().dispatch(request, *args, **kwargs)