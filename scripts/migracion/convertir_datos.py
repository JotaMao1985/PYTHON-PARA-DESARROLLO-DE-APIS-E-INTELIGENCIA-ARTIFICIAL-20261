#!/usr/bin/env python3
"""
Convierte un módulo heredado de la familia `courseData` en secciones de
LP-CORE.

Los módulos 1 y 2 no son HTML estático como el 10, el 11 y el 12: son una
aplicación de una sola página. Todo el contenido vive en un objeto JavaScript
—`courseData`— con un `modules[]`, y el armazón lo pinta con plantillas
literales (`loadModule`, `renderNav`, `renderChart`…). En el HTML no hay ni
una `<section id>` de contenido ni una caja `div.box`, que es de lo que parten
`convertir.py` y `graficas.py`; por eso ninguno de los dos sirve aquí.

Sale más barato, no más caro: el contenido ya está estructurado, así que no
hay que analizar HTML. Se lee el objeto y se emite JSX.

El guion produce **el mismo contrato que consume `montar.py`** —`jsx/<id>.jsx`
y `graficas.jsx`—, de modo que la cadena de montaje y el formato de receta no
cambian. Sólo cambia la boca de entrada.

Uso:
    python3 scripts/migracion/convertir_datos.py <archivo.html> --salida dir/
    python3 scripts/migracion/convertir_datos.py <archivo.html> --volcar
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Las tres se estrenaron en `convertir.py` y llevan tres módulos en uso. El
# problema que resuelven —llaves de la prosa que JSX lee como expresión,
# comillas que cierran un atributo antes de tiempo, `class` que es palabra
# reservada— es del destino, no del origen, así que es el mismo aquí.
from convertir import atributo, detectar_lang, escapar_jsx, limpiar_jsx
# `a_js` da el literal JS legible que espera `usePlotly`; es de graficas.py
# porque allí nació, con las gráficas de los módulos 10, 11 y 12.
from graficas import a_js

# `courseData` no es JSON y no hay forma honrada de fingir que lo es: trae
# plantillas literales de varias líneas, comas finales, claves sin comillas y
# comentarios. Lo evalúa quien sabe, que es Node. El programa lee la fuente
# por la entrada estándar para no dejar archivos temporales por el camino.
LECTOR_JS = r"""
let fuente = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", d => fuente += d);
process.stdin.on("end", () => {
    let objeto;
    try {
        objeto = (0, eval)("(" + fuente + ")");
    } catch (e) {
        process.stderr.write(e.message);
        process.exit(1);
    }
    process.stdout.write(JSON.stringify(objeto));
});
"""


def tramo_objeto(texto, nombre="courseData"):
    """(inicio, fin) del literal de `const <nombre> = {…}`, o None.

    Contar llaves aquí no funciona, y no es una sutileza: dentro de
    `courseData` hay fragmentos de código Python en plantillas literales, y
    esos fragmentos traen llaves de diccionario en la columna cero. En el
    módulo 2, el primer `}` a indentación de cierre aparece a 43 000
    caracteres del final verdadero — está dentro de un `dict` de ejemplo.

    Así que no se adivina: se proponen los cierres plausibles —una llave sola
    en su línea, a una indentación no mayor que la de la declaración— y se
    acepta el primero que Node consiga parsear. El parser decide, que para eso
    es el único que conoce las reglas.
    """
    m = re.search(r"\bconst\s+" + re.escape(nombre) + r"\s*=\s*\{", texto)
    if not m:
        return None
    ini = texto.index("{", m.start())
    sangria = len(re.search(r"[ \t]*$", texto[:m.start()]).group(0))
    # El tramo termina en la llave, no en el `;` que la sigue: lo que se
    # envuelve entre paréntesis para evaluarlo tiene que ser una expresión.
    for c in re.finditer(r"\n([ \t]*)(\})[;,]?[ \t]*(?=\n|$)", texto[ini:]):
        if len(c.group(1)) <= sangria:
            yield ini, ini + c.end(2)


def evaluar_js(fuente):
    """El literal JS, ya evaluado, como estructura de Python. None si no parsea."""
    r = subprocess.run(["node", "-e", LECTOR_JS], input=fuente,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def extraer(texto, avisos):
    """`courseData` del módulo heredado, como diccionario."""
    intentos = 0
    for ini, fin in tramo_objeto(texto):
        intentos += 1
        fuente = texto[ini:fin]

        datos = evaluar_js(fuente)
        # Que parsee no basta: un tramo corto podría ser un objeto válido por
        # casualidad. Lo que se busca tiene `modules`, y con contenido.
        if not isinstance(datos, dict) or not isinstance(datos.get("modules"), list):
            continue
        if not datos["modules"]:
            continue

        # `${` sin escapar dentro de una plantilla literal no da error: se
        # interpola en silencio y el contenido sale distinto del original.
        # Hoy no hay ninguno —el único, un f-string de Python en el módulo 2,
        # viene ya escapado—, así que esto es un cable trampa por si alguien
        # edita el material heredado más adelante.
        for suelto in re.findall(r"(?<!\\)\$\{[^}\n]{0,40}\}?", fuente):
            avisos.append(f"«{suelto}» sin escapar: si está en una plantilla "
                          f"literal, se habrá interpolado en vez de copiarse")
        return datos, intentos
    return None, intentos


# --------------------------------------------------------------- contenido

# `analogy` y `warning` abren con un emoji y una etiqueta en negrita: «⚡
# <strong>Analogía:</strong>», «⚠️ <strong>Error Común:</strong>». El emoji no
# es adorno: es lo único que distingue un aviso de un consejo, porque la
# etiqueta cambia de una sección a otra —«Error Común», «Consideración»,
# «Seguridad», «Tip Moderno», «Práctica Vital»—. Así que es el emoji, y no la
# etiqueta, quien elige el tipo de `Box`.
TIPO_POR_EMOJI = {"⚠": "warn", "💡": "tip"}

# Una etiqueta más larga que esto no es una etiqueta, es la primera frase.
# `Box` la pinta en versalitas dentro de una píldora y una frase entera ahí no
# se lee; se queda en el cuerpo, que es su sitio.
#
# De esa distinción depende también qué pasa con el emoji. `Box` sólo dibuja
# su icono cuando hay etiqueta, así que el emoji se descarta justo entonces
# —dejar los dos daría dos iconos seguidos diciendo lo mismo— y se conserva
# cuando no la hay, porque ahí es la única señal visual que le queda a la caja.
ETIQUETA_MAX = 30

CABECERA = re.compile(r"^\s*([^\s<]{0,4}?)\s*<strong>\s*(.{1,70}?)\s*:?\s*</strong>"
                      r"\s*(?:<br\s*/?>)?\s*", re.S)


def texto_llano(fragmento):
    """Sin marcado, para lo que va dentro de un atributo."""
    return " ".join(re.sub(r"<[^>]+>", "", fragmento or "").split())


def prosa(bruto):
    """Un fragmento de HTML del material, listo para vivir dentro de JSX.

    Se aplica aquí, pieza a pieza, y no de una vez sobre la sección entera: en
    cuanto se emite un `CodeBlock` o un `Quiz` hay llaves que son de JSX y que
    una pasada global escaparía, rompiéndolos. `convertir.py` resuelve lo
    mismo apartando los bloques con marcas; aquí no hace falta, porque el
    contenido llega troceado y se sabe qué trozo es prosa y cuál no.
    """
    return limpiar_jsx(escapar_jsx(bruto or ""))


def parrafos(bruto):
    """Prosa del material → uno o más `<p>`.

    El material separa párrafos con `<br><br>` y hace listas con `<br>•`. Sólo
    el doble se convierte en párrafo: convertir también el simple partiría las
    listas en un párrafo por viñeta.
    """
    trozos = [t.strip() for t in re.split(r"(?:<br\s*/?>\s*){2,}", bruto or "")]
    return "\n".join(f"<p>{prosa(t)}</p>" for t in trozos if t)


def caja(bruto, tipo_defecto, avisos):
    """`analogy` o `warning` → `<Box>`, con el tipo que dice su emoji."""
    if not bruto or not bruto.strip():
        return ""
    tipo, etiqueta, cuerpo = tipo_defecto, None, bruto

    m = CABECERA.match(bruto)
    if m:
        emoji, texto_etq = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        # Un emoji ilegible es un defecto del heredado, no del guion: el
        # módulo 1 trae un U+FFFD literal donde debería haber uno. Se avisa y
        # se cae al tipo por defecto, que es lo que haría un emoji que no
        # esté en la tabla.
        if emoji and emoji not in TIPO_POR_EMOJI and "�" in emoji:
            avisos.append(f"«{texto_etq[:34]}» abre con un carácter de reemplazo "
                          f"(U+FFFD): el heredado perdió ahí su emoji")
        tipo = TIPO_POR_EMOJI.get(emoji[:1], tipo_defecto)
        if len(texto_etq) <= ETIQUETA_MAX:
            etiqueta, cuerpo = texto_etq, bruto[m.end():]

    attr = f' label="{atributo(etiqueta)}"' if etiqueta else ""
    return f'<Box type="{tipo}"{attr}>\n{parrafos(cuerpo)}\n</Box>'


def bloque_concept(concept, avisos):
    """`content.concept` → subtítulo, prosa y las dos cajas."""
    if not concept:
        return []
    partes = []
    if concept.get("title"):
        partes.append(f"<h3>{prosa(concept['title'])}</h3>")
    if concept.get("text"):
        partes.append(parrafos(concept["text"]))
    # La analogía siempre es un consejo; el emoji que la abre cambia en cada
    # sección (⚡🧪🐳📋🛡️🎯📨📦🍰🍳) y ahí sí es decorativo.
    partes.append(caja(concept.get("analogy"), "tip", avisos))
    partes.append(caja(concept.get("warning"), "info", avisos))
    return partes


# --------------------------------------------------------------- el código

def literal(codigo):
    """Código dentro de una plantilla literal de JS, sin que la rompa."""
    return codigo.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def bloque_code(code, avisos):
    """`content.code` → `CodeBlock`, y la salida plegada en un `Accordion`.

    En el heredado la salida está precalculada y escondida tras un botón
    «Ejecutar simulación» que no ejecuta nada: sólo la revela. LP-CORE no
    tiene ese componente, así que desaparece el botón y se conserva el gesto,
    que es lo que sostiene el «predice antes de mirar». Es la misma decisión
    que `convertir.py` tomó al plegar las soluciones de los ejercicios.
    """
    if not code or not code.get("snippet"):
        return []
    lang = code.get("language")
    if not lang:
        # El módulo 1 no declara el lenguaje en ninguno de sus seis bloques;
        # el 2 sí en todos. Cuando falta se usa la heurística de convertir.py,
        # que devuelve None antes que arriesgar una gramática equivocada.
        lang = detectar_lang(code["snippet"])
        if lang is None:
            avisos.append(f"lang sin determinar en «{(code.get('title') or '')[:40]}»")
            lang = "text"
    titulo = f'title="{atributo(code["title"])}" ' if code.get("title") else ""
    partes = [f'<CodeBlock {titulo}lang="{lang}" code={{`{literal(code["snippet"])}`}} />']

    if code.get("output"):
        # La salida va en un `CodeBlock`, no en un `<pre>` suelto, y no es por
        # uniformidad: una salida del módulo 2 dice
        # `🐍 Original: <class 'datetime.datetime'>`, y ese `<class …>` metido
        # como JSX es una etiqueta que Babel intenta abrir y no cierra nunca.
        # Dentro de una plantilla literal es texto y ya está.
        partes.append(
            "<Accordion items={[{ titulo: 'Ver salida', contenido: (<>"
            f'<CodeBlock lang="text" code={{`{literal(code["output"])}`}} />'
            "</>) }]} />")
    return partes


def bloque_code_explanation(ce):
    """`content.codeExplanation` → un `Accordion` con un paso por pliegue."""
    pasos = (ce or {}).get("steps") or []
    if not pasos:
        return []
    items = ", ".join(
        "{ titulo: " + json.dumps(p.get("title", ""), ensure_ascii=False)
        + ", contenido: (<>" + parrafos(p.get("text", "")) + "</>) }"
        for p in pasos)
    encabezado = f"<h4>{prosa(ce['title'])}</h4>" if ce.get("title") else ""
    return [encabezado, "<Accordion items={[" + items + "]} />"]


def bloque_bonus(bonus, avisos):
    """`content.bonus` → un `Accordion`: es material de consulta fuera de sesión."""
    if not bonus:
        return []
    dentro = parrafos(bonus.get("content", ""))
    dentro += "".join(bloque_code(bonus.get("code"), avisos))
    titulo = (bonus.get("title") or "Bonus").strip()
    return ["<Accordion items={[{ titulo: " + json.dumps(titulo, ensure_ascii=False)
            + ", contenido: (<>" + dentro + "</>) }]} />"]


# ---------------------------------------------------------- cuestionarios

# En el heredado, `feedback` sólo se ve al acertar: fallar da un «❌
# Incorrecto» genérico y deja reintentar. El `Quiz` de LP-CORE enseña la
# justificación a todo el mundo al enviar, así que la felicitación de cabecera
# se queda sin su condición y le diría «✅ Correcto» a quien acaba de fallar.
# Se recorta; lo que sigue es la explicación, que es lo que se quería guardar.
FELICITACION = re.compile(r"^\s*[✅✔]\s*[¡!]*\s*(Correcto|Exacto|Excelente|Crucial|Muy bien)"
                          r"[!.]*\s*", re.I)


def bloque_quiz(contenido, avisos):
    """`content.quiz` o `content.quizzes[]` → un `Quiz` de LP-CORE."""
    preguntas = list(contenido.get("quizzes") or [])
    if contenido.get("quiz"):
        preguntas.append(contenido["quiz"])
    if not preguntas:
        return []

    emitidas, recortadas = [], 0
    for q in preguntas:
        justificacion, n = FELICITACION.subn("", q.get("feedback", ""))
        recortadas += n
        if q.get("correct") is None:
            avisos.append(f"la pregunta «{q.get('question','')[:38]}» no dice cuál "
                          f"es la correcta — saldría sin ninguna marcada")
        opciones = ", ".join(
            "{ texto: " + json.dumps(o, ensure_ascii=False)
            + ", correcta: " + ("true" if i == q.get("correct") else "false") + " }"
            for i, o in enumerate(q.get("options") or []))
        emitidas.append("{ pregunta: " + json.dumps(q.get("question", ""), ensure_ascii=False)
                        + ", opciones: [" + opciones + "]"
                        + ", justificacion: " + json.dumps(justificacion.strip(), ensure_ascii=False)
                        + " }")

    if recortadas:
        avisos.append(f"{recortadas} justificaciones abrían con «✅ Correcto»: en el "
                      f"original sólo se veían al acertar, aquí las lee todo el mundo")

    return ['<Quiz titulo="Comprueba lo que entendiste" preguntas={[\n            '
            + ",\n            ".join(emitidas) + "\n        ]} />"]


# ------------------------------------------------- comparativas y glosario

def celda(valor):
    """Una celda: lista → viñetas; texto → prosa."""
    if isinstance(valor, list):
        return "<ul>" + "".join(f"<li>{prosa(str(v))}</li>" for v in valor) + "</ul>"
    return prosa(str(valor or ""))


def tabla(cabeceras, filas):
    cab = "".join(f"<th>{c}</th>" for c in cabeceras)
    cuerpo = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f"<table><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>"


def bloque_comparison(lista, avisos):
    """`content.comparison` → una tabla. Vienen en dos formas distintas.

    `.prose-lp` ya estiliza las tablas —se comprobó al migrar el módulo 11—,
    así que no hace falta componente ni CSS propio.
    """
    if not lista:
        return []
    claves = set(lista[0])
    if {"tool", "use", "detail"} <= claves:
        filas = [(f"{i.get('icon','')} {celda(i.get('tool'))}".strip(),
                  celda(i.get("use")), celda(i.get("detail"))) for i in lista]
        return [tabla(("Herramienta", "Para qué", "Detalle"), filas)]
    if {"title", "pros", "cons"} <= claves:
        filas = [(celda(i.get("title")), celda(i.get("pros")), celda(i.get("cons")),
                  celda(i.get("bestFor"))) for i in lista]
        return [tabla(("Opción", "A favor", "En contra", "Mejor para"), filas)]
    avisos.append(f"forma de `comparison` desconocida: {sorted(claves)} — no se emite")
    return []


def bloque_ejemplo_conceptual(ej, avisos):
    """`glossary.conceptualExample` → el antes y el después, uno tras otro.

    Es un par de fragmentos contrapuestos —`codeOld` abre con «❌ SIN
    CLASES» y `codeNew` con «✅ CON CLASES»—, así que los títulos salen de
    ahí y no hay que inventarlos. `Comparador` de LP-CORE parece el
    componente natural y no lo es: exige las cuatro versiones del código y
    una pregunta de opción múltiple, que aquí no existen.
    """
    if not ej:
        return ""
    fuera = ""
    if ej.get("title"):
        fuera += f"<h4>{prosa(ej['title'])}</h4>"
    if ej.get("description"):
        fuera += parrafos(ej["description"])
    for clave, defecto in (("codeOld", "Antes"), ("codeNew", "Después")):
        if not ej.get(clave):
            continue
        primera = ej[clave].strip().split("\n")[0].lstrip("# ").strip()
        fuera += "".join(bloque_code(
            {"snippet": ej[clave], "title": primera or defecto, "language": "python"},
            avisos))
    return fuera


def bloque_glossary(g, avisos):
    """`content.glossary` → un `Accordion` con la tabla de términos dentro."""
    items = (g or {}).get("items") or []
    if not items:
        return []
    dentro = tabla(("Término", "Definición"),
                   [(f"<code>{prosa(i.get('term',''))}</code>", celda(i.get("definition")))
                    for i in items])
    dentro += bloque_ejemplo_conceptual(g.get("conceptualExample"), avisos)
    titulo = (g.get("title") or "Glosario").strip()
    return ["<Accordion items={[{ titulo: " + json.dumps(titulo, ensure_ascii=False)
            + ", contenido: (<>" + dentro + "</>) }]} />"]


def bloque_resources(lista):
    """`content.resources` → la lista de lecturas del cierre."""
    if not lista:
        return []
    filas = "".join(
        f'<li><a href="{atributo(r.get("url",""))}" target="_blank" rel="noopener noreferrer">'
        f'{prosa(r.get("name",""))}</a> — {prosa(r.get("desc",""))}</li>'
        for r in lista)
    return ["<h4>Para seguir leyendo</h4>", f"<ul>{filas}</ul>"]


# -------------------------------------------------------------- la portada

def sin_estilos(frag):
    """Quita el `style=` en línea del heredado.

    Migrar es, entre otras cosas, dejar de pintar a mano: la portada trae el
    color, el tamaño y el interlineado en cada etiqueta, y quien los ponga
    ahora es LP-CORE. Además `limpiar_jsx` los convertiría en `style={{…}}`,
    que es mucho ruido para un estilo que no queremos.
    """
    return re.sub(r'\s*style="[^"]*"', "", frag or "")


def tramo_fase3(texto, cual):
    m = re.search(r'<section data-fase3="' + cual + r'".*?</section>', texto, re.S)
    return m.group(0) if m else None


def bloque_portada(texto, avisos):
    """La apertura y el reparto del tiempo, que viven fuera de `courseData`.

    Son HTML estático en el cuerpo del archivo, delante del armazón. No los
    ve el conversor de datos porque no están en el objeto, y son justamente lo
    que sitúa la sesión: el gancho de por qué importa la semana y en qué se va
    el tiempo. Perderlos sería perder la parte más escrita del material.
    """
    partes = []

    apertura = tramo_fase3(texto, "apertura")
    if apertura:
        gancho = re.search(r"<h2[^>]*>(.*?)</h2>", apertura, re.S)
        cuerpo = "\n".join(f"<p>{prosa(sin_estilos(p))}</p>" for p in
                           re.findall(r"<p[^>]*>(.*?)</p>", apertura, re.S))
        titulo = texto_llano(gancho.group(1)) if gancho else "Antes de empezar"
        partes.append(f'<Motivacion gancho="{atributo(titulo)}">\n{cuerpo}\n</Motivacion>')

    reparto = tramo_fase3(texto, "reparto")
    if not reparto:
        avisos.append("no hay bloque `data-fase3=\"reparto\"`: la portada sale sin "
                      "el reparto del tiempo de la sesión")
        return partes

    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", reparto, re.S)
    if h2:
        partes.append(f"<h3>{prosa(texto_llano(h2.group(1)))}</h3>")
    entradilla = re.search(r"</h2>\s*<p[^>]*>(.*?)</p>", reparto, re.S)
    if entradilla:
        partes.append(f"<p>{prosa(sin_estilos(entradilla.group(1)))}</p>")

    # Las tres columnas —exposición, práctica, consulta— con su reparto y su
    # lista. En tabla, que es lo que `.prose-lp` ya sabe pintar.
    filas = []
    for col in re.split(r'<div style="flex:1 1 220px[^"]*">', reparto)[1:]:
        rotulos = re.findall(r"<div[^>]*>([^<]+)</div>", col)
        items = re.findall(r"<li[^>]*>(.*?)</li>", col, re.S)
        if len(rotulos) >= 2:
            filas.append((prosa(rotulos[0].strip()), prosa(rotulos[1].strip()),
                          "<ul>" + "".join(f"<li>{prosa(sin_estilos(i))}</li>"
                                           for i in items) + "</ul>"))
    if filas:
        partes.append(tabla(("Momento", "Tiempo", "Qué se hace"), filas))
    else:
        avisos.append("el reparto no trae las tres columnas donde se esperaban")

    # La nota final, después del contenedor de columnas.
    nota = re.findall(r"</div>\s*<p[^>]*>(.*?)</p>\s*</section>", reparto, re.S)
    if nota:
        partes.append(f'<Box type="info" label="Cómo leer este reparto">'
                      f"<p>{prosa(sin_estilos(nota[-1]))}</p></Box>")
    return partes


# -------------------------------------------------------------- gráficas

# La paleta y la tipografía que ya usan las gráficas de los módulos 10, 11 y
# 12, para que las tres familias de material se vean iguales.
TIPOGRAFIA = {"family": "Montserrat, Helvetica Neue, Arial, sans-serif",
              "size": 12, "color": "#1E293B"}
MORADO, ROSA = "#3D008D", "#ED1E79"


def grafica_jsx(chart, sid, avisos):
    """`content.chartData` de Chart.js → un componente con `usePlotly`.

    Aquí no hay que analizar marcado: en 10/11/12 la gráfica llegaba como
    salida de `plotly.io.to_html` y había que rescatar el JSON de dentro de un
    `<script>`; estos módulos la declaran como datos. La traducción es de
    vocabulario: `bar` es `bar` y `radar` es `scatterpolar` cerrado sobre sí
    mismo.
    """
    tipo = chart.get("type")
    etiquetas, valores = chart.get("labels") or [], chart.get("data") or []

    if tipo == "bar":
        data = [{"type": "bar", "x": etiquetas, "y": valores,
                 "name": chart.get("label", ""),
                 "marker": {"color": MORADO, "line": {"color": ROSA, "width": 1}},
                 "hovertemplate": "<b>%{x}</b><br>%{y}<extra></extra>"}]
        # `automargin` es lo que faltaba en la pirámide del módulo 11, donde
        # la etiqueta se salía 21 px. Allí se conservó el defecto porque
        # migrar no es editar; aquí la gráfica se genera de cero y no hay
        # nada que conservar.
        disposicion = {"xaxis": {"automargin": True},
                       "yaxis": {"title": {"text": chart.get("label", "")},
                                 "automargin": True},
                       "showlegend": False}
    elif tipo == "radar":
        data = [{"type": "scatterpolar", "r": valores, "theta": etiquetas,
                 "fill": "toself", "name": chart.get("label", ""),
                 "marker": {"color": MORADO}, "line": {"color": MORADO},
                 "hovertemplate": "<b>%{theta}</b><br>%{r} "
                                  + chart.get("unidad", "") + "<extra></extra>"}]
        disposicion = {"polar": {"radialaxis": {"visible": True,
                                                "range": [0, chart.get("max") or max(valores or [1])]}},
                       "showlegend": False}
    else:
        avisos.append(f"tipo de gráfica «{tipo}» sin traducción a Plotly — se omite")
        return None, None

    if chart.get("titulo"):
        disposicion["title"] = {"text": f"<b>{chart['titulo']}</b>", "x": 0.0,
                                "xanchor": "left", "font": {"size": 15, "color": "#1E293B"}}
    disposicion["font"] = TIPOGRAFIA
    disposicion["margin"] = {"l": 60, "r": 40, "t": 70 if chart.get("titulo") else 30, "b": 50}

    cid = f"chart-{sid}"
    comp = "Grafica" + "".join(p.capitalize() for p in re.split(r"[-_]", sid))
    fuente = (f"        const {comp} = ({{ caption }}) => {{\n"
              f"            usePlotly('{cid}',\n"
              f"                () => {a_js(data, 4)},\n"
              f"                () => ({a_js(disposicion, 4)}), []);\n"
              f'            return <ChartFrame id="{cid}" height="chart-h-360" caption={{caption}} />;\n'
              f"        }};")
    pie = " ".join(re.sub(r"<[^>]+>", "", chart.get("description") or "").split())
    uso = f'<{comp} caption="{atributo(pie)}" />' if pie else f"<{comp} />"
    return fuente, uso


# ------------------------------------------------------------- la sección

# El orden en que el heredado pinta los bloques no es el mismo en los dos
# módulos, así que se fija uno y se aplica a los dos. Sigue el arco de la
# sección: se explica, se ilustra, se compara, se muestra el código, se
# comprueba lo aprendido y se deja lo accesorio al final.
ORDEN = ("concept", "chartData", "comparison", "code", "codeExplanation",
         "quiz", "quizzes", "glossary", "bonus", "resources")


def seccion_jsx(modulo, avisos, grafica=None):
    """Un `module` del `courseData` → el JSX de una sección de LP-CORE."""
    c = modulo.get("content") or {}
    emitido, partes = set(), []

    for clave in ORDEN:
        if clave not in c or clave in emitido:
            continue
        if clave == "concept":
            partes += bloque_concept(c["concept"], avisos)
        elif clave == "chartData":
            partes.append(grafica or "")
        elif clave == "comparison":
            partes += bloque_comparison(c["comparison"], avisos)
        elif clave == "code":
            partes += bloque_code(c["code"], avisos)
        elif clave == "codeExplanation":
            partes += bloque_code_explanation(c["codeExplanation"])
        elif clave in ("quiz", "quizzes"):
            partes += bloque_quiz(c, avisos)
            emitido |= {"quiz", "quizzes"}
        elif clave == "glossary":
            partes += bloque_glossary(c["glossary"], avisos)
        elif clave == "bonus":
            partes += bloque_bonus(c["bonus"], avisos)
        elif clave == "resources":
            partes += bloque_resources(c["resources"])
        emitido.add(clave)

    for clave in c:
        if clave not in emitido:
            avisos.append(f"«{clave}» no se traduce — no hay regla para esa clave")

    return "\n\n".join(p for p in partes if p and p.strip())


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--salida", type=Path, help="carpeta de piezas; escribe datos.json")
    p.add_argument("--volcar", action="store_true",
                   help="imprime el JSON por la salida estándar y termina")
    args = p.parse_args()

    if not args.archivo.exists():
        print(f"ERROR: no existe {args.archivo}", file=sys.stderr)
        return 1
    if not args.salida and not args.volcar:
        print("ERROR: indique --salida o --volcar.", file=sys.stderr)
        return 2
    if not shutil.which("node"):
        print("ERROR: hace falta Node para leer `courseData`, que es JavaScript y no\n"
              "       JSON: trae plantillas literales, comas finales y claves sin\n"
              "       comillas. Instale Node o ejecute este paso en una máquina que\n"
              "       lo tenga y comparta el datos.json que produce.", file=sys.stderr)
        return 1

    texto = args.archivo.read_text(encoding="utf-8")
    avisos = []
    datos, intentos = extraer(texto, avisos)

    if datos is None:
        if intentos == 0:
            print(f"ERROR: {args.archivo.name} no declara `const courseData = {{…}}`.\n"
                  f"       Este guion es para los módulos 1 y 2. Para los que traen\n"
                  f"       <section id=…> use convertir.py.", file=sys.stderr)
        else:
            print(f"ERROR: se encontró `courseData` pero ninguno de los {intentos} cierres\n"
                  f"       candidatos parsea como objeto con `modules`. Compruebe que el\n"
                  f"       literal está completo.", file=sys.stderr)
        return 1

    if args.volcar:
        print(json.dumps(datos, ensure_ascii=False, indent=2))
        return 0

    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "datos.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    (args.salida / "jsx").mkdir(exist_ok=True)

    # La portada va antes que nada y no sale del `courseData`, sino del HTML
    # estático que hay delante del armazón.
    propios = []
    portada = "\n\n".join(p for p in bloque_portada(texto, propios) if p.strip())
    if portada:
        (args.salida / "jsx" / "portada.jsx").write_text(portada, encoding="utf-8")
        print(f"{'OK  ' if not propios else 'AVISO'} portada "
              f"{len(portada.splitlines()):4d} líneas · "
              f"{portada.count('<Motivacion'):2d} Motivacion · "
              f"{portada.count('<table'):2d} tabla", file=sys.stderr)
        for a in propios:
            print(f"        · {a}", file=sys.stderr)
        avisos += propios

    graficas = []
    for m in datos["modules"]:
        sid = m.get("id") or "?"
        propios = []

        uso = None
        chart = (m.get("content") or {}).get("chartData")
        if chart:
            fuente, uso = grafica_jsx(chart, sid, propios)
            if fuente:
                graficas.append(fuente)

        jsx = seccion_jsx(m, propios, grafica=uso)
        (args.salida / "jsx" / f"{sid}.jsx").write_text(jsx, encoding="utf-8")
        print(f"{'OK  ' if not propios else 'AVISO'} {sid:7s} "
              f"{len(jsx.splitlines()):4d} líneas · "
              f"{jsx.count('<Box'):2d} Box · {jsx.count('<CodeBlock'):2d} CodeBlock · "
              f"{jsx.count('<Quiz'):2d} Quiz · {jsx.count('<Accordion'):2d} Accordion · "
              f"{jsx.count('<table'):2d} tabla", file=sys.stderr)
        for a in propios:
            print(f"        · {a}", file=sys.stderr)
        avisos += propios

    # `montar.py` inserta este archivo tal cual entre sus centinelas, así que
    # se escribe siempre: vacío significa «este módulo no tiene gráficas», y
    # es la forma de que un módulo que las pierda no arrastre las de antes.
    (args.salida / "graficas.jsx").write_text(
        "\n\n".join(graficas) + ("\n" if graficas else ""), encoding="utf-8")

    print(f"\n{len(datos['modules'])} secciones → {args.salida}/jsx/ · "
          f"{len(graficas)} gráficas · {len(avisos)} avisos por revisar", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
