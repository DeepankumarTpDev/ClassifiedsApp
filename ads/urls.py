from django.urls import path
from . import views


app_name = 'ads'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),  
    path('category/<slug:category_slug>/ads/', views.AdsListView.as_view(), name='ads_by_category'),  
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/detail/', views.AdDetailView.as_view(), name='ad_detail'),
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/edit/', views.AdEditView.as_view( ), name='ad_edit'),
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/delete/', views.AdDeleteView.as_view( ), name='ad_delete'),
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/like/', views.AdLikeView.as_view() , name='ad_like'),
    path('category/<slug:category_slug>/ads/<slug:ad_slug>/toggle_contact_info/', views.AdToggleContactInfo.as_view() , name='toggle_contact_info'),

    path('ad/new/', views.AdCreateView.as_view(), name='ad_create') ,

]
