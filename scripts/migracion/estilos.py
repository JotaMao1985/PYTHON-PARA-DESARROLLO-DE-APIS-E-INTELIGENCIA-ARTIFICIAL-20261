#!/usr/bin/env python3
"""
Extrae del módulo heredado las reglas de CSS que LP-CORE no cubre.

Cada módulo trae en su `<style>` diagramas propios —pilas de capas, tartas
de capas de imagen, ventanas de log, pipelines, pirámides— que no tienen
componente equivalente en la librería. El resto del `<style>` sí sobra: el
resaltado escrito a mano lo rehace Prism, las cajas las pinta `Box` y la
navegación la pinta el `App`.

Se toman solo las reglas cuyas clases aparecen de verdad en el JSX ya
convertido. Partir del JSX y no del HTML original importa: así no se
arrastra el CSS de lo que la conversión ya sustituyó.

Las variables (`var(--line)`) se resuelven al valor literal, porque la hoja
de LP-CORE no las define y una variable que no existe deja la propiedad
en su valor inicial —un borde invisible, un texto negro— sin avisar.

Uso:
    python3 scripts/migracion/estilos.py <modulo.html> --piezas build/migracion/mNN
"""

import argparse
import re
import sys
from pathlib import Path

# Clases que la conversión ya resolvió: resaltado a mano (lo rehace Prism),
# cajas (`Box`) y estados. Aunque aparezcan en el JSX, su CSS no se trae.
RESUELTAS = {
    "kw", "str", "cm", "num", "fn", "builtin", "op", "var", "unit", "dec", "cls",
    "df-instr", "df-arg", "df-path", "df-flag", "sh-prompt", "sh-cmd", "sh-out",
    "box", "label", "info", "tip", "warn", "danger", "exercise", "solution",
    "small", "active", "chart-container", "chart-caption",
}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--piezas", type=Path, required=True)
    args = p.parse_args()

    jsx = args.piezas / "jsx"
    if not jsx.is_dir():
        print(f"ERROR: no hay JSX en {jsx}. Ejecute antes convertir.py.", file=sys.stderr)
        return 1

    # Las secciones y, al lado, `graficas.jsx`: una clase puede vivir solo en
    # las gráficas —le pasa al módulo 13, cuyos `chart-h-340` y `chart-h-380`
    # se fueron con ellas—, y mirar solo las secciones la daba por muerta.
    usadas = set()
    for f in sorted(jsx.glob("*.jsx")) + sorted(args.piezas.glob("*.jsx")):
        pieza = f.read_text(encoding="utf-8")
        for m in re.finditer(r'className="([^"]+)"', pieza):
            usadas |= set(m.group(1).split())
        # El `height` de `ChartFrame` es un nombre de clase aunque no se
        # escriba dentro de un `className`: el componente lo pone tal cual en
        # el `div` de la gráfica. Sin la regla, el marco mide cero y la
        # gráfica no se ve —y Plotly no se queja—.
        usadas |= set(re.findall(r'\bheight="([\w-]+)"', pieza))

    texto = args.archivo.read_text(encoding="utf-8")
    if "</style>" not in texto:
        (args.piezas / "estilos.css").write_text("", encoding="utf-8")
        print("El módulo no tiene <style> propio.", file=sys.stderr)
        return 0
    css = texto[:texto.index("</style>")]

    variables = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", css))
    faltan = (usadas & set(re.findall(r"\.([a-zA-Z][\w-]*)", css))) - RESUELTAS

    reglas, dentro_media = [], []
    for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", css):
        sel, cuerpo = m.group(1).strip(), m.group(2).strip()
        clases = set(re.findall(r"\.([\w-]+)", sel))
        if not (clases and clases & faltan and clases <= faltan | RESUELTAS):
            continue
        for k, v in variables.items():
            cuerpo = cuerpo.replace(f"var({k})", v.strip())
        linea = f"        {sel} {{ {' '.join(cuerpo.split())} }}"
        # Una regla dentro de un @media pierde su condición si se copia
        # suelta: la de escritorio y la de móvil se pisarían.
        (dentro_media if en_media(css, m.start()) else reglas).append((linea, m.start()))

    salida = [r for r, _ in reglas]
    for linea, pos in dentro_media:
        cond = re.search(r"@media[^{]*", css[:pos][::-1].split("}")[0][::-1] or "")
        cond = re.findall(r"(@media[^{]*)\{", css[:pos])
        salida.append(f"        {cond[-1].strip() if cond else '@media screen'} {{\n    {linea}\n        }}")

    (args.piezas / "estilos.css").write_text("\n".join(salida) + ("\n" if salida else ""), encoding="utf-8")
    print(f"{len(faltan)} clases sin equivalente en LP-CORE · {len(salida)} reglas → "
          f"{args.piezas}/estilos.css", file=sys.stderr)
    for c in sorted(faltan):
        print(f"    .{c}", file=sys.stderr)
    return 0


def en_media(css, pos):
    """¿La regla que empieza en `pos` está dentro de un bloque @media?"""
    trozo = css[:pos]
    return trozo.count("{") - trozo.count("}") > 0


if __name__ == "__main__":
    sys.exit(main())
