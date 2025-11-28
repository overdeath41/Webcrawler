from django.contrib import admin
from django.utils.html import format_html
from .models import CrawlTask

@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status_badge', 'urls_count', 'items_scraped', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['user__username', 'user__email', 'urls']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'celery_task_id', 'urls_count', 'items_scraped']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'urls', 'status', 'urls_count')
        }),
        ('Résultats', {
            'fields': ('items_scraped', 'result_file', 'error_message')
        }),
        ('Métadonnées', {
            'fields': ('celery_task_id', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'running': '#17a2b8',
            'done': '#28a745',
            'error': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle depuis l'admin
        return False