from django.test import TestCase
from django.contrib.auth.models import User
from .models import Chat
from ads.models import Ads, Category
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from .utils import get_last_message_opposite_user_and_related_ad, get_user_conversations

class ChatModelTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='password123')
        self.receiver = User.objects.create_user(username='receiver', password='password123')
        self.category = Category.objects.create(name="Test Category")
        self.ad = Ads.objects.create(
            user=self.sender,
            title="Test Ad",
            category=self.category,
            description="This is a test ad.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=99.99,
            image='image.jpg'
        )

    def test_chat_creation_with_valid_data(self):
        """Test creating a chat instance with valid data."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ad = self.ad,
            message='Hello, how are you?'
        )
        self.assertIsInstance(chat, Chat)

    def test_profile_creation_with_empty_sender_fields(self):
        """Test creating a chat with empty sender fields."""
        
        with self.assertRaises(ObjectDoesNotExist):
            Chat.objects.create(
                        receiver=self.receiver,
                        ad = self.ad,
                        message='This is a test message.'
                    )
            
    def test_profile_creation_with_empty_receiver_fields(self):
        """Test creating a chat with empty reciever fields."""
        
        with self.assertRaises(ObjectDoesNotExist):
            Chat.objects.create(
                        sender=self.sender,
                        ad = self.ad,
                        message='This is a test message.'
                    )       
    def test_profile_creation_with_empty_ad_fields(self):
        """Test creating a chat with empty reciever fields."""
        
        with self.assertRaises(ObjectDoesNotExist):
            Chat.objects.create(
                        sender=self.sender,
                        receiver = self.receiver,
                        message='This is a test message.'
                    )       
    
    def test_chat_message_field(self):
        """Ensure that message field can store text."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ad = self.ad,
            message='This is a test message.'
        )
        self.assertEqual(chat.message, 'This is a test message.')

    def test_timestamp_default_value(self):
        """Verify that timestamp is set to now when created."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ad = self.ad,
            message='Timestamp test.'
        )
        self.assertIsNotNone(chat.timestamp)

    def test_conversation_id_generation(self):
        """Ensure conversation_id is generated correctly."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ad = self.ad,
            message='Testing conversation ID.'
        )
        if self.sender.id > self.receiver.id:
            user1, user2 = self.receiver, self.sender
        else:
            user1, user2 = self.sender, self.receiver
        expected_conversation_id = f"{user1.id}-{user1.username}-{self.ad.slug}-{user2.id}-{user2.username}"
        self.assertEqual(chat.conversation_id, expected_conversation_id)

    def test_string_representation(self):
        """Check string representation of the chat."""

        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ad = self.ad,
            message='String representation test.'
        )
        if self.sender.id > self.receiver.id:
            user1, user2 = self.receiver, self.sender
        else:
            user1, user2 = self.sender, self.receiver
        expected_str = f"{user1.id}-{user1.username}-{self.ad.slug}-{user2.id}-{user2.username}"
        self.assertEqual(str(chat), expected_str)

    def test_ordering_by_timestamp(self):
        """Verify messages are ordered by timestamp."""
        chat1 = Chat.objects.create(sender=self.sender, receiver=self.receiver, ad = self.ad, message='First message.')
        chat2 = Chat.objects.create(sender=self.sender, receiver=self.receiver, ad = self.ad, message='Second message.')
        
        chats = Chat.objects.all()
        
        self.assertEqual(list(chats), [chat1, chat2])  

    def test_unique_conversation_id(self):
        """Ensure conversation IDs are unique for each sender-receiver pair."""
        chat1 = Chat.objects.create(sender=self.sender, receiver=self.receiver, ad = self.ad, message='First conversation.')
        user3 = User.objects.create_user(username='third_user', password='password')
        chat2 = Chat.objects.create(sender=self.receiver, receiver=user3, ad = self.ad, message='Reply to first conversation.')

        self.assertNotEqual(chat1.conversation_id, chat2.conversation_id)  

    def test_conversation_id_with_same_users_reversed(self):
        """Test that the conversation ID remains the same regardless of sender/receiver order."""
        message1 = Chat(sender=self.sender, receiver=self.receiver, ad = self.ad, message="Hello!")
        message1.save()
        
        message2 = Chat(sender=self.receiver, receiver=self.sender, ad = self.ad, message="Hi!")
        message2.save()

        self.assertEqual(message1.conversation_id, message2.conversation_id)

    def test_conversation_id_with_same_users_same_order(self):
        """Test that creating multiple messages between the same users results in the same conversation ID."""
        message1 = Chat(sender=self.sender, receiver=self.receiver, ad = self.ad, message="Hello!")
        message1.save()

        message2 = Chat(sender=self.sender, receiver=self.receiver, ad = self.ad, message="How are you?")
        message2.save()

        self.assertEqual(message1.conversation_id, message2.conversation_id)


class ConversationListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.user3 = User.objects.create_user(username='testuser3', password='testpass3')

        self.ad1 = Ads.objects.create(
            user=self.user,
            title="Test Ad 1",
            category=self.category,
            description="This is a test ad 1.",
            location="Test Location",
            postal_code="12345",
            contact_info="test1@example.com",
            price=99.99,
            image='image1.jpg'
        )

        self.ad2 = Ads.objects.create(
            user=self.user,
            title="Test Ad 2",
            category=self.category,
            description="This is a test ad 2.",
            location="Test Location",
            postal_code="54321",
            contact_info="test2@example.com",
            price=199.99,
            image='image2.jpg'
        )

        self.client.login(username='testuser', password='testpass')

        self.chat1 = Chat.objects.create(sender=self.user, receiver=self.user2, message='Hello User2', ad=self.ad1)
        self.chat2 = Chat.objects.create(sender=self.user2, receiver=self.user, message='Hi User1', ad=self.ad1)
        self.chat3 = Chat.objects.create(sender=self.user, receiver=self.user3, message='Hello User3', ad=self.ad2)

    def test_conversation_list_view(self):
        response = self.client.get(reverse('chat:conversation_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/conversationlist.html')

        self.assertIn('conversation_data', response.context)
        self.assertEqual(len(response.context['conversation_data']), 2)  


class ConversationDetailViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.opposite_user = User.objects.create_user(username='user2', password='password')
        self.category = Category.objects.create(name='Test Category') 
        self.ad = Ads.objects.create(
            user=self.user,
            title="Test Ad",
            category=self.category,
            description="This is a test ad.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=99.99,
            image='image.jpg'
        )
        self.conversation_id = 1 
        self.chat_message = Chat.objects.create(
            sender=self.user,
            receiver=self.opposite_user,
            ad=self.ad,
            conversation_id=self.conversation_id,
            message='Initial Message'
        )
        self.client.login(username='user1', password='password')  

    def test_get_queryset_valid(self):
        response = self.client.get(reverse('chat:conversation_detail', args=[self.ad.slug, self.conversation_id]))
        self.assertEqual(response.status_code, 200)  
        self.assertIn('messages', response.context) 
        self.assertEqual(len(response.context['messages']), 1)  

    def test_get_queryset_invalid(self):
        response = self.client.get(reverse('chat:conversation_detail', args=[self.ad.slug, 999]))  
        self.assertEqual(response.status_code, 404)  

    def test_send_message_valid(self):
        response = self.client.post(reverse('chat:conversation_detail', args=[self.ad.slug, self.conversation_id]), {'message': 'Hello!'})
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Chat.objects.count(), 2)  

    def test_send_message_empty(self):
        response = self.client.post(reverse('chat:conversation_detail', args=[self.ad.slug, self.conversation_id]), {'message': ''})
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Chat.objects.count(), 1)  

    def test_edit_message_valid(self):
        response = self.client.post(reverse('chat:edit_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]), {'editedmessage': 'Edited Message'})
        self.chat_message.refresh_from_db()
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(self.chat_message.message, 'Edited Message')

    def test_edit_message_not_belonging_to_user(self):
        self.client.logout() 
        self.client.login(username='user2', password='password')  
        response = self.client.post(reverse('chat:edit_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]), {'editedmessage': 'Should Fail'})
        self.assertEqual(response.status_code, 404) 

    def test_delete_message_valid(self):
        response = self.client.post(reverse('chat:delete_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Chat.objects.count(), 0) 

    def test_delete_message_not_belonging_to_user(self):
        self.client.logout()  
        self.client.login(username='user2', password='password')  
        response = self.client.post(reverse('chat:delete_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]))
        self.assertEqual(response.status_code, 404)  

    def test_dispatch_edit(self):
        response = self.client.post(reverse('chat:edit_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]), {'editedmessage': 'Another Edit'})
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Chat.objects.first().message, 'Another Edit')  

    def test_dispatch_delete(self):
        response = self.client.post(reverse('chat:delete_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Chat.objects.count(), 0)  

    def test_dispatch_other_method(self):
        response = self.client.get(reverse('chat:conversation_detail', args=[self.ad.slug,self.conversation_id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_last_message_redirects_to_conversation_list(self):
        response = self.client.post(reverse('chat:delete_message', args=[self.ad.slug, self.conversation_id, self.chat_message.id]))

        self.assertEqual(Chat.objects.count(), 0)
        self.assertRedirects(response, reverse('chat:conversation_list'))




class UtilityTests(TestCase):
    def setUp(self):
        
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass3')
        self.category = Category.objects.create(name='Test Category')
        self.ad = Ads.objects.create(
            user=self.user1,
            title="Test Ad",
            category=self.category,
            description="This is a test ad.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=99.99,
            image='image.jpg'
        )

        self.chat1 = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            ad=self.ad,
            conversation_id="conv123",
            message="Hello, how are you?"
        )
        self.chat2 = Chat.objects.create(
            sender=self.user2,
            receiver=self.user1,
            ad=self.ad,
            conversation_id="conv123",
            message="I'm fine, thanks!"
        )

    def test_get_last_message_opposite_user_and_related_ad_sender(self):
        last_message, opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.user1, "conv123")
        self.assertEqual(last_message, self.chat2)
        self.assertEqual(opposite_user, self.user2)
        self.assertEqual(related_ad, self.ad)

    def test_get_last_message_opposite_user_and_related_ad_receiver(self):
        last_message, opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.user2, "conv123")
        self.assertEqual(last_message, self.chat2)
        self.assertEqual(opposite_user, self.user1)
        self.assertEqual(related_ad, self.ad)

    def test_get_last_message_no_messages(self):
        last_message, opposite_user, related_ad = get_last_message_opposite_user_and_related_ad(self.user1, "conv456")
        self.assertIsNone(last_message)
        self.assertIsNone(opposite_user)
        self.assertIsNone(related_ad)

    def test_get_user_conversations(self):
        conversations = get_user_conversations(self.user1)
        self.assertEqual(len(conversations), 2)
        self.assertEqual(conversations[0]['conversation_id'], "conv123")

    def test_get_user_conversations_no_conversations(self):
        conversations = get_user_conversations(self.user3)
        self.assertEqual(len(conversations), 0)  


class ConversationDetailTemplateTests(TestCase):
    def setUp(self):

        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.category = Category.objects.create(name='Test Category')
        self.ad = Ads.objects.create(
            user=self.user1,
            title="Test Ad",
            category=self.category,
            description="Test Description",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=99.99
        )

        self.chat1 = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            ad=self.ad,
            conversation_id="conv123",
            message="Hello!"
        )
        self.chat2 = Chat.objects.create(
            sender=self.user2,
            receiver=self.user1,
            ad=self.ad,
            conversation_id="conv123",
            message="Hi there!"
        )

    def test_render_template_of_deleted_conversation_messages(self):
        Chat.objects.all().delete()  
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('chat:conversation_detail', args=[self.ad.slug, "conv123"]))
        self.assertEqual(response.status_code, 404)

    def test_send_message_success(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:conversation_detail', args=[self.ad.slug, "conv123"]), {
            'message': 'A new message'
        })
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Chat.objects.filter(message='A new message').exists())

    def test_edit_message(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:edit_message', args=[self.ad.slug, "conv123", self.chat1.id]), {
            'editedmessage': 'Edited message'
        })
        self.chat1.refresh_from_db()
        self.assertEqual(self.chat1.message, 'Edited message')

    def test_delete_message(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:delete_message', args=[self.ad.slug, "conv123", self.chat1.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertFalse(Chat.objects.filter(id=self.chat1.id).exists())

    def test_back_button_redirect(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('chat:conversation_detail', args=[self.ad.slug, "conv123"]))
        back_button_url = reverse('chat:conversation_list')
        
        self.assertContains(response, 'Back')
        response = self.client.get(back_button_url)
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'chat/conversationlist.html')  


