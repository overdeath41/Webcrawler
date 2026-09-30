from django.contrib import admin
from django.utils.html import format_html

from .models import CrawlTask

STATUS_COLORS = {"pending": "#c9a227", "running": "#2f7fd1", "done": "#2e9e5b", "error": "#c0392b"}


@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "display_name", "status_badge", "urls_count", "urls_failed",
                    "items_scraped", "created_at", "completed_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "user__email", "urls", "name"]
    readonly_fields = ["created_at", "updated_at", "started_at", "completed_at", "celery_task_id",
                       "urls_count", "urls_done", "urls_failed", "items_scraped"]
    list_select_related = ["user"]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Mission", {"fields": ("user", "name", "urls", "status", "urls_count")}),
        ("Résultats", {"fields": ("urls_done", "urls_failed", "items_scraped", "result_file", "error_message")}),
        ("Métadonnées", {"fields": ("celery_task_id", "created_at", "updated_at", "started_at", "completed_at"),
                         "classes": ("collapse",)}),
    )

    @admin.display(description="Statut")
    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:3px">{}</span>',
            STATUS_COLORS.get(obj.status, "#666"), obj.get_status_display(),
        )

    def has_add_permission(self, request):
        return False
