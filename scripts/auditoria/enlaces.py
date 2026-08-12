#!/usr/bin/env python3
"""Verificacion de enlaces externos de los modulos (T1.1b del PLAN_AUDITORIA_MODULOS).

Solo lectura. Hace una peticion HEAD (con reintento en GET) por URL unica y
reporta el codigo de estado. Un 403 no siempre es un enlace muerto: hay sitios
que bloquean clientes sin navegador. Se marcan como 'revisar a mano'.

Uso:
    python3 scripts/auditoria/enlaces.py
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Infraestructura: se comprueba igual, pero se lista aparte del contenido docente.
INFRA = ("cdn.tailwindcss.com", "cdnjs.cloudflare.com", "unpkg.com",
         "cdn.jsdelivr.net", "cdn.plot.ly", "fonts.googleapis.com", "fonts.gstatic.com")


def urls_por_modulo() -> tuple[dict[str, list[str]], set[str]]:
    """Devuelve (urls por modulo, urls que solo aparecen como preconnect/dns-prefetch).

    Un `<link rel="preconnect" href="https://fonts.gstatic.com">` no es un enlace
    navegable: el origen suele devolver 404 en la raiz y eso no es un defecto.
    """
    mapa: dict[str, list[str]] = {}
    solo_preconnect: set[str] = set()
    navegables: set[str] = set()
    for p in sorted(RAIZ.glob("*.html")):
        if not re.match(r"^\d+_", p.name):
            continue
        html = p.read_text(encoding="utf-8", errors="replace")
        for etiqueta in re.findall(r"<link\b[^>]*>", html, re.I):
            if re.search(r'rel\s*=\s*["\'](?:preconnect|dns-prefetch)["\']', etiqueta, re.I):
                m = re.search(r'href\s*=\s*["\'](https?://[^"\']+)["\']', etiqueta, re.I)
                if m:
                    solo_preconnect.add(m.group(1))
        urls = {
            u for u in re.findall(r'(?:href|src)\s*=\s*["\'](https?://[^"\']+)["\']', html)
            if "${" not in u
        }
        mapa[p.name] = sorted(urls)
        navegables |= urls
    # Un preconnect apunta al origen desnudo; si ademas se usa una URL con ruta,
    # esa otra URL es distinta y se comprueba por su cuenta.
    return mapa, solo_preconnect


def comprobar(url: str) -> tuple[str, int | str]:
    limpia = url.replace("&amp;", "&")
    for metodo in ("HEAD", "GET"):
        req = urllib.request.Request(limpia, method=metodo, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return url, r.status
        except urllib.error.HTTPError as e:
            if metodo == "HEAD":
                continue  # muchos sitios responden mal a HEAD; el veredicto lo da el GET
            return url, e.code
        except Exception as e:
            if metodo == "HEAD":
                continue
            return url, f"{type(e).__name__}"
    return url, "sin respuesta"


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    mapa, preconnect = urls_por_modulo()
    todas = sorted({u for v in mapa.values() for u in v})
    print(f"Comprobando {len(todas)} URL unicas de {len(mapa)} modulos "
          f"({len(preconnect)} son solo preconnect y no se cuentan como rotas)...\n")

    with ThreadPoolExecutor(max_workers=8) as ex:
        estados = dict(ex.map(comprobar, todas))

    def es_ok(v) -> bool:
        return isinstance(v, int) and 200 <= v < 400

    problemas = {u: v for u, v in estados.items()
                 if not es_ok(v) and u not in preconnect}

    print("--- Enlaces que NO devuelven 2xx/3xx ---")
    if not problemas:
        print("  ninguno")
    for u, v in sorted(problemas.items(), key=lambda x: str(x[1])):
        donde = [f for f, us in mapa.items() if u in us]
        clase = "infra" if any(d in u for d in INFRA) else "contenido"
        print(f"  [{v}] ({clase}) {u}")
        for d in donde:
            print(f"          en {d}")

    (SALIDA / "enlaces.json").write_text(
        json.dumps({"estados": {u: str(v) for u, v in estados.items()},
                    "por_modulo": mapa}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{len(todas) - len(problemas)}/{len(todas)} responden bien.")
    print(f"JSON en {SALIDA / 'enlaces.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
