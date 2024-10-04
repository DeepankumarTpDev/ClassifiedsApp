from django.urls import path
from . import views


app_name = 'ads'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),  
    path('category/<slug:category_slug>/ads/', views.AdsListView.as_view(), name='ads_by_category'),  
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/detail/', views.AdDetailView.as_view(), name='ad_detail'),  
]
