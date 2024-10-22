# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile
import re
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):          
        cd = self.cleaned_data  

        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords doesn\'t match.')
        
        return cd['password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo', 'phone_number', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        mobile_regex = r'^\d{15}$'
            
        if not (re.match(mobile_regex, phone_number)):
            raise ValidationError("Give Valid mobile number.")
            
        return phone_number