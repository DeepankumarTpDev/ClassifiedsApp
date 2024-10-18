from django import forms
from .models import Ads
from django.core.exceptions import ValidationError
import re


class AdsForm(forms.ModelForm):
    class Meta:
        model = Ads
        fields = ("category","title","slug","description",
                  "price","tags","location",
                  "postal_code","contact_info","show_contact_info",
                  "event_start_date","event_end_date")
        
        widgets = {
            'event_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_contact_info(self):
            contact_info = self.cleaned_data.get('contact_info')
            print('contact_info')
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            mobile_regex = r'^\d{10}$'
            
            if not (re.match(email_regex, contact_info) or re.match(mobile_regex, contact_info)):
                raise ValidationError("Contact info must be a valid email address or a 10-digit mobile number.")
            
            return contact_info
