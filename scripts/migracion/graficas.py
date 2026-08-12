#!/usr/bin/env python3
"""
Extrae las gráficas de Plotly de un módulo heredado y las emite como
componentes de LP-CORE.

El material las trae como salida de `plotly.io.to_html`: un `<script>` con
`Plotly.newPlot(id, data, layout, config)` y el JSON en línea. LP-CORE tiene
`ChartFrame` —el marco— y el hook `usePlotly` —el dibujo—, de modo que la
conversión es mecánica: `data` y `layout` pasan tal cual.

Dos cosas se descartan por el camino:

  · El `template` por defecto de Plotly, que `to_html` incrusta entero
    (unos 3 KB por gráfica) y que el `layout` del material ya pisa con sus
    propios `paper_bgcolor`, `plot_bgcolor` y `font`.
  · La clave `height`, porque aquí la altura la fija la clase de
    `ChartFrame` y tenerla en los dos sitios acabaría en discrepancia.

Los identificadores UUID que genera `to_html` se sustituyen por otros
legibles, derivados de la sección: `chart-piramide-1`.

Escribe dos archivos en la carpeta de salida:
    graficas.jsx    los componentes, listos para pegar en el capítulo
    graficas.json   el mapa sección → componente, que lee convertir.py

Uso:
    python3 scripts/migracion/graficas.py <archivo.html> --salida dir/
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Alturas que ofrece `ChartFrame`. La del material se redondea a la más
# cercana por arriba: recortar una gráfica es peor que dejarle aire.
ALTURAS = (320, 360, 420)


def clase_altura(px):
    if px is None:
        return "chart-h-360"
    return f"chart-h-{next((a for a in ALTURAS if a >= px), ALTURAS[-1])}"


def a_js(valor, nivel=0):
    """JSON → literal JS legible, con las claves sin comillas cuando se puede."""
    pad = "    " * nivel
    if isinstance(valor, dict):
        if not valor:
            return "{}"
        filas = []
        for k, v in valor.items():
            clave = k if re.fullmatch(r"[A-Za-z_$][\w$]*", k) else json.dumps(k)
            filas.append(f"{pad}    {clave}: {a_js(v, nivel + 1)}")
        return "{\n" + ",\n".join(filas) + f"\n{pad}}}"
    if isinstance(valor, list):
        if not valor:
            return "[]"
        plano = json.dumps(valor, ensure_ascii=False)
        if all(isinstance(x, (int, float, str)) for x in valor) and len(plano) < 95:
            return plano
        return "[\n" + ",\n".join(f"{pad}    {a_js(x, nivel + 1)}" for x in valor) + f"\n{pad}]"
    return json.dumps(valor, ensure_ascii=False)


def nombre_componente(seccion, n):
    partes = re.split(r"[-_]", seccion)
    base = "".join(p.capitalize() for p in partes)
    return f"Grafica{base}" + (str(n) if n > 1 else "")


def titulo_de(layout):
    t = layout.get("title")
    if isinstance(t, dict):
        t = t.get("text", "")
    return re.sub(r"<[^>]+>", "", t or "").strip()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()

    texto = args.archivo.read_text(encoding="utf-8")
    secciones = [(m.start(), m.end(), m.group(1))
                 for m in re.finditer(r'<section[^>]*id="([^"]+)".*?</section>', texto, re.S)]

    # Los espacios son libres: `to_html` los coloca de una forma en unos
    # módulos y de otra en otros —el 12 abre paréntesis y salta de línea
    # antes del identificador—, y un patrón rígido daba «no hay gráficas»
    # en un módulo que tiene cuatro.
    patron = re.compile(
        r'Plotly\.newPlot\(\s*"([^"]+)"\s*,\s*(\[.*?\])\s*,\s*(\{.*?\})\s*,\s*\{\s*"displayModeBar"',
        re.S)
    hallazgos = list(patron.finditer(texto))
    if not hallazgos:
        print("No hay gráficas de Plotly en este módulo.", file=sys.stderr)
        args.salida.mkdir(parents=True, exist_ok=True)
        (args.salida / "graficas.jsx").write_text("", encoding="utf-8")
        (args.salida / "graficas.json").write_text(json.dumps({"mapa": {}, "componentes": {}}), encoding="utf-8")
        return 0

    por_seccion, salida, mapa, comps = {}, [], {}, {}
    for m in hallazgos:
        _, data_s, layout_s = m.groups()
        sec = next((s[2] for s in secciones if s[0] <= m.start() < s[1]), "suelta")
        por_seccion[sec] = por_seccion.get(sec, 0) + 1
        n = por_seccion[sec]

        data = json.loads(data_s)
        layout = json.loads(layout_s)
        tenia_template = layout.pop("template", None) is not None
        alto = layout.pop("height", None)

        cid = f"chart-{sec}" + (f"-{n}" if n > 1 else "")
        comp = nombre_componente(sec, n)
        mapa.setdefault(sec, []).append(cid)
        comps[cid] = comp

        pie = titulo_de(layout) or "Gráfica del módulo"
        salida.append(
            f"        const {comp} = ({{ caption }}) => {{\n"
            f"            usePlotly('{cid}',\n"
            f"                () => {a_js(data, 4)},\n"
            f"                () => ({a_js(layout, 4)}), []);\n"
            f'            return <ChartFrame id="{cid}" height="{clase_altura(alto)}" caption={{caption}} />;\n'
            f"        }};"
        )
        print(f"  {cid:28s} {comp:24s} {len(data)} trazas · h={alto} → {clase_altura(alto)}"
              f"{' · template descartado' if tenia_template else ''}", file=sys.stderr)
        print(f"        {' ' * 28}   título: {pie[:60]}", file=sys.stderr)

    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "graficas.jsx").write_text("\n\n".join(salida) + "\n", encoding="utf-8")
    (args.salida / "graficas.json").write_text(
        json.dumps({"mapa": mapa, "componentes": comps}, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(hallazgos)} gráficas → {args.salida}/graficas.jsx", file=sys.stderr)
    print("Los pies de figura los pone convertir.py: los toma del `.chart-caption` que\n"
          "sigue a la gráfica en el material, que es donde el docente ya los escribió.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
