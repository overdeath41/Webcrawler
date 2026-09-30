/* WebCrawler — comportements de l'interface (sans dépendance) */
(function () {
  "use strict";

  // Ouverture des fenêtres en cascade
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce) {
    document.querySelectorAll(".window").forEach(function (w, i) {
      w.style.animationDelay = Math.min(i, 8) * 55 + "ms";
    });
  }

  // Fermeture des messages
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-dismiss]");
    if (btn) btn.closest(".message").remove();
  });

  // Confirmation des actions destructrices
  document.addEventListener("submit", function (e) {
    var msg = e.target.getAttribute("data-confirm");
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  // Horloge de session (fenêtre « Temps »)
  var clock = document.querySelector("[data-clock]");
  if (clock) {
    var pad = function (n) { return String(n).padStart(2, "0"); };
    var tick = function () {
      var d = new Date();
      clock.textContent = pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
    };
    tick();
    setInterval(tick, 1000);
  }

  // Compteur de lignes saisies dans le formulaire de mission
  var urlsField = document.querySelector("[data-url-counter]");
  if (urlsField) {
    var out = document.getElementById(urlsField.getAttribute("data-url-counter"));
    var max = parseInt(urlsField.getAttribute("data-max"), 10);
    var count = function () {
      var n = urlsField.value.split(/\s+|[,;](?=\s*https?:\/\/)/i).filter(Boolean).length;
      out.textContent = n + " / " + max + " URL" + (n > 1 ? "s" : "");
      out.classList.toggle("status-tag--error", n > max);
    };
    urlsField.addEventListener("input", count);
    count();
  }

  // Suivi en direct des missions actives (jauges ATB)
  var tracker = document.querySelector("[data-track-ids]");
  if (tracker) {
    var ids = tracker.getAttribute("data-track-ids");
    var endpoint = tracker.getAttribute("data-endpoint");
    var delay = 2500;

    var render = function (t) {
      document.querySelectorAll('[data-task="' + t.id + '"]').forEach(function (root) {
        var gauge = root.querySelector(".gauge");
        if (gauge) {
          gauge.style.setProperty("--value", t.progress + "%");
          gauge.classList.toggle("gauge--running", t.status === "running");
          gauge.classList.toggle("gauge--error", t.status === "error");
          gauge.classList.toggle("gauge--full", t.status === "done");
          gauge.setAttribute("aria-valuenow", t.progress);
        }
        root.querySelectorAll("[data-field]").forEach(function (el) {
          var f = el.getAttribute("data-field");
          if (f === "status") {
            el.textContent = t.status_label;
            el.className = "status-tag status-tag--" + t.status;
          } else if (f in t) {
            el.textContent = t[f];
          }
        });
      });
    };

    var poll = function () {
      fetch(endpoint + "?ids=" + encodeURIComponent(ids), {
        headers: { "Accept": "application/json" }, credentials: "same-origin"
      })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
        .then(function (data) {
          var stillActive = [];
          var finished = false;
          data.tasks.forEach(function (t) {
            render(t);
            if (t.status === "pending" || t.status === "running") stillActive.push(t.id);
            else finished = true;
          });
          if (finished) {
            // Une mission vient de se terminer : on recharge pour afficher
            // le bouton de téléchargement et le récapitulatif.
            setTimeout(function () { window.location.reload(); }, 900);
            return;
          }
          ids = stillActive.join(",");
          if (ids) setTimeout(poll, delay);
        })
        .catch(function () { setTimeout(poll, delay * 4); });
    };
    if (ids) setTimeout(poll, 1200);
  }
})();
