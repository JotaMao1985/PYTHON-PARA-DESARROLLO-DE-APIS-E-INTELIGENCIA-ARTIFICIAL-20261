#!/usr/bin/env python3
"""
Registro único del estado de los hallazgos de la auditoría.

El problema que resuelve: los hallazgos viven repartidos en tres informes
—Fase 1, Fase 2 y Fase 3— y para saber si `I11` sigue abierto había que leer
los tres. Aquí están todos en un sitio, y los que se pueden comprobar contra
los archivos se comprueban, en vez de creerse el estado escrito.

Cada hallazgo lleva una `prueba` cuando su estado es verificable de forma
automática. La prueba devuelve (cumple, evidencia): `cumple=True` significa que
el defecto YA NO ESTÁ. Si la prueba contradice al estado declarado, el script lo
marca con «!!» — eso es una tabla que se ha quedado obsoleta, y es justo lo que
hay que ver.

Uso:
    python3 scripts/auditoria/hallazgos.py              # tabla en consola
    python3 scripts/auditoria/hallazgos.py --abiertos   # sólo lo que queda
    python3 scripts/auditoria/hallazgos.py --markdown   # regenera ESTADO_HALLAZGOS.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

CERRADO, PARCIAL, ABIERTO, NOTA = "cerrado", "parcial", "abierto", "nota"


def mod(n: int) -> str:
    return sorted(RAIZ.glob(f"{n}_*.html"))[0].read_text(encoding="utf-8")


def cuenta(n: int, patron: str, flags=re.I) -> int:
    return len(re.findall(patron, mod(n), flags))


# ---------------------------------------------------------------------------
# Pruebas. Devuelven (el defecto ya no está, evidencia)
# ---------------------------------------------------------------------------
def p_titulos_semana():
    malos = [n for n in range(1, 14)
             if not re.search(rf"<title>Semana {n} —", mod(n))]
    return not malos, f"módulos sin «Semana N» en el título: {malos or 'ninguno'}"


def p_meta(campo: str, patron: str):
    def f():
        malos = [n for n in range(1, 14) if not re.search(patron, mod(n))]
        return not malos, f"{campo} ausente en: {malos or 'ninguno'}"
    return f


def p_cloudflare():
    malos = [n for n in range(1, 14) if "cdn-cgi" in mod(n) or "[email" in mod(n)]
    return not malos, f"residuo de Cloudflare en: {malos or 'ninguno'}"


def p_react_produccion():
    malos = [n for n in (3, 4, 6, 13) if "react.development" in mod(n)
             or "@babel/standalone/babel" in mod(n)]
    return not malos, f"React en desarrollo o Babel sin pinear en: {malos or 'ninguno'}"


def p_python3119():
    malos = [n for n in range(3, 10) if "3.11.9" not in mod(n)]
    return not malos, f"sin mencionar 3.11.9: {malos or 'ninguno'}"


def p_flask_modulo5():
    fl, fa = cuenta(5, r"Flask", 0), cuenta(5, r"FastAPI", 0)
    return fa > fl, f"módulo 5: Flask {fl} · FastAPI {fa} (era 48/46)"


def p_railway():
    rw, rd = cuenta(12, r"Railway"), len(re.findall(r"\bRender\b", mod(12)))
    return rw < 15, f"módulo 12: Railway {rw} · Render {rd} (era 46/40)"


def p_clave_en_url():
    c = mod(3).count("generateContent?key=")
    return c == 0, f"módulo 3: «generateContent?key=» aparece {c} veces"


def p_puente_modulo3():
    t = mod(3)
    d = {k: len(re.findall(k, t, re.I)) for k in ("dataclass", "Pydantic", "SQLAlchemy", "FastAPI")}
    return all(v > 0 for v in d.values()), f"módulo 3: {d} (eran 0/0/0/0)"


def p_tablero():
    c = mod(13).lower().count("tablero")
    return c > 5, f"módulo 13: «tablero» {c} veces (era 0 en los 13)"


def p_celery():
    t = mod(7).lower()
    return t.count("celery") == 0, f"módulo 7: celery {t.count('celery')} · rabbitmq {t.count('rabbitmq')}"


def p_reparto():
    malos = [n for n in range(1, 14) if 'data-fase3="reparto"' not in mod(n)]
    return not malos, f"sin bloque de reparto: {malos or 'ninguno'}"


def p_reloj_a_mano():
    malos = [n for n in (1, 2) if "let mins = 120" in mod(n)]
    return not malos, f"total de minutos escrito a mano en: {malos or 'ninguno'}"


def p_radar_inventado():
    malos = [n for n in (1, 2) if "85, 90, 70, 80, 85" in mod(n)]
    return not malos, f"radar con datos inventados en: {malos or 'ninguno'}"


def p_usted():
    c = cuenta(6, r"\busted\b")
    return c == 0, f"módulo 6: «usted» {c} veces (eran 7)"


def p_semana_x():
    malos = [n for n in (10, 11) if re.search(r"Semana X(?!I)", mod(n))]
    return not malos, f"«Semana X» sin resolver en: {malos or 'ninguno'}"


def p_katex_muerto():
    return "katex" not in mod(8).lower(), f"módulo 8: katex {mod(8).lower().count('katex')} referencias"


def p_comentario_mathjax():
    return "MathJax for LaTeX" not in mod(7), "módulo 7: comentario «MathJax» sobre carga de KaTeX"


def p_guarda_temporizador():
    return "if (!timeDisplay) return" in mod(1), "módulo 1: guarda contra timeDisplay nulo"


def p_error_422():
    return cuenta(4, r"422", 0) > 3, f"módulo 4: «422» {cuenta(4, r'422', 0)} veces (era 0)"


def p_medium():
    tot = sum(cuenta(n, r"medium\.com|towardsai\.net") for n in (4, 6, 7))
    return tot == 0, f"enlaces a Medium/TowardsAI en 4, 6 y 7: {tot}"


def p_fa_pocos_iconos():
    detalle = {n: len(set(re.findall(r"fa-[a-z0-9-]+", mod(n)))) for n in (5, 7, 8, 9)}
    return all(v > 3 for v in detalle.values()), f"iconos distintos por módulo: {detalle}"


def p_plotly():
    malos = [n for n in (10, 11, 12, 13) if "plotly-3.5.0" in mod(n) or "plotly@3.5" in mod(n)]
    return not malos, f"Plotly 3.5.0 en: {malos or 'ninguno'} (el syllabus usa 2.35.2)"


def p_anio_2025():
    """
    Sólo cuenta las menciones de CADUCIDAD, no los años de publicación.

    `Garodia, S. (2025). "From Zero to API"` es una cita correcta: cambiarle el
    año sería falsear la fuente. Lo que el hallazgo persigue es el material que
    se anuncia a sí mismo como de hace dos años («Datos del Ecosistema
    2024-2025») en un curso que es 2026-II.
    """
    detalle = {}
    for n in (6, 7):
        t = mod(n)
        detalle[n] = len(re.findall(r"\b2025\b", t)) - len(re.findall(r"\(2025\)\.", t))
    return all(v == 0 for v in detalle.values()), f"«2025» de caducidad (sin citas): {detalle}"


def p_fa_version():
    malos = [n for n in range(1, 14) if "font-awesome/6.0.0" in mod(n)]
    return not malos, f"Font Awesome 6.0.0 en {len(malos)} módulos (el syllabus usa 6.5.2)"


def p_graficas_modulo7():
    t = mod(7)
    c = t.count("new Chart(") + t.count("Plotly.newPlot")
    return c > 0, f"módulo 7: {c} gráficas en {round(len(t.encode())/1024)} KB"


def p_segunda_persona():
    """
    Proxy de registro, no medida de calidad: cuenta marcas de segunda persona.

    El hallazgo era «no se dirigen al estudiante NI UNA VEZ». El listón se pone
    en 5 porque es lo que distingue un módulo que le habla al estudiante de uno
    que no: los tres estaban en 0 o 1. No dice que el registro sea bueno, dice
    que existe.
    """
    RE = re.compile(r"\b(puedes|tienes|debes|necesitas|tu |tus |vas a|te )\b", re.I)
    detalle = {n: len(RE.findall(mod(n))) for n in (1, 7, 13)}
    return all(v >= 5 for v in detalle.values()), f"marcas de segunda persona: {detalle}"


def p_estructura_html():
    from html.parser import HTMLParser
    VACIAS = {"br", "hr", "img", "input", "link", "meta", "source", "area",
              "base", "col", "embed", "param", "track", "wbr"}

    class C(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.pila, self.err = [], 0

        def handle_starttag(self, t, a):
            if t not in VACIAS:
                self.pila.append(t)

        def handle_endtag(self, t):
            if t in VACIAS:
                return
            if self.pila and self.pila[-1] == t:
                self.pila.pop()
            elif t in self.pila:
                i = len(self.pila) - 1 - self.pila[::-1].index(t)
                self.err += 1
                del self.pila[i:]
            else:
                self.err += 1

    malos = []
    for n in range(1, 14):
        c = C()
        c.feed(mod(n))
        if c.err:
            malos.append(n)
    return not malos, f"marcado desbalanceado en: {malos or 'ninguno'}"


def p_main_anidado():
    """
    Un documento HTML admite un solo `<main>`, y anidarlos no es válido.

    Los cuatro módulos de barra lateral abren `<main class="flex-1 ...">` para la
    zona con scroll y, dentro, otro `<main class="max-w-6xl ...">` que es sólo un
    contenedor de ancho. Para un lector de pantalla eso son dos landmarks
    principales, que es como no tener ninguno. Se descubrió al reconstruir la
    pila de etiquetas para arreglar F2.
    """
    malos = [n for n in range(1, 14) if len(re.findall(r"<main\b", mod(n))) > 1]
    return not malos, f"con <main> anidado: {malos or 'ninguno'}"


def p_aperturas():
    malos = [n for n in (1, 4, 7) if 'data-fase3="apertura"' not in mod(n)]
    return not malos, f"sin bloque de apertura: {malos or 'ninguno'}"


def p_presupuesto_modulo7():
    """
    El módulo 7 declaraba 128 min de prosa contra 60 de presupuesto. La cuestión
    nunca fue el total del archivo, sino que nada decía qué parte era exposición.
    La prueba exige que el bloque de reparto declare minutos medidos.
    """
    t = mod(7)
    tiene = "minutos medidos" in t and re.search(r"· \d+ min", t) is not None
    n = len(re.findall(r"· (\d+) min", t))
    return tiene, f"módulo 7: bloque de reparto con {n} secciones de exposición cronometradas"


# ---------------------------------------------------------------------------
# El registro
# ---------------------------------------------------------------------------
H = [
    # ── Fase 1 · bloqueantes, corregidos en la propia Fase 1 ──────────────
    ("B1", 1, "bloqueante", "7", "«IMPLEMENTACIÓN CORRECTA» no compila: IndentationError", CERRADO, "Fase 1", "94eaa09", None),
    ("B2", 1, "bloqueante", "7", "Error de sintaxis no intencionado en el ejemplo del error metodológico", CERRADO, "Fase 1", "94eaa09", None),
    ("B3", 1, "bloqueante", "7", "Rama `else` sin indentar", CERRADO, "Fase 1", "94eaa09", None),
    ("B4", 1, "bloqueante", "4", "`print(\"` partido por un `\\n` que resolvió JavaScript", CERRADO, "Fase 1", "deb0686", None),
    ("B5", 1, "bloqueante", "9", "4 literales de correo destruidos por Cloudflare", CERRADO, "Fase 1", "ba5b159", p_cloudflare),
    ("B6", 1, "bloqueante", "8", "Cadena de conexión con credencial destruida por Cloudflare", CERRADO, "Fase 1", "70c5499", p_cloudflare),

    # ── Fase 1 · importantes ──────────────────────────────────────────────
    ("I1", 1, "importante", "1, 12, 13", "El `<title>` declara una semana que no es la suya", CERRADO, "Fase 3", "4e31026", p_titulos_semana),
    ("I2", 1, "importante", "3–9", "Ningún `<title>` declara semana", CERRADO, "Fase 3", "4e31026", p_titulos_semana),
    ("I3", 1, "importante", "8, 9", "3 peticiones 404 en consola a `/cdn-cgi/`", CERRADO, "Fase 1", "ba5b159", p_cloudflare),
    ("I4", 1, "importante", "1", "Desborda 58 px a 375 px", CERRADO, "Fase 3", "e9dfeb2", None),
    ("I5", 1, "importante", "2", "Desborda 12 px a 375 px", CERRADO, "Fase 3", "f2a65fc", None),
    ("I6", 1, "importante", "3, 4, 6, 13", "React en build de desarrollo y `@babel/standalone` sin pinear", CERRADO, "Fase 3", "35412a2", p_react_produccion),
    ("I7", 1, "importante", "3–9", "Python 3.11.9 no se menciona nunca *(= P16)*", CERRADO, "Fase 3", "7d69b57", p_python3119),
    ("I8", 1, "importante", "5", "Enseña Flask donde el proyecto exige FastAPI *(= P4)*", CERRADO, "Fase 3", "1bb8eb7", p_flask_modulo5),
    ("I9", 1, "importante", "12", "Enseña Railway y Render en paralelo *(= P13)*", CERRADO, "Fase 3", "7d69b57", p_railway),
    ("I10", 1, "importante", "3", "Sin `description`, sin autor y sin Open Graph", CERRADO, "Fase 3", "35412a2", p_meta("description", r'name="description"')),
    ("I11", 1, "importante", "4, 6, 7", "4 referencias bibliográficas tras el muro de pago de Medium", ABIERTO, "—", "", p_medium),

    # ── Fase 1 · cosméticos ───────────────────────────────────────────────
    ("C1", 1, "cosmético", "7", "El comentario dice «MathJax» sobre una carga de KaTeX", CERRADO, "Fase 3", "7d69b57", p_comentario_mathjax),
    ("C2", 1, "cosmético", "8", "Carga los 3 archivos de KaTeX y renderiza 0 fórmulas", CERRADO, "Fase 3", "7d69b57", p_katex_muerto),
    ("C3", 1, "cosmético", "5, 7, 8, 9", "89 KB de Font Awesome para 1 o 2 iconos", ABIERTO, "—", "", p_fa_pocos_iconos),
    ("C4", 1, "cosmético", "10–13", "Plotly 3.5.0 frente al 2.35.2 del syllabus", ABIERTO, "—", "", p_plotly),
    ("C5", 1, "cosmético", "6, 7", "Referencias a «2025» que fechan el material", CERRADO, "Fase 3", "eca3261", p_anio_2025),
    ("C6", 1, "cosmético", "todos", "Ningún módulo declara el periodo 2026-II", CERRADO, "Fase 3", "4e31026", p_meta("periodo", r"2026-II")),
    ("C7", 1, "cosmético", "7, 13", "Bloques de código que continúan a otro sin decirlo", ABIERTO, "—", "", None),
    ("C8", 1, "cosmético", "2, 10, 11", "Semana correcta pero en tres notaciones distintas", CERRADO, "Fase 3", "4e31026", p_titulos_semana),
    ("C9", 1, "cosmético", "11 módulos", "Font Awesome 6.0.0 frente al 6.5.2 del syllabus", ABIERTO, "—", "", p_fa_version),

    # ── Fase 2 · bloqueantes ──────────────────────────────────────────────
    ("P1", 2, "bloqueante", "13", "La rúbrica evalúa «Tablero (frontend)» (3 %) y ningún módulo lo prepara", CERRADO, "Fase 3", "2f385db", p_tablero),
    ("P2", 2, "bloqueante", "3", "No nombra `dataclasses`, Pydantic, SQLAlchemy ni FastAPI", CERRADO, "Fase 3", "35412a2", p_puente_modulo3),
    ("P3", 2, "bloqueante", "3", "Envía la API Key del estudiante **en la URL**", CERRADO, "Fase 3", "35412a2", p_clave_en_url),
    ("P4", 2, "bloqueante", "5", "Enseña Flask donde el proyecto se evalúa en FastAPI", CERRADO, "Fase 3", "1bb8eb7", p_flask_modulo5),

    # ── Fase 2 · importantes ──────────────────────────────────────────────
    ("P5", 2, "importante", "7", "Celery/RabbitMQ/DLQ: 70 menciones que el syllabus no cita", CERRADO, "Fase 3", "7d69b57", p_celery),
    ("P6", 2, "importante", "7", "128 min de prosa contra un presupuesto de 60", CERRADO, "Fase 3", "eca3261", p_presupuesto_modulo7),
    ("P7", 2, "importante", "2", "Declara 120 min en cabecera; sus lecciones suman 170", CERRADO, "Fase 3", "f2a65fc", p_reloj_a_mano),
    ("P8", 2, "importante", "1, 2", "Radar «Competencias» con datos inventados y duplicado", CERRADO, "Fase 3", "f2a65fc", p_radar_inventado),
    ("P9", 2, "importante", "2", "40 min a Pydantic, que es la semana 4", CERRADO, "Fase 3 (D3: se declara)", "f2a65fc", None),
    ("P10", 2, "importante", "1", "25 min a Docker, que es la semana 11", CERRADO, "Fase 3 (D3: se declara)", "e9dfeb2", None),
    ("P11", 2, "importante", "11 módulos", "No declaran ninguna duración", CERRADO, "Fase 3", "4e31026", p_reparto),
    ("P12", 2, "importante", "todos", "Ningún módulo separa exposición de material de consulta", CERRADO, "Fase 3", "4e31026", p_reparto),
    ("P13", 2, "importante", "12", "Compara Railway y Render donde el proyecto exige Render", CERRADO, "Fase 3", "7d69b57", p_railway),
    ("P14", 2, "importante", "1, 7, 13", "No se dirigen al estudiante ni una vez", CERRADO, "Fase 3", "eca3261", p_segunda_persona),
    ("P15", 2, "importante", "6", "Único módulo que trata de **usted**", CERRADO, "Fase 3", "7d69b57", p_usted),
    ("P16", 2, "importante", "3–9", "Python 3.11.9 no se menciona nunca *(= I7)*", CERRADO, "Fase 3", "7d69b57", p_python3119),

    # ── Fase 2 · cosméticos ───────────────────────────────────────────────
    ("Q1", 2, "cosmético", "10", "El `<title>` dice «Semana 10» y la cabecera «Semana X»", CERRADO, "Fase 3", "7d69b57", p_semana_x),
    ("Q2", 2, "cosmético", "1, 4, 7", "Aperturas que indexan en vez de motivar", CERRADO, "Fase 3", "eca3261", p_aperturas),
    ("Q3", 2, "cosmético", "1", "Gráfica de barras sin fuente citada", CERRADO, "Fase 3", "e9dfeb2", None),
    ("Q4", 2, "cosmético", "7", "El módulo más pesado del curso no tiene ni una gráfica", ABIERTO, "—", "", p_graficas_modulo7),
    ("Q5", 2, "cosmético", "2", "«Bonus: Funciones en Python», por debajo del nivel de la semana", CERRADO, "Fase 3 (D3: se declara)", "f2a65fc", None),
    ("Q6", 2, "cosmético", "3", "Termina en un generador de clases con IA, no en el puente", CERRADO, "Fase 3", "35412a2", p_puente_modulo3),

    # ── Fase 3 · hallazgos nuevos ─────────────────────────────────────────
    ("F1", 3, "importante", "1", "`TypeError` en consola cada 60 s, en el primer módulo del curso", CERRADO, "Fase 3", "5e17c40", p_guarda_temporizador),
    ("F2", 3, "importante", "8, 9", "Marcado desbalanceado: un `<main>` que nunca se cierra *(preexistente)*", CERRADO, "Fase 3", "a25ebdb", p_estructura_html),
    ("F4", 3, "importante", "5, 7, 8, 9", "Dos `<main>` anidados: landmark duplicado, inválido en HTML", CERRADO, "Fase 3", "1f13603", p_main_anidado),
    ("F3", 3, "nota", "7", "El módulo **sí** tiene 82 fórmulas: corrige al informe de la Fase 2 §7.3", NOTA, "Fase 3", "7d69b57", None),

    # ── Cobertura del RA que la Fase 3 cerró de paso ──────────────────────
    ("R1", 2, "importante", "4", "El syllabus asigna el error HTTP 422 y el módulo no lo mencionaba", CERRADO, "Fase 3", "278175c", p_error_422),
]

CAMPOS = ("id", "fase", "gravedad", "modulos", "titulo", "estado", "cerrado_en", "commit", "prueba")
REG = [dict(zip(CAMPOS, h)) for h in H]


def ejecutar_pruebas() -> dict[str, tuple[bool, str]]:
    out = {}
    for h in REG:
        if h["prueba"]:
            try:
                out[h["id"]] = h["prueba"]()
            except Exception as e:                      # noqa: BLE001
                out[h["id"]] = (False, f"la prueba falló: {e}")
    return out


def discrepancias(pruebas) -> list[str]:
    """Estados declarados que la comprobación contra los archivos desmiente."""
    malas = []
    for h in REG:
        r = pruebas.get(h["id"])
        if not r:
            continue
        cumple, _ = r
        if h["estado"] == CERRADO and not cumple:
            malas.append(f"{h['id']} se declara cerrado y la prueba dice que no")
        if h["estado"] == ABIERTO and cumple:
            malas.append(f"{h['id']} se declara abierto y la prueba dice que ya está resuelto")
    return malas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--abiertos", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()

    pruebas = ejecutar_pruebas()
    filas = [h for h in REG if not args.abiertos or h["estado"] in (ABIERTO, PARCIAL)]

    if args.markdown:
        print(a_markdown(pruebas))
        return 0

    simbolo = {CERRADO: "✔", PARCIAL: "◐", ABIERTO: "✘", NOTA: "·"}
    print(f"{'ID':<5}{'F':<3}{'gravedad':<12}{'módulos':<13}{'estado':<9} prueba")
    print("-" * 108)
    for h in filas:
        r = pruebas.get(h["id"])
        ev = "" if not r else ("ok · " if r[0] else "NO · ") + r[1]
        print(f"{h['id']:<5}{h['fase']:<3}{h['gravedad']:<12}{h['modulos']:<13}"
              f"{simbolo[h['estado']]} {h['estado']:<7} {ev[:52]}")

    print("-" * 108)
    for est in (CERRADO, PARCIAL, ABIERTO, NOTA):
        print(f"  {est:<9} {sum(1 for h in REG if h['estado'] == est)}")
    print(f"  {'TOTAL':<9} {len(REG)}   ·   con prueba automática: {len(pruebas)}")

    d = discrepancias(pruebas)
    if d:
        print("\n!! LA TABLA CONTRADICE A LOS ARCHIVOS:")
        for x in d:
            print("   ", x)
        return 1
    print("\nNinguna prueba contradice al estado declarado.")
    return 0


def a_markdown(pruebas) -> str:
    hoy = "2026-08-08"
    L = [
        "# Estado de los hallazgos de la auditoría",
        "",
        "**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II  ",
        f"**Generado:** {hoy} por `scripts/auditoria/hallazgos.py --markdown`",
        "",
        "> **No edites esta tabla a mano.** El registro vive en `scripts/auditoria/hallazgos.py`,",
        f"> y {len(pruebas)} de los {len(REG)} hallazgos llevan una prueba que se ejecuta contra los",
        "> archivos: si el estado escrito y el archivo dejan de coincidir, el script lo dice y sale",
        "> con código 1. Las cifras de esta página se calculan, no se escriben.",
        "",
        "```bash",
        "python3 scripts/auditoria/hallazgos.py             # tabla completa y comprobación",
        "python3 scripts/auditoria/hallazgos.py --abiertos  # sólo lo que queda por hacer",
        "```",
        "",
        "---",
        "",
        "## Resumen",
        "",
        "| Estado | | Qué significa |",
        "|---|---|---|",
    ]
    n = lambda e: sum(1 for h in REG if h["estado"] == e)  # noqa: E731
    L += [
        f"| ✔ Cerrado | **{n(CERRADO)}** | Corregido y verificado |",
        f"| ◐ Parcial | **{n(PARCIAL)}** | Cerrado en unos módulos y abierto en otros |",
        f"| ✘ Abierto | **{n(ABIERTO)}** | Sigue ahí, con motivo declarado |",
        f"| · Nota | **{n(NOTA)}** | Corrección a un informe, no un defecto |",
        f"| | **{len(REG)}** | |",
        "",
        "Por fase de origen: "
        f"Fase 1 → {sum(1 for h in REG if h['fase'] == 1)} · "
        f"Fase 2 → {sum(1 for h in REG if h['fase'] == 2)} · "
        f"Fase 3 → {sum(1 for h in REG if h['fase'] == 3)}.",
        "",
        "---",
        "",
        "## Lo que queda por hacer",
        "",
        "| ID | Módulos | Hallazgo | Estado | Por qué sigue así |",
        "|---|---|---|---|---|",
    ]
    motivos = {
        "I11": "Hace falta buscar alternativas de acceso abierto: es trabajo de contenido",
        "C3": "Cosmético y sin efecto visible",
        "C4": "Cambiar de versión mayor sin verificar las 37 gráficas es peor negocio",
        "C7": "Requiere leer los bloques en contexto, uno a uno",
        "C9": "La Fase 1 demostró que no rompe ningún icono",
        "Q4": "Añadir gráficas es contenido nuevo, no corrección",
        "C5": "Quedan 3 referencias a «2025» en el módulo 6",
        "P6": "El bloque de reparto ya separa exposición de consulta; falta volver a medir la prosa",
        "P14": "El módulo 7 sigue sin dirigirse al estudiante",
        "Q2": "El módulo 4 sigue abriendo con un índice",
    }
    for h in REG:
        if h["estado"] not in (ABIERTO, PARCIAL):
            continue
        L.append(f"| **{h['id']}** | {h['modulos']} | {h['titulo']} | "
                 f"{'◐ parcial' if h['estado'] == PARCIAL else '✘ abierto'} | "
                 f"{motivos.get(h['id'], '—')} |")

    L += ["", "---", "", "## Registro completo", "",
          "| ID | Fase | Gravedad | Módulos | Hallazgo | Estado | Cerrado en | Commit |",
          "|---|---|---|---|---|---|---|---|"]
    simbolo = {CERRADO: "✔", PARCIAL: "◐", ABIERTO: "✘", NOTA: "·"}
    for h in REG:
        commit = f"`{h['commit']}`" if h["commit"] else "—"
        L.append(f"| {h['id']} | {h['fase']} | {h['gravedad']} | {h['modulos']} | {h['titulo']} | "
                 f"{simbolo[h['estado']]} {h['estado']} | {h['cerrado_en']} | {commit} |")

    L += ["", "---", "", "## Una corrección de aritmética a la Fase 2", "",
          "El informe de la Fase 2 cierra su §6 con «**4 bloqueantes, 16 importantes, 6",
          "cosméticos**», y **su propia tabla de importantes tiene 12 filas**, de P5 a P16. El 16",
          "sale de leer el identificador más alto como si fuera un recuento, olvidando que P1–P4",
          "son los bloqueantes. La Fase 2 encontró **22** hallazgos, no 26, y el «26 hallazgos",
          "abiertos» que suma con la Fase 1 arrastra el mismo error.",
          "",
          "No cambia ninguna conclusión —los cuatro bloqueantes siguen siendo cuatro—, pero es",
          "justo el tipo de cifra que esta tabla existe para no repetir.",
          ""]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
