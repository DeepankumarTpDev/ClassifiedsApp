from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False)  
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.name  
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ads(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to='ads/%Y/%m/%d/', blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    tags = TaggableManager()  # Using TaggableManager for tags
    location = models.CharField(max_length=255, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    contact_info = models.CharField(max_length=255, blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    show_contact_info = models.BooleanField(default=True)
    event_start_date = models.DateTimeField(null=True, blank=True)
    event_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')
        
        if self.event_start_date and self.event_end_date:
            if self.event_end_date < self.event_start_date:
                raise ValidationError("The end date must be greater than the start date.")
            
        if len(self.postal_code) < 5:
            raise ValidationError("Postal code must be at least 5 characters long.")
        
        if len(self.postal_code) > 10:
            raise ValidationError("Postal code must not exceed 10 characters.")

    def __str__(self):
        return f"{self.title} - {self.category.name} (${self.price})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        pass


    class Meta:
        ordering = ['-created_at']