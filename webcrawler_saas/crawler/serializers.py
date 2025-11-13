# crawler/serializers.py
from rest_framework import serializers
from .models import CrawlTask

class CrawlTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlTask
        fields = ['id', 'user', 'url', 'status', 'result_file', 'created_at']