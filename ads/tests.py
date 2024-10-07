from django.test import TestCase
from django.urls import reverse
from .models import Category, Ads
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from io import BytesIO
from django.contrib.auth.models import User

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
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.ad = Ads.objects.create(user=self.user, title='Test Ad', slug='test-ad',tags='ex', category=self.category, price=100.0, image='test_image.jpg', event_start_date="2024-12-01T10:00:00Z", event_end_date="2024-12-02T10:00:00Z")

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
        ad = Ads.objects.create(
            user=self.user,
            title='Test Ad',
            slug='test-a',
            tags='ex',
            category=category,  
            price=100.0,
            image='test_image.jpg',
            event_start_date="2024-12-01T10:00:00Z",
            event_end_date="2024-12-02T10:00:00Z"
        )

        response = self.client.get(reverse('ads:ad_detail', args=[category.slug, ad.slug]))
        
        self.assertContains(response, 'Event Start:')
        self.assertContains(response, 'Event End:')

