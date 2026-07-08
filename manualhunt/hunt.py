"""Busca un manual PDF en fuentes comunes y lo descarga verificado.

Estrategia en dos pasadas, sin dependencias:
  1. Buscar en DuckDuckGo lite y Bing; probar las ligas .pdf directas.
  2. Si no hubo, entrar a las primeras páginas de resultados (manua.ls,
     manualslib, panasonic.com...) y rastrear ligas .pdf adentro.
Cada candidata se acepta sólo si empieza con %PDF y pesa > 100 KB.
"""

import base64
import html
import re
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
MIN_BYTES = 100_000
MAX_PAGINAS = 5   # cuántas páginas de resultados rastrear en la pasada 2
MAX_PDFS = 10     # cuántos PDFs candidatos descargar en total


def _html(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode(errors="replace")


def _ddg(consulta):
    """DuckDuckGo lite: resultados envueltos en ?uddg=<url>."""
    q = urllib.parse.quote_plus(consulta)
    cuerpo = _html(f"https://lite.duckduckgo.com/lite/?q={q}")
    for liga in re.findall(r'href="([^"]*uddg=[^"]+)"', cuerpo):
        destino = urllib.parse.parse_qs(
            urllib.parse.urlparse(html.unescape(liga)).query).get("uddg")
        if destino:
            yield destino[0]


def _bing(consulta):
    """Bing envuelve resultados en /ck/a?...&u=a1<base64url>."""
    q = urllib.parse.quote_plus(consulta)
    cuerpo = _html(f"https://www.bing.com/search?q={q}")
    for crudo in re.findall(r'href="(https://www\.bing\.com/ck/a\?[^"]+)"', cuerpo):
        u = urllib.parse.parse_qs(
            urllib.parse.urlparse(html.unescape(crudo)).query).get("u", [""])[0]
        if not u.startswith("a1"):
            continue
        s = u[2:] + "=" * (-len(u[2:]) % 4)
        try:
            destino = base64.urlsafe_b64decode(s).decode(errors="replace")
        except ValueError:
            continue
        if destino.startswith("http") and "bing.com" not in destino \
                and "microsoft.com" not in destino:
            yield destino


FUENTES = (_ddg, _bing)


def _es_pdf(url):
    return url.lower().split("?")[0].endswith(".pdf")


def _slug(texto):
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")[:60]


def _descargar(url, consulta, destino, eco):
    eco(f"  probando: {url[:90]}")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as resp:
            datos = resp.read()
    except OSError:
        return None
    if not datos.startswith(b"%PDF") or len(datos) < MIN_BYTES:
        return None
    ruta = destino / f"{_slug(consulta)}.pdf"
    ruta.write_bytes(datos)
    eco(f"  OK -> {ruta} ({len(datos) // 1024} KB)")
    return ruta


def _pdfs_dentro(url_pagina, eco):
    """Rastrea una página de resultados y regresa sus ligas .pdf."""
    eco(f"  rastreando: {url_pagina[:90]}")
    try:
        cuerpo = _html(url_pagina)
    except OSError:
        return []
    ligas = re.findall(r'href="([^"]+\.pdf[^"]*)"', cuerpo, re.I)
    ligas += re.findall(r"href='([^']+\.pdf[^']*)'", cuerpo, re.I)
    absolutas = [urllib.parse.urljoin(url_pagina, html.unescape(l)) for l in ligas]
    return [u for u in absolutas if _es_pdf(u)]


TIENDAS = ("play.google", "amazon.", "walmart.", "bestbuy.", "ebay.",
           "mercadolibre", "wikipedia.org")


def buscar(consulta, destino, eco=print):
    """Busca `consulta` y descarga el primer PDF válido a `destino/`.
    Regresa (ruta_pdf | None, pagina_respaldo | None): si no hay PDF,
    la página de soporte más prometedora para abrir en el navegador."""
    destino.mkdir(parents=True, exist_ok=True)
    paginas, pdfs = [], []
    for fuente in FUENTES:
        try:
            for url in fuente(consulta + " manual pdf"):
                if "duckduckgo.com" in url:
                    continue  # anuncios/redirects internos
                (pdfs if _es_pdf(url) else paginas).append(url)
        except OSError as e:
            eco(f"  fuente {fuente.__name__} falló: {e}")
        if pdfs or paginas:
            break  # con una fuente que respondió alcanza

    utiles = [p for p in paginas if not any(t in p for t in TIENDAS)]
    respaldo = next((p for p in utiles
                     if any(w in p.lower() for w in ("support", "help", "manual", "guide"))),
                    utiles[0] if utiles else None)

    intentos = 0
    for url in pdfs:                      # pasada 1: PDFs directos
        if intentos >= MAX_PDFS:
            return None, respaldo
        intentos += 1
        ruta = _descargar(url, consulta, destino, eco)
        if ruta:
            return ruta, None

    vistos = set()
    for pagina in paginas[:MAX_PAGINAS]:  # pasada 2: rastrear un nivel
        for url in _pdfs_dentro(pagina, eco):
            if url in vistos or intentos >= MAX_PDFS:
                continue
            vistos.add(url)
            intentos += 1
            ruta = _descargar(url, consulta, destino, eco)
            if ruta:
                return ruta, None
    return None, respaldo


def buscar_pdf(consulta, destino, eco=print):
    return buscar(consulta, destino, eco)[0]
