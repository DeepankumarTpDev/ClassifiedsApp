from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('all/', views.ConversationListView.as_view(), name='conversation_list'),
    path('all/conversations/<int:chat_id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('all/conversations/<int:chat_id>/message/send/', views.ConversationMesageSendView.as_view(), name='send_message'),
    path('all/conversations/<int:chat_id>/message/<int:message_id>/delete/', views.ConversationMesageDeleteView.as_view(), name='delete_message'),
    path('all/conversations/<int:chat_id>/message/<int:message_id>/edit/', views.ConversationMesageEditView.as_view(), name='edit_message'),
]
