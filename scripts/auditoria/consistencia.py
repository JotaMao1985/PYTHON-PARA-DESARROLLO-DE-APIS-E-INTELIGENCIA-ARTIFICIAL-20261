#!/usr/bin/env python3
"""Mapa de consistencia transversal (T1.3 / criterio C6 del PLAN_AUDITORIA_MODULOS).

Solo lectura. Cuenta menciones de los terminos que el syllabus y el proyecto
integrador fijan como canonicos, y de sus competidores, con archivo y linea.

Uso:
    python3 scripts/auditoria/consistencia.py
    python3 scripts/auditoria/consistencia.py --detalle railway   # lineas exactas
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"

# (grupo, etiqueta, patron, veredicto)
#   canonico  = lo que syllabus/proyecto declaran obligatorio
#   divergente= alternativa que contradice al canonico
#   neutro    = se cuenta para contexto, no es defecto por si mismo
TERMINOS: list[tuple[str, str, str, str]] = [
    ("PaaS",       "Render",          r"\bRender\b(?!ing)",            "canonico"),
    ("PaaS",       "Railway",         r"\bRailway\b",                  "divergente"),
    ("PaaS",       "Heroku",          r"\bHeroku\b",                   "neutro"),
    ("PaaS",       "Fly.io",          r"\bFly\.io\b",                  "neutro"),
    ("PaaS",       "Vercel",          r"\bVercel\b",                   "neutro"),

    ("Python",     "3.11.9",          r"3\.11\.9",                     "canonico"),
    ("Python",     "3.11 (sin patch)", r"(?<!\.)3\.11(?!\.9)(?![\d])", "neutro"),
    ("Python",     "3.12",            r"(?<!\.)3\.12(?![\d])",         "divergente"),
    ("Python",     "3.10",            r"(?<!\.)3\.10(?![\d])",         "divergente"),
    ("Python",     "3.9",             r"(?<!\.)3\.9(?![\d])",          "divergente"),

    ("Framework",  "FastAPI",         r"\bFastAPI\b",                  "canonico"),
    ("Framework",  "Flask",           r"\bFlask\b",                    "divergente"),
    ("Framework",  "Django",          r"\bDjango\b",                   "neutro"),

    ("Pydantic",   "Pydantic v2",     r"[Pp]ydantic\s*v?2",            "canonico"),
    ("Pydantic",   "Pydantic v1",     r"[Pp]ydantic\s*v?1",            "divergente"),
    ("Pydantic",   "model_validator", r"\bmodel_validator\b",          "canonico"),
    ("Pydantic",   "@validator (v1)", r"@validator\b",                 "divergente"),
    ("Pydantic",   "field_validator", r"\bfield_validator\b",          "canonico"),
    ("Pydantic",   ".dict() (v1)",    r"\.dict\(\)",                   "divergente"),
    ("Pydantic",   ".model_dump()",   r"\.model_dump\(",               "canonico"),
    ("Pydantic",   "parse_obj (v1)",  r"\bparse_obj\b",                "divergente"),

    ("FastAPI",    "lifespan",        r"\blifespan\b",                 "canonico"),
    ("FastAPI",    "on_event (obs.)", r"@app\.on_event",               "divergente"),

    ("BD",         "SQLAlchemy 2.0",  r"SQLAlchemy\s*2",               "canonico"),
    ("BD",         "PostgreSQL",      r"\b[Pp]ostgre(?:SQL|s)\b",      "neutro"),
    ("BD",         "SQLite",          r"\bSQLite\b",                   "neutro"),

    ("Entorno",    "Docker",          r"\bDocker\b",                   "canonico"),
    ("Entorno",    "requirements.txt", r"requirements\.txt",           "canonico"),
    ("Entorno",    "Poetry",          r"\bPoetry\b",                   "neutro"),
    ("Entorno",    "conda",           r"\bconda\b",                    "neutro"),
    ("Entorno",    "venv",            r"\bvenv\b",                     "neutro"),

    ("Identidad",  "USTA",            r"\bUSTA\b|Santo Tom[aá]s",      "canonico"),
    ("Identidad",  "Montserrat",      r"Montserrat",                   "canonico"),
    ("Identidad",  "2026-II",         r"2026[-\s]?II\b",               "canonico"),
    ("Identidad",  "2026-I",          r"2026[-\s]?I\b(?!I)",           "divergente"),
    ("Identidad",  "2025",            r"\b2025\b",                     "divergente"),
]


def modulos() -> list[Path]:
    return sorted(
        (p for p in RAIZ.glob("*.html") if re.match(r"^\d+_", p.name)),
        key=lambda p: int(p.name.split("_")[0]),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detalle", help="etiqueta o patron: imprime archivo:linea de cada acierto")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)

    rutas = modulos()
    conteo: dict[str, dict[str, int]] = {}
    lineas: dict[str, dict[str, list[str]]] = {}

    for p in rutas:
        texto = p.read_text(encoding="utf-8", errors="replace")
        filas = texto.splitlines()
        conteo[p.name], lineas[p.name] = {}, {}
        for _, etiqueta, patron, _ in TERMINOS:
            rx = re.compile(patron)
            n = 0
            aciertos: list[str] = []
            for i, fila in enumerate(filas, 1):
                m = rx.findall(fila)
                if m:
                    n += len(m)
                    if len(aciertos) < 40:
                        aciertos.append(f"{p.name}:{i}: {fila.strip()[:150]}")
            conteo[p.name][etiqueta] = n
            lineas[p.name][etiqueta] = aciertos

    if args.detalle:
        clave = args.detalle.lower()
        for arch in conteo:
            for etiqueta, aciertos in lineas[arch].items():
                if clave in etiqueta.lower() and aciertos:
                    print(f"### {etiqueta} — {arch} ({conteo[arch][etiqueta]})")
                    for a in aciertos:
                        print("   ", a)
        return 0

    grupos: dict[str, list[tuple[str, str]]] = {}
    for grupo, etiqueta, _, veredicto in TERMINOS:
        grupos.setdefault(grupo, []).append((etiqueta, veredicto))

    cab = "  ".join(f"{p.name.split('_')[0]:>4}" for p in rutas)
    for grupo, etiquetas in grupos.items():
        print(f"\n=== {grupo} " + "=" * (60 - len(grupo)))
        print(f"{'termino':<20}{'':<4}{cab}")
        for etiqueta, veredicto in etiquetas:
            marca = {"canonico": "+", "divergente": "!", "neutro": " "}[veredicto]
            fila = "  ".join(
                f"{(conteo[p.name][etiqueta] or '.'):>4}" for p in rutas
            )
            print(f"{etiqueta:<20}{marca:<4}{fila}")

    (SALIDA / "consistencia.json").write_text(
        json.dumps({"conteo": conteo, "lineas": lineas}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n(+ canonico  ! divergente)   JSON en {SALIDA / 'consistencia.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
