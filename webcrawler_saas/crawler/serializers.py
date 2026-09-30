from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from rest_framework import serializers

from .models import CrawlTask
from .validators import validate_url_list


class CrawlTaskSerializer(serializers.ModelSerializer):
    urls_list = serializers.SerializerMethodField()
    progress = serializers.IntegerField(source="progress_percent", read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = CrawlTask
        fields = [
            "id", "name", "urls_list", "status", "progress", "urls_count", "urls_done",
            "urls_failed", "items_scraped", "error_message", "download_url",
            "created_at", "started_at", "completed_at",
        ]
        read_only_fields = fields

    def get_urls_list(self, obj):
        return obj.get_urls_list()

    def get_download_url(self, obj):
        if not obj.result_file:
            return None
        url = reverse("task-download", args=[obj.pk])
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class CrawlTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlTask
        fields = ["id", "name", "urls"]
        read_only_fields = ["id"]

    def validate_urls(self, value):
        try:
            urls = validate_url_list(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return "\n".join(urls)
