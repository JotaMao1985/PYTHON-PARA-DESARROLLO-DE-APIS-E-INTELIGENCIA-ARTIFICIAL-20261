#!/usr/bin/env python3
"""
Convierte una `<section>` del material heredado en un componente de sección
de LP-CORE.

El material de este curso es HTML estático con un vocabulario propio: cajas
`div.box`, resaltado de sintaxis escrito a mano dentro de `<pre>` (`kw`,
`str`, `df-instr`, `sh-prompt`…) y gráficas incrustadas como salida de
`plotly.io.to_html`. LP-CORE espera JSX con `Box`, `CodeBlock` y `ChartFrame`.
La traducción es mecánica y se repite en trece módulos, así que se automatiza.

Lo que el guion NO decide por su cuenta, y por eso deja marcas `TODO`:

  · El `lang` de un bloque cuando la heurística no llega a una respuesta
    clara. Adivinar mal es peor que preguntar: el bloque saldría resaltado
    con la gramática equivocada, que es más confuso que sin resaltar.
  · Los pares ejercicio/solución, que se emiten como `Box` + `Accordion`
    pero cuyo enunciado conviene revisar a mano.
  · Las gráficas, que se sustituyen por una llamada al componente y hay
    que haber generado antes con `graficas.py`.

Uso:
    python3 scripts/migracion/convertir.py <archivo.html> [--seccion id]
    python3 scripts/migracion/convertir.py <archivo.html> --todas --salida dir/
"""

import argparse
import html
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------- cajas
# `div.box <tipo>` del material heredado → `type` de `Box` en LP-CORE.
# `Box` solo conoce info/tip/warn/danger; cualquier otro valor cae a info en
# silencio, así que el mapa es explícito y lo que no esté aquí se avisa.
TIPO_BOX = {
    "info": "info",
    "tip": "tip",
    "warn": "warn",
    "danger": "danger",
    "exercise": "info",    # el enunciado; la solución va aparte, en Accordion
    "solution": None,      # se absorbe en el Accordion del ejercicio anterior
}

# Clases del resaltado escrito a mano. Se borran: las rehace Prism.
CLASES_RESALTADO = {
    "kw", "str", "cm", "num", "fn", "builtin", "op", "var", "unit",
    "df-instr", "df-arg", "df-path", "df-flag",
    "sh-prompt", "sh-cmd", "sh-out",
}


def texto_plano(fragmento):
    """Quita todo el marcado y devuelve el texto tal cual se escribiría."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragmento))


def detectar_lang(codigo):
    """Gramática del bloque, o None si no hay una respuesta clara.

    Devolver None a propósito es parte del diseño: un bloque etiquetado con
    la gramática equivocada se resalta mal, y eso despista más que el texto
    sin resaltar. Los None salen como TODO para que alguien decida.
    """
    s = codigo.strip()
    if not s:
        return "text"

    # Archivos que se nombran a sí mismos en la primera línea y no tienen
    # gramática: son listas de rutas o de paquetes.
    primera = s.split("\n")[0].strip()
    if re.match(r"^#\s*\.?(dockerignore|gitignore|env\b)", primera) or \
       re.match(r"^#\s*requirements(\.[\w.]+)?\b", primera):
        return "text"

    # Dockerfile: basta con `FROM` al principio de línea, o con dos o más
    # instrucciones. Exigir ambas cosas dejaba fuera los fragmentos que el
    # material usa para señalar un antipatrón, que empiezan por COPY.
    instr = len(re.findall(r"^\s*(RUN|COPY|CMD|ENTRYPOINT|WORKDIR|EXPOSE|ENV|USER|ARG)\s", s, re.M))
    if re.search(r"^\s*FROM\s+\S", s, re.M) or instr >= 2:
        return "dockerfile"

    # JSON: se ignoran los comentarios de cabecera que el material añade
    # encima (`# app/modelo.json — …`), que no son parte del JSON.
    cuerpo = "\n".join(l for l in s.split("\n") if not l.strip().startswith("#")).strip()
    if cuerpo.startswith(("{", "[")) and '":' in cuerpo:
        return "json"
    if re.search(r"^\s*(SELECT|CREATE TABLE|INSERT INTO|ALTER TABLE)\b", s, re.I | re.M):
        return "sql"
    if re.search(r"^(name|on|jobs|services|runtime|envVars):", s, re.M) or \
       re.search(r"^\s+-\s+(uses|run|name):", s, re.M):
        return "yaml"
    if re.search(r"^\s*\[[\w.\-]+\]\s*$", s, re.M) and re.search(r"^[\w.\-]+\s*=", s, re.M):
        return "toml"
    if re.search(r"^\s*(import |from [\w.]+ import|def |class |@app\.|@router\.|async def|if __name__)", s, re.M):
        return "python"
    # Shell: o lleva el prompt, o la primera línea útil es un comando conocido.
    if re.search(r"^\s*\$ ", s, re.M):
        return "shell"
    util = next((l for l in s.split("\n") if l.strip() and not l.strip().startswith("#")), "")
    if re.match(r"^(pip|python3?|docker|uvicorn|curl|git|cd |ls |export |pytest|"
                r"alembic|source |mkdir|apt|sudo|chmod|echo|cat )", util.strip()):
        return "shell"
    # Un bloque que solo son comentarios y rutas suele ser un árbol de archivos.
    if re.search(r"├──|└──", s):
        return "text"
    return None


def titulo_de(codigo):
    """Título del bloque, si la primera línea nombra un archivo.

    El material comenta el nombre del archivo arriba (`# Dockerfile`,
    `# .github/workflows/ci.yml`). Sirve de título y así no se repite.
    """
    primera = codigo.strip().split("\n")[0].strip()
    m = re.match(r"^(?:#|//|--)\s*([\w./-]+\.\w+|Dockerfile|\.dockerignore)\b", primera)
    return m.group(1) if m else None


def escapar_jsx(texto):
    """Llaves literales de la prosa, que en JSX abrirían una expresión.

    El material las usa al citar JSON dentro de un `<code>`: escrito
    `{"version": "0.1.0"}`, Babel lee `"version"` como expresión y falla al
    encontrar los dos puntos. Se llama en el único momento en que el
    fragmento no tiene todavía ninguna llave propia: con los bloques de
    código ya apartados y antes de generar `Accordion` o `style`.
    """
    return texto.replace("{", "&#123;").replace("}", "&#125;")


def convertir_pre(m, avisos):
    """`<pre><code>…</code></pre>` → `<CodeBlock … />`."""
    codigo = texto_plano(m.group(1)).strip("\n")
    lang = detectar_lang(codigo)
    if lang is None:
        avisos.append(f"lang sin determinar para el bloque que empieza por "
                      f"«{codigo.strip()[:46]}…»")
        lang = "text"
        marca = "  /* TODO revisar lang */"
    else:
        marca = ""
    titulo = titulo_de(codigo)
    attr_titulo = f'title="{titulo}" ' if titulo else ""
    # Las comillas invertidas y `${` romperían la plantilla literal de JS.
    seguro = codigo.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return (f'<CodeBlock {attr_titulo}lang="{lang}" code={{`{seguro}`}} />{marca}')


def convertir_boxes(cuerpo, avisos):
    """`div.box` → `Box`, y los pares ejercicio/solución → `Box` + `Accordion`."""

    def uno(m):
        clases = m.group(1).split()
        cuerpo_box = m.group(2)
        tipos = [c for c in clases if c != "box"]
        tipo_orig = tipos[0] if tipos else "info"
        if tipo_orig not in TIPO_BOX:
            avisos.append(f"tipo de caja desconocido: «{tipo_orig}» — se deja como info")
        tipo = TIPO_BOX.get(tipo_orig, "info")
        if tipo is None:      # solution: la absorbe el ejercicio
            return m.group(0)
        etq = re.search(r'<span class="label">(.*?)</span>', cuerpo_box, re.S)
        label = texto_plano(etq.group(1)).strip() if etq else None
        resto = re.sub(r'<span class="label">.*?</span>', "", cuerpo_box, count=1, flags=re.S)
        attr = f' label="{label}"' if label else ""
        return f'<Box type="{tipo}"{attr}>{resto}</Box>'

    return re.sub(r'<div class="box ([^"]*)">(.*?)</div>', uno, cuerpo, flags=re.S)


def emparejar_ejercicios(cuerpo):
    """Cada `box solution` pasa a un `Accordion` pegado a su ejercicio.

    En el original la solución está a la vista, justo debajo del enunciado.
    Plegarla es deliberado: el material dice «conviene intentar cada
    ejercicio antes de ver la retroalimentación», y con la solución visible
    esa recomendación no se sostiene sola.
    """
    def uno(m):
        interior = m.group(1)
        etq = re.search(r'<span class="label">(.*?)</span>', interior, re.S)
        titulo = texto_plano(etq.group(1)).strip() if etq else "Solución comentada"
        resto = re.sub(r'<span class="label">.*?</span>', "", interior, count=1, flags=re.S)
        return ('<Accordion items={[{ titulo: ' + repr(titulo).replace("'", "'")
                + ', contenido: (<>' + resto.strip() + '</>) }]} />')

    return re.sub(r'<div class="box solution">(.*?)</div>', uno, cuerpo, flags=re.S)


# Etiquetas que fluyen dentro del párrafo. El salto de línea junto a una de
# ellas es donde JSX se aparta de HTML, así que hay que tratarlas aparte.
INLINE = r"(?:code|strong|em|b|i|a|span|sub|sup|abbr|small|Termino)"


def recuperar_espacios(cuerpo):
    """Repone los espacios que JSX descarta y HTML sí respeta.

    En HTML, cualquier hueco con salto de línea vale por un espacio. JSX, en
    cambio, borra el hueco cuando toca una etiqueta, de modo que

        <code>CMD</code>
        permite pasar argumentos

    se lee «CMDpermite». No da error y no se ve en el código fuente: solo
    aparece leyendo la página. En este módulo eran 79 palabras pegadas.
    """
    cuerpo = re.sub(r"(</" + INLINE + r">)\s*\n\s*(?=[^\s<])", r"\1 ", cuerpo)
    cuerpo = re.sub(r"([^\s>])\s*\n\s*(?=<" + INLINE + r"\b)", r"\1 ", cuerpo)
    return cuerpo


def limpiar_jsx(cuerpo):
    """Ajustes de sintaxis para que el fragmento sea JSX válido."""
    cuerpo = recuperar_espacios(cuerpo)
    # Etiquetas vacías que en HTML se cierran solas y en JSX no.
    cuerpo = re.sub(r"<(br|hr)\s*/?>", r"<\1 />", cuerpo)
    cuerpo = re.sub(r"<img([^>]*?)/?>", r"<img\1 />", cuerpo)
    # `class` y `for` son palabras reservadas.
    cuerpo = re.sub(r'\bclass="', 'className="', cuerpo)
    cuerpo = re.sub(r'\bfor="', 'htmlFor="', cuerpo)
    # Estilos en línea: `style="a: b"` → `style={{ a: 'b' }}`.
    def estilo(m):
        pares = []
        for decl in m.group(1).split(";"):
            if ":" not in decl:
                continue
            k, v = decl.split(":", 1)
            k = re.sub(r"-(\w)", lambda x: x.group(1).upper(), k.strip())
            pares.append(f"{k}: '{v.strip()}'")
        return "style={{ " + ", ".join(pares) + " }}" if pares else ""
    cuerpo = re.sub(r'style="([^"]*)"', estilo, cuerpo)
    return cuerpo


def convertir_seccion(bruto, id_seccion, graficas, avisos):
    cuerpo = bruto

    # El <h2> lo pinta el App a partir del `curriculum`: repetirlo aquí
    # dejaría dos títulos iguales, uno debajo del otro.
    cuerpo = re.sub(r"<h2[^>]*>.*?</h2>", "", cuerpo, count=1, flags=re.S)
    cuerpo = re.sub(r"^<section[^>]*>|</section>$", "", cuerpo.strip())

    # Las gráficas van antes que nada: su <script> lleva JSON con llaves y
    # comillas que cualquier otra pasada estropearía.
    for cid in graficas.get(id_seccion, []):
        comp = graficas["componentes"][cid]
        cuerpo = re.sub(r"<div[^>]*>\s*<script>.*?newPlot.*?</script>\s*</div>",
                        f"<{comp} />", cuerpo, count=1, flags=re.S)
        cuerpo = re.sub(r"<script>.*?newPlot.*?</script>", f"<{comp} />",
                        cuerpo, count=1, flags=re.S)

    # Los bloques de código, antes de tocar `class`: su marcado de resaltado
    # se borra entero y no debe pasar por la conversión a className.
    trozos, marcas = [], []
    def guardar(m):
        marcas.append(convertir_pre(m, avisos))
        return f"@@BLOQUE{len(marcas) - 1}@@"
    cuerpo = re.sub(r"<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>", guardar, cuerpo, flags=re.S)
    cuerpo = re.sub(r"<pre[^>]*>(.*?)</pre>", guardar, cuerpo, flags=re.S)

    # Aquí, y solo aquí: el código ya está apartado y todavía no se ha
    # generado ninguna llave de JSX. Antes borraría las de los bloques;
    # después, las de `Accordion` y `style`.
    cuerpo = escapar_jsx(cuerpo)

    cuerpo = emparejar_ejercicios(cuerpo)
    cuerpo = convertir_boxes(cuerpo, avisos)
    cuerpo = limpiar_jsx(cuerpo)

    for i, b in enumerate(marcas):
        cuerpo = cuerpo.replace(f"@@BLOQUE{i}@@", b)

    return cuerpo.strip()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--seccion", help="id de una sola sección")
    p.add_argument("--todas", action="store_true")
    p.add_argument("--salida", type=Path, help="carpeta donde escribir los .jsx")
    args = p.parse_args()

    if not args.archivo.exists():
        print(f"ERROR: no existe {args.archivo}", file=sys.stderr)
        return 1

    texto = args.archivo.read_text(encoding="utf-8")
    secciones = re.findall(r'(<section[^>]*id="([^"]+)".*?</section>)', texto, re.S)
    if not secciones:
        print("ERROR: no se encontró ninguna <section id=…>.", file=sys.stderr)
        return 1

    # Qué gráfica va en qué sección. Se declara aquí porque depende del
    # módulo; `graficas.py` genera los componentes con estos mismos nombres.
    GRAFICAS = {
        "vms": ["chart-vm-vs-contenedor"],
        "imagen-base": ["chart-imagen-base"],
        "multistage": ["chart-multistage"],
        "componentes": {
            "chart-vm-vs-contenedor": "GraficaVmContenedor",
            "chart-imagen-base": "GraficaImagenBase",
            "chart-multistage": "GraficaMultistage",
        },
    }

    elegidas = [(c, i) for c, i in secciones
                if args.todas or i == args.seccion]
    if not elegidas:
        print(f"ERROR: sección «{args.seccion}» no encontrada. "
              f"Hay: {', '.join(i for _, i in secciones)}", file=sys.stderr)
        return 1

    total_avisos = 0
    for bruto, sid in elegidas:
        avisos = []
        jsx = convertir_seccion(bruto, sid, GRAFICAS, avisos)
        if args.salida:
            args.salida.mkdir(parents=True, exist_ok=True)
            (args.salida / f"{sid}.jsx").write_text(jsx, encoding="utf-8")
        else:
            print(jsx)
        estado = "OK  " if not avisos else "AVISO"
        print(f"{estado} {sid:14s} {len(jsx.splitlines()):4d} líneas", file=sys.stderr)
        for a in avisos:
            print(f"        · {a}", file=sys.stderr)
        total_avisos += len(avisos)

    print(f"\n{len(elegidas)} secciones · {total_avisos} avisos por revisar",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
