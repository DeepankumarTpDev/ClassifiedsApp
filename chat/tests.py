from django.contrib.auth.models import User
from django.test import TestCase
from ads.models import Category, Ads
from .models import User, Chat, Message
from django.urls import reverse


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
            price=99.99
        )
        self.ad2 = Ads.objects.create(
            user=self.user,
            title="Test Ad 2",
            category=self.category,
            description="This is a test ad 2.",
            location="Test Location",
            postal_code="54321",
            contact_info="test2@example.com",
            price=199.99
        )
        self.ad3 = Ads.objects.create(
            user=self.user,
            title="Test Ad 3",
            category=self.category,
            description="This is a test ad 3.",
            location="Test Location",
            postal_code="54321",
            contact_info="test2@example.com",
            price=199.99
        )
        self.client.login(username='testuser', password='testpass')

        self.chat1 = Chat.objects.create(ad=self.ad1)
        self.chat1.users.set([self.user, self.user2])
        self.message1 = Message.objects.create(chat=self.chat1, sender=self.user, receiver=self.user2, message="Hello!")
        self.message2 = Message.objects.create(chat=self.chat1, sender=self.user2, receiver=self.user, message="Hi there!")
        
        self.chat2 = Chat.objects.create(ad=self.ad2)
        self.chat2.users.set([self.user2, self.user])

        self.chat3 = Chat.objects.create(ad=self.ad1)
        self.chat3.users.set([self.user, self.user3])

    def test_conversation_list_view(self):
        response = self.client.get(reverse('chat:conversation_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/conversationlist.html')
        self.assertIn('conversations', response.context)
        self.assertEqual(len(response.context['conversations']), 3)

    def test_conversation_list_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('chat:conversation_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('chat:conversation_list')}")


class ConversationDetailViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
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
            price=99.99
        )
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.set([self.user, self.user2])

        self.chat_message = Message.objects.create(
            sender=self.user,
            receiver=self.opposite_user,
            chat=self.chat,
            message='Initial Message'
        )
        self.client.login(username='user1', password='password')  

    def test_get_queryset_valid(self):
        response = self.client.get(reverse('chat:conversation_detail', args=[self.chat.id]))
        self.assertEqual(response.status_code, 200)  
        self.assertIn('messages', response.context) 
        self.assertEqual(len(response.context['messages']), 1)  

    def test_get_queryset_invalid(self):
        response = self.client.get(reverse('chat:conversation_detail', args=[999]))  
        self.assertEqual(response.status_code, 404)  

    def test_conversation_detail_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('chat:conversation_detail', args=[self.chat.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('chat:conversation_detail', args=[self.chat.id])}")


class ConversationMessageSendViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
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
            price=99.99
        )
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.set([self.user, self.user2])

        self.chat_message = Message.objects.create(
            sender=self.user,
            receiver=self.opposite_user,
            chat=self.chat,
            message='Initial Message'
        )
        self.client.login(username='user1', password='password') 
    
    def test_send_message_valid(self):
        response = self.client.post(reverse('chat:send_message', args=[self.chat.id]), {'message': 'Hello!'})
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Message.objects.count(), 2)  

    def test_send_message_empty(self):
        response = self.client.post(reverse('chat:send_message', args=[self.chat.id]), {'message': ''})
        self.assertEqual(Message.objects.count(), 1)  

    def test_conversation_send_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.post(reverse('chat:send_message', args=[self.chat.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('chat:send_message', args=[self.chat.id])}")


class ConversationMessageEditViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
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
            price=99.99
        )
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.set([self.user, self.user2])

        self.chat_message = Message.objects.create(
            sender=self.user,
            receiver=self.opposite_user,
            chat=self.chat,
            message='Initial Message'
        )
        self.client.login(username='user1', password='password')  

    def test_edit_message_valid(self):
        response = self.client.post(reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id]), {'message': 'Edited Message'})
        self.chat_message.refresh_from_db()
        self.assertEqual(self.chat_message.message, 'Edited Message')

    def test_edit_message_not_belonging_to_user(self):
        self.client.logout() 
        self.client.login(username='user2', password='password')  
        response = self.client.post(reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id]), {'message': 'Should Fail'})
        self.assertEqual(response.status_code, 404) 

    def test_dispatch_edit(self):
        response = self.client.post(reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id]), {'message': 'Another Edit'})
        self.assertEqual(Message.objects.first().message, 'Another Edit') 

    def test_conversation_edit_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.post(reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id]))
        self.assertRedirects(response, f"{reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id])}")
    
    def test_conversation_edit_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('chat:edit_message', args=[self.chat.id, self.chat_message.id])}")



class ConversationMessagesDeleteViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
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
        )
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.set([self.user, self.user2])

        self.chat_message = Message.objects.create(
            sender=self.user,
            receiver=self.opposite_user,
            chat=self.chat,
            message='Initial Message'
        )
        self.client.login(username='user1', password='password')  

    def test_delete_message_valid(self):
        response = self.client.post(reverse('chat:delete_message', args=[self.chat.id, self.chat_message.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Message.objects.count(), 0) 

    def test_delete_message_not_belonging_to_user(self):
        self.client.logout()  
        self.client.login(username='user2', password='password')  
        response = self.client.post(reverse('chat:delete_message', args=[self.chat.id, self.chat_message.id]))
        self.assertEqual(response.status_code, 404)   

    def test_dispatch_delete(self):
        response = self.client.post(reverse('chat:delete_message', args=[self.chat.id, self.chat_message.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Message.objects.count(), 0)  

    def test_conversation_delete_view_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.post(reverse('chat:delete_message', args=[self.chat.id, self.chat_message.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('chat:delete_message', args=[self.chat.id, self.chat_message.id])}")



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
        self.chat = Chat.objects.create(ad=self.ad)
        self.chat.users.set([self.user1, self.user2])
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            chat=self.chat,
            message="Hello!"
        )

        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            chat=self.chat,
            message="Hi there!"
        )

    def test_render_template_of_deleted_conversation_messages(self):
        Chat.objects.all().delete()  
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('chat:conversation_detail', args=[self.chat.id]))
        self.assertEqual(response.status_code, 404)

    def test_send_message_success(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:send_message', args=[self.chat.id]), {
            'message': 'A new message'
        })
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Message.objects.filter(message='A new message').exists())

    def test_edit_message(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:edit_message', args=[self.chat.id, self.message1.id]), {
            'message': 'Edited message'
        })
        self.message1.refresh_from_db()
        self.assertEqual(self.message1.message, 'Edited message')

    def test_delete_message(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('chat:delete_message', args=[self.chat.id, self.message1.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertFalse(Message.objects.filter(id=self.message1.id).exists())

    def test_back_button_redirect(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('chat:conversation_detail', args=[self.chat.id]))
        back_button_url = reverse('chat:conversation_list')
        
        self.assertContains(response, 'Back')
        response = self.client.get(back_button_url)
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'chat/conversationlist.html') 

