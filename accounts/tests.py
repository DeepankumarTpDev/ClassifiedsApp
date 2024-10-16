from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile
from django.db import IntegrityError
import time
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, ProfileForm

User = get_user_model()

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_profile_creation_with_valid_data(self):
        """Test creating a profile with valid data."""

        profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),  
            phone_number='1234567890',
            address='Test Address'
        )

        self.assertIsInstance(profile, Profile)  
    

    def test_profile_creation_with_empty_required_fields(self):
        """Test creating a profile with empty required fields."""
        
        with self.assertRaises(IntegrityError):
            Profile.objects.create(date_of_birth=None, phone_number='', address='Test Address')


    def test_date_of_birth_validation(self):
        """Test that the date_of_birth cannot be in the future."""
        
        future_date = timezone.now().date() + timedelta(days=365)  
        profile = Profile(user=self.user, date_of_birth=future_date)

        with self.assertRaises(ValidationError):
            profile.clean()  

    def test_phone_number_length_validation(self):
        """Check that the phone number cannot exceed 15 characters."""
        
        profile = Profile(
            user=self.user,
            date_of_birth=date(1990, 1, 1),  
            phone_number='1234567890123456',  
            address='Test Address'
        )

        with self.assertRaises(ValidationError):
            profile.full_clean()  

    def test_auto_generated_timestamps(self):
        """Check that created_at and updated_at are set correctly."""
        
        profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),  
            phone_number='1234567890',
            address='Test Address'
        )
        
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_profile_update_timestamp(self):
        """Verify updated_at changes when the profile is updated."""
        
        profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),  
            phone_number='1234567890',
            address='Test Address'
        )
        
        original_updated_at = profile.updated_at
        
        time.sleep(1)
        
        profile.address = 'New Test Address'
        profile.save()
        
        self.assertNotEqual(original_updated_at, profile.updated_at)


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile

class UserRegistrationTests(TestCase):

    def test_successful_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'validuser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'validuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertTrue(User.objects.filter(username='validuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='validuser').exists())

    def test_registration_invalid_username(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'validuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'This field is required.')

    def test_registration_existing_username(self):
        User.objects.create_user(username='existinguser', password='testpassword123', email='existinguser@example.com')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'newuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'A user with that username already exists.')

    def test_registration_invalid_email_format(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'invalidemail',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123',
            'password2': 'DifferentPassword123',
            'email': 'newuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords doesn&#x27;t match.')

    def test_registration_future_date_of_birth(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'newuser@example.com',
            'date_of_birth': '2050-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The date of birth cannot be in the future.')

    def test_registration_empty_required_profile_fields(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'newuser@example.com',
            'date_of_birth': '2000-01-01',  
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_authenticated_user_accessing_registration(self):
        User.objects.create_user(username='existinguser', password='testpassword123', email='existinguser@example.com')
        self.client.login(username='existinguser', password='testpassword123')
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('ads:home'))  

    def test_registration_invalid_profile_picture_upload(self):
        
        with open('invalidfile.txt', 'w') as f:
            f.write('This is a test file.')  

        with open('invalidfile.txt', 'rb') as f:
            response = self.client.post(reverse('register'), {
                'username': 'newuser',
                'password': 'ValidPassword123',
                'password2': 'ValidPassword123',
                'email': 'newuser@example.com',
                'date_of_birth': '2000-01-01',
                'phone_number': '1234567890',
                'address': '123 Test St',
                'photo': f,
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Upload a valid image.')

    def test_registration_no_profile_picture_upload(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123',
            'password2': 'ValidPassword123',
            'email': 'newuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '1234567890',
            'address': '123 Test St',
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())

    def test_registration_all_fields_empty(self):
        response = self.client.post(reverse('register'), {})
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'This field is required.')


