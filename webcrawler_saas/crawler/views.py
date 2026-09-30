import logging
from pathlib import Path

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError as DRFValidationError

from . import ratelimit
from .forms import CrawlTaskForm, RegisterForm
from .models import CrawlTask
from .serializers import CrawlTaskCreateSerializer, CrawlTaskSerializer
from .tasks import run_crawl_task

logger = logging.getLogger(__name__)

HISTORY_SIZE = 50


# ============================================================================
# Utilitaires
# ============================================================================
def active_tasks_count(user):
    return CrawlTask.objects.filter(user=user, status__in=CrawlTask.ACTIVE_STATUSES).count()


def check_active_limit(user):
    limit = settings.MAX_ACTIVE_TASKS_PER_USER
    if active_tasks_count(user) >= limit:
        raise ValidationError(
            f"Vous avez déjà {limit} missions en attente ou en cours. "
            "Attendez qu'une mission se termine avant d'en lancer une nouvelle."
        )


def launch(task):
    """Envoie la tâche à Celery une fois la transaction validée (pas de course)."""
    transaction.on_commit(lambda: run_crawl_task.delay(task.pk))


def task_payload(task):
    return {
        "id": task.pk,
        "status": task.status,
        "status_label": task.get_status_display(),
        "urls_count": task.urls_count,
        "urls_done": task.urls_done,
        "urls_failed": task.urls_failed,
        "items_scraped": task.items_scraped,
        "progress": task.progress_percent,
        "duration": task.duration_display,
        "has_result": bool(task.result_file),
    }


# ============================================================================
# Pages publiques
# ============================================================================
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "crawler/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Compte créé. Bienvenue !")
        return redirect("dashboard")
    return render(request, "crawler/register.html", {"form": form})


class ThrottledLoginView(LoginView):
    """Connexion avec blocage temporaire après trop d'échecs (IP et identifiant)."""

    template_name = "crawler/login.html"
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "")
        if ratelimit.is_locked(request, username):
            minutes = max(1, settings.LOGIN_LOCKOUT_SECONDS // 60)
            logger.warning("Connexion bloquée (rate limit) ip=%s", ratelimit.client_ip(request))
            form = self.get_form()
            form.add_error(None, f"Trop de tentatives. Réessayez dans {minutes} minutes.")
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        ratelimit.register_failure(self.request, self.request.POST.get("username", ""))
        return super().form_invalid(form)

    def form_valid(self, form):
        ratelimit.reset(self.request, self.request.POST.get("username", ""))
        return super().form_valid(form)


LEGAL_PAGES = {
    "cgu": ("CGU.md", "Conditions générales d'utilisation"),
    "confidentialite": ("POLITIQUE_CONFIDENTIALITE.md", "Politique de confidentialité"),
    "utilisation-responsable": ("UTILISATION_RESPONSABLE.md", "Utilisation responsable"),
}


def legal_page(request, slug):
    if slug not in LEGAL_PAGES:
        raise Http404
    filename, title = LEGAL_PAGES[slug]
    path = Path(settings.LEGAL_DOCS_DIR) / filename
    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise Http404 from exc
    # Contenu rédigé par l'éditeur du site (fichiers du dépôt), pas par les utilisateurs.
    html = markdown.markdown(source, extensions=["tables", "sane_lists"])
    return render(request, "crawler/legal.html", {"title": title, "content": mark_safe(html)})


@require_GET
def healthz(request):
    return JsonResponse({"status": "ok"})


# ============================================================================
# Espace connecté
# ============================================================================
@login_required
def dashboard(request, form=None):
    qs = CrawlTask.objects.filter(user=request.user)
    counts = qs.aggregate(
        pending=Count("id", filter=Q(status=CrawlTask.Status.PENDING)),
        running=Count("id", filter=Q(status=CrawlTask.Status.RUNNING)),
        done=Count("id", filter=Q(status=CrawlTask.Status.DONE)),
        error=Count("id", filter=Q(status=CrawlTask.Status.ERROR)),
        total=Count("id"),
    )
    tasks = list(qs[:HISTORY_SIZE])
    context = {
        "tasks": tasks,
        "counts": counts,
        "form": form or CrawlTaskForm(),
        "active_ids": ",".join(str(t.pk) for t in tasks if t.is_active),
        "max_active": settings.MAX_ACTIVE_TASKS_PER_USER,
    }
    return render(request, "crawler/dashboard.html", context)


@login_required
@require_POST
def create_task_view(request):
    form = CrawlTaskForm(request.POST)
    if form.is_valid():
        try:
            check_active_limit(request.user)
        except ValidationError as exc:
            form.add_error(None, exc)
    if not form.is_valid():
        # On réaffiche le tableau de bord avec la saisie et les erreurs : rien n'est créé.
        return dashboard(request, form=form)

    task = CrawlTask.objects.create(
        user=request.user,
        name=form.cleaned_data["name"],
        urls=form.cleaned_data["urls"],
    )
    launch(task)
    messages.success(request, f"{task.display_name} lancée : {task.urls_count} URL(s) en file d'attente.")
    return redirect("task-detail-web", task_id=task.pk)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(CrawlTask, pk=task_id, user=request.user)
    return render(request, "crawler/task_detail.html", {"task": task})


@login_required
@require_POST
def task_relaunch(request, task_id):
    source = get_object_or_404(CrawlTask, pk=task_id, user=request.user)
    try:
        # Les URLs sont revalidées : les règles ont pu changer depuis.
        urls = CrawlTaskForm({"name": source.name, "urls": source.urls})
        if not urls.is_valid():
            raise ValidationError(urls.errors.get("urls") or "URLs invalides.")
        check_active_limit(request.user)
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
        return redirect("task-detail-web", task_id=source.pk)

    task = CrawlTask.objects.create(user=request.user, name=source.name, urls=urls.cleaned_data["urls"])
    launch(task)
    messages.success(request, f"Mission relancée : {task.display_name}.")
    return redirect("task-detail-web", task_id=task.pk)


@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(CrawlTask, pk=task_id, user=request.user)
    if task.status == CrawlTask.Status.RUNNING:
        messages.error(request, "Une mission en cours ne peut pas être supprimée.")
        return redirect("task-detail-web", task_id=task.pk)
    name = task.display_name
    if task.result_file:
        task.result_file.delete(save=False)
    task.delete()
    messages.success(request, f"{name} supprimée.")
    return redirect("dashboard")


@login_required
def task_download(request, task_id):
    """Téléchargement du CSV : uniquement pour son propriétaire (jamais d'URL publique)."""
    task = get_object_or_404(CrawlTask, pk=task_id, user=request.user)
    if not task.result_file:
        raise Http404("Aucun résultat pour cette mission.")
    try:
        handle = task.result_file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("Fichier expiré ou supprimé.") from exc
    filename = f"webcrawler_mission_{task.pk}_{task.created_at:%Y%m%d}.csv"
    return FileResponse(handle, as_attachment=True, filename=filename, content_type="text/csv")


@login_required
@require_GET
def tasks_status(request):
    """Progression des missions (polling léger du tableau de bord)."""
    try:
        ids = [int(i) for i in request.GET.get("ids", "").split(",") if i][:HISTORY_SIZE]
    except ValueError:
        return JsonResponse({"error": "ids invalides"}, status=400)
    tasks = CrawlTask.objects.filter(user=request.user, pk__in=ids)
    return JsonResponse({"tasks": [task_payload(t) for t in tasks]})


# ============================================================================
# API REST
# ============================================================================
class CrawlTaskListCreate(generics.ListCreateAPIView):
    """GET : liste des missions — POST : création + lancement."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CrawlTask.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return CrawlTaskCreateSerializer if self.request.method == "POST" else CrawlTaskSerializer

    def perform_create(self, serializer):
        try:
            check_active_limit(self.request.user)
        except ValidationError as exc:
            raise DRFValidationError({"detail": exc.messages}) from exc
        task = serializer.save(user=self.request.user)
        launch(task)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        task = CrawlTask.objects.get(pk=response.data["id"])
        response.data = CrawlTaskSerializer(task, context={"request": request}).data
        return response


class CrawlTaskDetail(generics.RetrieveAPIView):
    serializer_class = CrawlTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CrawlTask.objects.filter(user=self.request.user)
