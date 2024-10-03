from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile
from django.db import IntegrityError
import time
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta

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
            user_type='buyer',
            address='Test Address'
        )

        self.assertIsInstance(profile, Profile)  
    

    def test_profile_creation_with_empty_required_fields(self):
        """Test creating a profile with empty required fields."""
        
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user, date_of_birth=None, phone_number='', user_type='buyer', address='Test Address')


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
            user_type='buyer',
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
            user_type='buyer',
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
            user_type='buyer',
            address='Test Address'
        )
        
        original_updated_at = profile.updated_at
        
        time.sleep(1)
        
        profile.address = 'New Test Address'
        profile.save()
        
        self.assertNotEqual(original_updated_at, profile.updated_at)
