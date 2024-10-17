from django.test import TestCase
from django.urls import reverse
from .models import Category, Ads
from chat.models import Chat, Message
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from io import BytesIO
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class CategoryModelTest(TestCase):
    """
    Test suite for the Category model, which checks the creation, validation,
    and behavior of category instances in the database.
    """

    def test_valid_category_creation(self):
        """Test that a valid category can be created successfully."""

        category = Category.objects.create(name='Test Category')
        self.assertIsInstance(category, Category)

    def test_category_name_uniqueness(self):
        """Test that category names are unique; duplicate names should raise an IntegrityError."""

        Category.objects.create(name='Unique Category')
        
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Unique Category')

    def test_slug_generation_on_save(self):
        """Test that a slug is generated automatically based on the category name upon saving."""

        category = Category.objects.create(name='Test Category')
        self.assertEqual(category.slug, 'test-category')

    def test_custom_slug_input(self):
        """Test that a custom slug can be provided and is used instead of the auto-generated slug."""

        category = Category.objects.create(name='Test Category', slug='custom-slug')
        self.assertEqual(category.slug, 'custom-slug')

    def test_category_description_field(self):
        """Test that the description field is functioning as expected and can be saved."""

        category = Category.objects.create(name='Category with Description', description='This is a test description.')
        self.assertEqual(category.description, 'This is a test description.')

    def test_category_name_cannot_be_blank(self):
        """Test that attempting to create a category with a blank name raises a ValidationError."""

        with self.assertRaises(ValidationError):
            category = Category(name='')
            category.full_clean()  

    def test_created_at_timestamp(self):
        """Test that the created_at timestamp is automatically set upon creation of a category."""

        category = Category.objects.create(name='Timestamp Category')
        self.assertIsNotNone(category.created_at)

    def test_string_representation(self):
        """Test the string representation of the category; it should return the name."""

        category = Category.objects.create(name='String Test')
        self.assertEqual(str(category), 'String Test')

    def test_update_category_name(self):
        """Test that updating a category's name correctly updates the name, but slug remains unchanged."""

        category = Category.objects.create(name='Old Name')
        category.name = 'New Name'
        category.save()
        self.assertEqual(category.slug, 'old-name')  

    def test_category_name_length_validation(self):
        """Test that a category name exceeding the maximum length raises a ValidationError."""

        with self.assertRaises(ValidationError):
            category = Category(name='x' * 256)  
            category.full_clean()  

    def test_slug_field_length_validation(self):
        """Test that a slug exceeding the maximum length raises a ValidationError."""

        category = Category(name='Valid Name', slug='x' * 201)  
        with self.assertRaises(ValidationError):
            category.full_clean()  


class AdsModelTest(TestCase):
    """
    Test suite for the Ads model, focusing on the creation, validation,
    and functionality of ads instances.
    """

    def setUp(self):
        """Create a category for use in ad tests."""

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Test Category")

    def test_create_ads_with_valid_data(self):
        """Test that an ad can be created with valid data, and its slug is generated correctly."""

        ad = Ads.objects.create(
            user=self.user,
            title="Test Ad",
            category=self.category,
            description="This is a test ad.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=99.99,
            image=self.create_image()
        )
        self.assertIsNotNone(ad.id)  
        self.assertEqual(ad.slug, slugify(ad.title))  

    def test_create_ads_without_user_field(self):
        """Test that an ad raise error when created without user field."""
        with self.assertRaises(IntegrityError):
            Ads.objects.create(
                title="Test Ad",
                category=self.category,
                description="This is a test ad.",
                location="Test Location",
                postal_code="12345",
                contact_info="test@example.com",
                price=99.99,
                image=self.create_image()
            )

    def test_ads_without_title(self):
        """Test that attempting to create an ad without a title raises a ValidationError."""

        with self.assertRaises(ValidationError):
            ad = Ads(
                user=self.user,
                category=self.category,
                description="This ad has no title.",
                location="Test Location",
                postal_code="12345",
                contact_info="test@example.com",
                price=99.99,
                image=self.create_image()
            )
            ad.full_clean() 

    def test_ads_without_category(self):
        """Test that attempting to create an ad without a category raises an IntegrityError."""

        with self.assertRaises(IntegrityError):
            ad = Ads(
                user=self.user,
                title="Ad without Category",
                description="This ad has no category.",
                location="Test Location",
                postal_code="12345",
                contact_info="test@example.com",
                price=99.99,
                image=self.create_image()
            )
            ad.save()  

    def test_slug_generation(self):
        """Test that the slug is generated correctly based on the ad title upon creation."""
        
        ad = Ads.objects.create(
            user=self.user,
            title="Slug Test",
            category=self.category,
            description="This ad tests slug generation.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=50.00,
            image=self.create_image()
        )
        self.assertEqual(ad.slug, "slug-test")  

    def test_price_validation(self):
        """Test that attempting to create an ad with a negative price raises a ValidationError."""

        ad = Ads(
            user=self.user,
            title="Invalid Price Ad",
            category=self.category,
            description="This ad has an invalid price.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=-10.00,  
            image=self.create_image()
        )

        with self.assertRaises(ValidationError):
            ad.full_clean()  

    def test_invalid_postal_code_length_too_long(self):
        """Test that attempting to create an ad with a postal code longer than 10 characters raises a ValidationError."""
        
        ad = Ads(
            user=self.user,
            title="Long Postal Code Ad",
            category=self.category,
            description="This ad has a long postal code.",
            location="Test Location",
            postal_code="123456849393",  
            contact_info="test@example.com",
            price=20.00,
            image=self.create_image()
        )
        
        with self.assertRaises(ValidationError):
            ad.full_clean()

    def test_invalid_postal_code_length_too_short(self):
        """Test that attempting to create an ad with a postal code lesser than 5 characters raises a ValidationError."""
        
        ad = Ads(
            user=self.user,
            title="Long Postal Code Ad",
            category=self.category,
            description="This ad has a long postal code.",
            location="Test Location",
            postal_code="1234",  
            contact_info="test@example.com",
            price=20.00,
            image=self.create_image()
        )
        
        with self.assertRaises(ValidationError):
            ad.full_clean()

    def test_show_contact_info_default(self):
        """Test that the default value for show_contact_info is True when an ad is created."""
        ad = Ads.objects.create(
            user=self.user,
            title="Default Show Contact",
            category=self.category,
            description="This ad checks default show contact info.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=10.00,
            image=self.create_image()
        )
        self.assertTrue(ad.show_contact_info) 

    def test_event_dates(self):
        """Test that the end date is greater than the start date when both are set."""

        ad = Ads.objects.create(
            user=self.user,
            title="Event Ad",
            category=self.category,
            description="This ad has event dates.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=20.00,
            event_start_date="2024-12-01T10:00:00Z",
            event_end_date="2024-12-02T10:00:00Z",
            image=self.create_image()
        )
        self.assertGreater(ad.event_end_date, ad.event_start_date)  

    def test_event_dates_invalid(self):
        """Test that attempting to create an ad with an end date less than or equal to the start
           date raises a ValidationError."""
        
        ad = Ads(
            user=self.user,
            title="Invalid Event Ad",
            category=self.category,
            description="This ad has invalid event dates.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=20.00,
            event_start_date="2024-12-02T10:00:00Z",  
            event_end_date="2024-12-01T10:00:00Z",    
            image=self.create_image()
        )
        
        with self.assertRaises(ValidationError):
            ad.full_clean()  

    def test_created_at_auto_now_add(self):
        """Test that the created_at timestamp is set automatically upon ad creation."""

        ad = Ads.objects.create(
            user=self.user,
            title="Timestamp Ad",
            category=self.category,
            description="This ad checks timestamp fields.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=25.00,
            image=self.create_image()
        )
        self.assertIsNotNone(ad.created_at)  

    def test_tags_functionality(self):
        """Test that tags can be added to an ad successfully."""

        ad = Ads.objects.create(
            user=self.user,
            title="Taggable Ad",
            category=self.category,
            description="This ad supports tags.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=30.00,
            image=self.create_image()
        )
        ad.tags.add("tag1", "tag2")  
        self.assertEqual(ad.tags.count(), 2)  

    def test_image_upload(self):
        """Test that the image field is correctly populated with an uploaded image."""

        ad = Ads.objects.create(
            user=self.user,
            title="Image Ad",
            category=self.category,
            description="This ad has an image.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=40.00,
            image=self.create_image()
        )
        self.assertIsNotNone(ad.image.url)  

    def test_image_empty_field(self):
        """Test that an ad without an image raises a ValidationError."""

        ad = Ads(
            user=self.user,
            title="Image Ad",
            category=self.category,
            description="This ad has an image.",
            location="Test Location",
            postal_code="12345",
            contact_info="test@example.com",
            price=40.00,
        )
        
        with self.assertRaises(ValidationError):
            ad.full_clean()  

    def create_image(self):
        """Helper method to create a dummy image file for testing."""

        return InMemoryUploadedFile(
            BytesIO(b"image data"),  
            None,  
            'test_image.jpg',  
            'image/jpeg',  
            len(b"image data"),  
            None  
        )


class HomeViewTests(TestCase):
    def setUp(self):
        self.categories = []
        for i in range(15):  # Creating 15 categories
            category = Category.objects.create(name=f'Category {i+1}', slug=f'category-{i+1}')
            self.categories.append(category)

    def test_home_view_status_code(self):
        response = self.client.get(reverse('ads:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_context_contains_categories(self):
        response = self.client.get(reverse('ads:home'))
        self.assertIn('categories', response.context)

    def test_home_view_template_used(self):
        response = self.client.get(reverse('ads:home'))
        self.assertTemplateUsed(response, 'ads/home.html')

    def test_pagination_links(self):
        response = self.client.get(reverse('ads:home') + '?page=1')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Previous')
        self.assertContains(response, 'Next')
        self.assertContains(response, 'Last')
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded">1<span class="sr-only">(current)</span></span>', html=True)

        response = self.client.get(reverse('ads:home') + '?page=2')
        self.assertContains(response, 'Previous')  
        self.assertContains(response, 'Next')      
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded">2<span class="sr-only">(current)</span></span>', html=True)

    def test_pagination_edge_cases(self):
        response = self.client.get(reverse('ads:home') + '?page=3') 
        self.assertContains(response, 'Previous')  
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-200 rounded">Next</span>', html=True)
        self.assertContains(response, 'First')
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-200 rounded">Last</span>', html=True)

    def test_no_categories_pagination(self):
        
        Category.objects.all().delete()
        response = self.client.get(reverse('ads:home') + '?page=1')
        self.assertContains(response, 'No categories available')


class AdsListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ads = [
            Ads.objects.create(user=self.user ,title=f'Test Ad {i}', slug=f'test-ad-{i}', category=self.category, price=100 + i, image='test_image.jpg')
            for i in range(1, 21)
        ]
    def test_ads_list_view_status_code(self):
        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)

    def test_ads_list_view_with_valid_category(self):
        ad=Ads.objects.create(user=self.user ,title=f'Test Ad ', slug=f'test-ad', category=self.category, price=100, image='test_image.jpg')
            
        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]))
        self.assertIn(ad, response.context['ads'])

    def test_ads_list_view_with_invalid_category(self):
        response = self.client.get(reverse('ads:ads_by_category', args=['invalid-slug']))
        self.assertEqual(response.status_code, 404)

    def test_ads_list_view_template_used(self):
        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]))
        self.assertTemplateUsed(response, 'ads/ads_list.html')

    def test_pagination_links(self):
        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]) + '?page=1')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Previous')
        self.assertContains(response, 'Next')
        self.assertContains(response, 'Last')

        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded">1<span class="sr-only">(current)</span></span>', html=True)

        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]) + '?page=2')
        self.assertContains(response, 'Previous')  
        self.assertContains(response, 'Next')      
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded">2<span class="sr-only">(current)</span></span>', html=True)

    def test_pagination_edge_cases(self):
        response = self.client.get(reverse('ads:ads_by_category', args=[self.category.slug]) + '?page=4')
        self.assertContains(response, 'Previous')  
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-200 rounded">Next</span>', html=True)   

        self.assertContains(response, 'First')
        self.assertContains(response, '<span class="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-200 rounded">Last</span>', html=True)

    def test_no_ads_pagination(self):
        empty_category = Category.objects.create(name='Empty Category', slug='empty-category')
        response = self.client.get(reverse('ads:ads_by_category', args=[empty_category.slug]) + '?page=1')
        self.assertContains(response, 'No ads available')


class AdDetailViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ad = Ads.objects.create(user=self.user2, title='Test Ad', slug='test-ad', tags='ex', category=self.category, price=100.00, image='test_image.jpg', event_start_date="2024-12-01T10:00:00Z", event_end_date="2024-12-02T10:00:00Z")

    def test_ad_detail_view_status_code(self):
        response = self.client.get(reverse('ads:ad_detail', args=[self.category.slug, self.ad.slug]))
        self.assertEqual(response.status_code, 200)

    def test_ad_detail_view_with_valid_slugs(self):
        response = self.client.get(reverse('ads:ad_detail', args=[self.category.slug, self.ad.slug]))
        self.assertEqual(response.context['ad'], self.ad)

    def test_ad_detail_view_with_invalid_ad_slug(self):
        response = self.client.get(reverse('ads:ad_detail', args=[self.category.slug, 'invalid-ad-slug']))
        self.assertEqual(response.status_code, 404)

    def test_ad_detail_view_with_invalid_category_slug(self):
        response = self.client.get(reverse('ads:ad_detail', args=['invalid-category', self.ad.slug]))
        self.assertEqual(response.status_code, 404)

    def test_ad_detail_view_template_used(self):
        response = self.client.get(reverse('ads:ad_detail', args=[self.category.slug, self.ad.slug]))
        self.assertTemplateUsed(response, 'ads/ad_detail.html')

    def test_ad_detail_view_event_dates_display(self):
        category = Category.objects.create(name='Events', slug='events')
        ad = Ads.objects.create(user=self.user1, title='Event Ad', slug='event-ad', category=category, price=100.0, image='event_image.jpg', event_start_date="2024-12-01T10:00:00Z", event_end_date="2024-12-02T10:00:00Z")
        response = self.client.get(reverse('ads:ad_detail', args=[category.slug, ad.slug]))
        self.assertContains(response, 'Event Start:')
        self.assertContains(response, 'Event End:')

    def test_initiate_new_conversation(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('ads:ad_detail', args=[self.category.slug, self.ad.slug]))

        self.assertEqual(Message.objects.count(), 1)
        chat_message = Message.objects.first()
        self.assertEqual(chat_message.sender, self.user1)
        self.assertEqual(chat_message.receiver, self.user2)
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_existing_conversation(self):
        self.client.login(username='user1', password='password')
        chat1=Chat.objects.create(ad=self.ad)
        chat1.users.set([self.user1, self.user2])
        Message.objects.create(sender=self.user1, receiver=self.user2, chat=chat1, message="Existing Message",)
        response = self.client.post(reverse('ads:ad_detail', args=[self.category.slug, self.ad.slug]))
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(response.status_code, 302)


class AdCreateViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        image_path = os.path.join('media', 'ads', 'events.jpg') 
        with open(image_path, 'rb') as img_file:
            self.image_file = SimpleUploadedFile(
                name='your_image.jpg',
                content=img_file.read(),
                content_type='image/jpeg'  
            )

    def test_create_ad_valid(self):
        self.client.login(username='testuser', password='password')
        
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ads:ads_by_category', args=[self.category.slug]))

    def test_create_ad_invalid_missing_title(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })
        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('title', form.errors)  
        self.assertEqual(form.errors['title'], ['This field is required.'])

    def test_create_ad_invalid_missing_category(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('category', form.errors)  
        self.assertEqual(form.errors['category'], ['This field is required.']) 

    def test_create_ad_invalid_missing_description(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('description', form.errors)  
        self.assertEqual(form.errors['description'], ['This field is required.'])
        
    def test_create_ad_invalid_missing_price(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('price', form.errors)  
        self.assertEqual(form.errors['price'], ['This field is required.'])

    def test_create_ad_invalid_negative_price(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": -50,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']
        self.assertIn('Price is Invalid.', form.non_field_errors())

    def test_create_ad_invalid_missing_location(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('location', form.errors)  
        self.assertEqual(form.errors['location'], ['This field is required.'])

    def test_create_ad_invalid_postal_code_too_short(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "123",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']
        self.assertIn('Postal code must be at least 5 characters long.', form.non_field_errors())

    def test_create_ad_invalid_missing_image(self):
        response = self.client.post(reverse('ads:ad_create'), {
            "title": "Valid Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        form = response.context['form']  
        self.assertTrue(form.errors)  
        self.assertIn('image', form.errors)  
        self.assertEqual(form.errors['image'], ['This field is required.'])

    def test_create_ad_template_used(self):
        """Test that the correct template is used for the ad creation view."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ad_create'))
        self.assertTemplateUsed(response, 'ads/ad_create.html')

    def test_create_ad_form_rendering(self):
        """Test that the ad creation form renders correctly."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ad_create'))
        
        self.assertIn('form', response.context)
        
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="category"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="price"')
        self.assertContains(response, 'name="location"')
        self.assertContains(response, 'name="tags"')
        self.assertContains(response, 'name="image"')
        self.assertContains(response, 'name="postal_code"')
        self.assertContains(response, 'name="contact_info"')

    def test_create_ad_invalid_form_submission(self):
        """Test that invalid form submission returns to the same template with errors."""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(reverse('ads:ad_create'), {
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        })

        self.assertEqual(response.status_code, 200)

    def test_create_ad_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('ads:ad_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ads:ad_create')}")

    def test_create_ad_authenticated(self):
        """Authenticated users can access the ad creation page"""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('ads:ad_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_create.html')

    def test_post_ad_authenticated(self):
        """Authenticated users can create an ad"""
        self.client.login(username='testuser', password='password')
        post_data = {
            "title": "Test Ad",
            "category": self.category.id,
            "description": "This ad has valid data.",
            "price": 100,
            "location": "Valid Location",
            "tags": 'gas',
            "image": self.image_file,
            "postal_code": "12345",
            "contact_info": "valid@example.com",
        }
        response = self.client.post(reverse('ads:ad_create'), post_data)
        self.assertEqual(Ads.objects.count(), 1)
        ad = Ads.objects.first()
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.user, self.user)
        self.assertRedirects(response, reverse('ads:ads_by_category', args=[self.category.slug]))


class AdEditViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.client.login(username='testuser', password='testpass')
        image_path = os.path.join('media', 'ads', 'events.jpg') 
        self.ad = Ads.objects.create(
            title=" Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = 'test.jpeg',
            location="Original Location",
            user=self.user
        )
        with open(image_path, 'rb') as img_file:
            self.image_file = SimpleUploadedFile(
                name='your_image.jpg',
                content=img_file.read(),
                content_type='image/jpeg'  
            )

    def test_edit_ad_valid(self):
        ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00,
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = self.image_file,
            location="Original Location",
            user=self.user  
        )
        response = self.client.post(reverse('ads:ad_edit', args=[ad.category.slug, ad.slug]), {
            "title": "Updated Title",
            "category": self.category.id,
            "slug": ad.slug,
            "description": "Updated description.",
            "price": 150.00,
            "location": "Updated Location",
            "tags": 'gas',
            "postal_code": "54321",
            "contact_info": "updated@example.com",
        })
        
        self.assertRedirects(response, reverse('ads:ad_detail', args=[ad.category.slug, ad.slug]))
        ad.refresh_from_db()
        self.assertEqual(ad.title, "Updated Title")
        self.assertEqual(ad.description, "Updated description.")
        self.assertEqual(ad.price, 150)

    def test_edit_ad_non_owner(self):
        other_user = User.objects.create_user(username="otheruser", password="pass")
        ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = self.image_file,
            location="Original Location",
            user=other_user  
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('ads:ad_edit', args=[ad.category.slug, ad.slug]), {
            "title": "Updated Title",
            "category": self.category,
            "slug": ad.slug,
            "description": "Updated description.",
            "price": 150.00,
            "location": "Updated Location",
            "tags": 'gas',
            "postal_code": "54321",
            "contact_info": "updated@example.com",
        })
        self.assertEqual(response.status_code, 403)

    def test_edit_ad_not_found(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ad_edit', args=['non-existent-category', 'non-existent-ad']))
        self.assertEqual(response.status_code, 404)

    def test_edit_ad_redirect(self):
        ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = self.image_file,
            location="Original Location",
            user=self.user
        )
        response = self.client.post(reverse('ads:ad_edit', args=[ad.category.slug, ad.slug]), {
            "title": "Updated Title",
            "category": self.category.id,
            "slug": ad.slug,
            "description": "Updated description.",
            "price": 150.00,
            "location": "Updated Location",
            "tags": 'gas',
            "postal_code": "54321",
            "contact_info": "updated@example.com",
        })

        self.assertRedirects(response, reverse('ads:ad_detail', args=[ad.category.slug, ad.slug]))

    def test_edit_ad_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('ads:ad_edit', args=[self.category.slug, self.ad.slug]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ads:ad_edit', args=[self.category.slug, self.ad.slug])}")


class AdDeleteViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.ad = Ads.objects.create(
            title="Original Title",
            category=self.category,
            description="Original description",
            price=100.00,
            tags='test',
            contact_info='original@example.com',
            postal_code='638056',
            image='test_image.jpg',
            location="Original Location",
            user=self.user  
        )

    def test_delete_existing_ad(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:ad_delete', args=[self.ad.category.slug, self.ad.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ads.objects.filter(id=self.ad.id).exists())

    def test_delete_non_existent_ad(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:ad_delete', args=['hsdad', 'sda']))  # Non-existent ID
        self.assertEqual(response.status_code, 404)

    def test_user_lacks_permission(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('ads:ad_delete', args=[self.ad.category.slug, self.ad.slug]))
        self.assertEqual(response.status_code, 403)

    def test_check_redirect_after_deletion(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:ad_delete', args=[self.ad.category.slug, self.ad.slug]))
        self.assertRedirects(response, expected_url=reverse('ads:ads_by_category', args=[self.category.slug]))

    def test_check_database_state_after_deletion(self):
        self.client.login(username='testuser', password='password')
        self.client.post(reverse('ads:ad_delete', args=[self.ad.category.slug, self.ad.slug]))
        self.assertFalse(Ads.objects.filter(id=self.ad.id).exists())

    def test_delete_ad_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('ads:ad_delete', args=[self.category.slug, self.ad.slug]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ads:ad_delete', args=[self.category.slug, self.ad.slug])}")


class baseTemplateTests(TestCase):

    def setUp(self):
        self.url = reverse('ads:home')  

    def test_navbar_authenticated_user(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        response = self.client.get(self.url)

        self.assertContains(response, 'Messages')
        self.assertContains(response, 'Post Ad')
        self.assertContains(response, 'testuser')

    def test_navbar_unauthenticated_user(self):
        response = self.client.get(self.url)

        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertNotContains(response, 'testuser')


class AdDetailTemplateTests(TestCase):

    def setUp(self):
        # Create a user and an ad
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info ='original@example.com',
            postal_code= '638056',
            image = 'test.jpeg',
            location="Original Location",
            user=self.user
        )
        self.url = reverse('ads:ad_detail', args=[self.ad.category.slug, self.ad.slug]) 

    def test_edit_delete_links_for_owner(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)

        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Delete')

    def test_edit_delete_links_for_non_owner(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.get(self.url)

        self.assertNotContains(response, 'Edit')
        self.assertNotContains(response, 'Delete')

    def test_edit_delete_links_for_unauthenticated_user(self):
        response = self.client.get(self.url)

        self.assertNotContains(response, 'Edit')
        self.assertNotContains(response, 'Delete')


class AdLikeViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ad = Ads.objects.create(
            title="Original Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info='original@example.com',
            postal_code='638056',
            image='test.jpeg',
            location="Original Location",
            user=self.user,
            total_likes=0  
        )
        self.like_url = reverse('ads:ad_like', kwargs={'category_slug': self.ad.category.slug, 'ad_slug': self.ad.slug})

    def test_like_ad_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertTrue(self.ad.users_like.filter(id=self.user.id).exists())
        self.assertEqual(response.json()['liked'], True)
        self.assertEqual(response.json()['total_likes'], 1)

    def test_unlike_ad_authenticated_user(self):
        self.ad.users_like.add(self.user)
        self.ad.total_likes += 1
        self.ad.save()
        
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertFalse(self.ad.users_like.filter(id=self.user.id).exists())
        self.assertEqual(response.json()['liked'], False)
        self.assertEqual(response.json()['total_likes'], 0)

    def test_like_ad_unauthenticated_user(self):
        response = self.client.post(self.like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

    def test_like_ad_total_likes(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.users_like.count(), 1)
        self.assertEqual(response.json()['total_likes'], 1)

    def test_unlike_ad_total_likes_decrease(self):
        self.ad.users_like.add(self.user)
        self.ad.total_likes += 1
        self.ad.save()
        
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.users_like.count(), 0)
        self.assertEqual(response.json()['total_likes'], 0)

    def test_invalid_ad_slug(self):
        self.client.login(username='testuser', password='password')
        invalid_like_url = reverse('ads:ad_like', kwargs={'category_slug': 'gigs', 'ad_slug': 'invalid-slug'})
        response = self.client.post(invalid_like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)


class AdToggleContactInfoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ad = Ads.objects.create(
            title="ContactInfo Title", 
            category=self.category,
            description="Original description", 
            price=100.00, 
            tags='test',
            contact_info='original@example.com',
            postal_code='638056',
            image='test.jpeg',
            location="Original Location",
            user=self.user
        )

    def test_toggle_contact_info_hide(self):
        self.ad.save()

        self.assertTrue(self.ad.show_contact_info)

        response = self.client.post(reverse('ads:toggle_contact_info', kwargs={
            'category_slug': self.ad.category.slug,
            'ad_slug': self.ad.slug
        }), {
            'ad_id': self.ad.id,
            'show_contact_info': 'True'
        })

        self.ad.refresh_from_db()

        self.assertFalse(self.ad.show_contact_info)
        self.assertRedirects(response, reverse('ads:ad_detail', kwargs={
            'category_slug': self.ad.category.slug,
            'ad_slug': self.ad.slug
        }))


    def test_toggle_contact_info_show(self):
        self.ad.show_contact_info=False
        self.assertFalse(self.ad.show_contact_info)
        response = self.client.post(reverse('ads:toggle_contact_info', kwargs={
            'category_slug': self.ad.category.slug,
            'ad_slug': self.ad.slug
        }), {
            'ad_id': self.ad.id,
            'show_contact_info': 'False'  
        })

        self.ad.refresh_from_db()

        self.assertTrue(self.ad.show_contact_info)
        self.assertRedirects(response, reverse('ads:ad_detail', kwargs={
            'category_slug': self.ad.category.slug,
            'ad_slug': self.ad.slug
        }))