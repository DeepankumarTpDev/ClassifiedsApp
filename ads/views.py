from django.views.generic import ListView, DetailView
from .models import Ads, Category
from django.shortcuts import get_object_or_404


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