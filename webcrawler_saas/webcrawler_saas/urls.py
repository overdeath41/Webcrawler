from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from crawler import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", views.healthz, name="healthz"),

    # Pages publiques
    path("", views.home, name="home"),
    path("inscription/", views.register, name="register"),
    path("connexion/", views.ThrottledLoginView.as_view(), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),  # POST uniquement
    path("legal/<slug:slug>/", views.legal_page, name="legal"),

    # Espace connecté
    path("tableau-de-bord/", views.dashboard, name="dashboard"),
    path("mission/nouvelle/", views.create_task_view, name="create-task-web"),
    path("mission/<int:task_id>/", views.task_detail, name="task-detail-web"),
    path("mission/<int:task_id>/csv/", views.task_download, name="task-download"),
    path("mission/<int:task_id>/relancer/", views.task_relaunch, name="task-relaunch"),
    path("mission/<int:task_id>/supprimer/", views.task_delete, name="task-delete"),
    path("missions/statut/", views.tasks_status, name="tasks-status"),

    # API REST
    path("api/tasks/", views.CrawlTaskListCreate.as_view(), name="api-tasks"),
    path("api/tasks/<int:pk>/", views.CrawlTaskDetail.as_view(), name="api-task-detail"),
]

admin.site.site_header = "WebCrawler — administration"
admin.site.site_title = "WebCrawler"
