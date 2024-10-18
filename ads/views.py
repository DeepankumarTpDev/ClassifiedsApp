from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Ads, Category
from chat.models import Chat,Message
from django.shortcuts import get_object_or_404,redirect
from .forms import AdsForm, AdImageFormSet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from functools import wraps
from django.views import View
from django.http import JsonResponse,HttpResponseRedirect


class HomeView(ListView):
    model = Category
    template_name = 'ads/home.html'
    context_object_name = 'categories'
    paginate_by = 6


class AdsListView(ListView):
    model = Ads
    template_name = 'ads/ads_list.html'
    context_object_name = 'ads'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Ads.objects.filter(category=self.category)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class AdDetailView(DetailView):
    model = Ads
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_object(self):
        return get_object_or_404(Ads, slug=self.kwargs['ad_slug'], category__slug=self.kwargs['category_slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.get_object()
        context['user_has_liked'] = self.request.user in ad.users_like.all()
        return context
    
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseForbidden("You need to log in to start a conversation.")
        
        self.ad = self.get_object()
        chat = Chat.objects.filter(ad=self.ad, users=request.user).filter(users=self.ad.user).first()
        print('chat',chat)
        if chat:
            return redirect('chat:conversation_detail', chat_id=chat.id)
        else:   
            chat_obj = Chat.objects.create(ad=self.ad)
            chat_obj.users.set([request.user, self.ad.user])
            
            Message.objects.create(
                sender=request.user,
                receiver=self.ad.user,
                chat=chat_obj,
                message=f"Hi, I am {request.user.username}. I am interested in your ad posting."
            )
            return redirect('chat:conversation_detail', chat_id=chat_obj.id)
    

class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ads
    form_class = AdsForm
    template_name = 'ads/ad_create.html'
    
    def get_success_url(self):
        return reverse_lazy('ads:ads_by_category', args=[self.object.category.slug])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = AdImageFormSet()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        image_form = AdImageFormSet(self.request.POST,self.request.FILES, instance=self.object)

        if form.is_valid() and image_form.is_valid():
            print("form.is_valid()")
            self.object = form.save()
            image_form.instance = self.object
            image_form.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.form_invalid(form)


def user_is_ad_owner(view_func):
    @wraps(view_func)
    def _wrapped_view(self, *args, **kwargs):
        ad = self.get_object()
        if ad.user != self.request.user:
            return HttpResponseForbidden()
        return view_func(self, *args, **kwargs)
    return _wrapped_view

class AdEditView(LoginRequiredMixin, UpdateView):
    model = Ads
    form_class = AdsForm
    template_name = 'ads/ad_edit.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    @user_is_ad_owner
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @user_is_ad_owner
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdEditView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['image_form'] = AdImageFormSet(self.request.POST,self.request.FILES, instance=self.object)
        else:
            context['image_form'] = AdImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_form = context['image_form']

        if form.is_valid() and image_form.is_valid():
            self.object = form.save()
            image_form.instance = self.object
            image_form.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', args=[self.object.category.slug, self.object.slug])
    
    def get_object(self):
        return get_object_or_404(Ads, slug=self.kwargs['ad_slug'], category__slug=self.kwargs['category_slug'])
    

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model=Ads
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['previous_url'] = reverse_lazy('ads:ad_detail', args=[self.object.category.slug, self.object.slug])
        return context
    
    def get_success_url(self):
        return reverse_lazy('ads:ads_by_category', args=[self.object.category.slug])
    
    def get_object(self):
        return get_object_or_404(Ads, slug=self.kwargs['ad_slug'], category__slug=self.kwargs['category_slug'])

    @user_is_ad_owner
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @user_is_ad_owner
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdLikeView(LoginRequiredMixin, View):
    def post(self, request, category_slug, ad_slug, *args, **kwargs):
        ad = get_object_or_404(Ads, category__slug=category_slug, slug=ad_slug)

        if request.user in ad.users_like.all():
            ad.users_like.remove(request.user)
            ad.total_likes -= 1
            ad.save()
            liked = False
        else:
            ad.users_like.add(request.user)
            liked = True
            ad.total_likes += 1
            ad.save()

        return JsonResponse({
            'liked': liked,
            'total_likes': ad.total_likes,
        })


class AdToggleContactInfo(LoginRequiredMixin, View):
    def post(self, request, category_slug, ad_slug, *args, **kwargs):
        ad = get_object_or_404(Ads, category__slug=category_slug, slug=ad_slug)

        show_contact_info = request.POST.get('show_contact_info') == 'True'
        ad.show_contact_info = not show_contact_info  
        ad.save()

        return redirect('ads:ad_detail', category_slug=ad.category.slug, ad_slug=ad.slug)
    