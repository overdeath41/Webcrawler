from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CrawlTask
from .serializers import CrawlTaskSerializer, CrawlTaskCreateSerializer
from .tasks import run_crawl_task

# ==================== VUES WEB ====================

def home(request):
    """Page d'accueil"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crawler/home.html')


def register(request):
    """Inscription utilisateur"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès !')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'crawler/register.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard utilisateur avec liste des tâches"""
    tasks = CrawlTask.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'tasks': tasks,
        'pending_count': tasks.filter(status='pending').count(),
        'running_count': tasks.filter(status='running').count(),
        'done_count': tasks.filter(status='done').count(),
        'error_count': tasks.filter(status='error').count(),
    }
    
    return render(request, 'crawler/dashboard.html', context)


@login_required
def create_task_view(request):
    """Vue pour créer une nouvelle tâche de crawl"""
    if request.method == 'POST':
        urls = request.POST.get('urls', '')
        
        if not urls.strip():
            messages.error(request, "Veuillez fournir au moins une URL")
            return redirect('dashboard')
        
        try:
            # Créer la tâche
            task = CrawlTask.objects.create(
                user=request.user,
                urls=urls
            )
            
            # Valider le nombre d'URLs
            task.validate_urls_count()
            
            # Lancer la tâche Celery
            run_crawl_task.delay(task.id)
            
            messages.success(request, f'Tâche #{task.id} créée et lancée !')
            return redirect('dashboard')
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
            return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def task_detail(request, task_id):
    """Détails d'une tâche"""
    task = get_object_or_404(CrawlTask, id=task_id, user=request.user)
    return render(request, 'crawler/task_detail.html', {'task': task})


# ==================== API REST ====================

class CrawlTaskListCreate(generics.ListCreateAPIView):
    """
    GET: Liste les tâches de l'utilisateur
    POST: Crée une nouvelle tâche et la lance
    """
    serializer_class = CrawlTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CrawlTask.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CrawlTaskCreateSerializer
        return CrawlTaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        # Lancer la tâche Celery de manière asynchrone
        run_crawl_task.delay(task.id)


class CrawlTaskDetail(generics.RetrieveAPIView):
    """
    GET: Récupère les détails d'une tâche
    """
    serializer_class = CrawlTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CrawlTask.objects.filter(user=self.request.user)