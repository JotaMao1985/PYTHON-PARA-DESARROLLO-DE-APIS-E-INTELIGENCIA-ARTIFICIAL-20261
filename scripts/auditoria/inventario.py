#!/usr/bin/env python3
"""Inventario tecnico estatico de los modulos del curso (T1.1a del PLAN_AUDITORIA_MODULOS).

Solo lectura. No modifica ningun archivo del material.

Uso:
    python3 scripts/auditoria/inventario.py            # tabla en consola + salida/inventario.json
    python3 scripts/auditoria/inventario.py --sin-red  # omite la descarga del CSS de Font Awesome
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"

# --- Modulos auditados -------------------------------------------------------
# Clave = numero de semana esperada segun el cronograma del syllabus.
def modulos() -> list[tuple[int, Path]]:
    encontrados = []
    for p in sorted(RAIZ.glob("*.html")):
        m = re.match(r"^(\d+)_", p.name)
        if m:
            encontrados.append((int(m.group(1)), p))
    return sorted(encontrados)


# --- Numero de semana declarado en el <title> --------------------------------
ROMANOS = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
}


def semana_declarada(titulo: str) -> tuple[str | None, int | None]:
    """Devuelve (literal encontrado, numero) o (None, None) si el titulo no declara semana."""
    if not titulo:
        return None, None
    m = re.search(r"\b(Semana|Clase|Sesi[oó]n)\s+([IVXLC]+|\d+)\b", titulo, re.I)
    if not m:
        return None, None
    literal = m.group(0)
    valor = m.group(2)
    if valor.isdigit():
        return literal, int(valor)
    return literal, ROMANOS.get(valor.upper())


# --- Font Awesome ------------------------------------------------------------
MODIFICADORES_FA = {
    "fa-solid", "fa-regular", "fa-brands", "fa-light", "fa-thin", "fa-duotone",
    "fa-sharp", "fa-classic", "fa-fw", "fa-lg", "fa-sm", "fa-xs", "fa-xl", "fa-2xl",
    "fa-spin", "fa-pulse", "fa-border", "fa-pull-left", "fa-pull-right",
    "fa-inverse", "fa-stack", "fa-stack-1x", "fa-stack-2x", "fa-ul", "fa-li",
    "fa-beat", "fa-fade", "fa-bounce", "fa-shake", "fa-flip", "fa-beat-fade",
    "fa-spin-pulse", "fa-spin-reverse", "fa-layers", "fa-rotate-by",
}
RE_MOD_NUM = re.compile(r"^fa-(\d+x|rotate-\d+|flip-(horizontal|vertical|both))$")


def iconos_usados(html: str) -> set[str]:
    """Nombres de icono referenciados en atributos class (no los modificadores)."""
    nombres: set[str] = set()
    for bloque in re.findall(r'class(?:Name)?\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\{`([^`]*)`\})', html):
        texto = bloque[0] or bloque[1] or bloque[2]
        if "fa-" not in texto:
            continue
        for tok in re.findall(r"\bfa-[a-z0-9-]+\b", texto):
            if tok in MODIFICADORES_FA or RE_MOD_NUM.match(tok):
                continue
            nombres.add(tok)
    return nombres


_cache_catalogo: dict[str, set[str]] = {}


def catalogo_fa(version: str) -> set[str] | None:
    """Iconos que existen en esa version de Font Awesome, leidos del CSS del CDN."""
    if version in _cache_catalogo:
        return _cache_catalogo[version]
    url = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{version}/css/all.min.css"
    try:
        css = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    except Exception as exc:  # red caida, version inexistente
        print(f"  [aviso] no se pudo leer el catalogo FA {version}: {exc}", file=sys.stderr)
        _cache_catalogo[version] = None
        return None
    nombres = set(re.findall(r"\.(fa-[a-z0-9-]+):+before", css))
    _cache_catalogo[version] = nombres
    return nombres


# --- Stack de render ---------------------------------------------------------
def stack(html: str) -> dict:
    react = re.search(r"react@(\d+)/umd/react\.(development|production\.min)\.js", html)
    return {
        "react": (f"{react.group(1)} ({react.group(2).split('.')[0]})" if react else None),
        "babel": bool(re.search(r"@babel/standalone", html)),
        "jsx_inline": bool(re.search(r'type="text/babel"', html)),
        "tailwind_cdn": bool(re.search(r"cdn\.tailwindcss\.com", html)),
        "css_propio": "<style" in html,
    }


def librerias(html: str) -> dict[str, str | None]:
    def v(patron: str) -> str | None:
        m = re.search(patron, html)
        return m.group(1) if m else None

    mathjax_cargado = bool(re.search(r'src="[^"]*mathjax[^"]*"', html, re.I))
    return {
        "font_awesome": v(r"font-awesome/([\d.]+)/css"),
        "chartjs": v(r"Chart\.js/([\d.]+)/"),
        "plotly": v(r"plotly-([\d.]+)\.min\.js"),
        "katex": v(r"katex@([\d.]+)/"),
        "mathjax": "3 (jsdelivr)" if mathjax_cargado else None,
        "mathjax_mencionado_sin_cargar": (
            bool(re.search(r"mathjax", html, re.I)) and not mathjax_cargado
        ),
        "prism": v(r"prism/([\d.]+)/"),
        "highlightjs": v(r"highlight\.js/([\d.]+)/"),
        "babel_pineado": bool(re.search(r"@babel/standalone@[\d.]+", html)),
    }


# --- Metadatos ---------------------------------------------------------------
def metadatos(html: str) -> dict:
    def meta(nombre: str, attr: str = "name") -> str | None:
        m = re.search(
            rf'<meta[^>]*{attr}=["\']{re.escape(nombre)}["\'][^>]*content=["\'](.*?)["\']',
            html, re.S | re.I,
        )
        if m:
            return " ".join(m.group(1).split())
        m = re.search(
            rf'<meta[^>]*content=["\'](.*?)["\'][^>]*{attr}=["\']{re.escape(nombre)}["\']',
            html, re.S | re.I,
        )
        return " ".join(m.group(1).split()) if m else None

    lang = re.search(r"<html[^>]*lang=[\"'](.*?)[\"']", html, re.I)
    h1s = [
        " ".join(re.sub(r"<[^>]+>", " ", x).split())
        for x in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    ]
    return {
        "lang": lang.group(1) if lang else None,
        "charset": bool(re.search(r'charset=["\']?utf-8', html, re.I)),
        "viewport": bool(re.search(r'name=["\']viewport["\']', html, re.I)),
        "description": meta("description"),
        "author": meta("author"),
        "keywords": meta("keywords"),
        "og_title": meta("og:title", "property"),
        "og_description": meta("og:description", "property"),
        "h1": h1s,
    }


# --- Residuos de Cloudflare (email obfuscation) ------------------------------
def cloudflare(html: str) -> dict:
    """Cloudflare reescribe cualquier cadena con '@' como [email protected].

    Si el HTML se guardo desde una pagina servida por Cloudflare, los literales de
    correo y las cadenas de conexion de los ejemplos quedan destruidos, y el script
    que los descifra apunta a una ruta que en local da 404.
    """
    def descifrar(hexa: str) -> str:
        b = bytes.fromhex(hexa)
        return "".join(chr(c ^ b[0]) for c in b[1:])

    cifrados = re.findall(r'data-cfemail="([0-9a-f]+)"', html)
    return {
        "literales_destruidos": [descifrar(h) for h in cifrados],
        "enlaces_email_protection": html.count("/cdn-cgi/l/email-protection"),
        "script_decode_404": html.count("cloudflare-static/email-decode"),
    }


# --- Enlaces -----------------------------------------------------------------
def enlaces(html: str) -> dict:
    crudos = re.findall(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', html)
    externos, internos, anclas = set(), set(), set()
    for u in crudos:
        u = u.strip()
        if not u or u.startswith(("data:", "javascript:", "mailto:", "tel:", "#!")):
            continue
        if u.startswith("#"):
            anclas.add(u[1:])
        elif u.startswith(("http://", "https://", "//")):
            externos.add(u)
        else:
            internos.add(u)
    ids = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))
    nombres = set(re.findall(r'<a[^>]*\bname\s*=\s*["\']([^"\']+)["\']', html))
    return {
        "externos": sorted(externos),
        "internos": sorted(internos),
        "anclas": sorted(anclas),
        "anclas_rotas": sorted(a for a in anclas if a and a not in ids | nombres),
    }


# --- Programa ----------------------------------------------------------------
def analizar(num: int, ruta: Path, sin_red: bool) -> dict:
    html = ruta.read_text(encoding="utf-8", errors="replace")
    t = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    titulo = " ".join(t.group(1).split()) if t else None
    literal, semana = semana_declarada(titulo or "")
    libs = librerias(html)

    usados = iconos_usados(html)
    fa_ver = libs["font_awesome"]
    faltantes: list[str] = []
    catalogo = None
    if fa_ver and usados and not sin_red:
        catalogo = catalogo_fa(fa_ver)
        if catalogo:
            faltantes = sorted(usados - catalogo)

    e = enlaces(html)
    interno_roto = sorted(
        u for u in e["internos"]
        if not (RAIZ / u.split("#")[0].split("?")[0]).exists()
    )

    return {
        "num": num,
        "archivo": ruta.name,
        "bytes": ruta.stat().st_size,
        "lineas": html.count("\n") + 1,
        "titulo": titulo,
        "semana_literal": literal,
        "semana_declarada": semana,
        "semana_esperada": num,
        "semana_ok": (semana == num) if semana is not None else None,
        "stack": stack(html),
        "librerias": libs,
        "meta": metadatos(html),
        "fa_iconos_usados": sorted(usados),
        "fa_iconos_inexistentes": faltantes,
        "fa_catalogo_consultado": catalogo is not None,
        "enlaces": e,
        "enlaces_internos_rotos": interno_roto,
        "cloudflare": cloudflare(html),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-red", action="store_true", help="no consultar el catalogo de Font Awesome")
    args = ap.parse_args()

    SALIDA.mkdir(parents=True, exist_ok=True)
    datos = [analizar(n, p, args.sin_red) for n, p in modulos()]
    (SALIDA / "inventario.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{'#':>2}  {'KB':>5}  {'semana':<12} {'react':<10} {'babel':<6} {'FA':<7} {'mates':<10} graficas")
    print("-" * 84)
    for d in datos:
        libs, st = d["librerias"], d["stack"]
        mates = "katex " + libs["katex"] if libs["katex"] else ("mathjax" if libs["mathjax"] else "-")
        graf = "plotly " + libs["plotly"] if libs["plotly"] else ("chartjs " + libs["chartjs"] if libs["chartjs"] else "-")
        marca = "OK " if d["semana_ok"] else ("!! " if d["semana_ok"] is False else "-- ")
        sem = f"{marca}{d['semana_literal'] or 'sin semana'}"
        print(f"{d['num']:>2}  {d['bytes']//1024:>5}  {sem:<12} "
              f"{str(st['react'] or '-'):<10} {str(st['babel']):<6} "
              f"{str(libs['font_awesome'] or '-'):<7} {mates:<10} {graf}")

    print("\n--- Iconos Font Awesome inexistentes en la version cargada ---")
    hubo = False
    for d in datos:
        if d["fa_iconos_inexistentes"]:
            hubo = True
            print(f"  {d['archivo']} (FA {d['librerias']['font_awesome']}): "
                  f"{', '.join(d['fa_iconos_inexistentes'])}")
    if not hubo:
        print("  ninguno")

    print("\n--- Enlaces internos y anclas rotas ---")
    hubo = False
    for d in datos:
        if d["enlaces_internos_rotos"] or d["enlaces"]["anclas_rotas"]:
            hubo = True
            print(f"  {d['archivo']}: rutas={d['enlaces_internos_rotos']} "
                  f"anclas={d['enlaces']['anclas_rotas']}")
    if not hubo:
        print("  ninguna")

    print("\n--- Residuos de Cloudflare (literales destruidos en los ejemplos) ---")
    hubo = False
    for d in datos:
        cf = d["cloudflare"]
        if cf["literales_destruidos"] or cf["script_decode_404"]:
            hubo = True
            print(f"  {d['archivo']}: {len(cf['literales_destruidos'])} literales, "
                  f"{cf['script_decode_404']} script(s) 404 -> {cf['literales_destruidos']}")
    if not hubo:
        print("  ninguno")

    print(f"\nJSON completo en {SALIDA / 'inventario.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
