#!/usr/bin/env python3
"""
Comprueba que la migración no perdió contenido por el camino.

Compara el `courseData` extraído con el JSX que se emitió: cada palabra del
origen tiene que aparecer, con su frecuencia, en la sección o en las gráficas.
Es la red que cazó que la salida de un bloque se estaba inyectando como JSX
—una del módulo 2 dice `🐍 Original: <class 'datetime.datetime'>`, y ese
`<class …>` Babel lo abría como etiqueta—.

**No intenta interpretar el JSX**, y ahí está la gracia. Tres versiones
anteriores de este guion fallaron por lo mismo: quitar «etiquetas» con una
expresión regular destroza el código —`if p_value < alpha:` abre una que
nunca cierra— y destroza el propio JSX, donde `<Accordion items={[…(<>` tiene
su primer `>` a cincuenta caracteres del principio. Se compara texto crudo
contra texto crudo, deshaciendo sólo los escapes que aplica el guion. Que en
el lado de la salida sobren palabras da igual: lo que se comprueba es que no
falte ninguna del origen.

Uso:
    python3 scripts/migracion/auditar.py 1 2
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Lo único que la traducción descarta a propósito:
#
#   · La felicitación que abría cada justificación. En el heredado sólo se
#     veía al acertar —fallar daba un «❌ Incorrecto» genérico—; el `Quiz` de
#     LP-CORE la enseña a todo el mundo al enviar, así que «✅ Correcto» le
#     estaría diciendo a quien falló que acertó.
#   · Los pictogramas, que en `analogy` y `warning` pasan a ser el tipo del
#     `Box` y ahí siguen diciendo lo mismo.
DESCARTES = {"correcto", "exacto", "excelente", "crucial", "muy", "bien"}

# El marcado sí cambia, y también a propósito: `<br><br>` pasa a ser un corte
# de párrafo y el `<strong>` de la cabecera pasa a ser el `label` del `Box`.
# Se cuenta aparte en vez de ignorarse, para que se vea cuánto se transformó.
MARCADO = {"br", "strong", "/strong", "p", "/p", "em", "/em", "span", "/span"}

# Metadatos, no contenido: nadie los lee en la página.
META = {"language", "type", "correct", "max"}


def cadenas(x, clave=None):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in META:
                yield from cadenas(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from cadenas(v, clave)


def normalizar(s):
    s = (s.replace("&#123;", "{").replace("&#125;", "}")
          .replace("&quot;", '"').replace("&amp;", "&")
          .replace("\\`", "`").replace("\\${", "${").replace("\\\\", "\\"))
    s = s.replace("className=", "class=")
    # Sólo los pictogramas (categoría So). Filtrar toda la categoría S se
    # lleva por delante `<` y `>`, que son Sm, y pega las etiquetas a las
    # palabras: `datos.<br><br><strong>¿Por` se vuelve un único token.
    return "".join(c for c in s if unicodedata.category(c) != "So" and c != "️")


def cuenta(s):
    # La comilla invertida separa: sin ella, la primera palabra de cada
    # ``code={`…`` se queda pegada al acento y no casa con la del origen.
    trozos = re.split(r"[\s:·•☐❌,;()\[\]{}<>\"'`]+", normalizar(s))
    return Counter(t for t in trozos
                   if t and t.strip("¡!.¿?").lower() not in DESCARTES)


def auditar(n):
    base = Path(f"build/migracion/m{n}")
    if not (base / "datos.json").exists():
        print(f"ERROR: no hay piezas en {base}. Ejecute antes convertir_datos.py.",
              file=sys.stderr)
        return 1

    datos = json.loads((base / "datos.json").read_text(encoding="utf-8"))
    graf = (base / "graficas.jsx")
    conteo_graf = cuenta(graf.read_text(encoding="utf-8")) if graf.exists() else Counter()

    print("=" * 66, f"módulo {n}")
    malas = 0
    for m in datos["modules"]:
        origen = Counter()
        for t in cadenas(m.get("content") or {}):
            origen += cuenta(t)
        salida = cuenta((base / "jsx" / f"{m['id']}.jsx").read_text(encoding="utf-8")) + conteo_graf

        faltan = {w: c - salida[w] for w, c in origen.items() if salida[w] < c}
        marcado = {w: c for w, c in faltan.items() if w.lower() in MARCADO}
        faltan = {w: c for w, c in faltan.items() if w.lower() not in MARCADO}

        print(f"  {m['id']:6s} {'OK    ' if not faltan else 'PIERDE'} "
              f"{sum(origen.values()):5d} piezas · "
              f"{sum(marcado.values()):2d} etiquetas transformadas"
              + (f"  → {dict(list(faltan.items())[:8])}" if faltan else ""))
        malas += bool(faltan)
    return malas


def main():
    modulos = sys.argv[1:] or ["1", "2"]
    malas = sum(auditar(n) for n in modulos)
    print()
    print("sin pérdidas" if not malas else f"{malas} secciones pierden texto")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
