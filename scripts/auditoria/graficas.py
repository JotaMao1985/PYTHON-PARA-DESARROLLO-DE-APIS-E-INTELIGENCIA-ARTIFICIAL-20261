#!/usr/bin/env python3
"""Inventario de graficas y de sus datos (T2.x, criterio C4). Solo lectura.

C4 pregunta si las graficas informan o decoran, y si sus datos son reales y
derivados o inventados. Para responder hace falta ver los NUMEROS, no los
`<canvas>`.

CORRECCION de metodo: contar `new Chart(` da el numero de RAMAS del renderizador,
no de graficas. El modulo 2 tiene un solo grafico y dos `new Chart(` (una rama
para `bar` y otra para `radar`). Aqui se cuentan las DEFINICIONES DE DATOS.

Uso:
    python3 scripts/auditoria/graficas.py
    python3 scripts/auditoria/graficas.py --detalle 12
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"

# Chart.js: definicion de datos dentro del almacen del modulo.
CHARTJS = re.compile(
    r"type:\s*'(bar|radar|line|pie|doughnut|scatter|bubble|polarArea)'\s*,\s*"
    r"label:\s*'([^']*)'\s*,\s*labels:\s*(\[[^\]]*\])\s*,\s*data:\s*(\[[^\]]*\])"
    r"(?:.{0,200}?description:\s*\"([^\"]*)\")?",
    re.S,
)

# Plotly: los modulos 10-13 NO escriben Plotly a mano. Llevan la salida de
# `plotly.io.to_html` de Python: `Plotly.newPlot("id", [trazas JSON], {layout})`
# con claves entre comillas dobles y los acentos escapados en \uXXXX. Se localiza
# la llamada y se parsea el JSON de verdad, en vez de adivinar con una regex.
PLOTLY_LLAMADA = re.compile(r"Plotly\.newPlot\(\s*\"([^\"]+)\"\s*,\s*")


def _json_equilibrado(texto: str, inicio: int) -> tuple[object | None, int]:
    """Lee el valor JSON que empieza en `inicio` contando llaves y corchetes."""
    if inicio >= len(texto) or texto[inicio] not in "[{":
        return None, inicio
    pares = {"[": "]", "{": "}"}
    pila = [texto[inicio]]
    i = inicio + 1
    en_cadena = False
    escapado = False
    while i < len(texto) and pila:
        c = texto[i]
        if en_cadena:
            if escapado:
                escapado = False
            elif c == "\\":
                escapado = True
            elif c == '"':
                en_cadena = False
        elif c == '"':
            en_cadena = True
        elif c in "[{":
            pila.append(c)
        elif c in "]}":
            if pares[pila[-1]] == c:
                pila.pop()
            else:
                return None, i
        i += 1
    if pila:
        return None, i
    try:
        return json.loads(texto[inicio:i]), i
    except json.JSONDecodeError:
        return None, i


def modulos():
    for p in sorted(RAIZ.glob("*.html")):
        m = re.match(r"^(\d+)_", p.name)
        if m and int(m.group(1)) > 0:
            yield int(m.group(1)), p


def analizar(html: str) -> list[dict]:
    graficas = []

    for m in CHARTJS.finditer(html):
        tipo, etiqueta, labels, datos, desc = m.groups()
        graficas.append({
            "motor": "Chart.js", "tipo": tipo, "titulo": etiqueta,
            "labels": re.sub(r"\s+", " ", labels),
            "datos": re.sub(r"\s+", " ", datos),
            "descripcion": desc or "",
        })

    for m in PLOTLY_LLAMADA.finditer(html):
        trazas, fin = _json_equilibrado(html, m.end())
        if not isinstance(trazas, list):
            continue
        layout, _ = _json_equilibrado(html, html.find("{", fin))
        titulo = ""
        if isinstance(layout, dict):
            t = layout.get("title")
            titulo = t.get("text", "") if isinstance(t, dict) else (t or "")

        for tr in trazas:
            if not isinstance(tr, dict):
                continue
            ejes = {k: tr[k] for k in ("x", "y", "z", "values", "labels", "text")
                    if k in tr}
            graficas.append({
                "motor": "Plotly",
                "tipo": tr.get("type") or tr.get("mode") or "?",
                "titulo": tr.get("name") or titulo,
                "titulo_figura": titulo,
                "id": m.group(1),
                "labels": json.dumps(ejes.get("x") or ejes.get("labels") or
                                     ejes.get("text") or "", ensure_ascii=False)[:400],
                "datos": json.dumps(ejes.get("y") or ejes.get("values") or
                                    ejes.get("z") or "", ensure_ascii=False)[:400],
                "descripcion": tr.get("hovertemplate", "")[:160],
            })

    return graficas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detalle", type=int)
    args = ap.parse_args()

    todo = {}
    for n, ruta in modulos():
        html = ruta.read_text(encoding="utf-8", errors="replace")
        gs = analizar(html)
        todo[str(n)] = gs
        if args.detalle == n:
            print(f"=== Modulo {n}: {len(gs)} graficas ===")
            for g in gs:
                print(f"\n  [{g['motor']} · {g['tipo']}] {g['titulo']}")
                print(f"    labels: {g['labels'][:190]}")
                print(f"    datos : {g['datos'][:190]}")
                if g["descripcion"]:
                    print(f"    desc  : {g['descripcion'][:170]}")
                if g.get("_titulos_layout"):
                    print(f"    titulos de layout: {g['_titulos_layout']}")
            return 0

    print(f"{'#':>3}  {'graficas':>8}  motor · tipos")
    for n, _ in modulos():
        gs = todo[str(n)]
        tipos = ", ".join(sorted({f"{g['motor']}:{g['tipo']}" for g in gs})) or "—"
        print(f"{n:>3}  {len(gs):>8}  {tipos}")

    # Graficas repetidas entre modulos: misma serie de datos y mismas etiquetas.
    print("\n=== Series identicas reutilizadas entre modulos ===")
    indice: dict[tuple[str, str], list[int]] = {}
    for n, _ in modulos():
        for g in todo[str(n)]:
            indice.setdefault((g["labels"], g["datos"]), []).append(n)
    hubo = False
    for (labels, datos), ns in indice.items():
        if len(set(ns)) > 1:
            hubo = True
            print(f"  modulos {sorted(set(ns))}: {labels[:90]} -> {datos[:70]}")
    if not hubo:
        print("  ninguna")

    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "graficas.json").write_text(
        json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {SALIDA}/graficas.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
