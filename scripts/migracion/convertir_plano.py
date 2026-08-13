#!/usr/bin/env python3
"""
Convierte un módulo heredado de la familia «un artículo por `<h2>`» en
secciones de LP-CORE.

Los módulos 5, 7, 8 y 9 no traen `<section id>` como el 10, el 11 y el 12, ni
un `courseData` como el 1 y el 2. Traen **un `<article id>` por cada `<h2>`
del temario** —la navegación propia los enseña y los esconde con
`style.display`— y su vocabulario no es el de las cajas `div.box`, sino el de
Tailwind: `usta-card`, `tip-box`, `<details>` plegables y bloques de código
con su barra de título y su botón de copiar.

Eso hace que el troceo sea barato —el `<article id>` ya delimita la sección y
su `<h2>` da el título— y que el trabajo esté en otro sitio: **los diagramas**.
Son 231 SVG escritos a mano con 1 822 atributos con guion (`stroke-width`,
`text-anchor`, `font-size`…). El navegador los tolera porque el analizador de
HTML corrige los nombres al entrar en contenido SVG; JSX no analiza HTML, así
que ahí `stroke-width` es una propiedad desconocida y el diagrama sale sin
trazo. Lo mismo con `viewbox`, que el heredado escribe en minúscula 27 veces:
en SVG el nombre es sensible a mayúsculas y sin `viewBox` el dibujo no escala.

El guion produce **el mismo contrato que consume `montar.py`** —`jsx/<id>.jsx`—
de modo que la cadena de montaje y el formato de receta no cambian. Sólo cambia
la boca de entrada. Escribe además `titulos.json` con el `<h2>` de cada
artículo, que es lo que hay que copiar en la receta.

Uso:
    python3 scripts/migracion/convertir_plano.py <archivo.html> --salida dir/
    python3 scripts/migracion/convertir_plano.py <archivo.html> --seccion modulo-1
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Las cuatro se estrenaron en `convertir.py` y llevan tres módulos en uso. El
# problema que resuelven —llaves de la prosa que JSX lee como expresión,
# comillas que cierran un atributo antes de tiempo, `class` que es palabra
# reservada— es del destino, no del origen, así que es el mismo aquí.
from convertir import atributo, detectar_lang, escapar_jsx, limpiar_jsx, texto_plano
# La apertura y el reparto de la sesión son el mismo bloque `data-fase3` que
# en los módulos 1 y 2, con el mismo marcado. Se reutiliza tal cual. Y la
# insignia del enunciado es la misma marca que lleva la lección de la que sale
# una pregunta del módulo 6: un solo sitio donde está escrita.
from convertir_datos import bloque_portada, insignia

# Nombres de atributo que el analizador de HTML corrige al entrar en contenido
# SVG y que JSX deja pasar tal como se escriban. Los que llevan guion salen de
# una regla —`a-b` → `aB`—; éstos no, porque el heredado los escribe todos en
# minúscula y no hay guion del que tirar.
MINUSCULAS = {
    "viewbox": "viewBox",
    "preserveaspectratio": "preserveAspectRatio",
    "gradientunits": "gradientUnits",
    "gradienttransform": "gradientTransform",
    "spreadmethod": "spreadMethod",
    "patternunits": "patternUnits",
    "patterncontentunits": "patternContentUnits",
    "patterntransform": "patternTransform",
    "clippathunits": "clipPathUnits",
    "maskunits": "maskUnits",
    "maskcontentunits": "maskContentUnits",
    "filterunits": "filterUnits",
    "primitiveunits": "primitiveUnits",
    "markerunits": "markerUnits",
    "markerwidth": "markerWidth",
    "markerheight": "markerHeight",
    "refx": "refX",
    "refy": "refY",
    "stddeviation": "stdDeviation",
    "textlength": "textLength",
    "lengthadjust": "lengthAdjust",
    "startoffset": "startOffset",
    "baseprofile": "baseProfile",
    "attributename": "attributeName",
    "repeatcount": "repeatCount",
    "calcmode": "calcMode",
}

# Nombres de **elemento** que el analizador de HTML también corrige. Hoy no
# aparece ninguno dentro de los artículos, así que el guion no los toca: sólo
# avisa. Transformar a ciegas lo que no se ha visto nunca es como resaltar un
# bloque con la gramática que se supone.
ELEMENTOS_CORREGIDOS = {
    "lineargradient", "radialgradient", "clippath", "foreignobject", "textpath",
    "femerge", "femergenode", "fegaussianblur", "feoffset", "feflood",
    "fecomposite", "feblend", "fedropshadow", "femorphology", "feturbulence",
    "fecolormatrix", "fespecularlighting", "fediffuselighting", "fetile",
    "animatetransform", "animatemotion",
}

# Los prefijos que en JSX se escriben con guion, igual que en HTML. React los
# pasa al DOM sin tocarlos, que es justo lo que se quiere.
PREFIJOS_LITERALES = ("data-", "aria-")

# `.tip-box` es una sola clase para cuatro cosas distintas, y lo único que las
# separa es cómo abre el texto. El rótulo en negrita dice de qué va —«Analogía»,
# «⚠️ Punto de Atención», «Definición 1.1»—, así que de ahí sale el tipo.
PALABRAS_CAJA = (
    ("danger", ("sql injection", "nunca uses", "peligro")),
    ("warn", ("⚠", "atención", "atencion", "importante", "cuidado", "error común",
              "antipatrón", "antipatron")),
    ("tip", ("analogía", "analogia", "punto clave", "tip", "en la práctica",
             "recuerda", "regla")),
)

# Fórmula en línea del heredado. Escribe las matemáticas con los
# delimitadores de KaTeX, que es lo que carga; LP-CORE compone con MathJax, y
# su configuración sólo reconoce `\(…\)` en línea. En bloque no hay problema:
# `$$…$$` lo entienden los dos.
#
# Tres precauciones, y las tres hicieron falta:
#
#   · Ni el `$` de apertura ni el de cierre pueden tener otro `$` al lado, o
#     la pareja se mete dentro de un bloque `$$…$$` y lo parte: `$$X$$` salía
#     como `$\(X\)$`, con los dólares por fuera y la fórmula sin componer.
#   · La pareja no puede cruzar una etiqueta. Es lo que impide que un `$` sin
#     pareja —el módulo 7 escribe un precio, `"$1,500.00"`— se enganche con
#     el siguiente de verdad y se trague el párrafo de en medio.
#   · Y no puede pasar de 200 caracteres, por lo mismo, cuando entre los dos
#     no hay ninguna etiqueta que lo pare.
#
# Lo que NO se hace es descartar por el aspecto del contenido. La primera
# versión daba por dinero todo `$` seguido de cifra; en este material `$0.0$`
# y `$1-\beta$` son fórmulas, así que se quedaban sin componer.
MATE_EN_LINEA = re.compile(
    r"(?<!\$)\$(?!\$)((?:[^$<]|<(?![A-Za-z/!])){1,200}?)\$(?!\$)")

# El resumen de los `<details>` que guardan la respuesta de un cuestionario.
# No son plegables de contenido: son la retroalimentación de una pregunta y se
# absorben en el `Quiz`, que ya la enseña al calificar.
RESUMEN_RESPUESTA = re.compile(r"ver\s+respuesta", re.I)


# ------------------------------------------------------------ leer el árbol

def fin_elemento(texto, ini, etiqueta):
    """Índice justo después del `</etiqueta>` que cierra el que abre en `ini`.

    Hace falta contar: los artículos anidan `<div>` hasta seis niveles y una
    expresión regular perezosa cierra en el primer `</div>` que encuentra, que
    suele ser el de un icono de tres píxeles.
    """
    patron = re.compile(r"<" + etiqueta + r"\b[^>]*?(/?)>|</" + etiqueta + r"\s*>", re.S)
    nivel = 0
    for m in patron.finditer(texto, ini):
        if m.group(0).startswith("</"):
            nivel -= 1
            if nivel == 0:
                return m.end()
        elif m.group(1) != "/":
            nivel += 1
    return None


def rango_envolvente(texto, pos, etiqueta="div"):
    """(inicio, fin) del `<etiqueta>` más interno que contiene `pos`.

    Sirve para subir del `<pre>` a la tarjeta que lo envuelve, que es lo que
    hay que sustituir entero: la barra de título con el nombre del archivo y
    el botón de copiar son parte del mismo componente en LP-CORE.
    """
    patron = re.compile(r"<" + etiqueta + r"\b[^>]*?(/?)>|</" + etiqueta + r"\s*>", re.S)
    pila = []
    for m in patron.finditer(texto):
        if m.start() >= pos:
            break
        if m.group(0).startswith("</"):
            if pila:
                pila.pop()
        elif m.group(1) != "/":
            pila.append(m.start())
    if not pila:
        return None
    ini = pila[-1]
    fin = fin_elemento(texto, ini, etiqueta)
    return (ini, fin) if fin and fin > pos else None


def articulos(texto):
    """(id, contenido) de cada `<article id=…>`, en el orden del temario."""
    for m in re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>', texto):
        fin = fin_elemento(texto, m.start(), "article")
        if fin:
            yield m.group(1), texto[m.end():fin - len("</article>")]


# --------------------------------------------------------------- la cabecera

def cabecera(cuerpo):
    """Quita la banda de título y devuelve (título, resto).

    La banda es el icono en un cuadro con degradado y el `<h2>`. El `<h2>` lo
    pinta el App a partir del `curriculum`, y el icono lo elige la receta, así
    que dejar la banda daría dos títulos y dos iconos.
    """
    m = re.search(r'<h2\b[^>]*>(.*?)</h2>', cuerpo, re.S)
    if not m:
        return None, cuerpo
    titulo = " ".join(re.sub(r"<[^>]+>", "", m.group(1)).split())
    env = rango_envolvente(cuerpo, m.start(), "div")
    ini, fin = env if env else (m.start(), m.end())
    return titulo, cuerpo[:ini] + cuerpo[fin:]


def quitar_paginador(cuerpo):
    """Quita el «Anterior / 1 de 8 / Siguiente» del pie de cada artículo.

    Es la navegación del armazón heredado, que enseñaba y escondía artículos
    con `style.display` y saltaba con `href="#modulo-1"`. En LP-CORE los
    artículos ya no están todos en la página, así que esos enlaces no llevan
    a ninguna parte; y el App pinta su propio paso a paso, con lo que además
    habría dos contadores diciendo cosas distintas.
    """
    while True:
        m = re.search(r'<div\b[^>]*class="[^"]*\bmodule-controls\b[^"]*"[^>]*>', cuerpo)
        if not m:
            return cuerpo
        fin = fin_elemento(cuerpo, m.start(), "div")
        if not fin:
            return cuerpo
        cuerpo = cuerpo[:m.start()] + cuerpo[fin:]


# ------------------------------------------------------------- los diagramas

def camelizar(nombre):
    """`stroke-width` → `strokeWidth`; `viewbox` → `viewBox`."""
    if nombre.startswith(PREFIJOS_LITERALES):
        return nombre
    if nombre in MINUSCULAS:
        return MINUSCULAS[nombre]
    if "-" not in nombre:
        return nombre
    cabeza, *resto = nombre.split("-")
    return cabeza + "".join(p[:1].upper() + p[1:] for p in resto)


def camelizar_svg(cuerpo, avisos):
    """Pasa a camelCase los nombres de atributo de los diagramas.

    Sólo dentro de `<svg>`: fuera, el guion es correcto —`data-language` se
    escribe así también en JSX— y hay prosa que habla de `font-size` sin que
    eso sea un atributo.

    Se cambia el nombre y nada más: ni el valor, ni el orden, ni el `<style>`
    del propio SVG, donde `font-size:` es una declaración de CSS y camelCasear
    la rompería.
    """
    cambios = 0
    salida, i = [], 0
    for m in re.finditer(r"<svg\b", cuerpo):
        if m.start() < i:
            continue
        fin = fin_elemento(cuerpo, m.start(), "svg")
        if not fin:
            avisos.append("un <svg> se quedó sin cerrar; se deja tal cual")
            continue
        salida.append(cuerpo[i:m.start()])
        bloque = cuerpo[m.start():fin]

        sueltos = {e for e in re.findall(r"</?([a-z]{4,})\b", bloque)
                   if e in ELEMENTOS_CORREGIDOS}
        if sueltos:
            avisos.append(f"el diagrama trae elementos SVG en minúscula "
                          f"({', '.join(sorted(sueltos))}): JSX los crea con ese "
                          f"nombre literal y no dibujan. Hay que corregirlos a mano")

        def una_etiqueta(t):
            nonlocal cambios
            def un_atributo(a):
                nonlocal cambios
                nuevo = camelizar(a.group(2))
                if nuevo != a.group(2):
                    cambios += 1
                return a.group(1) + nuevo + a.group(3)
            return re.sub(r"([\s\"'])([a-zA-Z][\w:-]*)(\s*=)", un_atributo, t.group(0))

        # Sólo dentro de las etiquetas: el texto del diagrama y el `<style>`
        # que a veces lleva dentro quedan intactos.
        bloque = re.sub(r"<[a-zA-Z][^>]*>", una_etiqueta, bloque)
        salida.append(bloque)
        i = fin
    salida.append(cuerpo[i:])
    return "".join(salida), cambios


# ----------------------------------------------------------- bloques de código

def barra_titulo(envoltorio):
    """El nombre del archivo que el heredado escribe en la barra del bloque.

    Es el `<span>` de en medio —entre los tres círculos de semáforo y el botón
    de copiar—, y suele traer delante el icono de Font Awesome del lenguaje.
    """
    for m in re.finditer(r"<span\b[^>]*>(.*?)</span>", envoltorio, re.S):
        texto = " ".join(texto_plano(m.group(1)).split())
        if texto and texto.lower() not in ("copiar", "¡copiado!"):
            return texto
    return None


def convertir_codigo(cuerpo, marcas, avisos):
    """Cada `<pre>` con su tarjeta → un `<CodeBlock>`.

    El heredado dibuja a mano lo que `CodeBlock` ya hace: la barra oscura con
    el nombre del archivo, el botón de copiar y el resaltado, escrito con
    `<span class="text-pink-500 font-bold">` alrededor de cada palabra clave.
    Todo eso se descarta —el resaltado lo rehace Prism— y se queda el texto.
    """
    while True:
        m = re.search(r"<pre\b[^>]*>", cuerpo)
        if not m:
            break
        fin = fin_elemento(cuerpo, m.start(), "pre")
        if not fin:
            avisos.append("un <pre> se quedó sin cerrar; se corta el bloque ahí")
            fin = len(cuerpo)
        interior = cuerpo[m.end():fin - len("</pre>")]
        interior = re.sub(r"^\s*<code\b[^>]*>|</code>\s*$", "", interior.strip("\n"))

        # Un `<pre>` con un `<svg>` dentro no es código: es un diagrama al que
        # el heredado le puso la tarjeta oscura de los bloques para reutilizar
        # el estilo. Tratarlo como código lo aplana —`texto_plano` se queda
        # con las etiquetas de los rótulos y tira el dibujo—, y el módulo 7
        # perdía así sus tres diagramas grandes. Se saca de la tarjeta y se
        # deja como el diagrama que es.
        if "<svg" in interior:
            env = rango_envolvente(cuerpo, m.start(), "div")
            ini, corte = (env if env and "bg-gray-800" in cuerpo[env[0]:m.start()]
                          else (m.start(), fin))
            cuerpo = (cuerpo[:ini] + '<div className="my-6">' + interior.strip()
                      + "</div>" + cuerpo[corte:])
            avisos.append("un diagrama venía dentro de un <pre>; sale como SVG y no "
                          "como bloque de código")
            continue

        codigo = texto_plano(interior).strip("\n")

        # La tarjeta que envuelve el `<pre>` es suya si delante lleva la barra
        # oscura del heredado; si no, el `<pre>` va suelto dentro de la prosa
        # y sólo se sustituye él. La barra se reconoce por su clase y no por
        # el `onclick="copyCode(…)"`, que para cuando llega aquí ya lo ha
        # quitado `sin_estorbos`.
        env = rango_envolvente(cuerpo, m.start(), "div")
        ini, corte = m.start(), fin
        titulo = None
        if env and "bg-gray-800" in cuerpo[env[0]:m.start()]:
            ini, corte = env
            titulo = barra_titulo(cuerpo[env[0]:m.start()])

        decl = re.search(r'data-language="([^"]+)"', m.group(0))
        lang = decl.group(1) if decl else detectar_lang(codigo)
        if lang is None:
            avisos.append(f"lang sin determinar para el bloque que empieza por "
                          f"«{codigo.strip()[:46]}…»")
            lang, aviso = "text", "  /* TODO revisar lang */"
        else:
            aviso = ""
        if lang == "bash":
            lang = "shell"

        attr = f'title="{atributo(titulo)}" ' if titulo else ""
        seguro = codigo.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        marcas.append(f"<CodeBlock {attr}lang=\"{lang}\" code={{`{seguro}`}} />{aviso}")
        cuerpo = cuerpo[:ini] + f"@@PIEZA{len(marcas) - 1}@@" + cuerpo[corte:]
    return cuerpo


# --------------------------------------------------------- prosa y fórmulas

def traducir_mate(cuerpo, avisos):
    """`$x$` → `\\(x\\)`, que es el delimitador que LP-CORE compone.

    Se traduce en vez de dejarlo porque, sin traducir, la fórmula no falla:
    sale como texto con dólares, que es peor —parece contenido y no lo es—.
    """
    n = 0
    def una(m):
        nonlocal n
        n += 1
        return "\\(" + m.group(1) + "\\)"
    cuerpo = MATE_EN_LINEA.sub(una, cuerpo)
    # Los `$$…$$` de bloque no se tocan: MathJax los entiende igual que KaTeX.
    sobran = len(re.findall(r"(?<!\$)\$(?!\$)", re.sub(r"\$\$.*?\$\$", "", cuerpo, flags=re.S)))
    if n or sobran:
        avisos.append(f"{n} fórmulas en línea pasaron de `$…$` a `\\(…\\)`"
                      + (f"; quedan {sobran} `$` sin pareja sin tocar — compruebe "
                         f"que son dinero y no una fórmula sin cerrar" if sobran else ""))
    return cuerpo


def escapar_menor(cuerpo, avisos):
    """El `<` que no abre etiqueta, que en JSX es un error de sintaxis.

    Pasa dentro de las matemáticas —`$p < 0.05$`— y ahí no hay ambigüedad
    posible: un `<` seguido de espacio o de cifra no es una etiqueta en
    ningún dialecto. El caso dudoso, `<` pegado a una letra, no se toca: el
    analizador de HTML también lo leería como etiqueta, así que traducirlo
    sería cambiar el significado, no conservarlo.
    """
    cuerpo, n = re.subn(r"<(?![A-Za-z/!])", "&lt;", cuerpo)
    if n:
        avisos.append(f"{n} «<» sueltos escapados a &lt;: en JSX abrían una "
                      f"etiqueta y no compilaba")
    return cuerpo


# ------------------------------------------------------------ cuestionarios

def opciones_de(contenedor):
    """Las opciones de una pregunta, con cuál es la correcta.

    La marca de la correcta es `font-medium` en el `<span>` del texto, que es
    lo que mira el guion de barajado del heredado antes de quitarla. Aquí se
    quita también: con la respuesta en `correcta`, dejar la negrita sería
    enseñar la solución antes de contestar.
    """
    opciones = []
    for m in re.finditer(r"<label\b[^>]*>(.*?)</label>", contenedor, re.S):
        span = re.search(r'<span\b([^>]*)>(.*?)</span>\s*$', m.group(1), re.S)
        if not span:
            continue
        correcta = bool(re.search(r'class="[^"]*\bfont-medium\b', span.group(1)))
        # El heredado numera «A) », «B) »… y el barajado se lo quita al
        # cargar. `Quiz` numera solo, así que aquí sobra igual.
        texto = re.sub(r"^\s*(?:<strong>)?[A-Za-z]\)(?:</strong>)?\s*", "",
                       span.group(2).strip(), flags=re.S)
        opciones.append((texto, correcta))
    return opciones


def convertir_cuestionarios(cuerpo, marcas, avisos, prosa):
    """«Verificación de Comprensión» → un `Quiz` de LP-CORE.

    No es una mejora opcional: los radios del heredado sólo funcionan con su
    guion de barajado, que es el que quita la negrita de la respuesta correcta
    al cargar la página. Sin él —y no se lleva, porque LP-CORE no tiene dónde
    ponerlo— la opción correcta saldría en negrita desde el principio, con la
    solución a la vista. `Quiz` hace lo mismo que hacía el guion y además
    califica.
    """
    while True:
        m = re.search(r'<div\b[^>]*class="[^"]*\bbg-indigo-50\b[^"]*"[^>]*>', cuerpo)
        if not m:
            break
        fin = fin_elemento(cuerpo, m.start(), "div")
        if not fin:
            avisos.append("un bloque de «Verificación de Comprensión» sin cerrar")
            break
        bloque = cuerpo[m.start():fin]

        titulo = re.search(r"<h3\b[^>]*>(.*?)</h3>", bloque, re.S)
        titulo = (" ".join(texto_plano(titulo.group(1)).split()) if titulo
                  else "Verificación de comprensión")

        preguntas = []
        for c in re.finditer(r'<div\b[^>]*class="[^"]*\bspace-y-2\b[^"]*\bmb-4\b[^"]*"[^>]*>',
                             bloque):
            fin_c = fin_elemento(bloque, c.start(), "div")
            tarjeta = rango_envolvente(bloque, c.start(), "div")
            if not fin_c or not tarjeta:
                continue
            trozo = bloque[tarjeta[0]:tarjeta[1]]

            enunciado = re.search(r'<p\b[^>]*>(.*?)</p>', trozo, re.S)
            opciones = opciones_de(bloque[c.end():fin_c])
            just = re.search(r"<details\b[^>]*>.*?</summary>(.*?)</details>", trozo, re.S)

            if not enunciado or not opciones:
                avisos.append("una pregunta del cuestionario no tiene enunciado u "
                              "opciones donde se esperaban; se deja fuera")
                continue
            if sum(1 for _, ok in opciones if ok) != 1:
                avisos.append(f"la pregunta «{texto_plano(enunciado.group(1))[:38]}» no "
                              f"marca exactamente una opción correcta")

            # La insignia de dificultad —«Nivel Básico», «Nivel Medio»,
            # «Nivel Avanzado»— va delante del enunciado. `Quiz` no tiene
            # campo para ella, y perderla sería perder lo único que le dice
            # al estudiante cuánto debería costarle la pregunta, así que
            # entra en el enunciado con su etiqueta.
            marca = re.search(r'<span\b[^>]*class="[^"]*\binline-block\b[^"]*"[^>]*>'
                              r'\s*(Nivel[^<]*)</span>', trozo, re.S)
            rotulo = insignia(marca.group(1)) if marca else ""

            campos = ["pregunta: (<>" + rotulo
                      + prosa(enunciado.group(1)).strip() + "</>)"]
            campos.append("opciones: [" + ", ".join(
                "{ texto: (<>" + prosa(t).strip() + "</>), correcta: "
                + ("true" if ok else "false") + " }" for t, ok in opciones) + "]")
            if just:
                campos.append("justificacion: (<>" + prosa(just.group(1)).strip() + "</>)")
            preguntas.append("{ " + ", ".join(campos) + " }")

        if not preguntas:
            avisos.append("un bloque de «Verificación de Comprensión» se quedó sin "
                          "preguntas legibles; se deja como estaba")
            cuerpo = cuerpo[:m.start()] + bloque.replace("bg-indigo-50", "bg-indigo-100", 1) \
                + cuerpo[fin:]
            continue

        marcas.append(f'<Quiz titulo="{atributo(titulo)}" preguntas={{[\n    '
                      + ",\n    ".join(preguntas) + "\n]} />")
        cuerpo = cuerpo[:m.start()] + f"@@PIEZA{len(marcas) - 1}@@" + cuerpo[fin:]
    return cuerpo


# --------------------------------------------------------------- plegables

def convertir_desplegables(cuerpo, avisos):
    """`<details><summary>` → `Accordion`.

    Los `<details>` de las respuestas ya los absorbió el `Quiz`; los que
    quedan son material de consulta —«¿Qué es una escala Likert?»— y son
    exactamente lo que `Accordion` pinta.
    """
    def uno(m):
        interior = m.group(1)
        s = re.search(r"<summary\b[^>]*>(.*?)</summary>", interior, re.S)
        titulo = (" ".join(texto_plano(s.group(1)).split()).rstrip(" ▼▸")
                  if s else "Ver más")
        resto = re.sub(r"<summary\b[^>]*>.*?</summary>", "", interior, count=1, flags=re.S)
        if s and RESUMEN_RESPUESTA.search(titulo):
            avisos.append(f"queda un «{titulo}» fuera de su cuestionario; sale como "
                          f"plegable suelto")
        return ("<Accordion items={[{ titulo: " + json.dumps(titulo, ensure_ascii=False)
                + ", contenido: (<>" + resto.strip() + "</>) }]} />")

    return re.sub(r"<details\b[^>]*>(.*?)</details>", uno, cuerpo, flags=re.S)


# ------------------------------------------------------------------- cajas

def tipo_de_caja(texto):
    for tipo, palabras in PALABRAS_CAJA:
        if any(p in texto for p in palabras):
            return tipo
    return "info"


def convertir_cajas(cuerpo):
    """`div.tip-box` → `Box`, con el tipo que dice su rótulo.

    El heredado usa una sola clase para el consejo, el aviso y la definición;
    lo único que los distingue es cómo abre el texto —«Analogía», «⚠️ Punto de
    Atención», «Definición 1.1»—. Ese rótulo pasa a ser el `label` del `Box`,
    que es donde LP-CORE lo espera, y de ahí sale también el tipo.
    """
    while True:
        m = re.search(r'<div\b[^>]*class="[^"]*\btip-box\b[^"]*"[^>]*>', cuerpo)
        if not m:
            return cuerpo
        fin = fin_elemento(cuerpo, m.start(), "div")
        if not fin:
            return cuerpo
        interior = cuerpo[m.end():fin - len("</div>")]

        rotulo = re.match(r"\s*<strong>(.*?)</strong>", interior, re.S)
        etiqueta = (" ".join(texto_plano(rotulo.group(1)).split()).rstrip(":")
                    if rotulo else None)
        tipo = tipo_de_caja((etiqueta or texto_plano(interior)[:120]).lower())
        if rotulo:
            interior = interior[rotulo.end():].lstrip()
        attr = f' label="{atributo(etiqueta)}"' if etiqueta else ""
        cuerpo = (cuerpo[:m.start()] + f'<Box type="{tipo}"{attr}>' + interior
                  + "</Box>" + cuerpo[fin:])


# ---------------------------------------------------------------- limpieza

def sin_estorbos(cuerpo):
    """Lo que no puede viajar a JSX y no es contenido.

    · Los comentarios de HTML, que en JSX se escriben de otra forma y aquí
      sólo rotulan («<!-- Ejercicio 2 -->»).
    · Los `onclick=`, que apuntan a funciones del armazón heredado —`copyCode`,
      `setActiveModule`— que no se llevan. Como cadena, React ni siquiera los
      registra: sólo estorban.
    · Los `id=` de los `<pre>`, que sólo servían para que `copyCode` los
      encontrara. Repetidos entre módulos no molestaban porque cada archivo
      era uno; dentro de una sola página de LP-CORE, sí.
    """
    cuerpo = re.sub(r"<!--.*?-->", "", cuerpo, flags=re.S)
    cuerpo = re.sub(r'\s*onclick="[^"]*"', "", cuerpo)
    return cuerpo


def cerrar_vacias(cuerpo):
    """Etiquetas que en HTML se cierran solas y en JSX no.

    `limpiar_jsx` ya cierra `<br>`, `<hr>` e `<img>`. Aquí hace falta `<input>`
    —los radios de los cuestionarios que no llegaron a `Quiz`— y las del SVG,
    que el heredado escribe de las dos formas.
    """
    for etq in ("input", "col", "source", "area", "track", "wbr", "embed"):
        cuerpo = re.sub(r"<" + etq + r"\b([^>]*?)/?>", r"<" + etq + r"\1 />", cuerpo)
    return cuerpo


def proteger_estilos(cuerpo, marcas):
    """El `<style>` que algunos diagramas llevan dentro.

    Es CSS, no JSX: sus llaves las escaparía `escapar_jsx` y el bloque saldría
    con `&#123;` en vez de `{`, que no es CSS. Se aparta como un bloque de
    código y se devuelve dentro de una plantilla literal, que es como JSX
    admite texto con llaves.
    """
    while True:
        m = re.search(r"<style\b[^>]*>(.*?)</style>", cuerpo, re.S)
        if not m:
            return cuerpo
        css = m.group(1).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        marcas.append("<style>{`" + css + "`}</style>")
        cuerpo = cuerpo[:m.start()] + f"@@PIEZA{len(marcas) - 1}@@" + cuerpo[m.end():]


# ------------------------------------------------------------- la sección

def convertir_articulo(bruto, avisos):
    """Un `<article>` del heredado → el cuerpo de un componente de sección."""
    titulo, cuerpo = cabecera(bruto)
    cuerpo = quitar_paginador(cuerpo)
    cuerpo = sin_estorbos(cuerpo)

    # El orden es el de `convertir.py` y por el mismo motivo: lo que trae
    # llaves propias —código, CSS, `Quiz`— se aparta antes de escapar las de
    # la prosa, y se devuelve al final, cuando ya no queda ninguna pasada que
    # pudiera estropearlas.
    marcas = []
    cuerpo = proteger_estilos(cuerpo, marcas)
    cuerpo = convertir_codigo(cuerpo, marcas, avisos)

    # Con el código ya apartado: aquí `$` y `<` sólo pueden ser de la prosa.
    # Dentro de un bloque de código un `$` es una variable de shell y un `<`
    # una redirección, y ninguno de los dos hay que tocarlo.
    cuerpo = traducir_mate(cuerpo, avisos)
    cuerpo = escapar_menor(cuerpo, avisos)

    # El cuestionario se emite ya terminado —con sus llaves de JSX— porque su
    # contenido no vuelve a pasar por las pasadas de después. Por eso lleva su
    # propia `prosa`: es la misma que se aplica al resto, pieza a pieza.
    def prosa(t):
        return limpiar_jsx(escapar_jsx(t or ""))
    cuerpo = convertir_cuestionarios(cuerpo, marcas, avisos, prosa)

    cuerpo, cambios = camelizar_svg(cuerpo, avisos)
    cuerpo = escapar_jsx(cuerpo)
    cuerpo = convertir_desplegables(cuerpo, avisos)
    cuerpo = convertir_cajas(cuerpo)
    cuerpo = cerrar_vacias(cuerpo)
    cuerpo = limpiar_jsx(cuerpo)

    for i, pieza in enumerate(marcas):
        cuerpo = cuerpo.replace(f"@@PIEZA{i}@@", pieza)

    return titulo, cuerpo.strip(), cambios


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--seccion", help="id de un solo artículo")
    p.add_argument("--salida", type=Path, help="carpeta donde escribir los .jsx")
    args = p.parse_args()

    if not args.archivo.exists():
        print(f"ERROR: no existe {args.archivo}", file=sys.stderr)
        return 1

    texto = args.archivo.read_text(encoding="utf-8")
    secciones = list(articulos(texto))
    if not secciones:
        print("ERROR: no se encontró ningún <article id=…>.\n"
              "       Este guion es para los módulos 5, 7, 8 y 9. Para los que traen\n"
              "       <section id=…> use convertir.py; para `courseData`,\n"
              "       convertir_datos.py.", file=sys.stderr)
        return 1

    elegidas = [(i, c) for i, c in secciones if not args.seccion or i == args.seccion]
    if not elegidas:
        print(f"ERROR: artículo «{args.seccion}» no encontrado. Hay: "
              f"{', '.join(i for i, _ in secciones)}", file=sys.stderr)
        return 1

    if args.salida:
        (args.salida / "jsx").mkdir(parents=True, exist_ok=True)

    # La portada no sale de ningún artículo: es el HTML estático `data-fase3`
    # que va delante, con la apertura de la semana y el reparto del tiempo.
    total_avisos, titulos = 0, {}
    propios = []
    portada = "\n\n".join(b for b in bloque_portada(texto, propios) if b.strip())
    if portada and args.salida:
        (args.salida / "jsx" / "portada.jsx").write_text(portada, encoding="utf-8")
        print(f"{'OK  ' if not propios else 'AVISO'} {'portada':22s} "
              f"{len(portada.splitlines()):4d} líneas · "
              f"{portada.count('<Motivacion'):2d} Motivacion", file=sys.stderr)
        for a in propios:
            print(f"        · {a}", file=sys.stderr)
        total_avisos += len(propios)

    for sid, bruto in elegidas:
        avisos = []
        titulo, jsx, cambios = convertir_articulo(bruto, avisos)
        titulos[sid] = titulo
        if args.salida:
            (args.salida / "jsx" / f"{sid}.jsx").write_text(jsx, encoding="utf-8")
        else:
            print(jsx)
        print(f"{'OK  ' if not avisos else 'AVISO'} {sid:22s} "
              f"{len(jsx.splitlines()):4d} líneas · "
              f"{jsx.count('<CodeBlock'):2d} CodeBlock · {jsx.count('<Box'):2d} Box · "
              f"{jsx.count('<Accordion'):2d} Accordion · {jsx.count('<Quiz'):2d} Quiz · "
              f"{jsx.count('<svg'):2d} svg ({cambios} atributos)", file=sys.stderr)
        for a in avisos:
            print(f"        · {a}", file=sys.stderr)
        total_avisos += len(avisos)

    if args.salida:
        (args.salida / "titulos.json").write_text(
            json.dumps(titulos, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(elegidas)} secciones · {total_avisos} avisos por revisar",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
