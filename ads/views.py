from django.views.generic import ListView, DetailView
from .models import Ads, Category
from django.http import Http404


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
        try:
            self.category = Category.objects.get(slug=self.kwargs['category_slug'])
            return Ads.objects.filter(category=self.category)
        except Category.DoesNotExist:
            raise Http404("Category not found.")
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class AdDetailView(DetailView):
    model = Ads
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_object(self, queryset=None):
        category_slug = self.kwargs['category_slug']
        ad_slug = self.kwargs['ad_slug']
        queryset = self.get_queryset().filter(slug=ad_slug, category__slug=category_slug)
        obj = queryset.first()  

        if obj is None:
            raise Http404("Ad not found.")
        
        return obj