from django.shortcuts import render,get_list_or_404,get_object_or_404
from django.views.generic import ListView
from .models import Chat
from django.db import models
from django.db.models import Q
from django.shortcuts import redirect
from .utils import get_last_message_opposite_user_and_related_ad, get_user_conversations
from django.urls import reverse

class ConversationListView(ListView):
    model= Chat
    template_name = 'chat/conversationlist.html'

    def get_queryset(self):
        return get_user_conversations(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversations = self.get_queryset()
        
        conversation_data = []
        unique_conversation_ids = {conv['conversation_id'] for conv in conversations}  

        for conversation_id in unique_conversation_ids:
            last_message, opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.request.user, conversation_id)

            if last_message:
                conversation_data.append({
                    'conversation_id': conversation_id,
                    'opposite_user': opposite_user,
                    'ad': related_ad,
                    'last_message': last_message,
                })

        context['conversation_data'] = conversation_data
        return context


class ConversationDetailView(ListView):
    model = Chat
    template_name = 'chat/conversationdetail.html'
    context_object_name = 'messages'


    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return get_list_or_404( Chat.objects.filter(conversation_id=conversation_id).order_by('timestamp'))
         

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation_id = self.kwargs['conversation_id']
        
        last_message,opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.request.user, conversation_id)

        if last_message and related_ad:
            context['opposite_user'] = opposite_user 
            context['related_ad'] = related_ad

        return context  

    def post(self, request, *args, **kwargs):
        conversation_id = self.kwargs['conversation_id']
        message_content = request.POST.get('message').strip()

        _,opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.request.user, conversation_id)

        if not message_content:
            return redirect('chat:conversation_detail', ad_slug=related_ad.slug, conversation_id=conversation_id)
            
        Chat.objects.create(
                sender=request.user,
                receiver= opposite_user,
                ad=related_ad,
                conversation_id=conversation_id,
                message=message_content
            )
            
         
        return redirect('chat:conversation_detail', ad_slug=related_ad.slug, conversation_id=conversation_id)

    def edit_message(self, request, ad_slug, conversation_id, message_id):
        chat = get_object_or_404(Chat, id=message_id, sender=request.user, conversation_id=conversation_id, ad__slug=ad_slug)

        if request.method == "POST":
            new_content = request.POST.get('editedmessage').strip()

        if not new_content:
            return redirect('chat:conversation_detail', ad_slug, conversation_id)
        
        chat.message = new_content.strip()
        chat.save()

        return redirect('chat:conversation_detail', ad_slug, conversation_id)

    def delete_message(self, request, ad_slug, conversation_id, message_id):
        print("delete")
        message = get_object_or_404(Chat, id=message_id, sender=request.user, conversation_id=conversation_id, ad__slug=ad_slug)

        if request.method == "POST":
            message.delete()

        ismessagesinCurrentConversation = Chat.objects.filter(conversation_id=conversation_id)

        if not ismessagesinCurrentConversation:
            return redirect('chat:conversation_list')

        return redirect('chat:conversation_detail', ad_slug, conversation_id)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            if 'edit' in request.path:
                return self.edit_message(request, kwargs['ad_slug'], kwargs['conversation_id'], kwargs['message_id'])
            elif 'delete' in request.path:
                print("delete")
                return self.delete_message(request, kwargs['ad_slug'], kwargs['conversation_id'], kwargs['message_id'])
        return super().dispatch(request, *args, **kwargs)