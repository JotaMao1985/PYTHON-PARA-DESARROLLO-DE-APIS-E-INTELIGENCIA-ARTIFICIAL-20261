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

# El JSX de una pieza sale a ras de margen y hay que encajarlo dentro de la
# plantilla, que lo quiere sangrado. Pero `textwrap.indent` sangra TODAS las
# líneas, y dentro de un `code={`…`}` las líneas no son JSX: son el programa
# que el estudiante va a copiar. Sangrarlas le mete al código dieciséis
# espacios que no escribió nadie —la primera línea no los lleva, porque va
# pegada al acento de apertura—, y lo que queda no es Python válido:
#
#     class Coin:                    ← columna 0, la escribió el acento
#                     def toss(self):    ← columna 16, la escribió montar.py
#
# No se puede arreglar al pintar: en tiempo de render ya no hay forma de saber
# cuáles de esos espacios son del JSX y cuáles del programa. Cuando TODAS las
# líneas de un bloque están dentro de una clase, la sangría común incluye el
# nivel real del código y quitarla entera rompe el bloque. Aquí sí se sabe,
# porque aquí es donde se añade: la respuesta es no añadirla.
_LITERAL_CODIGO = re.compile(r"code=\{`(?:[^`\\]|\\.)*`\}", re.S)


def indentar_jsx(cuerpo: str, ancho: int) -> str:
    """Sangra el JSX `ancho` espacios sin tocar lo que va dentro de `code={`…`}`."""
    guardados: list[str] = []

    def guardar(m):
        guardados.append(m.group(0))
        return f"__LP_CODIGO_{len(guardados) - 1}__"

    # El literal se colapsa a una marca de una sola línea, se sangra el JSX
    # —que ya es sólo JSX— y se devuelve el literal intacto a su sitio.
    protegido = _LITERAL_CODIGO.sub(guardar, cuerpo)
    sangrado = textwrap.indent(textwrap.dedent(protegido), " " * ancho).rstrip()
    return re.sub(r"__LP_CODIGO_(\d+)__",
                  lambda m: guardados[int(m.group(1))], sangrado)


# La línea que `lp-base.html` trae escrita a mano al pie del menú. Es de LPF,
# no de este curso, y se sustituye por el `stack` de la receta. Ver el paso 3b.
PIE_LPF = "<p>Pseudocódigo · Python · R · VBA</p>"

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

    # Y el mismo defecto con otra cara: un `<Icons.X />` escrito dentro del
    # contenido. Ahí no pasa por `renderIcon`, así que un nombre que no existe
    # no devuelve `null`: es `undefined` en posición de componente y React tira
    # la página entera con un «Minified React error #130» que no dice de dónde
    # viene. Pasó con `Icons.Structure`, del módulo 4.
    usados = set()
    for pieza in sorted((piezas / "jsx").glob("*.jsx")):
        usados |= set(re.findall(r"<Icons\.(\w+)", pieza.read_text(encoding="utf-8")))
    if receta.get("componentes"):
        p = ruta("componentes")
        if p.exists():
            usados |= set(re.findall(r"<Icons\.(\w+)", p.read_text(encoding="utf-8")))
    inventados = sorted(usados - iconos)
    if inventados:
        print(f"ERROR: el contenido usa <Icons.{', Icons.'.join(inventados)} /> y `Icons`\n"
              f"       no los define. No es que salgan en blanco ellos: dejan en blanco\n"
              f"       la página entera, con un error de React que no dice de dónde viene.\n"
              f"       Los {len(iconos)} que hay son: {', '.join(sorted(iconos))}",
              file=sys.stderr)
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

    # 3b · el pie de la barra lateral
    #
    # `lp-base.html` escribe ahí, a mano, la lista de lenguajes de Lógica de
    # Programación Financiera —«Pseudocódigo · Python · R · VBA»—, y de los
    # cuatro este curso sólo usa uno. Estuvo en los trece capítulos publicados
    # hasta agosto de 2026: nadie lo vio porque es una línea de diez píxeles al
    # pie del menú, que es donde mejor se esconde una cosa falsa.
    #
    # Pasa a salir de la receta, con el mismo `stack` que el syllabus declara
    # para esa semana —«FastAPI · Uvicorn · OpenAPI»— para que el capítulo y el
    # syllabus no puedan decir cosas distintas.
    #
    # Se comprueban las dos mitades, porque las dos fallan calladas: sin
    # `stack` en la receta el pie diría `undefined`, y si la plantilla cambia
    # esa línea la sustitución no encuentra nada y vuelve la de LPF a los
    # trece.
    if not receta["config"].get("stack"):
        print("ERROR: la receta no declara `config.stack`, que es lo que va al pie de\n"
              "       la barra lateral. Cópielo del syllabus, de la fila de esa semana.",
              file=sys.stderr)
        return 1
    texto, n = re.subn(re.escape(PIE_LPF), "<p>{CONFIG.stack}</p>", texto)
    if n != 1:
        print(f"ERROR: la plantilla ya no trae «{PIE_LPF}» al pie de la barra lateral\n"
              f"       ({n} coincidencias). Si LP-CORE cambió esa línea, hay que\n"
              f"       actualizar `PIE_LPF`; si no, el capítulo saldría publicando los\n"
              f"       lenguajes de otro curso.", file=sys.stderr)
        return 1

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
        cuerpo = indentar_jsx(propio.read_text(encoding="utf-8"), 8)
        texto = poner(texto, INI_COMP, FIN_COMP, cuerpo, "        const curriculum = [")

    # 6 · secciones
    comps, filas = [], []
    for s in receta["secciones"]:
        cuerpo = (piezas / "jsx" / f"{s['id']}.jsx").read_text(encoding="utf-8").rstrip()
        cuerpo = indentar_jsx(cuerpo, 16)
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
