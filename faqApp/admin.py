from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('question', 'answer', 'translations')
    readonly_fields = ('created_at', 'updated_at', 'translations')
    
    fieldsets = (
        ('Content', {
            'fields': ('question', 'answer', 'is_active')
        }),
        ('Translations', {
            'fields': ('translations',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
