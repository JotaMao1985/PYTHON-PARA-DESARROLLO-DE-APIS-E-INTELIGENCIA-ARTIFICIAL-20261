#!/usr/bin/env python3
"""
Fase 3 · Aplicación de la convención compartida a los 13 módulos.

Cubre SÓLO las partes mecánicas y verificables de la Opción A revisada:
título con su semana, metadatos y periodo. El bloque de reparto 60/180 lo
GENERA este script (--reparto N) pero lo coloca una persona, porque el punto
de inserción depende del stack y hay cinco stacks distintos.

Los títulos NO se inventan: salen de `SEMANAS` del syllabus (0_Syllabus_P_A_IA.html,
línea 1949), que es la única fuente de verdad del cronograma.

Uso:
    python3 scripts/auditoria/fase3.py --verificar        # estado actual, no toca nada
    python3 scripts/auditoria/fase3.py --simular          # qué cambiaría
    python3 scripts/auditoria/fase3.py --aplicar 1        # aplica al módulo 1
    python3 scripts/auditoria/fase3.py --reparto 1        # imprime el bloque HTML
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SYLLABUS = RAIZ / "0_Syllabus_P_A_IA.html"

PERIODO = "2026-II"
AUTOR = "Javier Mauricio Sierra"
ASIGNATURA = "Python para Desarrollo de APIs e Inteligencia Artificial"
INSTITUCION = "Universidad Santo Tomás · Estadística"

# Reparto de la sesión de 4 h. Coincide con CONFIG del syllabus (L1911) a propósito:
# si allí cambia, aquí tiene que cambiar, y --verificar lo comprueba.
MINUTOS_TEORIA = 60
MINUTOS_PRACTICA = 180


# ---------------------------------------------------------------------------
# El cronograma, leído del syllabus y no escrito a mano
# ---------------------------------------------------------------------------
def leer_semanas() -> dict[int, dict]:
    """Extrae n, titulo, material y ra de SEMANAS del syllabus."""
    texto = SYLLABUS.read_text(encoding="utf-8")
    bloque = texto[texto.index("const SEMANAS = ["):]
    bloque = bloque[: bloque.index("\n        ];")]

    semanas: dict[int, dict] = {}
    for crudo in re.split(r"\n\s{12}\{", bloque)[1:]:
        def campo(nombre: str) -> str | None:
            m = re.search(rf"{nombre}:\s*'((?:[^'\\]|\\.)*)'", crudo)
            return m.group(1).replace("\\'", "'") if m else None

        m_n = re.search(r"n:\s*(\d+)", crudo)
        m_mod = re.search(r"modulo:\s*(\d+|null)", crudo)
        if not m_n or not m_mod or m_mod.group(1) == "null":
            continue
        n = int(m_n.group(1))
        semanas[n] = {
            "n": n,
            "modulo": int(m_mod.group(1)),
            "titulo": campo("titulo"),
            "ra": campo("ra"),
            "material": campo("material"),
            "stack": campo("stack"),
        }
    return semanas


def verificar_config_syllabus() -> tuple[int, int]:
    """El reparto de este script tiene que ser el del syllabus, no otro."""
    texto = SYLLABUS.read_text(encoding="utf-8")
    t = int(re.search(r"minutosTeoria:\s*(\d+)", texto).group(1))
    p = int(re.search(r"minutosPractica:\s*(\d+)", texto).group(1))
    return t, p


# ---------------------------------------------------------------------------
# Descripciones: se conserva la del módulo si existe; sólo se completa lo que falta
# ---------------------------------------------------------------------------
DESCRIPCION_POR_DEFECTO = {
    3: "Modelado de entidades estadísticas con clases en Python 3.11.9: atributos, "
       "métodos, composición frente a herencia, dataclasses y por qué Pydantic, "
       "SQLAlchemy y FastAPI exigen entender esto primero.",
    6: "Implementación de APIs con FastAPI: routers, el type hinting como contrato "
       "ejecutable, OpenAPI, Swagger UI y async/await.",
}


# ---------------------------------------------------------------------------
# El reparto de cada módulo.
#
# Aquí vive la única decisión de esta fase que NO es mecánica: qué parte de cada
# módulo se expone en los 60 min, qué parte sostiene los 180 de práctica y qué
# parte el estudiante lee por su cuenta. Sale de cruzar las secciones reales del
# módulo con la `teoria`, la `practica` y el trabajo `autonomo` que el syllabus
# declara para esa semana. Está en un solo sitio para que se pueda discutir de
# una vez, en vez de repartido por trece archivos.
# ---------------------------------------------------------------------------
REPARTO: dict[int, dict] = {
    1: {
        "exposicion": [
            "Por qué Python 3.11.9: rendimiento y estabilidad",
            "Entornos virtuales: venv frente a conda",
            "Git para un solo desarrollador",
            "Decoradores como guardianes",
        ],
        "practica": [
            "Instalar Python 3.11.9 y crear el entorno virtual",
            "Inicializar el repositorio y hacer el primer commit",
            "Escribir un script con type hinting estricto",
            "Escribir un decorador propio de validación",
            "Pipeline completo: de idea a análisis reproducible",
        ],
        "consulta": [
            "Docker frente a entornos virtuales (adelanto de la semana 11)",
            "Bonus: limpieza en Pandas y modularización",
            "Las cinco lecturas recomendadas del cierre",
        ],
        "nota": "El bloque de Docker es un adelanto deliberado: da el criterio para "
                "elegir entre venv y contenedor, pero construir imágenes es materia de "
                "la semana 11. El trabajo autónomo de esta semana es seleccionar el "
                "dataset del proyecto y modularizar su limpieza.",
    },
    2: {
        "exposicion": [
            "Verbos, códigos de estado y cabeceras",
            "JSON frente a Pickle: por qué Pickle no viaja",
            "requirements.txt y el congelado de dependencias",
        ],
        "practica": [
            "Parsear un JSON de entrada y validarlo a mano",
            "Responder con un diccionario serializado",
            "Congelar las dependencias del proyecto",
            "Redactar los esquemas de entrada y salida del dataset elegido",
        ],
        "consulta": [
            "Validación con Pydantic (adelanto de la semana 4)",
            "Bonus: funciones en Python (repaso, por debajo del nivel de la semana)",
            "Las lecturas recomendadas del cierre",
        ],
        "nota": "El bloque de Pydantic es un adelanto deliberado: aquí se ve para qué "
                "sirve validar de forma declarativa, y la semana 4 es un módulo entero "
                "dedicado a ello. El bonus de funciones es un repaso de apoyo: si ya "
                "escribes funciones con soltura, sáltatelo.",
    },
    3: {
        "exposicion": [
            "Clases, constructor y atributos",
            "Métodos y métodos especiales",
            "Composición frente a herencia, y polimorfismo",
            "Por qué Pydantic, SQLAlchemy y FastAPI exigen entender esto primero",
        ],
        "practica": [
            "Convertir el módulo de limpieza de la semana 1 en una clase con estado",
            "Separar responsabilidades del pipeline en clases distintas",
            "Escribir la dataclass de la observación del proyecto, con sus tipos",
            "Comprobar en Python 3.11.9 que @dataclass no valida los tipos que declara",
        ],
        "consulta": [
            "Constructor IA: generar una clase a partir de un concepto",
            "Conexión a una API desde Python",
            "Referencia bibliográfica",
        ],
        "nota": "La sección «Por qué esto es el cimiento del curso» es la bisagra de la "
                "semana: enseña qué parte de lo que has visto hoy reaparece en las "
                "semanas 4, 6 y 9. El entorno es Python 3.11.9, el mismo de la semana 1.",
    },
    4: {
        "modo": "autonomo",
        "exposicion": [
            "El tipo como fuente de verdad",
            "Modelos, campos y coerción",
            "Field, valores por defecto y campos opcionales",
            "Validadores de campo con @field_validator",
            "Serialización y deserialización",
            "El error 422 como respuesta HTTP",
        ],
        "practica": [
            "Construir los modelos de entrada y salida de tu dataset",
            "Provocar a propósito cada tipo de error de validación",
            "Dejar los esquemas del proyecto listos para la semana 6",
        ],
        "consulta": [
            "Validación de DataFrames de Pandas",
            "Autoevaluación",
            "Referencia bibliográfica",
        ],
        "nota": "Ésta es la única semana sin sesión de exposición: el syllabus la "
                "declara «módulo de estudio autónomo: recorrer el material completo». "
                "Por eso este material es más corto que el resto — no le falta nada, "
                "está dimensionado para lo que es. Entorno: Python 3.11.9.",
    },
}


def ruta_modulo(n: int) -> Path:
    candidatas = sorted(RAIZ.glob(f"{n}_*.html"))
    if not candidatas:
        raise SystemExit(f"No encuentro el módulo {n}")
    return candidatas[0]


# ---------------------------------------------------------------------------
# Lectura del estado actual
# ---------------------------------------------------------------------------
RE_TITLE = re.compile(r"<title>(.*?)</title>", re.S)


def meta_actual(texto: str, nombre: str) -> str | None:
    """Lee un <meta name=...> tolerando las dos ordenaciones de atributos."""
    for patron in (
        rf'<meta\s+name=["\']{nombre}["\']\s+content=["\'](.*?)["\']\s*/?>',
        rf'<meta\s+content=["\'](.*?)["\']\s+name=["\']{nombre}["\']\s*/?>',
    ):
        m = re.search(patron, texto, re.S)
        if m:
            return " ".join(m.group(1).split())
    return None


def og_actual(texto: str, prop: str) -> str | None:
    m = re.search(rf'<meta\s+property=["\']og:{prop}["\']\s+content=["\'](.*?)["\']', texto, re.S)
    return " ".join(m.group(1).split()) if m else None


def estado(n: int, semanas: dict[int, dict]) -> dict:
    ruta = ruta_modulo(n)
    texto = ruta.read_text(encoding="utf-8")
    m = RE_TITLE.search(texto)
    return {
        "modulo": n,
        "archivo": ruta.name,
        "kb": round(len(texto.encode("utf-8")) / 1024),
        "titulo": " ".join(m.group(1).split()) if m else None,
        "titulo_esperado": titulo_esperado(n, semanas),
        "description": meta_actual(texto, "description"),
        "author": meta_actual(texto, "author"),
        "og_title": og_actual(texto, "title"),
        "periodo": PERIODO in texto,
        "reparto": 'data-fase3="reparto"' in texto,
    }


def titulo_esperado(n: int, semanas: dict[int, dict]) -> str:
    s = semanas[n]
    return f"Semana {s['n']} — {s['titulo']} · Python para APIs e IA"


# ---------------------------------------------------------------------------
# El bloque de reparto 60/180
# ---------------------------------------------------------------------------
def bloque_reparto(n: int, semanas: dict[int, dict], exposicion: list[str],
                   practica: list[str], consulta: list[str],
                   nota: str | None = None, modo: str = "sesion") -> str:
    """
    HTML plano con estilos en línea: tiene que verse igual en los cinco stacks.
    Sin Tailwind (10-12 no lo cargan), sin React (nueve no lo usan) y sin clases
    propias (colisionarían con la hoja de cada módulo).

    `modo="autonomo"` es para el módulo 4, que el syllabus define como estudio
    autónomo. Fingirle un reparto 60/180 seria declarar una sesión que no existe.
    """
    s = semanas[n]
    P, S, N = "#3D008D", "#ED1E79", "#001A4D"

    if modo == "autonomo":
        rotulos = ("Recorrido del material", "Trabajo sobre el proyecto", "Material de consulta")
        cifras = ("a tu ritmo", "entregable de la semana", "de apoyo")
        subtitulo = (f"Semana {s['n']} · <strong>módulo de estudio autónomo</strong>. "
                     f"El syllabus no asigna sesión de exposición a esta semana: el "
                     f"material está escrito para recorrerlo entero por tu cuenta.")
    else:
        rotulos = ("Exposición", "Práctica guiada", "Material de consulta")
        cifras = (f"{MINUTOS_TEORIA} min", f"{MINUTOS_PRACTICA} min", "fuera de sesión")
        subtitulo = (f"Semana {s['n']} · sesión de 4 h · {MINUTOS_TEORIA} min de "
                     f"exposición y {MINUTOS_PRACTICA} min de práctica guiada.")

    def columna(titulo: str, minutos: str, color: str, items: list[str]) -> str:
        lis = "".join(
            f'<li style="margin:0 0 .3rem 0;">{html.escape(i)}</li>' for i in items
        )
        return (
            f'<div style="flex:1 1 220px;min-width:0;">'
            f'<div style="font-weight:700;color:{color};font-size:.82rem;'
            f'letter-spacing:.04em;text-transform:uppercase;margin-bottom:.15rem;">{titulo}</div>'
            f'<div style="font-size:1.35rem;font-weight:800;color:{N};line-height:1.1;'
            f'margin-bottom:.4rem;">{minutos}</div>'
            f'<ul style="margin:0;padding-left:1.1rem;font-size:.86rem;color:#334155;'
            f'line-height:1.45;">{lis}</ul></div>'
        )

    partes = [
        columna(rotulos[0], cifras[0], P, exposicion),
        columna(rotulos[1], cifras[1], S, practica),
        columna(rotulos[2], cifras[2], "#0E7490", consulta),
    ]

    pie = ""
    if nota:
        pie = (
            f'<p style="margin:.9rem 0 0 0;padding-top:.7rem;border-top:1px solid #E2E8F0;'
            f'font-size:.83rem;color:#475569;line-height:1.5;">{nota}</p>'
        )

    return (
        f'\n<!-- Fase 3 · reparto declarado de la sesión (60/180, CONFIG del syllabus) -->\n'
        f'<section data-fase3="reparto" aria-labelledby="reparto-titulo-{n}"\n'
        f'    style="max-width:1100px;margin:1.5rem auto;padding:1.15rem 1.35rem;'
        f'background:#FFFFFF;border:1px solid #E2E8F0;border-left:5px solid {P};'
        f'border-radius:10px;font-family:Montserrat,\'Helvetica Neue\',Arial,sans-serif;'
        f'box-shadow:0 1px 3px rgba(0,0,0,.06);">\n'
        f'  <h2 id="reparto-titulo-{n}" style="margin:0 0 .2rem 0;font-size:1rem;'
        f'font-weight:800;color:{N};">Cómo se usa este material en la sesión</h2>\n'
        f'  <p style="margin:0 0 .9rem 0;font-size:.86rem;color:#475569;">{subtitulo}</p>\n'
        f'  <div style="display:flex;flex-wrap:wrap;gap:1.4rem;">\n    '
        + "\n    ".join(partes)
        + f'\n  </div>{pie}\n</section>\n'
    )


# ---------------------------------------------------------------------------
# Aplicación de las partes mecánicas
# ---------------------------------------------------------------------------
def aplicar(n: int, semanas: dict[int, dict], simular: bool) -> list[str]:
    ruta = ruta_modulo(n)
    texto = original = ruta.read_text(encoding="utf-8")
    cambios: list[str] = []
    s = semanas[n]
    nuevo_titulo = titulo_esperado(n, semanas)

    # 1 · Título
    m = RE_TITLE.search(texto)
    if m and " ".join(m.group(1).split()) != nuevo_titulo:
        cambios.append(f"título: {m.group(1).strip()!r} → {nuevo_titulo!r}")
        texto = texto[: m.start()] + f"<title>{nuevo_titulo}</title>" + texto[m.end():]

    # 2 · description (se respeta la que exista; sólo se crea si falta)
    desc = meta_actual(texto, "description")
    if not desc:
        desc = DESCRIPCION_POR_DEFECTO.get(n) or f"{s['ra']}"
        cambios.append(f"description: creada ({len(desc)} car.)")
        texto = insertar_en_head(texto, f'<meta name="description" content="{html.escape(desc, quote=True)}">')

    # 3 · author
    if not meta_actual(texto, "author"):
        cambios.append("author: creado")
        texto = insertar_en_head(texto, f'<meta name="author" content="{AUTOR}">')

    # 4 · Open Graph
    if not og_actual(texto, "title"):
        og = (
            f'<meta property="og:title" content="{html.escape(nuevo_titulo, quote=True)}">\n'
            f'    <meta property="og:description" content="{html.escape(desc, quote=True)}">\n'
            f'    <meta property="og:type" content="article">'
        )
        cambios.append("open graph: creado")
        texto = insertar_en_head(texto, og)

    # 5 · Periodo académico
    if PERIODO not in texto:
        cambios.append(f"periodo {PERIODO}: creado")
        texto = insertar_en_head(
            texto,
            f'<meta name="dc.date" content="{PERIODO}">\n'
            f'    <meta name="course.period" content="{PERIODO}">\n'
            f'    <meta name="course.subject" content="{ASIGNATURA}">\n'
            f'    <meta name="course.institution" content="{INSTITUCION}">',
        )

    if texto != original and not simular:
        bak = ruta.with_suffix(ruta.suffix + ".bak")
        if not bak.exists():
            bak.write_text(original, encoding="utf-8")
        ruta.write_text(texto, encoding="utf-8")

    return cambios


def insertar_reparto(n: int, semanas: dict[int, dict], ancla: str,
                     simular: bool = False) -> str:
    """
    Coloca el bloque de reparto justo DESPUÉS de `ancla`, que es distinta en cada
    módulo porque hay cinco stacks. El ancla se pasa a mano y se comprueba que
    aparezca exactamente una vez: si aparece dos, el script se niega en vez de
    insertar en el sitio equivocado.
    """
    if n not in REPARTO:
        raise SystemExit(f"El módulo {n} no tiene reparto decidido en REPARTO")
    ruta = ruta_modulo(n)
    texto = ruta.read_text(encoding="utf-8")

    if 'data-fase3="reparto"' in texto:
        return "ya tenía bloque de reparto; no se toca"

    apariciones = texto.count(ancla)
    if apariciones != 1:
        raise SystemExit(
            f"El ancla aparece {apariciones} veces en el módulo {n}; "
            f"hace falta una que aparezca exactamente una vez"
        )

    r = REPARTO[n]
    bloque = bloque_reparto(n, semanas, r["exposicion"], r["practica"],
                            r["consulta"], r.get("nota"), r.get("modo", "sesion"))
    corte = texto.index(ancla) + len(ancla)
    nuevo = texto[:corte] + bloque + texto[corte:]

    if not simular:
        bak = ruta.with_suffix(ruta.suffix + ".bak")
        if not bak.exists():
            bak.write_text(texto, encoding="utf-8")
        ruta.write_text(nuevo, encoding="utf-8")
    return f"bloque insertado tras {ancla!r} ({len(bloque)} car.)"


def insertar_en_head(texto: str, etiqueta: str) -> str:
    """Inserta justo antes de </title>… no: justo después del <title>, que existe en los 13."""
    m = RE_TITLE.search(texto)
    if not m:
        raise SystemExit("El módulo no tiene <title>; hay que mirarlo a mano")
    corte = m.end()
    return texto[:corte] + "\n    " + etiqueta + texto[corte:]


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--aplicar", type=int, metavar="N")
    ap.add_argument("--reparto", type=int, metavar="N")
    ap.add_argument("--insertar-reparto", type=int, metavar="N")
    ap.add_argument("--ancla", type=str, help="texto tras el que insertar el bloque")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    semanas = leer_semanas()
    t, p = verificar_config_syllabus()
    if (t, p) != (MINUTOS_TEORIA, MINUTOS_PRACTICA):
        print(f"AVISO: el syllabus declara {t}/{p} y este script {MINUTOS_TEORIA}/{MINUTOS_PRACTICA}")
        return 2

    if args.reparto:
        n = args.reparto
        if n not in REPARTO:
            print(f"El módulo {n} todavía no tiene reparto decidido en REPARTO.")
            return 1
        r = REPARTO[n]
        print(bloque_reparto(n, semanas, r["exposicion"], r["practica"],
                             r["consulta"], r.get("nota"), r.get("modo", "sesion")))
        return 0

    if args.insertar_reparto:
        if not args.ancla:
            print("Hace falta --ancla")
            return 1
        print(f"Módulo {args.insertar_reparto}: "
              f"{insertar_reparto(args.insertar_reparto, semanas, args.ancla, args.simular)}")
        return 0

    if args.aplicar:
        cambios = aplicar(args.aplicar, semanas, simular=False)
        print(f"Módulo {args.aplicar}: {len(cambios)} cambios")
        for c in cambios:
            print(f"  · {c}")
        return 0

    if args.simular:
        for n in range(1, 14):
            cambios = aplicar(n, semanas, simular=True)
            print(f"\nMódulo {n:>2} — {ruta_modulo(n).name}")
            for c in cambios or ["(sin cambios mecánicos)"]:
                print(f"  · {c}")
        return 0

    # --verificar por defecto
    filas = [estado(n, semanas) for n in range(1, 14)]
    if args.json:
        print(json.dumps(filas, ensure_ascii=False, indent=2))
        return 0

    print(f"{'#':>3}  {'KB':>4}  {'tít':>3} {'des':>3} {'aut':>3} {'og':>3} {'per':>3} {'rep':>3}   título actual")
    print("-" * 110)
    ok = 0
    for f in filas:
        bien = f["titulo"] == f["titulo_esperado"]
        ok += bien
        print(
            f"{f['modulo']:>3}  {f['kb']:>4}  "
            f"{'✓' if bien else '✗':>3} "
            f"{'✓' if f['description'] else '✗':>3} "
            f"{'✓' if f['author'] else '✗':>3} "
            f"{'✓' if f['og_title'] else '✗':>3} "
            f"{'✓' if f['periodo'] else '✗':>3} "
            f"{'✓' if f['reparto'] else '✗':>3}   {f['titulo']}"
        )
    print("-" * 110)
    print(f"Títulos conformes: {ok}/13 · "
          f"description {sum(1 for f in filas if f['description'])}/13 · "
          f"author {sum(1 for f in filas if f['author'])}/13 · "
          f"og {sum(1 for f in filas if f['og_title'])}/13 · "
          f"periodo {sum(1 for f in filas if f['periodo'])}/13 · "
          f"reparto {sum(1 for f in filas if f['reparto'])}/13")
    return 0


if __name__ == "__main__":
    sys.exit(main())
