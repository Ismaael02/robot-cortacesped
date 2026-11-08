#!/usr/bin/env python3
"""
Generador estatico de robotdecesped.es
Sin dependencias externas. Ejecutar:  python build.py
Salida: carpeta dist/ lista para publicar.
"""
from __future__ import annotations

import json
import html
import shutil
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
DATA = ROOT / "data"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
MODELS = json.loads((DATA / "models.json").read_text(encoding="utf-8"))

# Permite compilar para distintos hostings sin tocar el JSON.
import os

if os.environ.get("SITE_DOMAIN"):
    SITE["dominio"] = os.environ["SITE_DOMAIN"]
if "SITE_BASE_PATH" in os.environ:
    SITE["base_path"] = os.environ["SITE_BASE_PATH"]

ORIGIN = SITE["dominio"].rstrip("/")
BASE_PATH = (SITE.get("base_path") or "").rstrip("/")
BASE = ORIGIN + BASE_PATH
YEAR = SITE["anio"]


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def eur(value: int) -> str:
    return f"{value:,.0f}".replace(",", ".") + " €"


def url(path: str) -> str:
    return BASE + path


def rebase(html_text: str) -> str:
    """Prefija los enlaces internos cuando el sitio se publica en un subdirectorio
    (por ejemplo GitHub Pages: usuario.github.io/repositorio)."""
    if not BASE_PATH:
        return html_text
    return (
        html_text.replace('href="/', f'href="{BASE_PATH}/')
        .replace('src="/', f'src="{BASE_PATH}/')
    )


def amazon_url(model: dict) -> str:
    tag = (SITE.get("amazon_tag") or "").strip()
    valid_tag = tag and not tag.upper().startswith("PENDIENTE")
    if model.get("amazon_asin"):
        base_url = f"https://www.amazon.es/dp/{model['amazon_asin']}/"
    else:
        base_url = f"https://www.amazon.es/s?k={model['nombre'].replace(' ', '+')}"
    return f"{base_url}?tag={tag}" if valid_tag else base_url


def cta(model: dict, label: str = "Ver precio en Amazon", small: bool = False) -> str:
    cls = "btn btn--small" if small else "btn"
    return (
        f'<a class="{cls}" href="{esc(amazon_url(model))}" target="_blank" '
        f'rel="sponsored nofollow noopener">{esc(label)}'
        f'<span class="btn__arrow" aria-hidden="true">→</span></a>'
    )


def jsonld(obj: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def layout(title: str, description: str, path: str, body: str, head_extra: str = "") -> str:
    canonical = url(path)
    nav = "".join(
        f'<a href="{esc(item["href"])}"{" aria-current=\"page\"" if item["href"] == path else ""}>{esc(item["texto"])}</a>'
        for item in SITE["nav"]
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE['nombre'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/static/style.css">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
{head_extra}
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="{esc(SITE['nombre'])} — inicio">
      <span class="brand__mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20h18"/><path d="M5 20V9l7-5 7 5v11"/><path d="M9 20v-6h6v6"/><path d="M2 9l3-2 3 2"/></svg>
      </span>
      <span class="brand__text">{esc(SITE['nombre'])}</span>
    </a>
    <nav class="nav" aria-label="Principal">{nav}</nav>
    <button class="nav-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="Abrir menú">
      <span></span><span></span><span></span>
    </button>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Menú móvil" hidden>{nav}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-brand">{esc(SITE['nombre'])}</p>
      <p class="muted small">{esc(SITE['tagline'])}</p>
    </div>
    <nav aria-label="Legal" class="footer-links">
      <a href="/aviso-legal/">Aviso legal</a>
      <a href="/privacidad/">Privacidad</a>
      <a href="/cookies/">Cookies</a>
      <a href="/afiliados/">Afiliados</a>
    </nav>
  </div>
  <div class="wrap">
    <p class="disclosure small">{esc(SITE['aviso_afiliados'])}</p>
    <p class="muted small">© {YEAR} {esc(SITE['nombre'])}. Todos los derechos reservados.</p>
  </div>
</footer>
<script src="/static/app.js" defer></script>
</body>
</html>"""


# --------------------------------------------------------------------------
# Componentes
# --------------------------------------------------------------------------
def model_card(m: dict, index: int | None = None) -> str:
    ribbon = '<span class="card__ribbon">Recomendado</span>' if m.get("destacado") else ""
    nav_badge = "Sin cable" if m["sin_cable"] else "Con cable"
    num = f'<span class="card__num">{index:02d}</span>' if index else ""
    return f"""
<article class="card">
  {ribbon}
  {num}
  <div class="card__head">
    <p class="card__brand">{esc(m['marca'])}</p>
    <h3 class="card__title"><a href="/modelos/{esc(m['id'])}/">{esc(m['nombre'])}</a></h3>
  </div>
  <ul class="specs">
    <li><span>Superficie</span><strong>{m['area_max']} m²</strong></li>
    <li><span>Pendiente</span><strong>{m['pendiente_max']}°</strong></li>
    <li><span>Instalación</span><strong>{nav_badge}</strong></li>
    <li><span>Precio desde</span><strong>{eur(m['precio'])}</strong></li>
  </ul>
  <p class="card__ideal">{esc(m['ideal_para'])}</p>
  {cta(m, small=True)}
</article>"""


def spec_table(m: dict) -> str:
    rows = [
        ("Marca", m["marca"]),
        ("Superficie máxima", f"{m['area_max']} m²"),
        ("Pendiente máxima", f"{m['pendiente_max']}°"),
        ("Navegación", m["navegacion"]),
        ("Instalación", "Sin cable perimetral" if m["sin_cable"] else "Con cable perimetral"),
        ("Ancho de corte", f"{m['ancho_corte']} cm"),
        ("Aplicación móvil", "Sí" if m["app"] else "No"),
        ("Nivel sonoro", f"{m['ruido_db']} dB"),
        ("Peso", f"{m['peso']} kg"),
        ("Batería", m["bateria"]),
        ("Garantía", f"{m['garantia']} años"),
        ("Precio orientativo", eur(m["precio"])),
    ]
    body = "".join(f"<tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in rows)
    return f'<table class="spec-table"><tbody>{body}</tbody></table>'


def pros_cons(m: dict) -> str:
    pros = "".join(f"<li>{esc(p)}</li>" for p in m["pros"])
    contras = "".join(f"<li>{esc(c)}</li>" for c in m["contras"])
    return f"""
<div class="proscons">
  <div class="proscons__col proscons__col--good">
    <h3>Puntos fuertes</h3>
    <ul class="tick">{pros}</ul>
  </div>
  <div class="proscons__col proscons__col--bad">
    <h3>A tener en cuenta</h3>
    <ul class="cross">{contras}</ul>
  </div>
</div>"""


def breadcrumbs(items: list[tuple[str, str]]) -> str:
    parts = ['<a href="/">Inicio</a>']
    for label, href in items:
        parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    body = " <span aria-hidden=\"true\">/</span> ".join(parts)
    ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label, "item": url(href)}
            for i, (label, href) in enumerate(items)
        ],
    }
    return f'<nav class="crumbs small" aria-label="Ruta de navegación">{body}</nav>' + jsonld(ld)


# --------------------------------------------------------------------------
# Paginas
# --------------------------------------------------------------------------
def page_home() -> str:
    top = sorted(MODELS, key=lambda m: m["score_base"], reverse=True)[:3]
    cards = "".join(model_card(m, i + 1) for i, m in enumerate(top))
    cheapest = min(MODELS, key=lambda m: m["precio"])
    biggest = max(MODELS, key=lambda m: m["area_max"])
    body = f"""
<section class="hero">
  <div class="wrap hero__inner">
    <p class="eyebrow">Guía independiente · Actualizada {YEAR}</p>
    <h1>Tu jardín se corta solo.<br><span class="hl">Tú eliges el robot.</span></h1>
    <p class="lead">Comparativas honestas y un selector gratuito que te dice qué robot cortacésped necesita tu jardín según metros, pendiente y presupuesto. Sin cable, sin humo y sin comisiones escondidas.</p>
    <div class="hero__actions">
      <a class="btn btn--big" href="/calculadora/">Usar el selector<span class="btn__arrow" aria-hidden="true">→</span></a>
      <a class="btn btn--ghost btn--big" href="/comparativa/">Ver los 12 modelos</a>
    </div>
    <dl class="hero__stats">
      <div><dt>Modelos analizados</dt><dd>{len(MODELS)}</dd></div>
      <div><dt>Superficie cubierta</dt><dd>500–3.000 m²</dd></div>
      <div><dt>Precio de entrada</dt><dd>{eur(cheapest['precio'])}</dd></div>
    </dl>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <h2>Los tres que más recomendamos</h2>
      <p class="muted">Elegidos por equilibrio entre superficie, pendiente y precio. No por comisión.</p>
    </div>
    <div class="cards">{cards}</div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap split">
    <div>
      <p class="eyebrow">El error más caro</p>
      <h2>Comprar por metros y olvidar la pendiente</h2>
      <p>El 80% de las devoluciones de robots cortacésped tienen el mismo motivo: el robot no sube el talud del jardín. La ficha del fabricante dice «hasta 35°», pero eso solo se cumple con el césped seco, la batería llena y las ruedas limpias.</p>
      <p>Nuestro selector aplica un margen de seguridad del 20% sobre la superficie y filtra por pendiente real antes de recomendarte nada.</p>
      <a class="link-arrow" href="/guia-de-compra/">Leer la guía completa<span aria-hidden="true">→</span></a>
    </div>
    <aside class="callout">
      <p class="callout__kicker">Dato rápido</p>
      <p class="callout__big">{biggest['area_max']} m²</p>
      <p class="muted small">es la superficie máxima que cubre un solo robot de nuestra comparativa: el {esc(biggest['nombre'])}.</p>
    </aside>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <h2>Empieza por aquí</h2>
      <p class="muted">Tres formas de llegar a tu modelo, según cuánto tiempo quieras dedicarle.</p>
    </div>
    <div class="paths">
      <a class="path" href="/calculadora/">
        <span class="path__icon" aria-hidden="true">1</span>
        <h3>Tengo prisa</h3>
        <p>Responde cuatro preguntas y te digo los dos modelos que mejor encajan. Dos minutos.</p>
        <span class="link-arrow">Abrir el selector<span aria-hidden="true">→</span></span>
      </a>
      <a class="path" href="/comparativa/">
        <span class="path__icon" aria-hidden="true">2</span>
        <h3>Quiero comparar</h3>
        <p>Tabla completa con superficie, pendiente, navegación y precio de los 12 modelos.</p>
        <span class="link-arrow">Ver la tabla<span aria-hidden="true">→</span></span>
      </a>
      <a class="path" href="/guia-de-compra/">
        <span class="path__icon" aria-hidden="true">3</span>
        <h3>Quiero entenderlo</h3>
        <p>Cable o sin cable, GPS o LiDAR, cuánto cuesta al año y qué errores evitar.</p>
        <span class="link-arrow">Leer la guía<span aria-hidden="true">→</span></span>
      </a>
    </div>
  </div>
</section>
"""
    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE["nombre"],
        "url": BASE,
        "description": SITE["descripcion"],
        "inLanguage": "es-ES",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{BASE}/comparativa/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    })
    return layout(
        f"{SITE['nombre']} — Comparativa y selector de robots cortacésped",
        "Comparativa independiente de robots cortacésped y selector gratuito por metros, pendiente y presupuesto. Descubre qué modelo necesita tu jardín.",
        "/",
        body,
        ld,
    )


def page_calculadora() -> str:
    payload = [
        {
            "id": m["id"],
            "nombre": m["nombre"],
            "marca": m["marca"],
            "precio": m["precio"],
            "area": m["area_max"],
            "pendiente": m["pendiente_max"],
            "sinCable": m["sin_cable"],
            "navegacion": m["navegacion"],
            "score": m["score_base"],
            "ideal": m["ideal_para"],
            "url": f"{BASE_PATH}/modelos/{m['id']}/",
            "amazon": amazon_url(m),
        }
        for m in MODELS
    ]
    body = f"""
{breadcrumbs([("Calculadora", "/calculadora/")])}
<section class="section section--tight">
  <div class="wrap narrow">
    <p class="eyebrow">Selector gratuito</p>
    <h1>¿Qué robot cortacésped necesita tu jardín?</h1>
    <p class="lead">Cuatro datos. Cero registro. Te devuelvo los dos modelos que mejor encajan y por qué.</p>

    <form class="calc" id="calc-form" novalidate>
      <div class="field">
        <label for="area">Superficie de césped <span class="hint">en metros cuadrados</span></label>
        <input type="number" id="area" name="area" min="50" max="5000" step="10" value="400" inputmode="numeric" required>
        <p class="field__help">Mide solo la zona de césped, no la parcela entera. Si tienes varias zonas separadas, súmalas.</p>
      </div>

      <div class="field">
        <label for="pendiente">Pendiente del jardín</label>
        <select id="pendiente" name="pendiente">
          <option value="15">Llano o casi llano (menos de 15°)</option>
          <option value="30" selected>Con algún desnivel (hasta 30°)</option>
          <option value="45">Taludes pronunciados (más de 30°)</option>
        </select>
      </div>

      <div class="field">
        <label for="cable">¿Quieres enterrar cable perimetral?</label>
        <select id="cable" name="cable">
          <option value="no" selected>No, prefiero instalación sin cable</option>
          <option value="da-igual">Me da igual, quiero la mejor opción</option>
          <option value="si">Sí, no me importa instalar cable</option>
        </select>
      </div>

      <div class="field">
        <label for="presupuesto">Presupuesto máximo <span class="hint">precio de compra</span></label>
        <input type="number" id="presupuesto" name="presupuesto" min="300" max="5000" step="100" value="1500" inputmode="numeric">
        <p class="field__help">Sin contar instalación ni accesorios. Los precios bajan bastante en temporada baja (otoño e invierno).</p>
      </div>

      <button class="btn btn--big btn--full" type="submit">Ver mi recomendación<span class="btn__arrow" aria-hidden="true">→</span></button>
    </form>

    <div id="calc-result" class="calc-result" aria-live="polite"></div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap narrow">
    <h2>Cómo se calcula la recomendación</h2>
    <p>No es una lista pagada. El selector aplica tres filtros duros y luego ordena por puntuación técnica:</p>
    <ol class="steps">
      <li><strong>Superficie con margen.</strong> Descartamos todo robot cuya superficie máxima sea inferior a la tuya. Un robot al 100% de su capacidad corta peor y se desgasta antes.</li>
      <li><strong>Pendiente real.</strong> Filtramos por el ángulo que declares. Si tu jardín tiene taludes, los modelos sin tracción suficiente desaparecen.</li>
      <li><strong>Presupuesto y cable.</strong> Aplicamos tu límite de precio y tu preferencia de instalación.</li>
    </ol>
    <p class="muted small">Si ningún modelo cumple todo, el selector te lo dice y te enseña la opción más cercana, indicando qué condición has de ceder.</p>
  </div>
</section>
<script type="application/json" id="models-data">{json.dumps(payload, ensure_ascii=False)}</script>
"""
    return layout(
        "Calculadora: qué robot cortacésped necesito | " + SITE["nombre"],
        "Selector gratuito de robot cortacésped. Indica metros de césped, pendiente y presupuesto y obtén una recomendación razonada al instante.",
        "/calculadora/",
        body,
    )


def page_comparativa() -> str:
    rows = ""
    for m in sorted(MODELS, key=lambda x: x["score_base"], reverse=True):
        cable = "Sin cable" if m["sin_cable"] else "Con cable"
        rows += f"""
    <tr>
      <td class="c-name"><a href="/modelos/{esc(m['id'])}/">{esc(m['nombre'])}</a><span class="c-brand">{esc(m['marca'])}</span></td>
      <td data-sort="{m['area_max']}">{m['area_max']} m²</td>
      <td data-sort="{m['pendiente_max']}">{m['pendiente_max']}°</td>
      <td data-sort="{1 if m['sin_cable'] else 0}">{cable}</td>
      <td data-sort="0">{esc(m['navegacion'])}</td>
      <td data-sort="{m['precio']}">{eur(m['precio'])}</td>
      <td data-sort="{m['score_base']}"><span class="score">{m['score_base']}</span></td>
      <td class="c-cta">{cta(m, 'Ver precio', small=True)}</td>
    </tr>"""
    body = f"""
{breadcrumbs([("Comparativa", "/comparativa/")])}
<section class="section section--tight">
  <div class="wrap">
    <p class="eyebrow">Comparativa {YEAR}</p>
    <h1>Los 12 robots cortacésped que merecen la pena</h1>
    <p class="lead">Ordenados por puntuación técnica, no por precio ni por comisión. Pulsa cualquier cabecera para reordenar.</p>
    <p class="muted small">{esc(SITE['nota_precios'])}</p>

    <div class="table-tools">
      <label class="switch">
        <input type="checkbox" id="only-cablefree">
        <span>Solo sin cable</span>
      </label>
      <label class="switch">
        <input type="checkbox" id="only-under1000">
        <span>Menos de 1.000 €</span>
      </label>
    </div>

    <p class="scroll-hint small">Desliza la tabla para ver todas las columnas <span aria-hidden="true">→</span></p>
    <div class="table-wrap">
      <table class="compare" id="compare-table">
        <thead>
          <tr>
            <th scope="col"><button data-col="0">Modelo</button></th>
            <th scope="col"><button data-col="1">Superficie</button></th>
            <th scope="col"><button data-col="2">Pendiente</button></th>
            <th scope="col"><button data-col="3">Instalación</button></th>
            <th scope="col"><button data-col="4">Navegación</button></th>
            <th scope="col"><button data-col="5">Precio</button></th>
            <th scope="col"><button data-col="6">Nota</button></th>
            <th scope="col"><span class="sr-only">Enlace</span></th>
          </tr>
        </thead>
        <tbody>{rows}
        </tbody>
      </table>
    </div>
    <p class="muted small">La nota es una puntuación editorial de 0 a 100 que combina superficie, pendiente, tipo de navegación, relación calidad-precio y fiabilidad de marca. No es una valoración de usuarios.</p>
  </div>
</section>
"""
    return layout(
        "Comparativa de robots cortacésped " + str(YEAR) + " | " + SITE["nombre"],
        "Tabla comparativa de 12 robots cortacésped con superficie, pendiente, navegación y precio actualizado. Ordena y filtra por lo que te importa.",
        "/comparativa/",
        body,
    )


def page_guia() -> str:
    body = f"""
{breadcrumbs([("Guía de compra", "/guia-de-compra/")])}
<article class="section section--tight">
  <div class="wrap narrow prose">
    <p class="eyebrow">Guía de compra {YEAR}</p>
    <h1>Cómo elegir robot cortacésped sin arrepentirte</h1>
    <p class="lead">Lo que importa de verdad, lo que es marketing y los tres errores que provocan la mayoría de las devoluciones.</p>

    <h2 id="superficie">1. La superficie: coge el metro, no la ficha del fabricante</h2>
    <p>Los fabricantes anuncian la superficie máxima en condiciones ideales: césped llano, seco, sin obstáculos y con el robot trabajando varias horas al día. En la vida real, un robot al 100% de su capacidad corta peor, tarda más y se desgasta antes.</p>
    <p><strong>Regla práctica:</strong> elige un robot con al menos un 20-30% más de superficie de la que tienes. Si tu jardín son 400 m², busca 500 m² o más.</p>
    <p>Y mide solo el césped. Si tienes zonas separadas por caminos o parterres, o el robot no puede pasar de una a otra, cada zona cuenta como un jardín independiente.</p>

    <h2 id="pendiente">2. La pendiente: el dato que casi nadie mira y todos sufren</h2>
    <p>Un robot que no sube tu talud es un robot que se queda atascado cada dos días. Y los grados que anuncia el fabricante se miden en seco y con neumáticos limpios.</p>
    <p>Para orientarte: una pendiente del 20% equivale a unos 11°, y del 50% a unos 27°. La mayoría de jardines domésticos con talud están entre 15° y 30°.</p>
    <ul>
      <li><strong>Hasta 15°:</strong> casi cualquier modelo sirve.</li>
      <li><strong>15-30°:</strong> necesitas tracción decente y ruedas con buen agarre.</li>
      <li><strong>Más de 30°:</strong> solo modelos con tracción a las cuatro ruedas o sistemas específicos. Aquí el precio sube de verdad.</li>
    </ul>

    <h2 id="cable">3. Con cable o sin cable: el debate que decide tu instalación</h2>
    <p><strong>Con cable perimetral:</strong> el robot sigue un cable enterrado o grapado al césped que delimita la zona. Es la tecnología más probada, funciona con cualquier cobertura y suele ser más barata. A cambio, la instalación lleva medio día y el cable se puede romper con el tiempo.</p>
    <p><strong>Sin cable:</strong> el robot se orienta con GPS RTK, cámara o LiDAR. Se instala en una hora y puedes cambiar el mapa desde la app. A cambio, el GPS necesita vista al cielo (los árboles densos y los edificios altos lo complican) y la visión puede fallar con poca luz.</p>
    <p>Si tu jardín está rodeado de árboles altos, el LiDAR es la opción más estable. Si es abierto y sin obstáculos, el GPS RTK funciona muy bien.</p>

    <h2 id="navegacion">4. Navegación: qué significa cada sigla</h2>
    <ul>
      <li><strong>Cable perimetral:</strong> límites físicos. Muy fiable, poca flexibilidad.</li>
      <li><strong>GPS RTK:</strong> el robot se posiciona con precisión centimétrica mediante una base. Excelente en espacios abiertos.</li>
      <li><strong>Cámara / visión:</strong> reconoce obstáculos y bordes. Buena en jardines con objetos, sensible a la iluminación.</li>
      <li><strong>LiDAR:</strong> láser para mapear. Independiente de la luz, muy preciso, normalmente más caro.</li>
    </ul>

    <h2 id="coste">5. Cuánto cuesta de verdad al año</h2>
    <p>El precio de compra es solo el principio. Un robot cortacésped consume:</p>
    <ul>
      <li><strong>Cuchillas:</strong> 15-30 € al año. Se cambian cada 2-3 meses en temporada.</li>
      <li><strong>Electricidad:</strong> entre 5 y 15 € al año para un jardín medio.</li>
      <li><strong>Mantenimiento:</strong> limpieza de la base y las ruedas, revisión de sensores. Gratis si lo haces tú.</li>
      <li><strong>Reparaciones:</strong> si hay suerte, cero. Un motor o una batería fuera de garantía puede costar 100-250 €.</li>
    </ul>
    <p>Frente a un cortacésped de gasolina, el ahorro en combustible y mantenimiento suele compensar en 4-6 años. No es una inversión que se pague sola en un año, y conviene saberlo antes de comprar.</p>

    <h2 id="errores">6. Los tres errores que más se repiten</h2>
    <ol>
      <li><strong>Comprar por metros sin mirar la pendiente.</strong> El robot llega, no sube el talud y se devuelve.</li>
      <li><strong>No comprobar la cobertura GPS.</strong> Un jardín entre edificios altos puede dejar el RTK sin señal.</li>
      <li><strong>Ignorar el servicio técnico.</strong> Un robot es un electrodoméstico de exterior. Que haya un servicio cerca importa más de lo que parece.</li>
    </ol>

    <div class="cta-band">
      <div>
        <h2>¿Prefieres que te lo diga directamente?</h2>
        <p>Responde cuatro preguntas y te doy los dos modelos que mejor encajan con tu jardín.</p>
      </div>
      <a class="btn btn--big" href="/calculadora/">Usar el selector<span class="btn__arrow" aria-hidden="true">→</span></a>
    </div>
  </div>
</article>
"""
    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Cómo elegir robot cortacésped sin arrepentirte",
        "description": "Guía de compra de robots cortacésped: superficie, pendiente, cable frente a sin cable, navegación y coste anual real.",
        "inLanguage": "es-ES",
        "datePublished": f"{YEAR}-11-08",
        "dateModified": f"{YEAR}-11-08",
        "author": {"@type": "Organization", "name": SITE["nombre"]},
        "publisher": {"@type": "Organization", "name": SITE["nombre"]},
        "mainEntityOfPage": url("/guia-de-compra/"),
    })
    return layout(
        "Guía de compra: cómo elegir robot cortacésped | " + SITE["nombre"],
        "Guía completa para elegir robot cortacésped: superficie real, pendiente, cable o sin cable, navegación GPS y LiDAR, y coste anual de mantenimiento.",
        "/guia-de-compra/",
        body,
        ld,
    )


FAQS = [
    ("¿Merece la pena un robot cortacésped?",
     "Si tu jardín tiene más de 200 m² y cortas el césped al menos una vez cada dos semanas en temporada, sí. El ahorro de tiempo es real: entre 30 y 60 horas al año en un jardín medio. Si el jardín es muy pequeño o muy irregular, un cortacésped manual o uno de batería sigue siendo más práctico."),
    ("¿Cuántos metros cuadrados cubre un robot cortacésped?",
     "Los modelos domésticos van de 400 a 3.000 m². Lo importante es no comprar al límite: elige un 20-30% más de superficie de la que tienes para que el robot trabaje con margen y dure más."),
    ("¿Funciona con lluvia?",
     "La mayoría tiene sensor de lluvia y vuelve a la base. No es recomendable que corte con el césped mojado: las cuchillas arrancan mal la hierba y el robot patina en las pendientes."),
    ("¿Qué pasa con las mascotas y los erizos?",
     "Los modelos con cámara o LiDAR detectan obstáculos y animales mejor que los de cable. Aun así, revisa el jardín antes de programar el corte en zonas donde haya fauna, y evita las horas de actividad de erizos (amanecer y anochecer)."),
    ("¿Se puede instalar sin cable en cualquier jardín?",
     "No. Los sistemas GPS RTK necesitan vista despejada al cielo. Si hay árboles altos, edificios o muros que bloquean la señal, la cámara o el LiDAR son más fiables."),
    ("¿Cuánto tarda en cortar un jardín de 500 m²?",
     "Entre 2 y 4 horas según el modelo, el ancho de corte y la complejidad del jardín. Los robots trabajan por ciclos y vuelven a la base a cargar, así que no es un trabajo continuo."),
    ("¿Es ruidoso?",
     "Entre 54 y 60 dB, similar a una conversación tranquila. Puedes programarlo de noche sin molestar a los vecinos en la mayoría de los casos."),
    ("¿Qué mantenimiento necesita?",
     "Limpiar la base y las ruedas cada dos semanas, revisar las cuchillas cada 2-3 meses y sustituirlas cuando estén romas. Un juego de cuchillas cuesta entre 15 y 30 € al año."),
    ("¿Puedo comprarlo en Amazon y hacer la instalación yo?",
     "Sí. La instalación sin cable se hace en una hora siguiendo la app. La instalación con cable perimetral lleva medio día y, si no te ves con ganas, conviene contratar un instalador."),
    ("¿Los precios bajan en alguna época?",
     "Sí. Los mejores precios suelen darse entre octubre y febrero, fuera de temporada de jardín, y en eventos como Black Friday. En primavera la demanda sube y los descuentos se reducen."),
]


def page_faq() -> str:
    items = "".join(
        f'<details class="faq"><summary>{esc(q)}</summary><div class="faq__body"><p>{esc(a)}</p></div></details>'
        for q, a in FAQS
    )
    body = f"""
{breadcrumbs([("Preguntas frecuentes", "/preguntas-frecuentes/")])}
<section class="section section--tight">
  <div class="wrap narrow">
    <p class="eyebrow">Dudas resueltas</p>
    <h1>Preguntas frecuentes sobre robots cortacésped</h1>
    <p class="lead">Las diez dudas que más nos llegan antes de comprar.</p>
    {items}
  </div>
</section>
"""
    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQS
        ],
    })
    return layout(
        "Preguntas frecuentes sobre robots cortacésped | " + SITE["nombre"],
        "Respuestas a las dudas más comunes sobre robots cortacésped: superficie, lluvia, mascotas, ruido, mantenimiento y precios.",
        "/preguntas-frecuentes/",
        body,
        ld,
    )


def page_model(m: dict) -> str:
    related = [x for x in MODELS if x["id"] != m["id"] and abs(x["area_max"] - m["area_max"]) <= 500][:3]
    rel_cards = "".join(model_card(r) for r in related)
    cable_txt = "sin cable perimetral" if m["sin_cable"] else "con cable perimetral"
    body = f"""
{breadcrumbs([("Comparativa", "/comparativa/"), (m["nombre"], f"/modelos/{m['id']}/")])}
<article class="section section--tight">
  <div class="wrap">
    <div class="model-hero">
      <div class="model-hero__text">
        <p class="eyebrow">{esc(m['marca'])} · Nota editorial {m['score_base']}/100</p>
        <h1>{esc(m['nombre'])}</h1>
        <p class="lead">{esc(m['ideal_para'])}</p>
        <div class="model-hero__meta">
          <span class="pill">{m['area_max']} m²</span>
          <span class="pill">{m['pendiente_max']}° pendiente</span>
          <span class="pill">{'Sin cable' if m['sin_cable'] else 'Con cable'}</span>
          <span class="pill">{esc(m['navegacion'])}</span>
        </div>
        <div class="model-hero__cta">
          <p class="price">{eur(m['precio'])}<span class="price__note">precio orientativo</span></p>
          {cta(m)}
        </div>
      </div>
      <aside class="model-hero__aside">
        <p class="callout__kicker">Ideal para</p>
        <p class="verdict">{esc(m['ideal_para'])}</p>
      </aside>
    </div>

    <div class="model-grid">
      <section>
        <h2>Ficha técnica</h2>
        {spec_table(m)}
      </section>
      <section>
        <h2>Análisis</h2>
        {pros_cons(m)}
        <h3>Veredicto</h3>
        <p>El {esc(m['nombre'])} cubre hasta {m['area_max']} m² y trabaja {cable_txt} con navegación {esc(m['navegacion'].lower())}. Con una pendiente máxima de {m['pendiente_max']}°{' — recuerda que ese dato se mide en seco y con el césped bien cuidado' if m['pendiente_max'] >= 35 else ''}, está pensado para {esc(m['ideal_para'].lower().rstrip('.'))}.</p>
        <p>Su precio orientativo es de {eur(m['precio'])}. {esc(SITE['nota_precios'])}</p>
        {cta(m)}
      </section>
    </div>

    <section class="section__head section__head--left">
      <h2>Alternativas parecidas</h2>
      <p class="muted">Modelos con superficie similar que también conviene mirar.</p>
    </section>
    <div class="cards cards--3">{rel_cards}</div>
  </div>
</article>
"""
    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": m["nombre"],
        "brand": {"@type": "Brand", "name": m["marca"]},
        "description": m["ideal_para"],
        "category": "Robot cortacésped",
        "url": url(f"/modelos/{m['id']}/"),
        "offers": {
            "@type": "Offer",
            "price": m["precio"],
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock",
            "url": amazon_url(m),
        },
    })
    return layout(
        f"{m['nombre']}: análisis, precio y alternativas | {SITE['nombre']}",
        f"Análisis del {m['nombre']}: {m['area_max']} m², pendiente máxima {m['pendiente_max']}°, navegación {m['navegacion'].lower()} y precio orientativo. Puntos fuertes y limitaciones reales.",
        f"/modelos/{m['id']}/",
        body,
        ld,
    )


def page_legal(slug: str, title: str, intro: str, sections: list[tuple[str, str]]) -> str:
    body = f"""
{breadcrumbs([(title, f"/{slug}/")])}
<section class="section section--tight">
  <div class="wrap narrow prose">
    <h1>{esc(title)}</h1>
    <p class="lead">{esc(intro)}</p>
    {''.join(f'<h2>{esc(h)}</h2>{c}' for h, c in sections)}
  </div>
</section>
"""
    return layout(f"{title} | {SITE['nombre']}", intro, f"/{slug}/", body)


def pages_legal() -> dict[str, str]:
    titular = SITE["titular"]
    nif = SITE["nif"]
    ciudad = SITE["ciudad"]
    email = SITE.get("email") or "PENDIENTE"
    contacto = f"<p>{esc(titular)}<br>NIF: {esc(nif)}<br>Domicilio: {esc(ciudad)}, España<br>Correo de contacto: {esc(email)}</p>"
    return {
        "aviso-legal": page_legal(
            "aviso-legal", "Aviso legal",
            "Información obligatoria sobre el titular de este sitio web.",
            [
                ("Titular del sitio", contacto),
                ("Objeto", "<p>Este sitio web ofrece información y comparativas sobre robots cortacésped, así como enlaces de afiliado a tiendas de terceros. El acceso es gratuito y no requiere registro.</p>"),
                ("Responsabilidad", "<p>La información publicada tiene carácter orientativo. Los precios, especificaciones y disponibilidad pueden variar sin previo aviso; el dato válido es el que muestre la tienda en el momento de la compra. El titular no se hace responsable del uso que se dé a la información.</p>"),
                ("Propiedad intelectual", "<p>Los textos y el diseño de este sitio son de su titular. Las marcas y nombres comerciales mencionados pertenecen a sus respectivos propietarios.</p>"),
                ("Legislación aplicable", "<p>Esta relación se rige por la legislación española. Para cualquier controversia serán competentes los juzgados y tribunales del domicilio del titular.</p>"),
            ],
        ),
        "privacidad": page_legal(
            "privacidad", "Política de privacidad",
            "Qué datos tratamos, para qué y cómo ejercer tus derechos.",
            [
                ("Responsable", f"<p>{esc(titular)}, NIF {esc(nif)}, con domicilio en {esc(ciudad)}, España.</p>"),
                ("Datos que recogemos", "<p>Este sitio no tiene formularios de registro ni recoge datos personales de forma directa. Utilizamos una herramienta de analítica web que registra datos agregados de navegación (páginas visitadas, dispositivo, país de origen) sin identificar personalmente al usuario.</p>"),
                ("Finalidad", "<p>Medir el uso del sitio para mejorar sus contenidos. Base legal: interés legítimo en la mejora del servicio.</p>"),
                ("Destinatarios", "<p>Los datos de navegación pueden ser tratados por el proveedor de analítica y por el proveedor de alojamiento, que actúan como encargados del tratamiento. No se ceden datos a terceros con fines publicitarios.</p>"),
                ("Derechos", "<p>Puedes ejercer los derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo al correo de contacto que figura en el aviso legal, indicando el derecho que deseas ejercer.</p>"),
                ("Conservación", "<p>Los datos agregados se conservan durante el tiempo necesario para el análisis y, en todo caso, no más de 24 meses.</p>"),
            ],
        ),
        "cookies": page_legal(
            "cookies", "Política de cookies",
            "Este sitio usa el mínimo número de cookies posible.",
            [
                ("Qué son", "<p>Una cookie es un pequeño archivo que se almacena en tu navegador al visitar un sitio web. Puede servir para recordar preferencias o para medir visitas.</p>"),
                ("Cookies que usamos", "<p>Este sitio no instala cookies publicitarias ni de perfilado. Únicamente puede utilizar cookies técnicas necesarias para el funcionamiento de la página y cookies de analítica agregada.</p>"),
                ("Cookies de terceros", "<p>Al pulsar un enlace de afiliado hacia Amazon, el sitio de destino puede instalar sus propias cookies. Esas cookies se rigen por la política de privacidad de Amazon, no por la de este sitio.</p>"),
                ("Cómo desactivarlas", "<p>Puedes bloquear o eliminar cookies desde la configuración de tu navegador. Ten en cuenta que algunas funciones del sitio podrían dejar de funcionar correctamente.</p>"),
            ],
        ),
        "afiliados": page_legal(
            "afiliados", "Política de afiliados",
            "Cómo ganamos dinero y por qué eso no condiciona nuestras recomendaciones.",
            [
                ("Transparencia", f"<p>{esc(SITE['aviso_afiliados'])}</p>"),
                ("Cómo nos afecta", "<p>Cuando compras a través de un enlace de este sitio, recibimos una comisión de Amazon sin coste adicional para ti. Esa comisión es idéntica para todos los modelos de una misma categoría, por lo que no nos incentiva a recomendar uno sobre otro.</p>"),
                ("Cómo elegimos los modelos", "<p>La comparativa se construye a partir de especificaciones oficiales, experiencia de uso documentada y relación calidad-precio. La puntuación editorial no se vende ni se negocia con los fabricantes.</p>"),
                ("Precios", f"<p>{esc(SITE['nota_precios'])}</p>"),
            ],
        ),
    }


def page_404() -> str:
    body = """
<section class="section section--tight">
  <div class="wrap narrow center">
    <p class="eyebrow">Error 404</p>
    <h1>Esta página se ha perdido en el jardín</h1>
    <p class="lead">Puede que el enlace esté roto o que la página ya no exista.</p>
    <p><a class="btn btn--big" href="/">Volver al inicio</a></p>
  </div>
</section>
"""
    return layout("Página no encontrada | " + SITE["nombre"], "La página que buscas no existe.", "/404/", body)


# --------------------------------------------------------------------------
# SEO
# --------------------------------------------------------------------------
def sitemap(paths: list[str]) -> str:
    today = date.today().isoformat()
    items = "".join(
        f"<url><loc>{url(p)}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>{'weekly' if p in ('/', '/comparativa/') else 'monthly'}</changefreq>"
        f"<priority>{'1.0' if p == '/' else '0.8'}</priority></url>"
        for p in paths
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{items}</urlset>")


def reset_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main() -> None:
    reset_dir(DIST)

    out: dict[str, str] = {}
    out["/"] = page_home()
    out["/calculadora/"] = page_calculadora()
    out["/comparativa/"] = page_comparativa()
    out["/guia-de-compra/"] = page_guia()
    out["/preguntas-frecuentes/"] = page_faq()
    for m in MODELS:
        out[f"/modelos/{m['id']}/"] = page_model(m)
    out.update({f"/{k}/": v for k, v in pages_legal().items()})
    out["/404.html"] = page_404()

    for path, content in out.items():
        target = DIST / path.strip("/") / "index.html" if path.endswith("/") else DIST / path.lstrip("/")
        if path == "/404.html":
            target = DIST / "404.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rebase(content), encoding="utf-8")

    indexable = [p for p in out if p != "/404.html"]
    (DIST / "sitemap.xml").write_text(sitemap(indexable), encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

    # Necesario para que GitHub Pages no procese el sitio con Jekyll.
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    static_out = DIST / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(STATIC, static_out)

    total = len(indexable)
    print(f"OK · {total} páginas generadas en dist/")


if __name__ == "__main__":
    main()
