from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from crawler import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pages web
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='crawler/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/create/', views.create_task_view, name='create-task-web'),
    path('task/<int:task_id>/', views.task_detail, name='task-detail-web'),
    
    # API REST
    path('api/tasks/', views.CrawlTaskListCreate.as_view(), name='api-tasks'),
    path('api/task/<int:pk>/', views.CrawlTaskDetail.as_view(), name='api-task-detail'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)