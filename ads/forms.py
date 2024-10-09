from django import forms
from .models import Ads


class AdsForm(forms.ModelForm):
    class Meta:
        model = Ads
        fields = ("category","title","slug","description",
                  "image","price","tags","location",
                  "postal_code","contact_info","show_contact_info",
                  "event_start_date","event_end_date")
        
        widgets = {
            'event_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
