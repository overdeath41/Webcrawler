from django.shortcuts import render
# crawler/views.py
from rest_framework import generics, permissions
from .models import CrawlTask
from .serializers import CrawlTaskSerializer

class CrawlTaskCreate(generics.CreateAPIView):
    serializer_class = CrawlTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CrawlTaskDetail(generics.RetrieveAPIView):
    queryset = CrawlTask.objects.all()
    serializer_class = CrawlTaskSerializer
    permission_classes = [permissions.IsAuthenticated]