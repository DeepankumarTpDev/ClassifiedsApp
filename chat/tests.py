from django.contrib.auth.models import User
from django.test import TestCase
from ads.models import Ads, Category
from .models import Chat, Message

class ChatMessageModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00,
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = 'test.jpg',
            location="Original Location",
            user=self.user1  
        )
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.add(self.user1, self.user2)

    def test_chat_creation(self):
        self.assertEqual(self.chat.ad, self.ad)
        self.assertEqual(self.chat.users.count(), 2)
        self.assertIn(self.user1, self.chat.users.all())
        self.assertIn(self.user2, self.chat.users.all())

    def test_chat_str(self):
        expected_str = f"Chat for {self.ad} with users user1, user2"
        self.assertEqual(str(self.chat), expected_str)

    def test_chat_created_on(self):
        self.assertIsNotNone(self.chat.created_on)

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message="Hello!",
            chat=self.chat
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.message, "Hello!")
        self.assertEqual(message.chat, self.chat)

    def test_message_ordering(self):
        message1 = Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello!", chat=self.chat)
        message2 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hi!", chat=self.chat)
        messages = Message.objects.all()
        self.assertEqual(list(messages), [message1, message2])


    def test_chat_without_users(self):
        chat_without_users = Chat.objects.create(ad=self.ad)
        self.assertEqual(chat_without_users.users.count(), 0)
