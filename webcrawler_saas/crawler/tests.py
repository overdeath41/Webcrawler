import http.server
import socket
import threading
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from netguard import BlockedURL, check_url, is_public_ip

from .models import CrawlTask, parse_urls
from .validators import validate_url_list

PUBLIC_DNS = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]


def fake_dns(ip):
    return mock.patch("netguard.socket.getaddrinfo",
                      return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))])


# ============================================================================
# Anti-SSRF
# ============================================================================
class NetguardTests(TestCase):
    def test_private_and_special_ips_are_blocked(self):
        for ip in ["127.0.0.1", "10.0.0.5", "172.17.0.2", "192.168.1.1", "169.254.169.254",
                   "100.64.0.1", "0.0.0.0", "::1", "fe80::1", "fc00::1", "::ffff:127.0.0.1",
                   "224.0.0.1", "not-an-ip"]:
            self.assertFalse(is_public_ip(ip), ip)

    def test_public_ips_are_allowed(self):
        for ip in ["93.184.216.34", "1.1.1.1", "2606:4700:4700::1111"]:
            self.assertTrue(is_public_ip(ip), ip)

    def test_literal_private_urls_rejected(self):
        for url in ["http://127.0.0.1/", "http://[::1]/", "http://169.254.169.254/latest/meta-data/",
                    "http://localhost/", "http://redis.localhost/", "http://192.168.1.1/admin"]:
            with self.assertRaises(BlockedURL, msg=url):
                check_url(url)

    def test_scheme_credentials_and_ports(self):
        for url in ["ftp://exemple.fr/", "file:///etc/passwd", "http://user:pw@exemple.fr/",
                    "http://exemple.fr:6379/", "http://exemple.fr:5432/"]:
            with fake_dns("93.184.216.34"), self.assertRaises(BlockedURL, msg=url):
                check_url(url)

    def test_hostname_resolving_to_private_ip_rejected(self):
        with fake_dns("10.1.2.3"), self.assertRaises(BlockedURL):
            check_url("https://intranet.exemple.fr/")

    def test_public_hostname_accepted(self):
        with fake_dns("93.184.216.34"):
            self.assertEqual(check_url("https://exemple.fr/page"), "https://exemple.fr/page")

    def test_unknown_domain(self):
        with mock.patch("netguard.socket.getaddrinfo", side_effect=socket.gaierror), \
                self.assertRaisesMessage(BlockedURL, "introuvable"):
            check_url("https://nexiste-pas.invalid/")


# ============================================================================
# Parsing et validation de la saisie
# ============================================================================
class UrlParsingTests(TestCase):
    def test_parse_urls_separators_and_duplicates(self):
        raw = "https://a.fr/1\nhttps://b.fr/2, https://c.fr/3;https://a.fr/1\n\n  https://d.fr/?x=1,2"
        self.assertEqual(parse_urls(raw), ["https://a.fr/1", "https://b.fr/2", "https://c.fr/3", "https://d.fr/?x=1,2"])

    @override_settings(MAX_URLS_PER_TASK=3)
    def test_too_many_urls(self):
        with self.assertRaisesMessage(ValidationError, "maximum est de 3"):
            validate_url_list("\n".join(f"https://ex{i}.fr/" for i in range(4)))

    def test_mixed_errors_are_all_reported(self):
        with mock.patch("netguard.socket.getaddrinfo", return_value=PUBLIC_DNS):
            with self.assertRaises(ValidationError) as ctx:
                validate_url_list("https://ok.fr/\nhttp://127.0.0.1/\npas-une-url")
        self.assertEqual(len(ctx.exception.messages), 2)


# ============================================================================
# Vues web
# ============================================================================
@mock.patch("crawler.views.run_crawl_task.delay")
@mock.patch("netguard.socket.getaddrinfo", return_value=PUBLIC_DNS)
class WebViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("marc", "marc@exemple.fr", "motdepasse-solide-42")
        self.other = User.objects.create_user("intrus", "i@exemple.fr", "motdepasse-solide-42")
        self.client.force_login(self.user)

    def test_pages_render(self, *_):
        CrawlTask.objects.create(user=self.user, urls="https://a.fr/")
        for name in ["dashboard"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.client.logout()
        for name in ["home", "login", "register"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        for slug in ["cgu", "confidentialite", "utilisation-responsable"]:
            resp = self.client.get(reverse("legal", args=[slug]))
            self.assertContains(resp, "<h2")

    def test_task_detail_renders_for_every_status(self, *_):
        for status, _label in CrawlTask.Status.choices:
            task = CrawlTask.objects.create(user=self.user, urls="https://a.fr/\nhttps://b.fr/", status=status,
                                            error_message="boom" if status == "error" else "")
            resp = self.client.get(reverse("task-detail-web", args=[task.pk]))
            self.assertContains(resp, task.display_name)

    def test_create_task_launches_after_commit(self, _dns, delay):
        with self.captureOnCommitCallbacks(execute=True):
            resp = self.client.post(reverse("create-task-web"), {"urls": "https://a.fr/\nhttps://b.fr/", "name": "Veille"})
        task = CrawlTask.objects.get()
        self.assertRedirects(resp, reverse("task-detail-web", args=[task.pk]))
        self.assertEqual(task.urls_count, 2)
        delay.assert_called_once_with(task.pk)

    def test_invalid_urls_create_nothing(self, _dns, delay):
        resp = self.client.post(reverse("create-task-web"), {"urls": "http://127.0.0.1/\nhttp://exemple.fr:6379/"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Adresse interne ou privée interdite")
        self.assertContains(resp, "Port 6379 non autorisé")
        self.assertFalse(CrawlTask.objects.exists())
        delay.assert_not_called()

    @override_settings(MAX_URLS_PER_TASK=2)
    def test_too_many_urls_create_nothing(self, *_):
        self.client.post(reverse("create-task-web"), {"urls": "https://a.fr/\nhttps://b.fr/\nhttps://c.fr/"})
        self.assertFalse(CrawlTask.objects.exists())

    @override_settings(MAX_ACTIVE_TASKS_PER_USER=1)
    def test_active_task_limit(self, *_):
        CrawlTask.objects.create(user=self.user, urls="https://a.fr/", status="running")
        resp = self.client.post(reverse("create-task-web"), {"urls": "https://b.fr/"})
        self.assertContains(resp, "missions en attente ou en cours")
        self.assertEqual(CrawlTask.objects.count(), 1)

    def test_isolation_between_users(self, *_):
        task = CrawlTask.objects.create(user=self.other, urls="https://a.fr/")
        task.result_file.save("secret.csv", ContentFile(b"url\nx\n"))
        for name in ["task-detail-web", "task-download"]:
            self.assertEqual(self.client.get(reverse(name, args=[task.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("task-delete", args=[task.pk])).status_code, 404)
        data = self.client.get(reverse("tasks-status"), {"ids": str(task.pk)}).json()
        self.assertEqual(data["tasks"], [])
        task.result_file.delete()

    def test_download_owner_only(self, *_):
        task = CrawlTask.objects.create(user=self.user, urls="https://a.fr/", status="done")
        task.result_file.save("r.csv", ContentFile("url;title\nhttps://a.fr/;Été\n".encode("utf-8-sig")))
        resp = self.client.get(reverse("task-download", args=[task.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp["Content-Disposition"])
        task.result_file.delete()

    def test_status_endpoint(self, *_):
        task = CrawlTask.objects.create(user=self.user, urls="https://a.fr/\nhttps://b.fr/", status="running", urls_done=1)
        data = self.client.get(reverse("tasks-status"), {"ids": f"{task.pk}"}).json()
        self.assertEqual(data["tasks"][0]["progress"], 50)

    def test_relaunch_and_delete(self, _dns, delay):
        task = CrawlTask.objects.create(user=self.user, urls="https://a.fr/", status="done", name="X")
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("task-relaunch", args=[task.pk]))
        self.assertEqual(CrawlTask.objects.filter(name="X").count(), 2)
        delay.assert_called_once()
        self.client.post(reverse("task-delete", args=[task.pk]))
        self.assertFalse(CrawlTask.objects.filter(pk=task.pk).exists())

    def test_logout_is_post(self, *_):
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("home"))


class AuthTests(TestCase):
    def setUp(self):
        cache.clear()
        User.objects.create_user("marc", "marc@exemple.fr", "motdepasse-solide-42")

    def test_register(self):
        resp = self.client.post(reverse("register"), {
            "username": "lea", "email": "lea@exemple.fr",
            "password1": "un-mot-de-passe-long", "password2": "un-mot-de-passe-long",
        })
        self.assertRedirects(resp, reverse("dashboard"))

    def test_register_duplicate_email(self):
        resp = self.client.post(reverse("register"), {
            "username": "autre", "email": "MARC@exemple.fr",
            "password1": "un-mot-de-passe-long", "password2": "un-mot-de-passe-long",
        })
        self.assertContains(resp, "existe déjà")

    @override_settings(LOGIN_MAX_ATTEMPTS=3)
    def test_login_rate_limit(self):
        for _ in range(3):
            self.assertEqual(self.client.post(reverse("login"), {"username": "marc", "password": "faux"}).status_code, 200)
        resp = self.client.post(reverse("login"), {"username": "marc", "password": "motdepasse-solide-42"})
        self.assertEqual(resp.status_code, 429)
        self.assertContains(resp, "Trop de tentatives", status_code=429)

    def test_login_success_resets_counter(self):
        self.client.post(reverse("login"), {"username": "marc", "password": "faux"})
        resp = self.client.post(reverse("login"), {"username": "marc", "password": "motdepasse-solide-42"})
        self.assertRedirects(resp, reverse("dashboard"))


# ============================================================================
# API REST
# ============================================================================
@mock.patch("crawler.views.run_crawl_task.delay")
@mock.patch("netguard.socket.getaddrinfo", return_value=PUBLIC_DNS)
class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("api", "api@exemple.fr", "motdepasse-solide-42")
        self.client.force_login(self.user)

    def test_create_and_list(self, *_):
        resp = self.client.post(reverse("api-tasks"), {"urls": "https://a.fr/\nhttps://b.fr/"}, content_type="application/json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["urls_count"], 2)
        listing = self.client.get(reverse("api-tasks")).json()
        self.assertEqual(listing["count"], 1)

    def test_api_blocks_ssrf(self, *_):
        resp = self.client.post(reverse("api-tasks"), {"urls": "http://10.0.0.1/"}, content_type="application/json")
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(CrawlTask.objects.exists())

    def test_requires_auth(self, *_):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("api-tasks")).status_code, 403)


# ============================================================================
# Crawl de bout en bout (Scrapy réel contre un serveur HTTP local)
# ============================================================================
PAGE = """<html><head><title>Produit test</title>
<meta name="description" content="Une   description"></head>
<body><h1>Super produit</h1><span class="price">1 299,00 €</span>
<a href="/a">a</a><a href="/b">b</a></body></html>"""


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/robots.txt":
            body, code = b"User-agent: *\nDisallow: /prive\n", 200
        elif self.path.startswith("/prive"):
            body, code = b"secret", 200
        elif self.path == "/absent":
            body, code = b"nope", 404
        else:
            body, code = PAGE.encode(), 200
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8" if code == 200 else "text/plain")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@override_settings(CRAWL_DELAY=0)
class EndToEndCrawlTests(TransactionTestCase):
    def test_real_crawl(self):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        user = User.objects.create_user("e2e", "e@exemple.fr", "x-motdepasse-42")
        base = f"http://127.0.0.1:{port}"
        task = CrawlTask.objects.create(user=user, urls=f"{base}/produit\n{base}/prive\n{base}/absent")

        from .tasks import run_crawl_task
        # Le serveur de test est en 127.0.0.1 : on lève exceptionnellement la protection.
        with mock.patch.dict("os.environ", {"ALLOW_PRIVATE_TARGETS": "true"}):
            run_crawl_task.apply(args=[task.pk])
        server.shutdown()

        task.refresh_from_db()
        self.assertEqual(task.status, "done", task.error_message)
        self.assertEqual((task.urls_done, task.urls_failed, task.items_scraped), (3, 2, 3))
        content = task.result_file.read().decode("utf-8-sig")
        self.assertIn("url;status_code;title", content)
        self.assertIn("Produit test", content)
        self.assertIn("1299.00 €", content)
        self.assertIn("robots.txt", content)
        self.assertIn("Erreur HTTP 404", content)
        task.result_file.delete()

    def test_ssrf_blocked_inside_scrapy(self):
        """Même si une URL interne arrivait jusqu'au crawler, Scrapy la refuse."""
        user = User.objects.create_user("e2e2", "e2@exemple.fr", "x-motdepasse-42")
        task = CrawlTask.objects.create(user=user, urls="http://127.0.0.1:80/\nhttp://169.254.169.254/latest/")
        from .tasks import run_crawl_task
        with mock.patch.dict("os.environ", {"ALLOW_PRIVATE_TARGETS": "false"}):
            run_crawl_task.apply(args=[task.pk])
        task.refresh_from_db()
        self.assertEqual(task.status, "done", task.error_message)
        self.assertEqual(task.urls_failed, 2)
        self.assertIn("adresse interne", task.result_file.read().decode("utf-8-sig"))
        task.result_file.delete()
