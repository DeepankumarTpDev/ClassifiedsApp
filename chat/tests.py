from django.test import TestCase
from django.contrib.auth.models import User
from .models import Chat
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class ChatModelTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='password123')
        self.receiver = User.objects.create_user(username='receiver', password='password123')

    def test_chat_creation_with_valid_data(self):
        """Test creating a chat instance with valid data."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message='Hello, how are you?'
        )
        self.assertIsInstance(chat, Chat)

    def test_profile_creation_with_empty_sender_fields(self):
        """Test creating a chat with empty sender fields."""
        
        with self.assertRaises(ObjectDoesNotExist):
            Chat.objects.create(
                        receiver=self.receiver,
                        message='This is a test message.'
                    )
            
    def test_profile_creation_with_empty_receiver_fields(self):
        """Test creating a chat with empty reciever fields."""
        
        with self.assertRaises(ObjectDoesNotExist):
            Chat.objects.create(
                        sender=self.sender,
                        message='This is a test message.'
                    )       
    
    def test_chat_message_field(self):
        """Ensure that message field can store text."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message='This is a test message.'
        )
        self.assertEqual(chat.message, 'This is a test message.')

    def test_timestamp_default_value(self):
        """Verify that timestamp is set to now when created."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message='Timestamp test.'
        )
        self.assertIsNotNone(chat.timestamp)

    def test_conversation_id_generation(self):
        """Ensure conversation_id is generated correctly."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message='Testing conversation ID.'
        )
        expected_conversation_id = f'{self.sender.username}_{self.sender.id}_to_{self.receiver.username}_{self.receiver.id}'
        self.assertEqual(chat.conversation_id, expected_conversation_id)

    def test_string_representation(self):
        """Check string representation of the chat."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message='String representation test.'
        )
        expected_str = f'{self.sender.username}_{self.sender.id}_to_{self.receiver.username}_{self.receiver.id}'
        self.assertEqual(str(chat), expected_str)

    def test_ordering_by_timestamp(self):
        """Verify messages are ordered by timestamp."""
        chat1 = Chat.objects.create(sender=self.sender, receiver=self.receiver, message='First message.')
        chat2 = Chat.objects.create(sender=self.sender, receiver=self.receiver, message='Second message.')
        
        chats = Chat.objects.all()
        
        self.assertEqual(list(chats), [chat1, chat2])  

    def test_unique_conversation_id(self):
        """Ensure conversation IDs are unique for each sender-receiver pair."""
        chat1 = Chat.objects.create(sender=self.sender, receiver=self.receiver, message='First conversation.')
        chat2 = Chat.objects.create(sender=self.receiver, receiver=self.sender, message='Reply to first conversation.')

        self.assertNotEqual(chat1.conversation_id, chat2.conversation_id)  

