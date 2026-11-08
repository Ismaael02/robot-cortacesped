# Robot de Césped — proyecto de afiliación

Sitio estático completo, generado con Python puro (sin dependencias, sin Node, sin frameworks).
**Coste de funcionamiento: 0 €.**

```
robot-cortacesped/
├─ build.py                 ← genera el sitio entero
├─ data/
│  ├─ site.json             ← dominio, tag de Amazon, datos legales
│  └─ models.json           ← base de datos de los 12 robots
├─ static/                  ← CSS, JS, favicon
├─ dist/                    ← salida publicada
├─ publicar.ps1             ← sube el proyecto a GitHub en un comando
├─ vercel.json              ← configuración para Vercel
├─ netlify.toml             ← configuración para Netlify
├─ .github/workflows/       ← publicación automática en GitHub Pages
└─ README.md
```

Regenerar después de cualquier cambio:

```powershell
cd robot-cortacesped
python build.py
```

Genera 21 páginas más `sitemap.xml`, `robots.txt` y `.nojekyll`.

---

## Hosting: qué es gratis de verdad

| Plataforma | Gratis | ¿Permite uso comercial? | Nota |
|---|---|---|---|
| **Cloudflare Pages** | Sí | ✅ Sí | **Recomendado.** Sin límite de ancho de banda, HTTPS, CDN |
| **Netlify** | Sí | ✅ Sí | 100 GB/mes. Igual de válido |
| **GitHub Pages** | Sí | ✅ Sí | Publicación automática incluida en este repo |
| **Vercel** | Sí | ❌ **No** | El plan Hobby es solo para uso personal no comercial |

> **Aviso sobre Vercel:** su política de uso razonable dice literalmente que *«los equipos Hobby están restringidos al uso personal no comercial»*. Una web con enlaces de afiliado es uso comercial, así que pueden suspenderte la cuenta. He dejado el `vercel.json` preparado por si en el futuro pasas al plan Pro, pero no lo uses gratis para esto.

---

## Puesta en marcha (30 minutos, coste 0 €)

### 1. Crear el repositorio en GitHub

1. Entra en `github.com/new`.
2. Nombre: **`robot-cortacesped`** (importante: así la URL de Cloudflare coincidirá con la configuración).
3. Público. **No** marques «Add a README».
4. Crea el repositorio.

### 2. Subir el proyecto (un comando)

En PowerShell, desde la carpeta del proyecto:

```powershell
.\publicar.ps1 -UsuarioGitHub TU_USUARIO_DE_GITHUB
```

Eso genera el sitio, crea el repo local, hace el commit y lo sube. Si te pide credenciales, GitHub te dará un enlace para autenticarte en el navegador.

### 3. Publicar en Cloudflare Pages

1. Entra en `dash.cloudflare.com` → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Autoriza GitHub y elige el repositorio `robot-cortacesped`.
3. Configuración del build:
   - **Framework preset:** None
   - **Build command:** *(vacío)*
   - **Build output directory:** `dist`
4. **Save and Deploy**.

En un minuto tendrás `https://robot-cortacesped.pages.dev` funcionando. Gratis, sin tarjeta, sin límite de tráfico.

> Si eliges otro nombre de proyecto, cambia `"dominio"` en `data/site.json`, ejecuta `python build.py` y vuelve a subir. El canonical y el sitemap se actualizan solos.

### 4. Amazon Associates (el orden importa)

Amazon te pide una web **ya publicada**, así que primero publica.

1. Confirma que `https://robot-cortacesped.pages.dev` carga bien.
2. Solicita el alta en `afiliados.amazon.es`.
3. Cuando te den el ID de seguimiento (`tunombre-21`), edita:

```json
// data/site.json
"amazon_tag": "tunombre-21"
```

4. Regenera y sube:

```powershell
python build.py
.\publicar.ps1 -UsuarioGitHub TU_USUARIO_DE_GITHUB
```

Todos los botones pasan a llevar tu tag. Mientras esté en `PENDIENTE-TAG-21`, los enlaces funcionan pero no te acreditan comisión.

**Ojo:** necesitas 3 ventas en 180 días para mantener la cuenta. Sin tráfico no hay ventas.

### 5. Datos legales

En `data/site.json`:

```json
"titular": "Tu nombre o razón social",
"nif": "12345678A",
"ciudad": "Tu ciudad",
"email": "tu@email.com"
```

Sin esto, el aviso legal y la privacidad están incompletos y no cumplen la LSSI.

### 6. Analítica y Search Console (también gratis)

- **Cloudflare Web Analytics**: se activa desde el panel de Cloudflare. Gratis, sin cookies, sin banner de consentimiento.
- **Google Search Console**: añade la propiedad, verifica y envía `https://robot-cortacesped.pages.dev/sitemap.xml`.

---

## El único coste que merece la pena

Todo lo anterior es gratis para siempre. Pero hay una cosa que **no** es gratis y que deberías considerar más adelante: **un dominio propio** (~12 €/año).

Motivos:

1. **Amazon puede rechazar subdominios gratuitos** en la solicitud de Associates. No siempre, pero ocurre. Un dominio propio elimina ese riesgo.
2. `robotdecesped.es` transmite confianza; `algo.pages.dev` no.
3. Si algún día migras de hosting, el dominio te lo llevas.

Si decides comprarlo, solo hay que cambiar dos líneas en `data/site.json` y volver a subir. El sitio no cambia.

**Mi recomendación:** empieza gratis con `pages.dev`, solicita Amazon, y si te lo rechazan o el proyecto arranca, compra el dominio. Pero si quieres cero riesgo desde el día uno, son 12 € una vez al año.

---

## Alternativa: GitHub Pages (100 % gratis y automático)

Si prefieres no depender de otra plataforma, el repo ya incluye el flujo de publicación.

1. En GitHub: **Settings → Pages → Source: GitHub Actions**.
2. Cada `push` a `main` compila y publica solo.
3. URL: `https://TU_USUARIO.github.io/robot-cortacesped/`.

El workflow calcula automáticamente el dominio y la ruta base, así que **no tienes que tocar nada**. Es la opción más "todo dentro de GitHub" posible.

---

## Calendario realista

| Cuándo | Qué pasa |
|---|---|
| **Nov 2026** | Sitio publicado, Search Console configurado, 21 páginas indexándose |
| **Dic 2026 – Feb 2027** | Indexación. Tráfico casi cero. Es normal |
| **Mar – Jun 2027** | Temporada alta de jardín. Primeras visitas y comisiones |
| **Verano 2027** | Decides con datos: si hay clics y ventas, amplías. Si no, paras |

**Expectativa honesta:** 0 € los primeros 4-6 meses. Primer año, si funciona, entre 50 y 300 €/mes.

---

## Lo que decide si esto funciona

El sitio está construido. Lo que falta no es código, es **contenido con valor original**. Las tres acciones con más impacto, por orden:

1. **Fotos propias.** Una foto real del robot en tu jardín vale más que 2.000 palabras.
2. **Datos que nadie tiene.** Tiempo real de corte, consumo medido, ruido medido con el móvil.
3. **Long-tail.** En vez de «mejor robot cortacésped» (imposible), ataca «robot cortacésped para 400 m² con pendiente» o «¿funciona el Navimow sin wifi?».

---

## Mantenimiento

- **Precios:** `data/models.json` → campo `precio`. Revísalos cada 2-3 meses.
- **Modelos nuevos:** añade un objeto con el mismo esquema. Web, sitemap y calculadora se actualizan solos.
- **Borrar un modelo:** quita el objeto del array y regenera.
- **Textos:** están en `build.py`, funciones `page_*`.
- **Cambiar de hosting:** no hay nada acoplado. Es HTML plano.

---

## Notas técnicas

- HTML semántico, sin JS obligatorio para leer el contenido.
- Datos estructurados: `WebSite`, `Product`, `FAQPage`, `BreadcrumbList`.
- Enlaces de afiliado con `rel="sponsored nofollow noopener"` y `target="_blank"`.
- Aviso de afiliación en el pie de todas las páginas (exigido por Amazon).
- Sin cookies de terceros, sin fuentes externas, sin trackers.
- Un solo CSS y un solo JS. 78 KB de HTML en total.
- Soporta publicación en subdirectorio (`base_path`) para GitHub Pages.
