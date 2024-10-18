from django.contrib import admin
from .models import Ads, Category, AdImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')  
    search_fields = ('name', 'description')  
    prepopulated_fields = {'slug': ('name',)}  
    ordering = ('created_at',)  


@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'price', 'location', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'tags', 'location')
    ordering = ('-created_at',)


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('ad', 'image')  
    search_fields = ('ad',)
    ordering = ('-created_on',)  