#!/usr/bin/env python3
"""
Monta un módulo migrado a partir de `lp-base.html` y las piezas que producen
`graficas.py` y `convertir.py`.

Es la tercera pata del proceso. Las otras dos traducen contenido; esta arma
el archivo: `<head>` propio del curso, `CONFIG`, el CSS de los diagramas que
LP-CORE no cubre, las gráficas, las secciones y el `curriculum`.

Lo que hace y por qué:

  · **Sustituye el `<head>` de la plantilla.** `migrar.py` no estampa el
    `head` —en ningún curso—, así que el título, la descripción y los
    `<script>` de Prism son responsabilidad de cada archivo. Aquí se ponen
    los del curso una vez y no hay que acordarse en cada módulo.
  · **Inyecta el CSS propio del módulo.** Los diagramas heredados (pilas de
    capas, ventanas de log, pipelines) no tienen equivalente en LP-CORE y
    sus reglas viven en el `<style>` del archivo original.
  · **Deja centinelas** alrededor de las secciones, para poder regenerarlas
    sin volver a montar el archivo entero.

Es idempotente: si el archivo de salida ya existe y tiene centinelas, sólo
se reemplaza lo que hay entre ellos.

Uso:
    python3 scripts/migracion/montar.py receta.json
"""

import json
import re
import sys
import textwrap
from pathlib import Path

INI_SEC = "        /* === SECCIONES INICIO — generadas por scripts/migracion/convertir.py === */"
FIN_SEC = "        /* === SECCIONES FIN === */"
INI_CSS = "        /* === ESTILOS DEL MÓDULO INICIO — del <style> del archivo heredado === */"
FIN_CSS = "        /* === ESTILOS DEL MÓDULO FIN === */"
INI_GRAF = "        /* === GRÁFICAS INICIO — generadas por scripts/migracion/graficas.py === */"
FIN_GRAF = "        /* === GRÁFICAS FIN === */"
INI_COMP = "        /* === COMPONENTES DEL MÓDULO INICIO — escritos a mano, ver la receta === */"
FIN_COMP = "        /* === COMPONENTES DEL MÓDULO FIN === */"

# Gramáticas que el material de este curso necesita y la plantilla de LPF
# ya carga. Se comprueban, no se añaden: si faltan, el bloque sale sin
# resaltar y en silencio, que es el defecto que cerró `ensamblar.py`.
GRAMATICAS = ("prism-bash", "prism-docker", "prism-yaml", "prism-sql",
              "prism-toml", "prism-json", "prism-python")


def entre(texto, ini, fin):
    i, j = texto.find(ini), texto.find(fin)
    return (i, j + len(fin)) if i != -1 and j != -1 else None


def iconos_de(texto):
    """Los nombres que `Icons` conoce de verdad.

    Se declaran en dos sitios y hay que mirar los dos: el literal
    `const Icons = {…}` de la parte base y el `Object.assign(Icons, {…})` con
    el que `lp-core-extra.jsx` lo amplía. Leer sólo el primero da siete
    nombres en vez de diecisiete, y lleva a concluir que las recetas de los
    módulos 10, 11 y 12 están llenas de iconos inexistentes cuando no lo
    están. Esa comprobación a ojo ya salió mal una vez; para eso está aquí.
    """
    nombres = set()
    for ancla in ("const Icons = {", "Object.assign(Icons, {"):
        i = texto.find(ancla)
        if i == -1:
            continue
        # Los dos bloques cierran a la indentación de su apertura: `};` uno
        # y `});` el otro.
        j = texto.find("\n        }", i)
        nombres |= set(re.findall(r"^\s+(\w+):\s*\(\{", texto[i:j], re.M))
    return nombres


def poner(texto, ini, fin, bloque, ancla):
    """Reemplaza entre centinelas, o inserta antes del ancla la primera vez."""
    t = entre(texto, ini, fin)
    nuevo = ini + "\n" + bloque.rstrip() + "\n" + fin
    if t:
        return texto[:t[0]] + nuevo + texto[t[1]:]
    k = texto.index(ancla)
    return texto[:k] + nuevo + "\n\n" + texto[k:]


def podar(texto, vivos):
    """Quita del capítulo lo que quedó de la demo de la plantilla.

    Un módulo nace copiando `lp-base.html`, que trae un capítulo de muestra
    de Lógica de Programación Financiera: secciones de ejemplo y las
    constantes de las que tiran (`EJ_INTERES`, `SaldoChart`, `GLOSARIO`…).
    Nada de eso se referencia una vez puesto el `curriculum` propio, pero
    sobrevive al montaje: son 400 líneas de un curso ajeno dentro de un
    material de este.

    Se poda por alcance, no por lista de nombres: se retira toda constante
    de primer nivel que no aparezca en ningún otro sitio. Y en bucle,
    porque quitar una sección de muestra deja huérfanas sus constantes, que
    solo en la vuelta siguiente pasan a estar sin usar.

    El tramo se delimita por `LP-CORE FIN` y `const App`: la librería y el
    App son plantilla y los estampa `migrar.py`; en medio vive el capítulo.
    """
    while True:
        i = texto.index("LP-CORE FIN")
        j = texto.index("        const App = () => {")

        # Todo lo de primer nivel es una declaración, así que cada una llega
        # hasta donde empieza la siguiente. Es más fiable que buscar su
        # cierre: `};`, `);` y `` `; `` conviven aquí.
        decls = [i + m.start() for m in re.finditer(r"\n        const \w+\s*=", texto[i:j])]

        # Los centinelas cortan también. Si no, la última constante muerta de
        # la plantilla llega hasta la primera declaración del bloque generado
        # y se lleva por delante el comentario que lo abre. Pasaba siempre, y
        # no se notaba porque el `=== FIN ===` sí sobrevive: los módulos 10,
        # 11 y 12 se quedaron sin su `=== GRÁFICAS INICIO ===`.
        cortes = sorted(decls + [j] + [i + m.start() for m in
                                       re.finditer(r"\n        /\* === ", texto[i:j])])

        for ini in decls:
            nombre = re.match(r"\n        const (\w+)", texto[ini:]).group(1)
            if nombre in vivos or nombre == "CONFIG":
                continue
            if len(re.findall(r"\b" + nombre + r"\b", texto)) > 1:
                continue
            texto = texto[:ini] + texto[next(c for c in cortes if c > ini):]
            print(f"  podada «{nombre}», que ya no la referencia nadie", file=sys.stderr)
            break
        else:
            return texto


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().split("Uso:")[-1], file=sys.stderr)
        return 2
    ruta_receta = Path(sys.argv[1]).resolve()
    receta = json.loads(ruta_receta.read_text(encoding="utf-8"))

    # Todo se resuelve contra la raíz del repositorio, no contra el directorio
    # desde el que se invoque el guion ni contra el de la receta: así el
    # archivo montado sale igual se llame desde donde se llame, que es la
    # condición para poder tratarlo como salida regenerable y no versionarlo.
    #   scripts/migracion/recetas/x.json → …/recetas → …/migracion → scripts → raíz
    raiz = ruta_receta.parent.parent.parent.parent

    def ruta(clave):
        p = Path(receta[clave]).expanduser()
        return p if p.is_absolute() else (raiz / p).resolve()

    base, piezas, salida = ruta("base"), ruta("piezas"), ruta("salida")

    if not base.exists():
        print(f"ERROR: no se encuentra la plantilla {base}.\n"
              f"       Vive en el repositorio de Lógica de Programación; compruebe que las dos\n"
              f"       carpetas de curso siguen colgando del mismo directorio padre.",
              file=sys.stderr)
        return 1
    if not (piezas / "jsx").is_dir():
        print(f"ERROR: no hay piezas en {piezas}.\n"
              f"       Ejecute antes graficas.py y convertir.py con --salida {piezas}.",
              file=sys.stderr)
        return 1

    texto = base.read_text(encoding="utf-8")

    faltan = [g for g in GRAMATICAS if g not in texto[:texto.index("</head>")]]
    if faltan:
        print(f"ERROR: la plantilla no carga {', '.join(faltan)}. Los bloques de esos "
              f"lenguajes saldrían sin resaltar y sin avisar.", file=sys.stderr)
        return 1

    # Mismo defecto que el de las gramáticas, con otro vocabulario:
    # `renderIcon` devuelve null cuando el nombre no existe, así que un icono
    # mal escrito deja la sección sin icono, sin error de consola y sin que
    # nadie se entere hasta que lo mire.
    iconos = iconos_de(texto)
    fantasma = sorted({s["icono"] for s in receta["secciones"] if s.get("icono")} - iconos)
    if fantasma:
        print(f"ERROR: la receta usa iconos que `Icons` no define: {', '.join(fantasma)}.\n"
              f"       Saldrían en blanco y en silencio. Los {len(iconos)} que hay son:\n"
              f"       {', '.join(sorted(iconos))}", file=sys.stderr)
        return 1

    # Un componente que se llame como algo que la plantilla ya declara sale
    # declarado dos veces. Y no basta con confiar en `podar`: precisamente
    # porque la receta lo nombra, `podar` lo da por vivo y no lo retira. Pasó
    # con `PortadaSection`, que es una de las secciones de muestra de LPF.
    declarados = set(re.findall(r"\n        const (\w+)\s*=", texto))
    choque = sorted({s["componente"] for s in receta["secciones"]} & declarados)
    if choque:
        print(f"ERROR: la plantilla ya declara {', '.join(choque)}. Dos declaraciones\n"
              f"       del mismo nombre y Babel no compila la página entera.\n"
              f"       Renombre la sección en la receta.", file=sys.stderr)
        return 1

    # 1 · head propio del curso
    texto = re.sub(r"<title>.*?</title>", f"<title>{receta['titulo_html']}</title>", texto, count=1, flags=re.S)
    texto = re.sub(r'(<meta name="description"\s*\n?\s*content=")[^"]*(")',
                   lambda m: m.group(1) + receta["descripcion"] + m.group(2), texto, count=1)

    # 2 · CSS del módulo, antes del cierre del <style>
    css = (piezas / "estilos.css")
    if css.exists() and css.read_text(encoding="utf-8").strip():
        texto = poner(texto, INI_CSS, FIN_CSS, css.read_text(encoding="utf-8"), "    </style>")

    # 3 · CONFIG
    campos = "\n".join(f"            {k}: {json.dumps(v, ensure_ascii=False)},"
                       for k, v in receta["config"].items())
    bloque_cfg = "        const CONFIG = {\n" + campos + "\n        };"
    texto = re.sub(r"        const CONFIG = \{.*?\n        \};", lambda _: bloque_cfg,
                   texto, count=1, flags=re.S)

    # 4 · gráficas
    graf = piezas / "graficas.jsx"
    if graf.exists() and graf.read_text(encoding="utf-8").strip():
        texto = poner(texto, INI_GRAF, FIN_GRAF, graf.read_text(encoding="utf-8"),
                      "        const curriculum = [")

    # 5 · componentes propios del módulo
    #
    # No salen de ningún conversor: adaptar un componente a un sitio distinto
    # del que se escribió es un juicio, no una transformación mecánica. Por eso
    # viven en `componentes/modulo_N.jsx`, que sí se versiona, y por eso los
    # nombra la receta en vez de buscarlos el guion.
    if receta.get("componentes"):
        propio = ruta("componentes")
        if not propio.exists():
            print(f"ERROR: la receta declara componentes en {propio} y no está.",
                  file=sys.stderr)
            return 1
        cuerpo = textwrap.indent(textwrap.dedent(propio.read_text(encoding="utf-8")),
                                 " " * 8).rstrip()
        texto = poner(texto, INI_COMP, FIN_COMP, cuerpo, "        const curriculum = [")

    # 6 · secciones
    comps, filas = [], []
    for s in receta["secciones"]:
        cuerpo = (piezas / "jsx" / f"{s['id']}.jsx").read_text(encoding="utf-8").rstrip()
        cuerpo = textwrap.indent(textwrap.dedent(cuerpo), " " * 16).rstrip()
        comps.append(f"        const {s['componente']} = () => (\n"
                     f"            <div className=\"prose-lp\">\n{cuerpo}\n            </div>\n        );")
        filas.append(f"            {{ id: {s['id']!r}, title: {s['titulo']!r}, "
                     f"icon: {s['icono']!r}, component: {s['componente']} }},")
    texto = poner(texto, INI_SEC, FIN_SEC, "\n\n".join(comps), "        const curriculum = [")

    # 7 · curriculum
    cur = ("        const curriculum = [\n" + "\n".join(filas) + "\n        ];")
    texto = re.sub(r"        const curriculum = \[.*?\n        \];", lambda _: cur,
                   texto, count=1, flags=re.S)

    # Las secciones de la plantilla que ya no referencia nadie estorban:
    # sobreviven al montaje y confunden a quien lea el archivo.
    texto = podar(texto, {s["componente"] for s in receta["secciones"]})

    salida.write_text(texto, encoding="utf-8")
    print(f"OK  {salida}")
    print(f"    {len(texto.splitlines())} líneas · {len(receta['secciones'])} secciones · "
          f"{texto.count('<CodeBlock')} CodeBlock · {texto.count('<Box')} Box · "
          f"{texto.count('<Accordion')} Accordion · {texto.count('<table')} tablas")
    # Solo en las secciones: `usePlotly`, que es de LP-CORE, llama a
    # `Plotly.newPlot` y hacía saltar el aviso en todos los módulos.
    t = entre(texto, INI_SEC, FIN_SEC)
    if t and "newPlot" in texto[t[0]:t[1]]:
        print("    AVISO: queda un newPlot en las secciones sin sustituir", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
