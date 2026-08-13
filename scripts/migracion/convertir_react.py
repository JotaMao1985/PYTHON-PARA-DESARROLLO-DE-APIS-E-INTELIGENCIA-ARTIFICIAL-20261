#!/usr/bin/env python3
"""
Convierte un módulo heredado de la familia `curriculum` en secciones de
LP-CORE.

Los módulos 3, 4 y 6 ya son aplicaciones de React con Babel en el navegador
—el mismo montaje que LP-CORE— y ya tienen un `const curriculum = [...]` con
la forma que LP-CORE espera. Aquí no se traduce HTML a JSX: **el JSX ya está
escrito**. Lo que cambia es de quién es el armazón.

Por eso este guion hace menos que los otros dos, y a propósito. Cada entrada
del `curriculum` heredado es

    { id, title, codeTitle, icon, content: (<div>…</div>), pythonCode: `…` }

y de ahí sale una sección: `content` tal cual —ya es JSX válido— más un
`CodeBlock` con `codeTitle` y `pythonCode`. Lo único que se traduce es
`div.tip-box` → `Box`, porque es la caja del heredado y LP-CORE tiene la suya.

**Lo que no se toca: el `content`.** Es JSX escrito a mano, con sus
expresiones y sus comentarios `{/* … */}`. Pasarlo por `escapar_jsx` —que es
lo que se hace con el HTML de las otras dos familias— lo rompería: escaparía
las llaves que sí son de JSX. Se copia literal.

Los componentes propios del módulo —el `AIClassBuilder` del 3, el `Quiz` del
4, el `ComparisonDiagram` del 6— **no los mueve este guion**. Adaptar un
componente a un sitio distinto del que se escribió es un juicio, no una
transformación: el del módulo 3 vivía en un panel lateral de 384 px que en
LP-CORE no existe. Viven a mano en `componentes/modulo_N.jsx`, que se versiona,
y los estampa `montar.py`.

Uso:
    python3 scripts/migracion/convertir_react.py <archivo.html> --salida dir/
"""

import argparse
import json
import re
import sys
from pathlib import Path

from convertir import atributo, texto_plano
from convertir_plano import fin_elemento, tipo_de_caja
# El emisor de cuestionarios de los módulos 1 y 2, tal cual: la forma de
# `quizQuestions` es la misma que la de `courseData.quizzes` salvo el nombre de
# un campo, y con él viene gratis el recorte de la felicitación.
from convertir_datos import bloque_quiz

# Qué componente propio acompaña a cada `interactiveType`.
#
# En el módulo 3 sólo hay uno, y no es por pobreza del material: el heredado
# trae un «Laboratorio de Datos» completo —entrada de datos, media, mediana,
# varianza poblacional y muestral— gobernado por los otros cinco valores de
# `interactiveType`, y **no se ve nunca**. El panel derecho está detrás de
# `interactiveType === 'ai_builder'`, y dentro vuelve a preguntar lo mismo:
# la rama del laboratorio es inalcanzable. Se comprobó en el DOM de la página
# publicada, sección por sección. No se migra lo que no se publicaba.
ACOMPANANTES = {
    "ai_builder": "<AIClassBuilder />",
}

# La única frase que se reescribe, y por lo mismo que se recortaba la
# felicitación de las justificaciones en los módulos 1 y 2: **la traducción le
# quita el referente**. El heredado pone el constructor en un panel lateral de
# 384 px y el texto manda al estudiante «al panel derecho» tres veces. En
# LP-CORE la sección es una columna, así que el panel no existe y esa
# indicación deja de señalar nada.
SIN_PANEL = ("panel derecho", "constructor de abajo")

# Iconos que el contenido usa como componente —`<Icons.Structure size={18} />`—
# y que LP-CORE no tiene con ese nombre. Traducirlos no es cosmética: escrito
# así, un icono inexistente es `undefined` en posición de componente, y React
# no lo ignora como haría `renderIcon`, sino que tira la página entera con un
# «Minified React error #130». El de la receta falla en silencio; éste, a lo
# bruto.
#
# La firma es la misma —`{ size, className }`—, así que la sustitución es
# directa. `Structure` son cuatro cuadrados y `Grid` una rejilla con líneas:
# no son el mismo dibujo, pero sí la misma idea y el mismo tamaño.
ICONOS = {
    "Structure": "Grid",
}


def fin_de_linea_con(texto, desde, patron):
    """Índice del final de la primera línea que case `patron` desde `desde`.

    El `curriculum` viene formateado con una indentación regular —el `)` que
    cierra un `content` está siempre a dieciséis espacios—, y eso vale más que
    un analizador de JavaScript: contar paréntesis obliga a saber si el que se
    está mirando va dentro de una cadena, y la prosa del material lleva
    comillas simples en castellano y en los ejemplos de código.
    """
    m = re.compile(patron, re.M).search(texto, desde)
    return (m.start(), m.end()) if m else (None, None)


def entradas(cuerpo, avisos):
    """Las entradas del `const curriculum = [...]`, con sus campos crudos."""
    ini = cuerpo.index("const curriculum = [")
    # Hasta la siguiente declaración de primer nivel, no hasta `const App`.
    # Entre las dos puede haber más: el módulo 4 declara ahí su `quizQuestions`,
    # que está indentado igual que una entrada del curriculum y se colaba como
    # cinco secciones sin `id`.
    siguiente = re.search(r"\n        const \w+\s*=", cuerpo[ini + 20:])
    fin = ini + 20 + siguiente.start() if siguiente else len(cuerpo)
    cur = cuerpo[ini:fin]

    for m in re.finditer(r"^            \{$", cur, re.M):
        siguiente = re.compile(r"^            \{$", re.M).search(cur, m.end())
        trozo = cur[m.start():siguiente.start() if siguiente else len(cur)]

        d = {}
        for campo in ("id", "title", "codeTitle", "icon", "interactiveType"):
            v = re.search(r"\b" + campo + r":\s*'((?:[^'\\]|\\.)*)'", trozo)
            if v:
                d[campo] = v.group(1).replace("\\'", "'")
        for bandera in ("isQuiz", "isReference"):
            d[bandera] = bool(re.search(r"\b" + bandera + r":\s*true\b", trozo))

        c = re.search(r"^                content: \($", trozo, re.M)
        if c:
            _, cierre = fin_de_linea_con(trozo, c.end(), r"^                \),?$")
            d["content"] = trozo[c.end():cierre].rsplit("\n", 1)[0].strip("\n")

        p = trozo.find("                pythonCode: `")
        if p != -1:
            arranque = p + len("                pythonCode: `")
            j = arranque
            while j < len(trozo):
                j = trozo.find("`", j)
                if j == -1:
                    break
                if trozo[j - 1] != "\\":
                    break
                j += 1
            d["pythonCode"] = trozo[arranque:j] if j != -1 else ""
            if j == -1:
                avisos.append(f"el `pythonCode` de «{d.get('id')}» no cierra su "
                              f"plantilla literal")

        if not d.get("id"):
            avisos.append("una entrada del curriculum no declara `id`; se deja fuera")
            continue
        yield d


def cuestionario(cuerpo, avisos):
    """El `quizQuestions` del módulo, listo para el `Quiz` de LP-CORE.

    Está fuera del `curriculum` —es un array aparte— y la entrada que lo pinta
    sólo se marca con `isQuiz: true`. Se lee con `json.loads` después de
    entrecomillar las claves: son cadenas con comillas dobles, sin comas
    finales y sin plantillas literales, así que es JSON con las claves
    desnudas y no hace falta Node.

    Devuelve (jsx, título) o (None, None) si el módulo no trae cuestionario.
    """
    m = re.search(r"const quizQuestions\s*=\s*(\[.*?\n        \];)", cuerpo, re.S)
    if not m:
        return None, None
    try:
        crudo = json.loads(re.sub(r"(\n\s*)(\w+):", lambda x: f'{x.group(1)}"{x.group(2)}":',
                                  m.group(1).rstrip().rstrip(";")))
    except json.JSONDecodeError as e:
        avisos.append(f"`quizQuestions` no se pudo leer como JSON ({e}); el "
                      f"cuestionario se queda fuera")
        return None, None

    # El rótulo lo pone el App, no el `curriculum`, así que se saca de ahí.
    h3 = re.search(r"isQuiz \?[\s\S]{0,800}?<h3[^>]*>([^<]+)</h3>", cuerpo)
    titulo = " ".join(h3.group(1).split()) if h3 else None

    # `bloque_quiz` espera `feedback` donde este módulo escribe `explanation`.
    preguntas = [dict(q, feedback=q.get("explanation", "")) for q in crudo]
    jsx = bloque_quiz({"quizzes": preguntas}, avisos,
                      **({"titulo": titulo} if titulo else {}))
    return ("\n\n".join(jsx) if jsx else None), titulo


def convertir_cajas(cuerpo):
    """`div.tip-box` → `Box`, con el rótulo en negrita como etiqueta.

    Es la misma caja que en la familia de los artículos y se traduce igual,
    sólo que aquí el atributo ya viene escrito `className`, porque el origen
    es JSX y no HTML.

    Sólo los `<div>`: el módulo 4 marca también un `<li>` con esa clase, y
    sacarlo de su `<ul>` para meterlo en un `Box` rompería la lista. Ése se
    queda como está, y su CSS lo rescata `estilos.py`.

    La clase no tiene por qué ir primero. En los módulos 3, 4 y 6 siempre va,
    pero buscar `className="tip-box…` habría fallado en silencio el día que no
    —y una caja sin convertir no se nota: se ve igual, con el CSS heredado—.
    """
    while True:
        m = re.search(r'<div\s[^>]*className="[^"]*\btip-box\b[^"]*"[^>]*>', cuerpo)
        if not m:
            return cuerpo
        fin = fin_elemento(cuerpo, m.start(), "div")
        if not fin:
            return cuerpo
        interior = cuerpo[m.end():fin - len("</div>")]

        rotulo = re.match(r'\s*<strong[^>]*>(.*?)</strong>', interior, re.S)
        etiqueta = (" ".join(texto_plano(rotulo.group(1)).split()).rstrip(":")
                    if rotulo else None)
        tipo = tipo_de_caja((etiqueta or texto_plano(interior)[:120]).lower())
        if rotulo:
            interior = interior[rotulo.end():].lstrip()
        attr = f' label="{atributo(etiqueta)}"' if etiqueta else ""
        cuerpo = (cuerpo[:m.start()] + f'<Box type="{tipo}"{attr}>' + interior
                  + "</Box>" + cuerpo[fin:])


def seccion_jsx(entrada, avisos, quiz=None):
    """Una entrada del `curriculum` heredado → el cuerpo de una sección."""
    partes = []
    viejo, nuevo = SIN_PANEL
    reescritas = 0

    # La entrada del cuestionario no trae ni `content` ni `pythonCode`: sólo
    # se marca, y el contenido vive en el array de al lado.
    if entrada.get("isQuiz"):
        if quiz:
            return quiz
        avisos.append("la sección está marcada `isQuiz` y el módulo no trae un "
                      "`quizQuestions` legible: saldría vacía")
        return ""

    contenido = convertir_cajas(entrada.get("content", ""))
    contenido, n = re.subn(viejo, nuevo, contenido)
    reescritas += n

    def un_icono(m):
        if m.group(1) in ICONOS:
            return "<Icons." + ICONOS[m.group(1)]
        avisos.append(f"el contenido usa `<Icons.{m.group(1)}>`, que no está en la "
                      f"tabla de equivalencias: si LP-CORE tampoco lo tiene, la "
                      f"página sale en blanco")
        return m.group(0)
    contenido = re.sub(r"<Icons\.(\w+)", un_icono, contenido)
    if contenido.strip():
        partes.append(contenido)

    acompanante = ACOMPANANTES.get(entrada.get("interactiveType"))
    if acompanante:
        partes.append(acompanante)

    codigo = entrada.get("pythonCode", "")
    codigo, n = re.subn(viejo, nuevo, codigo)
    reescritas += n
    if reescritas:
        avisos.append(f"{reescritas} veces «{viejo}» → «{nuevo}»: el panel lateral "
                      f"del heredado no existe en LP-CORE")
    if codigo.strip():
        titulo = entrada.get("codeTitle")
        attr = f'title="{atributo(titulo)}" ' if titulo else ""
        # El literal se copia tal cual: ya está escrito para vivir dentro de
        # una plantilla de JS —el heredado también lo guardaba así—, con sus
        # `\n` escapados donde los tenía.
        partes.append(f'<CodeBlock {attr}lang="python" code={{`{codigo}`}} />')
    else:
        avisos.append(f"«{entrada['id']}» no trae `pythonCode`")

    return "\n\n".join(partes)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--salida", type=Path, help="carpeta donde escribir los .jsx")
    args = p.parse_args()

    if not args.archivo.exists():
        print(f"ERROR: no existe {args.archivo}", file=sys.stderr)
        return 1

    texto = args.archivo.read_text(encoding="utf-8")
    m = re.search(r'<script type="text/babel">(.*?)</script>', texto, re.S)
    if not m or "const curriculum = [" not in m.group(1):
        print("ERROR: el archivo no declara `const curriculum = [` dentro de un\n"
              "       <script type=\"text/babel\">. Este guion es para los módulos 3,\n"
              "       4 y 6. Para los que traen <article id=…> use convertir_plano.py.",
              file=sys.stderr)
        return 1

    avisos_globales = []
    lista = list(entradas(m.group(1), avisos_globales))
    # El cuestionario se lee una vez: vive fuera del `curriculum` y lo comparten
    # todas las entradas marcadas `isQuiz` (en la práctica, una).
    quiz, titulo_quiz = cuestionario(m.group(1), avisos_globales)
    if args.salida:
        (args.salida / "jsx").mkdir(parents=True, exist_ok=True)

    titulos, total = {}, 0
    for e in lista:
        avisos = []
        jsx = seccion_jsx(e, avisos, quiz)
        titulos[e["id"]] = e.get("title", "")
        if args.salida:
            (args.salida / "jsx" / f"{e['id']}.jsx").write_text(jsx, encoding="utf-8")
        else:
            print(jsx)
        acomp = ACOMPANANTES.get(e.get("interactiveType"))
        print(f"{'OK  ' if not avisos else 'AVISO'} {e['id']:18s} "
              f"{len(jsx.splitlines()):4d} líneas · {jsx.count('<CodeBlock'):2d} CodeBlock · "
              f"{jsx.count('<Box'):2d} Box"
              + (f" · {jsx.count('pregunta:')} preguntas" if e.get("isQuiz") else "")
              + (f" · {acomp}" if acomp else ""), file=sys.stderr)
        for a in avisos:
            print(f"        · {a}", file=sys.stderr)
        total += len(avisos)

    # Los `interactiveType` que no llevan a ninguna parte. Se dicen en voz alta
    # porque quien lea el heredado los verá y pensará que falta migrarlos.
    muertos = sorted({e.get("interactiveType") for e in lista
                      if e.get("interactiveType")} - set(ACOMPANANTES))
    if muertos:
        print(f"\nNOTA: {len(muertos)} valores de `interactiveType` sin componente "
              f"({', '.join(muertos)}).\n      Compruebe EN LA PÁGINA PUBLICADA si "
              f"pintaban algo antes de darlos por\n      perdidos. En el módulo 3 no: "
              f"el panel que los leía estaba detrás de una\n      condición que sólo "
              f"cumplía `ai_builder`, así que cinco de los seis eran\n      código "
              f"muerto. En otro módulo puede no ser así.", file=sys.stderr)

    if args.salida:
        (args.salida / "titulos.json").write_text(
            json.dumps(titulos, ensure_ascii=False, indent=1), encoding="utf-8")

    for a in avisos_globales:
        print(f"        · {a}", file=sys.stderr)
    print(f"\n{len(lista)} secciones · {total + len(avisos_globales)} avisos por revisar",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
