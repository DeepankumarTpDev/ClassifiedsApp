from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('all/', views.ConversationListView.as_view(), name='conversation_list'),
    path('all/<slug:ad_slug>/conversations/<str:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('all/<slug:ad_slug>/conversations/<str:conversation_id>/message/<int:message_id>/delete/', views.ConversationDetailView.as_view(), name='delete_message'),
    path('all/<slug:ad_slug>/conversations/<str:conversation_id>/message/<int:message_id>/edit/', views.ConversationDetailView.as_view(), name='edit_message'),
]
