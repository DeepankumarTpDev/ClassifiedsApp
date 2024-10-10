from .models import Chat
from django.db import models


def get_last_message_opposite_user_and_related_ad(user, conversation_id):
    """
    Fetches the last message of the conversation and identifies the opposite user (either sender or receiver).
    
    :param user: The current user (sender or receiver)
    :param conversation_id: The conversation ID for which the last message needs to be fetched
    :return: A tuple containing the last message and the opposite user
    """
    last_message = Chat.objects.filter(conversation_id=conversation_id).order_by('-timestamp').first()

    if last_message:
        if last_message.sender == user:
            opposite_user = last_message.receiver
        else:
            opposite_user = last_message.sender
        return last_message, opposite_user, last_message.ad

    return None, None, None


def get_user_conversations(user):
    """
    Returns a queryset of distinct conversation IDs where the user is either the sender or receiver.
    """
    return Chat.objects.filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).values('conversation_id').distinct()
