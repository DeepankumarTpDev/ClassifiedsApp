from django.db import models
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
     
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=False, null=False)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    user_type = models.CharField(max_length=10, blank=False, choices=USER_TYPE_CHOICES)
    address = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} : {self.user_type} Profile"
    
    def clean(self):
        if len(self.phone_number) > 15:
            raise ValidationError('Phone number cannot exceed 15 characters.')
        
        if self.date_of_birth is not None and self.date_of_birth  > timezone.now().date():
            raise ValidationError('The date of birth cannot be in the future.')
    
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)
