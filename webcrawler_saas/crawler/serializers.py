from rest_framework import serializers
from django.conf import settings
from .models import CrawlTask

class CrawlTaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    urls_list = serializers.SerializerMethodField()
    
    class Meta:
        model = CrawlTask
        fields = [
            'id', 'user', 'urls', 'urls_list', 'status', 
            'result_file', 'error_message', 'created_at', 
            'updated_at', 'completed_at', 'urls_count', 
            'items_scraped', 'celery_task_id'
        ]
        read_only_fields = [
            'status', 'result_file', 'error_message', 
            'created_at', 'updated_at', 'completed_at', 
            'urls_count', 'items_scraped', 'celery_task_id'
        ]
    
    def get_urls_list(self, obj):
        return obj.get_urls_list()
    
    def validate_urls(self, value):
        """Valide le format et le nombre d'URLs"""
        task = CrawlTask(urls=value)
        urls_list = task.get_urls_list()
        
        if not urls_list:
            raise serializers.ValidationError("Au moins une URL est requise")
        
        if len(urls_list) > settings.MAX_URLS_PER_TASK:
            raise serializers.ValidationError(
                f"Maximum {settings.MAX_URLS_PER_TASK} URLs autorisées"
            )
        
        # Validation basique du format URL
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        validator = URLValidator()
        for url in urls_list:
            try:
                validator(url)
            except DjangoValidationError:
                raise serializers.ValidationError(f"URL invalide: {url}")
        
        return value


class CrawlTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlTask
        fields = ['urls']
    
    def validate_urls(self, value):
        """Valide le format et le nombre d'URLs"""
        task = CrawlTask(urls=value)
        urls_list = task.get_urls_list()
        
        if not urls_list:
            raise serializers.ValidationError("Au moins une URL est requise")
        
        if len(urls_list) > settings.MAX_URLS_PER_TASK:
            raise serializers.ValidationError(
                f"Maximum {settings.MAX_URLS_PER_TASK} URLs autorisées"
            )
        
        return value