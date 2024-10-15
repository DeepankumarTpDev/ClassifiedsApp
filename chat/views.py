from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from .models import Chat, Message
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from .forms import MessageEditForm

class ConversationListView(ListView):
    model= Chat
    template_name = 'chat/conversationlist.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return Chat.objects.filter(users=self.request.user)
            

class ConversationDetailView(ListView):
    model = Message
    template_name = 'chat/conversationdetail.html'
    context_object_name = 'messages'

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        return Message.objects.filter(chat=chat, users=self.request.user).order_by('created_on')
         
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)

        opposite_user = chat.users.exclude(id=self.request.user.id).first()
        context['opposite_user'] = opposite_user
        context['related_ad'] = chat.ad  
        context['chat_id'] = chat_id

        return context


class ConversationMesageSendView(CreateView):
    model = Message
    fields = ['message']
    template_name = 'chat/conversationdetail.html'

    def form_valid(self, form):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        opposite_user = chat.users.exclude(id=self.request.user.id).first()
        
        form.instance.sender = self.request.user
        form.instance.receiver = opposite_user
        form.instance.chat = chat
        
        return super().form_valid(form)

    def form_invalid(self, form):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        opposite_user = chat.users.exclude(id=self.request.user.id).first()

        context = {
            'object_list': Message.objects.filter(chat=chat).order_by('created_on'),
            'message_send_form': form,
            'opposite_user': opposite_user,
            'related_ad': chat.ad,
            'chat_id': chat_id,  
        }

        return render(self.request, self.template_name, context)

    def get_success_url(self):
        return reverse_lazy('chat:conversation_detail', args=[self.kwargs['chat_id']])    


class ConversationMesageEditView(UpdateView):
    model = Message
    form_class = MessageEditForm
    template_name = 'chat/conversationdetail.html'

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'], users=self.request.user)
        return Message.objects.filter(chat=chat, sender=self.request.user) 

    def get_object(self, queryset=None):
        queryset = self.get_queryset()  
        obj = get_object_or_404(queryset, id=self.kwargs['message_id'])  
        return obj
    
    def form_invalid(self, form):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        opposite_user = chat.users.exclude(id=self.request.user.id).first()

        context = {
            'object_list': Message.objects.filter(chat=chat).order_by('created_on'),
            'message_edit_form': form,
            'opposite_user': opposite_user,
            'related_ad': chat.ad,
            'editMessage': 'true',
            'message_id': self.object.id,
            'chat_id': chat_id,  
        }

        return render(self.request, self.template_name, context)

    def get_success_url(self):
        return reverse_lazy('chat:conversation_detail', args=[self.kwargs['chat_id']])
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  
        form = self.get_form()  
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, users=self.request.user)
        opposite_user = chat.users.exclude(id=self.request.user.id).first()

        context = {
            'object_list': Message.objects.filter(chat=chat).order_by('created_on'),
            'message_edit_form': form,
            'opposite_user': opposite_user,
            'related_ad': chat.ad,
            'editMessage': 'true',
            'message_id': self.object.id,
            'chat_id': chat_id,  
        }

        return render(self.request, self.template_name, context)


class ConversationMesageDeleteView(DeleteView):
    model = Message

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'], users=self.request.user)
        return Message.objects.filter(chat=chat, sender=self.request.user) 

    def get_object(self, queryset=None):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'], users=self.request.user)
        message = get_object_or_404(
            Message,
            chat=chat,
            id=self.kwargs['message_id'],
            sender=self.request.user
        )
        return message

    def get_success_url(self):
        return reverse_lazy('chat:conversation_detail', args=[self.kwargs['chat_id']])
    