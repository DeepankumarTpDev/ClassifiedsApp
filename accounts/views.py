from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm, ProfileForm


def register(request):
    if request.user.is_authenticated:
            return redirect('ads:home') 
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])  
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user  
            profile.save()

            login(request, user)  
            return redirect('ads:home')  

    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })