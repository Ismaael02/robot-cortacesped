/* ============================================================
   Robot de Césped — comportamiento
   1. Menú móvil
   2. Selector de robot
   3. Tabla comparativa (orden y filtros)
   ============================================================ */
(function () {
  "use strict";

  var eur = new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  });

  function esc(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ---------- 1. Menú móvil ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var mobileNav = document.getElementById("mobile-nav");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      toggle.setAttribute("aria-label", open ? "Abrir menú" : "Cerrar menú");
      mobileNav.hidden = open;
    });
  }

  /* ---------- 2. Selector ---------- */
  var dataEl = document.getElementById("models-data");
  var form = document.getElementById("calc-form");
  var out = document.getElementById("calc-result");

  if (dataEl && form && out) {
    var models = JSON.parse(dataEl.textContent);

    var scoreModel = function (m, area, slope, budget, cablePref) {
      var score = m.score;
      score += Math.min(6, Math.max(0, (m.pendiente - slope)) * 0.15);
      score -= Math.min(8, Math.max(0, (m.area - area) / Math.max(area, 1)) * 4);
      if (m.precio <= budget * 0.75) score += 3;
      if (cablePref === "no" && m.sinCable) score += 2;
      return score;
    };

    var render = function (matches, relaxed, area, slope, budget) {
      var note = "";
      if (relaxed.length) {
        note =
          '<p class="result-note"><strong>He tenido que flexibilizar una condición.</strong> ' +
          esc(relaxed.join(" ")) +
          " Si ninguna te encaja, sube el presupuesto o revisa la pendiente real del jardín.</p>";
      }

      var cards = matches
        .map(function (m, i) {
          var why = [];
          why.push("Cubre " + m.area + " m², frente a los " + area + " m² de tu jardín.");
          why.push("Aguanta hasta " + m.pendiente + "° de pendiente.");
          why.push(m.sinCable ? "Se instala sin cable perimetral." : "Usa cable perimetral.");
          if (m.precio <= budget) {
            why.push("Entra en tu presupuesto de " + eur.format(budget) + ".");
          }
          return (
            '<article class="result' + (i === 0 ? " result--first" : "") + '">' +
            '<p class="result__rank">' + (i === 0 ? "Mejor opción" : "Alternativa") + "</p>" +
            "<h3><a href=\"" + esc(m.url) + "\">" + esc(m.nombre) + "</a></h3>" +
            '<ul class="result__facts">' +
            '<li><span class="pill">' + m.area + " m²</span></li>" +
            '<li><span class="pill">' + m.pendiente + "°</span></li>" +
            '<li><span class="pill">' + esc(m.navegacion) + "</span></li>" +
            "</ul>" +
            '<p class="result__why">' + esc(why.join(" ")) + "</p>" +
            '<p class="result__price">' + eur.format(m.precio) + " <span class=\"muted small\">orientativo</span></p>" +
            '<a class="btn btn--small" href="' + esc(m.amazon) + '" target="_blank" rel="sponsored nofollow noopener">Ver precio en Amazon<span class="btn__arrow" aria-hidden="true">→</span></a>' +
            "</article>"
          );
        })
        .join("");

      out.innerHTML =
        '<div class="result-head"><h2>Tu recomendación</h2>' +
        '<p class="muted small">Calculada con ' + area + " m², " + slope + "° de pendiente y " +
        eur.format(budget) + " de presupuesto máximo.</p></div>" +
        note +
        '<div class="result-grid">' + cards + "</div>";
    };

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var area = Math.max(50, parseInt(document.getElementById("area").value, 10) || 0);
      var slope = parseInt(document.getElementById("pendiente").value, 10) || 15;
      var cablePref = document.getElementById("cable").value;
      var budget = Math.max(300, parseInt(document.getElementById("presupuesto").value, 10) || 3000);

      var relaxed = [];
      var requestedArea = area;
      var pool = models.filter(function (m) { return m.area >= area; });

      if (!pool.length) {
        var maxArea = models.reduce(function (a, m) { return Math.max(a, m.area); }, 0);
        relaxed.push(
          "Ningún modelo de la comparativa cubre " + requestedArea + " m². El de mayor superficie llega a " +
          maxArea + " m², así que te enseño las opciones más grandes."
        );
        area = maxArea;
        pool = models.filter(function (m) { return m.area >= maxArea; });
      }

      var bySlope = pool.filter(function (m) { return m.pendiente >= slope; });
      if (!bySlope.length) {
        var maxSlope = pool.reduce(function (a, m) { return Math.max(a, m.pendiente); }, 0);
        relaxed.push(
          "Ningún modelo de tu rango de superficie llega a " + slope + "° de pendiente. El máximo disponible es " +
          maxSlope + "°, así que te muestro los que más suben."
        );
        slope = maxSlope;
        bySlope = pool.filter(function (m) { return m.pendiente >= maxSlope; });
      }

      var byBudget = bySlope.filter(function (m) { return m.precio <= budget; });
      if (!byBudget.length) {
        var cheapest = bySlope.reduce(function (a, m) { return Math.min(a, m.precio); }, Infinity);
        relaxed.push(
          "El modelo más barato que cumple superficie y pendiente cuesta " + eur.format(cheapest) +
          ", por encima de tu presupuesto de " + eur.format(budget) + "."
        );
      }
      var final = byBudget.length ? byBudget : bySlope;

      if (cablePref === "no") {
        var noCable = final.filter(function (m) { return m.sinCable; });
        if (noCable.length) {
          final = noCable;
        } else {
          relaxed.push("No hay opciones sin cable para tu caso, así que incluyo modelos con cable.");
        }
      }

      final = final
        .map(function (m) {
          return { m: m, s: scoreModel(m, area, slope, budget, cablePref) };
        })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 2)
        .map(function (x) { return x.m; });

      render(final, relaxed, requestedArea, slope, budget);

      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        out.scrollIntoView();
      } else {
        out.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  /* ---------- 3. Tabla comparativa ---------- */
  var table = document.getElementById("compare-table");
  if (table) {
    var tbody = table.tBodies[0];
    var rows = Array.prototype.slice.call(tbody.rows);
    var dir = -1;

    table.querySelectorAll("thead button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var col = parseInt(btn.dataset.col, 10);
        dir = -dir;

        var ordered = rows.slice().sort(function (a, b) {
          if (col === 0) {
            return dir * a.cells[0].innerText.localeCompare(b.cells[0].innerText, "es");
          }
          var av = parseFloat(a.cells[col].dataset.sort) || 0;
          var bv = parseFloat(b.cells[col].dataset.sort) || 0;
          return dir * (av - bv);
        });

        ordered.forEach(function (r) { tbody.appendChild(r); });
        table.querySelectorAll("thead button").forEach(function (b) {
          b.removeAttribute("aria-sort");
        });
        btn.setAttribute("aria-sort", dir === 1 ? "ascending" : "descending");
      });
    });

    var onlyCableFree = document.getElementById("only-cablefree");
    var onlyUnder1000 = document.getElementById("only-under1000");

    var applyFilters = function () {
      rows.forEach(function (row) {
        var sinCable = parseFloat(row.cells[3].dataset.sort) === 1;
        var precio = parseFloat(row.cells[5].dataset.sort);
        var hide =
          (onlyCableFree.checked && !sinCable) ||
          (onlyUnder1000.checked && precio >= 1000);
        row.classList.toggle("is-hidden", hide);
      });
    };

    if (onlyCableFree) onlyCableFree.addEventListener("change", applyFilters);
    if (onlyUnder1000) onlyUnder1000.addEventListener("change", applyFilters);
  }
})();
