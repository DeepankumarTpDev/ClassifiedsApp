from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Ads, Category
from django.shortcuts import get_object_or_404,redirect,render
from .forms import AdsForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from functools import wraps


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
    

class AdCreateView(CreateView):
    model = Ads
    form_class = AdsForm
    template_name = 'ads/ad_create.html'
    
    def get_success_url(self):
        return reverse_lazy('ads:ads_by_category', args=[self.object.category.slug])
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def user_is_ad_owner(view_func):
    @wraps(view_func)
    def _wrapped_view(self, *args, **kwargs):
        ad = self.get_object()
        if ad.user != self.request.user:
            return HttpResponseForbidden()
        return view_func(self, *args, **kwargs)
    return _wrapped_view

class AdEditView(UpdateView):
    model = Ads
    form_class = AdsForm
    template_name = 'ads/ad_edit.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    @user_is_ad_owner
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', args=[self.object.category.slug, self.object.slug])
    
    def get_object(self):
        return get_object_or_404(Ads, slug=self.kwargs['ad_slug'], category__slug=self.kwargs['category_slug'])
    

class AdDeleteView(DeleteView):
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
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)