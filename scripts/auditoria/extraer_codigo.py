#!/usr/bin/env python3
"""Extraccion de los bloques de codigo del material (T1.2, criterio C7).

Solo lectura. Los modulos guardan el codigo de tres formas distintas y hay que
cubrir las tres o se audita menos de lo que se cree:

  1. <pre>...</pre> con marcado de resaltado dentro (modulos 5, 7, 8, 9, 10-12)
  2. plantillas de JavaScript `const xxxCode = \\`...\\`` que React inyecta en un
     componente <CodeBlock> (modulos 0, 3, 4, 6, 13)
  3. objetos de datos JS con claves `snippet:` o `code:` (modulos 1, 2)

Salida: salida/bloques.json con un registro por bloque.

Uso:
    python3 scripts/auditoria/extraer_codigo.py
    python3 scripts/auditoria/extraer_codigo.py --ver 9   # vuelca los bloques del modulo 9
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"


# --- Limpieza ----------------------------------------------------------------
def descifrar_cfemail(hexa: str) -> str:
    b = bytes.fromhex(hexa)
    return "".join(chr(c ^ b[0]) for c in b[1:])


RE_CF = re.compile(
    r'<a\b[^>]*data-cfemail="([0-9a-f]+)"[^>]*>.*?</a>', re.S | re.I
)


def limpiar_html(fragmento: str) -> tuple[str, bool]:
    """Convierte un fragmento de HTML resaltado en el texto plano del codigo.

    Devuelve (codigo, tenia_residuo_cloudflare). El residuo se restituye a su
    valor original para poder ejecutar el bloque, pero se marca: lo que el
    estudiante ve en pantalla NO es esto.
    """
    tenia_cf = bool(RE_CF.search(fragmento))
    fragmento = RE_CF.sub(lambda m: descifrar_cfemail(m.group(1)), fragmento)
    fragmento = re.sub(r"<br\s*/?>", "\n", fragmento, flags=re.I)
    fragmento = re.sub(r"</(?:div|p|li)>", "\n", fragmento, flags=re.I)
    fragmento = re.sub(r"<[^>]+>", "", fragmento)
    return htmllib.unescape(fragmento).replace(" ", " "), tenia_cf


def desescapar_js(s: str) -> str:
    """Template literal de JS -> texto. Sin evaluar interpolaciones."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", "t": "\t", "r": "\r", "\\": "\\",
                        "`": "`", "$": "$", "'": "'", '"': '"'}.get(n, "\\" + n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


# --- Clasificacion de lenguaje ----------------------------------------------
# Los bloques suelen empezar con una cabecera de comentarios; clasificar por la
# primera linea da falsos "otro". Se puntua el cuerpo entero.
SENALES = {
    "dockerfile": [r"^\s*FROM\s+\w[\w.:/-]*\s*$", r"^\s*FROM\s+python:", r"^\s*(RUN|COPY|WORKDIR|ENTRYPOINT|CMD|EXPOSE|ENV)\s+\S"],
    "bash": [r"^\s*\$\s*\S", r"\bpip3?\s+install\b", r"\bpython3?\s+-m\s+venv\b",
             r"\bsource\s+\S+/bin/activate", r"\bdocker\s+(build|run|compose|ps|images)\b",
             r"\bgit\s+(init|add|commit|push|clone|config)\b", r"\bcurl\s+-", r"\buvicorn\s+\w",
             r"\bpytest\b\s*(-|$)", r"^\s*(cd|mkdir|ls|cat|export|chmod|echo)\s+\S"],
    "yaml": [r"^\s*(name|on|jobs|runs-on|steps|services|version|uses|with):",
             r"^\s*-\s+(uses|name|run):"],
    "sql": [r"^\s*(SELECT|INSERT INTO|UPDATE|DELETE FROM|CREATE TABLE|ALTER TABLE)\b"],
    "python": [r"^\s*def\s+\w+\s*\(", r"^\s*class\s+\w+", r"^\s*(import|from)\s+\w",
               r"^\s*@(app|router|pytest|property|staticmethod|classmethod|field_validator|model_validator)\b",
               r"\bprint\s*\(", r"^\s*if\s+__name__", r"\bself\.", r"->\s*\w+\s*:",
               r"^\s*\w+\s*:\s*(str|int|float|bool|list|dict|Optional|List|Dict)\b"],
}

# Sin una de estas, un <pre> con texto suelto no es codigo Python por mucho que
# contenga dos puntos y un parentesis.
ESTRUCTURALES_PY = re.compile(
    r"^\s*(def\s+\w+\s*\(|class\s+\w+|import\s+\w|from\s+\w[\w.]*\s+import\b|"
    r"@\w+|if\s+__name__)|(?<!\w)print\s*\(", re.M)


def lenguaje(codigo: str, pista: str | None) -> str:
    c = codigo.strip()
    if pista:
        p = pista.lower()
        canon = {"py": "python", "sh": "bash", "shell": "bash", "yml": "yaml",
                 "console": "bash", "docker": "dockerfile"}.get(p, p)
        if canon in {"python", "bash", "yaml", "json", "sql", "dockerfile",
                     "javascript", "html", "toml", "ini", "text"}:
            return canon

    puntos = {k: sum(len(re.findall(p, c, re.M | re.I)) for p in ps)
              for k, ps in SENALES.items()}
    # Un Dockerfile empieza siempre por FROM; gana aunque haya lineas RUN pip install
    if puntos["dockerfile"] >= 2:
        return "dockerfile"
    if re.match(r"^\s*[\{\[]", c) and c.rstrip().endswith(("}", "]")):
        try:
            json.loads(c)
            return "json"
        except Exception:
            pass
    mejor = max(puntos, key=lambda k: puntos[k])
    if puntos[mejor] == 0:
        # solo comentarios, texto de consola o salida pegada
        if re.match(r"^\s*(#|//)", c) and "\n" in c:
            return "comentarios"
        return "otro"
    # Varios <pre> del material son cajas de maquetacion (diagramas, tarjetas)
    # con texto suelto dentro. Una senal aislada no basta para llamarlo codigo.
    if mejor == "python" and (puntos["python"] < 2 or not ESTRUCTURALES_PY.search(c)):
        return "otro"
    return mejor


# --- Salida declarada --------------------------------------------------------
RE_COMENTARIO_SALIDA = re.compile(
    r"^[ \t]*#\s*(?:>>>|>|->|=>|Salida|Output|Resultado|Imprime|Devuelve|Retorna)\s*:?\s*(.*)$",
    re.I | re.M,
)
RE_REPL = re.compile(r"^>>> ", re.M)


def salida_declarada(codigo: str) -> dict:
    """Localiza afirmaciones de resultado dentro del propio bloque."""
    comentarios = [m.group(0).strip() for m in RE_COMENTARIO_SALIDA.finditer(codigo)]
    repl = bool(RE_REPL.search(codigo))
    return {
        "tiene_comentario_salida": bool(comentarios),
        "comentarios": comentarios,
        "es_transcripcion_repl": repl,
        "auditable": bool(comentarios) or repl,
    }


# --- Extractores -------------------------------------------------------------
def de_pre(html: str) -> list[dict]:
    bloques = []
    for m in re.finditer(r"<pre\b([^>]*)>(.*?)</pre>", html, re.S | re.I):
        attrs, cuerpo = m.group(1), m.group(2)
        pista = None
        mc = re.search(r'class="[^"]*language-([a-z]+)', attrs + cuerpo, re.I)
        if mc:
            pista = mc.group(1)
        codigo, cf = limpiar_html(cuerpo)
        # `<pre>${...}</pre>` dentro de una plantilla JS es el hueco donde se
        # inyecta el codigo, no el codigo: se descarta o se cuenta dos veces.
        if re.fullmatch(r"\s*\$\{[^}]*\}\s*", codigo):
            continue
        # En JSX el codigo va envuelto en `<pre>{\`...\`}</pre>`: las llaves y
        # las comillas invertidas son sintaxis de JSX, no del codigo.
        mj = re.fullmatch(r"\s*\{\s*`(.*)`\s*\}\s*", codigo, re.S)
        if mj:
            codigo = desescapar_js(mj.group(1))
        if codigo.strip():
            bloques.append({"origen": "pre", "pos": m.start(), "pista": pista,
                            "codigo": codigo, "cloudflare": cf})
    return bloques


# Plantillas de JS que NO son codigo del material: maquetacion, CSS, prompts de IA.
def _es_maquetacion(codigo: str) -> bool:
    if re.search(r"<(div|span|section|p|h[1-6]|table|li|button)\b", codigo, re.I):
        return True
    if re.search(r"(linear-gradient|rgba?\(|#[0-9a-fA-F]{6}\b|\d+px\b|\d+rem\b)", codigo):
        return True
    if codigo.count("${") >= 3 and codigo.count("\n") <= 3:
        return True
    return False


def de_plantillas_js(html: str) -> list[dict]:
    """Todo template literal asignado a una variable o a una clave de objeto.

    Cubre las tres variantes que usan los modulos: `const trainPyCode = ...`
    (13), `pythonCode: ...` (3, 4, 6) y `snippet: ...` (1, 2).
    """
    bloques = []
    patron = re.compile(
        r"(?:(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=|"          # const x =
        r"\b([A-Za-z_$][\w$]*)\s*:)\s*`(.*?)(?<!\\)`", re.S)
    for m in patron.finditer(html):
        nombre = m.group(1) or m.group(2)
        codigo = desescapar_js(m.group(3))
        if len(codigo.strip()) < 40 or codigo.strip().count("\n") < 1:
            continue
        if _es_maquetacion(codigo):
            continue
        bloques.append({"origen": f"js:{nombre}", "pos": m.start(),
                        "pista": None, "codigo": codigo, "cloudflare": False})
    return bloques


def linea_de(html: str, pos: int) -> int:
    return html.count("\n", 0, pos) + 1


def extraer(ruta: Path) -> list[dict]:
    html = ruta.read_text(encoding="utf-8", errors="replace")
    crudos = de_pre(html) + de_plantillas_js(html)
    vistos: set[str] = set()
    salida = []
    for i, b in enumerate(sorted(crudos, key=lambda x: x["pos"])):
        clave = b["codigo"].strip()
        if clave in vistos:
            continue
        vistos.add(clave)
        lang = lenguaje(b["codigo"], b["pista"])
        salida.append({
            "modulo": int(ruta.name.split("_")[0]),
            "archivo": ruta.name,
            "id": f"{ruta.name.split('_')[0]}#{len(salida) + 1}",
            "linea": linea_de(html, b["pos"]),
            "origen": b["origen"],
            "lenguaje": lang,
            "lineas_codigo": b["codigo"].strip().count("\n") + 1,
            "cloudflare_restituido": b["cloudflare"],
            "salida": salida_declarada(b["codigo"]),
            "codigo": b["codigo"].strip(),
        })
    return salida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", type=int, help="volcar los bloques de un modulo")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)

    rutas = sorted((p for p in RAIZ.glob("*.html") if re.match(r"^\d+_", p.name)),
                   key=lambda p: int(p.name.split("_")[0]))
    todos: list[dict] = []
    for p in rutas:
        todos.extend(extraer(p))

    if args.ver is not None:
        for b in todos:
            if b["modulo"] == args.ver:
                print(f"--- {b['id']} L{b['linea']} [{b['lenguaje']}] {b['origen']} "
                      f"auditable={b['salida']['auditable']}")
                print(b["codigo"][:1200])
                print()
        return 0

    (SALIDA / "bloques.json").write_text(
        json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")

    langs = sorted({b["lenguaje"] for b in todos})
    print(f"{'mod':>3} {'total':>5} " + " ".join(f"{l[:9]:>9}" for l in langs) + f" {'auditab.':>9}")
    print("-" * (10 + 10 * len(langs) + 10))
    for p in rutas:
        n = int(p.name.split("_")[0])
        bs = [b for b in todos if b["modulo"] == n]
        cuenta = " ".join(f"{sum(1 for b in bs if b['lenguaje'] == l) or '.':>9}" for l in langs)
        aud = sum(1 for b in bs if b["salida"]["auditable"])
        print(f"{n:>3} {len(bs):>5} {cuenta} {aud:>9}")
    bs = todos
    cuenta = " ".join(f"{sum(1 for b in bs if b['lenguaje'] == l):>9}" for l in langs)
    print("-" * (10 + 10 * len(langs) + 10))
    print(f"{'TOT':>3} {len(bs):>5} {cuenta} "
          f"{sum(1 for b in bs if b['salida']['auditable']):>9}")
    print(f"\nJSON en {SALIDA / 'bloques.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
