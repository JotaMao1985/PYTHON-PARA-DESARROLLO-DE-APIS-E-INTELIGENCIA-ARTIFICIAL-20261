#!/usr/bin/env python3
"""Extraccion del texto que el estudiante lee, modulo a modulo (T2.0 de la Fase 2).

Solo lectura. No modifica ningun archivo del material.

La prosa vive en sitios distintos segun el stack, y son CINCO, no cuatro:

  * HTML plano (5, 7, 8, 9, 10, 11, 12)  -> nodos de texto del <body>.
  * React + Babel (3, 4, 6, 13)          -> dentro de <script type="text/babel">,
                                            mezclada con JSX y con literales JS.
  * JS plano con almacen de datos (1, 2) -> un objeto `courseData` dentro de un
                                            <script> sin `type`, con HTML dentro
                                            de los literales. El <body> tiene 345
                                            caracteres de texto: todo lo demas lo
                                            inyecta el script.

  CORRECCION al informe tecnico §2: la tabla clasifica los modulos 1 y 2 como
  «HTML plano» y el plan original como «React sin Babel». Ninguna de las dos es
  cierta: no cargan React (0 `React.createElement`, 0 `useState`) y su DOM lo
  construye JS. Verificable con `grep -c React.createElement 1_*.html`.

Por eso NO se puede tirar ningun <script> inline: en 6 de los 13 modulos es donde
esta todo el contenido. Se procesan aparte, extrayendo los literales de cadena y
el texto suelto entre etiquetas, y descartando lo que es codigo.

Uso:
    python3 scripts/auditoria/prosa.py             # extrae los 13 y escribe salida/
    python3 scripts/auditoria/prosa.py --ver 5     # vuelca el texto del modulo 5
    python3 scripts/auditoria/prosa.py --secciones # solo el arbol de secciones
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"
SALIDA_PROSA = SALIDA / "prosa"

# Palabras por minuto de exposicion oral de material tecnico. Una charla normal
# va a 130-150 ppm; explicando codigo en vivo, con pausas y preguntas, baja a
# ~110. Se usa 110 y se declara: el numero es una estimacion, no una medicion.
PPM_EXPOSICION = 110

# Marcadores de nota interna de planeacion filtrada al material del estudiante.
#
# TRAMPA, y costo una pasada: `\bTODO\b` sin distinguir mayusculas caza la
# palabra espanola «todo» y da 11 falsos positivos solo en el modulo 1. Peor:
# tampoco basta con exigir mayusculas, porque el material escribe «Aísla TODO
# (SO, config, libs)» como enfasis. La forma fiable es exigir el marcador
# seguido de dos puntos o de parentesis, que es como se escribe en codigo.
MARCADORES_INTERNOS = [
    r"TODO\s*[:\-]", r"FIXME", r"\bXXX\b", r"\bHACK:", r"\bWIP\b",
    r"\blorem ipsum\b", r"\[pendiente\]", r"\bpor definir\b",
    r"\bNOTA (?:PARA|AL) (?:MI|EL) ",
    r"\bnota (?:del|para el) (?:profesor|docente)\b", r"\bpara el profe\b",
    r"\bdiapositiva\b", r"\bslide\b",
    r"\bhablar de esto en clase\b", r"\bmencionar que\b", r"\bpreguntar a\b",
    r"\bcompletar (?:esto|luego|despu[eé]s)\b", r"\brevisar (?:esto|luego)\b",
]

# Registro: como se dirige el material al estudiante.
REGISTRO = {
    "tu": [r"\bpuedes\b", r"\btienes\b", r"\bdebes\b", r"\btu c[oó]digo\b",
           r"\bnecesitas\b", r"\bhaz\b", r"\bescribe\b", r"\bfíjate\b",
           r"\bten en cuenta\b", r"\bimagina\b", r"\bver[aá]s\b"],
    "usted": [r"\bpuede usted\b", r"\bdebe usted\b", r"\busted\b",
              r"\bescriba\b", r"\bconsidere\b", r"\bobserve\b", r"\bnote que\b"],
    "nosotros": [r"\bvamos a\b", r"\bveremos\b", r"\bnuestro c[oó]digo\b",
                 r"\bhemos visto\b", r"\bpodemos\b", r"\bnecesitamos\b",
                 r"\bconstruiremos\b", r"\bempecemos\b"],
}

# Senales de que un bloque es actividad para el estudiante, no exposicion.
SENALES_PRACTICA = [
    r"\bejercicio\b", r"\bactividad\b", r"\breto\b", r"\btaller\b",
    r"\bpr[aá]ctica\b", r"\bautoevaluaci[oó]n\b", r"\bmanos a la obra\b",
    r"\bahora t[uú]\b", r"\bint[eé]ntalo\b", r"\bresuelve\b", r"\bimplementa\b",
    r"\bconstruye\b", r"\bescribe (?:un|una|el|la)\b", r"\bcrea (?:un|una)\b",
    r"\bquiz\b", r"\bpregunta \d", r"\bcuestionario\b",
]


def modulos() -> list[tuple[int, Path]]:
    encontrados = []
    for p in sorted(RAIZ.glob("*.html")):
        m = re.match(r"^(\d+)_", p.name)
        if m and int(m.group(1)) > 0:
            encontrados.append((int(m.group(1)), p))
    return sorted(encontrados)


# --- Prosa de un modulo de HTML plano ---------------------------------------

_ETIQUETAS_MUDAS = {"script", "style", "noscript", "svg", "canvas"}
_ETIQUETAS_CODIGO = {"pre", "code", "samp", "kbd"}


def _texto_html(soup: BeautifulSoup) -> tuple[list[str], list[str]]:
    """Devuelve (parrafos de prosa, bloques de codigo) del <body>."""
    cuerpo = soup.body or soup
    for c in cuerpo.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    codigo: list[str] = []
    for et in cuerpo.find_all(_ETIQUETAS_CODIGO):
        txt = et.get_text("\n", strip=True)
        if txt:
            codigo.append(txt)
        et.decompose()
    for et in cuerpo.find_all(_ETIQUETAS_MUDAS):
        et.decompose()

    parrafos = []
    for linea in cuerpo.get_text("\n", strip=True).split("\n"):
        linea = re.sub(r"\s+", " ", linea).strip()
        if linea:
            parrafos.append(linea)
    return parrafos, codigo


# --- Prosa de un modulo React (el contenido vive dentro del <script>) --------

# Un literal de cadena de JS: comillas dobles, simples o backtick.
_LITERAL = re.compile(
    r"`((?:[^`\\]|\\.)*)`"          # plantilla
    r"|\"((?:[^\"\\\n]|\\.)*)\""    # comilla doble
    r"|'((?:[^'\\\n]|\\.)*)'",      # comilla simple
    re.S,
)

# Texto suelto entre etiquetas JSX: >texto<
_TEXTO_JSX = re.compile(r">([^<>{}]{3,})<")

# Un literal que en realidad es codigo, no prosa.
_ES_CODIGO = re.compile(
    r"^(?:import |from |def |class |@|print\(|#!|\$ |pip |python |sudo |cd |"
    r"http[s]?://|/|\.|\w+/\w+|[a-z_]+\.[a-z_]+\(|<[a-z]|\{)",
)
_CLAVE_CSS = re.compile(
    r"^(?:[a-z-]+:|#[0-9a-fA-F]{3,8}$|\d+(?:px|rem|em|%|vh|vw)|"
    r"(?:bg|text|border|flex|grid|p|m|w|h|rounded|font|hover|md|lg|sm)-)",
)

# Una lista de clases de Tailwind pasa el filtro de prosa: «my-4 rounded-xl
# overflow-hidden border border-gray-700» tiene palabras en minuscula seguidas y
# no empieza por ningun prefijo de _CLAVE_CSS. Si se cuela, infla el recuento de
# palabras de los cuatro modulos React y con el la estimacion de minutos de
# exposicion, que es justo lo que hay que medir bien. Se detecta por densidad:
# una linea de clases no lleva puntuacion de frase y casi todos sus tokens son
# identificadores con guion, dos puntos o cifras.
_TOKEN_CSS = re.compile(
    r"^(?:[a-z]+:)?(?:-?[a-z]+(?:-[a-z0-9./\[\]%]+)+|[a-z]+-\d+|\d+/\d+)$")


def _es_lista_de_clases(linea: str) -> bool:
    tokens = linea.split()
    if len(tokens) < 3:
        return False
    if re.search(r"[.,;?!¿¡]", linea):     # una frase de verdad lleva puntuacion
        return False
    css = sum(1 for t in tokens if _TOKEN_CSS.match(t))
    return css / len(tokens) >= 0.5


_ETIQUETA_EN_LITERAL = re.compile(r"<br\s*/?>|</?[a-zA-Z][^>]{0,120}>")


def _texto_script(script: str) -> tuple[list[str], list[str]]:
    """Prosa y codigo de un <script> inline (JSX de Babel o almacen de datos).

    Los literales largos con saltos de linea y sintaxis de lenguaje se clasifican
    como codigo; los demas, si parecen frases, como prosa. Los modulos 1 y 2
    meten HTML dentro de los literales (`<code>`, `<strong>`, `<br>`), asi que hay
    que despojarlos antes de contar palabras.
    """
    prosa: list[str] = []
    codigo: list[str] = []

    for m in _LITERAL.finditer(script):
        crudo = next(g for g in m.groups() if g is not None)
        if not crudo.strip():
            continue
        texto = crudo.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')

        # Heuristica de codigo: varias lineas + palabras clave de lenguaje.
        lineas = texto.split("\n")
        if len(lineas) > 2 and re.search(
            r"^\s*(?:import |from |def |class |@|print\(|return |if |for |"
            r"FROM |RUN |COPY |pip |docker |curl |git )", texto, re.M
        ):
            codigo.append(texto)
            continue

        for linea in lineas:
            # Los modulos 1 y 2 guardan HTML dentro del literal: se despoja
            # antes de medir, porque si no las etiquetas cuentan como palabras.
            linea = _ETIQUETA_EN_LITERAL.sub(" ", linea)
            linea = re.sub(r"\s+", " ", linea).strip()
            if len(linea) < 3:
                continue
            if _ES_CODIGO.match(linea) or _CLAVE_CSS.match(linea):
                continue
            if _es_lista_de_clases(linea):
                continue
            # Prosa de verdad: tiene espacios y al menos una vocal acentuada,
            # signo de puntuacion o dos palabras seguidas en minuscula.
            if " " in linea and re.search(r"[a-záéíóúñ]{3,}\s+[a-záéíóúñ]{2,}", linea):
                prosa.append(linea)

    for m in _TEXTO_JSX.finditer(script):
        linea = re.sub(r"\s+", " ", m.group(1)).strip()
        if (len(linea) > 3 and " " in linea and not _CLAVE_CSS.match(linea)
                and not _es_lista_de_clases(linea)):
            prosa.append(linea)

    return prosa, codigo


def extraer(ruta: Path) -> dict:
    html = ruta.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    titulo = soup.title.get_text(strip=True) if soup.title else ""

    # Arbol de secciones: encabezados del HTML mas los que vivan en el JSX.
    secciones = []
    for h in soup.find_all(re.compile(r"^h[1-4]$")):
        txt = re.sub(r"\s+", " ", h.get_text(" ", strip=True))
        if txt:
            secciones.append({"nivel": int(h.name[1]), "texto": txt})

    # Todo <script> inline propio del modulo. Se filtran los cortos (config de
    # Tailwind, KaTeX, PlotlyConfig) por umbral de longitud, no por `type`:
    # en los modulos 1 y 2 el almacen de contenido no lleva `type`.
    scripts_inline = [
        s.get_text() for s in soup.find_all("script")
        if not s.get("src") and len(s.get_text()) > 2000
    ]

    prosa, codigo = _texto_html(soup)
    if scripts_inline:
        for s in scripts_inline:
            p, c = _texto_script(s)
            prosa += p
            codigo += c
            for m in re.finditer(r"<h([1-4])[^>]*>([^<{]{3,})<", s):
                secciones.append({"nivel": int(m.group(1)),
                                  "texto": re.sub(r"\s+", " ", m.group(2)).strip()})
            # Titulos de leccion/seccion declarados como datos.
            for m in re.finditer(
                r"(?:titulo|title|nombre|label|heading)\s*:\s*[\"'`]([^\"'`]{4,90})[\"'`]", s
            ):
                secciones.append({"nivel": 0, "texto": m.group(1).strip()})

    # Deduplicar secciones conservando el orden.
    vistas, secs = set(), []
    for s in secciones:
        if s["texto"] not in vistas:
            vistas.add(s["texto"])
            secs.append(s)

    texto = "\n".join(prosa)
    palabras = len(re.findall(r"\b[\wáéíóúñÁÉÍÓÚÑ]+\b", texto))
    lineas_codigo = sum(len(c.split("\n")) for c in codigo)

    internos = []
    for pat in MARCADORES_INTERNOS:
        for m in re.finditer(pat, texto, re.I | re.M):
            ini = max(0, m.start() - 70)
            internos.append({"patron": pat,
                             "contexto": texto[ini:m.end() + 70].replace("\n", " ")})

    registro = {k: sum(len(re.findall(p, texto, re.I)) for p in pats)
                for k, pats in REGISTRO.items()}

    practica = {}
    for pat in SENALES_PRACTICA:
        n = len(re.findall(pat, texto, re.I))
        if n:
            practica[pat.strip("\\b")] = n

    # Apertura: los primeros 60 nodos de prosa, que es lo que el estudiante ve
    # antes de decidir si sigue leyendo.
    apertura = prosa[:60]

    # Graficas: datos de Chart.js y Plotly.
    graficas = []
    for m in re.finditer(r"(?:new Chart\(|Plotly\.(?:newPlot|react)\()", html):
        ini = m.start()
        graficas.append(html[ini:ini + 900])

    # Duraciones que el propio modulo declara (`duration: "25 min"`). Solo las
    # traen los modulos 1 y 2; donde existen son el dato mas fiable de cuanto
    # tiempo de clase pide el material, porque lo dice el autor.
    duraciones = [int(x) for x in re.findall(
        r"duration:\s*[\"'](\d+)\s*min", html)]

    return {
        "duraciones_declaradas": duraciones,
        "min_declarados": sum(duraciones) if duraciones else None,
        "titulo": titulo,
        "kb": round(len(html) / 1024),
        "secciones": secs,
        "n_secciones": len(secs),
        "palabras_prosa": palabras,
        "min_exposicion_est": round(palabras / PPM_EXPOSICION),
        "n_bloques_codigo": len(codigo),
        "lineas_codigo": lineas_codigo,
        "notas_internas": internos,
        "registro": registro,
        "senales_practica": practica,
        "total_senales_practica": sum(practica.values()),
        "n_graficas": len(graficas),
        "apertura": apertura,
        "_prosa": prosa,
        "_graficas_crudo": graficas,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", type=int, help="volcar la prosa de un modulo")
    ap.add_argument("--secciones", action="store_true", help="solo el arbol de secciones")
    args = ap.parse_args()

    SALIDA_PROSA.mkdir(parents=True, exist_ok=True)
    resultados = {}

    for n, ruta in modulos():
        d = extraer(ruta)
        prosa = d.pop("_prosa")
        graficas = d.pop("_graficas_crudo")
        (SALIDA_PROSA / f"{n:02d}.txt").write_text("\n".join(prosa), encoding="utf-8")
        (SALIDA_PROSA / f"{n:02d}_graficas.txt").write_text(
            "\n\n---\n\n".join(graficas), encoding="utf-8")
        d["archivo"] = ruta.name
        resultados[str(n)] = d

        if args.ver == n:
            print("\n".join(prosa))
            return 0
        if args.secciones:
            print(f"\n### Modulo {n} — {d['titulo'][:70]}")
            for s in d["secciones"]:
                print(f"  h{s['nivel']}  {s['texto'][:88]}")

    (SALIDA / "prosa_metricas.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.secciones:
        print(f"{'#':>3} {'KB':>5} {'secs':>5} {'palabras':>9} {'min':>5} "
              f"{'cod':>5} {'lin':>6} {'graf':>5} {'práct':>6} {'notas':>6}")
        for n, _ in modulos():
            d = resultados[str(n)]
            print(f"{n:>3} {d['kb']:>5} {d['n_secciones']:>5} {d['palabras_prosa']:>9} "
                  f"{d['min_exposicion_est']:>5} {d['n_bloques_codigo']:>5} "
                  f"{d['lineas_codigo']:>6} {d['n_graficas']:>5} "
                  f"{d['total_senales_practica']:>6} {len(d['notas_internas']):>6}")
        print(f"\nprosa -> {SALIDA_PROSA}/NN.txt   metricas -> {SALIDA}/prosa_metricas.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
