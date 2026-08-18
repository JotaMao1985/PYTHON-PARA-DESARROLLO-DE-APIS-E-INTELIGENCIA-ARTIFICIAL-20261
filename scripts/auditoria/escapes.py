#!/usr/bin/env python3
"""Barras invertidas que el literal de plantilla de JavaScript se come.

Solo lectura. No modifica ningun archivo del material.

EL DEFECTO. Todo el codigo que lee el estudiante viaja dentro de un literal de
plantilla de JavaScript —`code={`...`}` en LP-CORE, `pythonCode: `...`` en el
heredado—. Al evaluar ese literal, JavaScript resuelve los escapes: `\\n` se
convierte en un salto de linea, y una barra seguida de un caracter que NO es un
escape reconocido simplemente PIERDE LA BARRA. Asi, esto:

    pattern=r"^\\d{5}$"        <- escrito en el archivo

llega a la pantalla como:

    pattern=r"^d{5}$"          <- lo que copia el estudiante

Es invisible a la lectura: el archivo se ve correcto y el navegador no protesta.
Se encontro en el modulo 4, donde ademas invertia la leccion —el ejemplo titulado
«Pattern invalido» rechazaba un correo valido—, y la misma pagina mostraba la
expresion correcta cuatro parrafos mas arriba, porque ahi era texto JSX y no
literal de plantilla.

LA REGLA, Y POR QUE NO ES LA OBVIA. La primera version de este detector marcaba
toda linea cuyo texto cambia al evaluarse. Es la regla equivocada, y da falsos
positivos justo sobre el codigo BIEN escrito: `\\\\w` TIENE que evaluarse a
`\\w`, y una continuacion de linea de Dockerfile (`\\\\` al final) tiene que
evaluarse a `\\`. Marcaba 18 lineas sanas del modulo 13 y las dos que se acababan
de arreglar en el 4.

La regla correcta no mira si el texto cambio, sino si la barra SOBREVIVE:

  * una racha PAR de barras se conserva (cada pareja deja una barra),
  * una racha IMPAR pierde la ultima, salvo que el caracter siguiente sea uno de
    los escapes que JavaScript reconoce.

Solo el segundo caso es el defecto. La correccion es doblar la barra en el
origen, que es como ya estaban escritos los `\\\\n` de los mismos bloques.

Uso:
    python3 scripts/auditoria/escapes.py                  # los 13 y heredado/
    python3 scripts/auditoria/escapes.py 4_*.html         # archivos sueltos
    python3 scripts/auditoria/escapes.py --autoprueba     # comprueba el detector
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SALIDA = Path(__file__).resolve().parent / "salida"
RAIZ = Path(__file__).resolve().parents[2]

# Donde vive el codigo que lee el estudiante. Son dos y no uno porque el
# heredado y el capitulo montado lo guardan distinto.
#
# El cuerpo se toma hasta el primer acento grave SIN ESCAPAR: `(?:[^`\\]|\\.)*`.
# Un `.*?` a secas se para en el primer acento grave que vea, incluido un
# `\`` escapado, y entonces el bloque queda truncado y todo lo que venga
# despues deja de mirarse. Se descubrio asi: el unico positivo del primer
# barrido era el corte, no un defecto.
CUERPO = r"((?:[^`\\]|\\.)*)"
PORTADORES = [
    ("code={`...`}", re.compile(r"code=\{`" + CUERPO + r"`\}")),
    ("pythonCode", re.compile(r"pythonCode:\s*`" + CUERPO + r"`")),
]

# Caracteres tras los que la barra SI sobrevive, porque JavaScript reconoce el
# escape. Incluye `/`, que no es un escape pero se usa a proposito para partir
# un `</script>` que si no cerraria la etiqueta antes de tiempo.
ESCAPES_VALIDOS = set("nrtbfv0xu$`\\'\"/\n")

RACHA = re.compile(r"(\\+)(.|$)", re.S)


def lineas_afectadas(codigo: str, linea_base: int) -> list[dict]:
    """Lineas del bloque en las que una barra desaparece al evaluarse."""
    hallazgos = []
    for i, linea in enumerate(codigo.split("\n")):
        for r in RACHA.finditer(linea):
            barras, siguiente = r.group(1), r.group(2)
            if len(barras) % 2 == 1 and siguiente not in ESCAPES_VALIDOS:
                hallazgos.append({
                    "linea": linea_base + i,
                    "escape": "\\" + siguiente,
                    "escrito": linea.strip()[:120],
                    "en_pantalla": _evaluar(linea).strip()[:120],
                })
                break  # una vez por linea: basta para ir a mirarla
    return hallazgos


def _evaluar(linea: str) -> str:
    """Reproduce lo que JavaScript hace con los escapes de la linea.

    Solo para ENSEÑAR el resultado en el informe; la deteccion no depende de
    esto. Una racha par deja la mitad de las barras; una impar deja la mitad
    baja y pierde la ultima si el caracter siguiente no es un escape valido.
    """
    def sustituir(r: re.Match) -> str:
        barras, siguiente = r.group(1), r.group(2)
        conservadas = "\\" * (len(barras) // 2)
        if len(barras) % 2 == 0:
            return conservadas + siguiente
        if siguiente in ESCAPES_VALIDOS:
            return conservadas + "\\" + siguiente
        return conservadas + siguiente
    return RACHA.sub(sustituir, linea)


def revisar_texto(texto: str) -> tuple[int, list[dict]]:
    bloques, defectos = 0, []
    for nombre, patron in PORTADORES:
        for m in patron.finditer(texto):
            bloques += 1
            linea_base = texto.count("\n", 0, m.start()) + 1
            for h in lineas_afectadas(m.group(1), linea_base):
                defectos.append({"portador": nombre, **h})
    return bloques, defectos


def revisar(archivo: Path) -> dict:
    bloques, defectos = revisar_texto(archivo.read_text(encoding="utf-8"))
    try:
        nombre = str(archivo.relative_to(RAIZ))
    except ValueError:
        nombre = str(archivo)  # archivo de fuera del repositorio: se admite
    return {"archivo": nombre, "bloques": bloques, "defectos": defectos}


def archivos_del_material() -> list[Path]:
    modulos = sorted(RAIZ.glob("[0-9]*.html"), key=lambda p: int(p.name.split("_")[0]))
    return modulos + sorted(RAIZ.glob("heredado/[0-9]*.html"),
                            key=lambda p: int(p.name.split("_")[0]))


CASOS_PRUEBA = [
    # (codigo, cuantas lineas deben salir marcadas, por que)
    (r'pattern=r"^\d{5}$"', 1, "barra impar ante 'd': se la come"),
    (r'pattern=r"^\\d{5}$"', 0, "barra doblada: sobrevive, es la forma correcta"),
    (r'print("\\n=== fin ===")', 0, "el \\\\n de un print de Python esta bien escrito"),
    (r'RUN apt-get update \\', 0, "continuacion de linea de Dockerfile, doblada"),
    (r'texto = "\w+"', 1, "misma clase de defecto sin ser una regex de Pydantic"),
    (r'msg = `hola`', 0, "sin barras: nada que marcar"),
    (r'roto = "<\/script>"', 0, "la barra ante / es deliberada"),
    (r'salto = "\n"', 0, "\\n es un escape que JavaScript reconoce"),
]


# La segunda mitad de la autoprueba: que el bloque se recorte entero. Un
# detector que trunca el bloque calla sobre todo lo que venga despues, y
# callar es justo lo que parece estar bien.
CASOS_EXTRACCION = [
    # (texto, bloques esperados, lineas afectadas esperadas, por que)
    (r"code={`hola`}", 1, 0, "bloque simple"),
    (r"code={`habla de \`projects\` y nada mas`}", 1, 0,
     "un acento grave escapado no corta el bloque ni es un defecto"),
    (r'code={`ver \`x\` y luego pattern=r"^\d{5}$"`}', 1, 1,
     "el defecto viene DESPUES del acento grave escapado: hay que verlo igual"),
    (r'pythonCode: `texto = "\w+"`', 1, 1, "el portador del heredado"),
    (r"code={`uno`} y code={`dos`}", 2, 0, "dos bloques seguidos, no uno largo"),
]


def autoprueba() -> int:
    """El detector tiene que fallar donde debe y callar donde no.

    Sin esto solo sabriamos que no marca nada en archivos limpios, que es
    exactamente lo que haria un detector roto.
    """
    fallos = 0
    print("--- la regla de la barra ---")
    for codigo, esperados, motivo in CASOS_PRUEBA:
        obtenidos = len(lineas_afectadas(codigo, 1))
        ok = obtenidos == esperados
        fallos += not ok
        print(f"  [{'OK ' if ok else 'MAL'}] {codigo!r}")
        print(f"        espera {esperados}, obtiene {obtenidos} — {motivo}")

    print("\n--- el recorte del bloque ---")
    for texto, n_bloques, n_lineas, motivo in CASOS_EXTRACCION:
        bloques, defectos = revisar_texto(texto)
        ok = bloques == n_bloques and len(defectos) == n_lineas
        fallos += not ok
        print(f"  [{'OK ' if ok else 'MAL'}] {texto!r}")
        print(f"        espera {n_bloques} bloques/{n_lineas} lineas, "
              f"obtiene {bloques}/{len(defectos)} — {motivo}")

    total = len(CASOS_PRUEBA) + len(CASOS_EXTRACCION)
    print(f"\n  {total - fallos}/{total} casos pasan")
    return 1 if fallos else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("archivos", nargs="*", help="por omision, los 13 modulos y heredado/")
    ap.add_argument("--autoprueba", action="store_true",
                    help="comprueba el detector contra casos conocidos y sale")
    args = ap.parse_args()

    if args.autoprueba:
        print("=== AUTOPRUEBA DEL DETECTOR ===")
        return autoprueba()

    objetivos = [Path(a).resolve() for a in args.archivos] or archivos_del_material()
    resultados = [revisar(f) for f in objetivos if f.is_file()]

    total_bloques = sum(r["bloques"] for r in resultados)
    sucios = [r for r in resultados if r["defectos"]]

    for r in resultados:
        marca = "✗" if r["defectos"] else "✓"
        print(f"{marca} {r['archivo']}  ({r['bloques']} bloques, "
              f"{len(r['defectos'])} lineas afectadas)")
        for d in r["defectos"]:
            print(f"    L{d['linea']}  «{d['escape']}» se pierde")
            print(f"      escrito:   {d['escrito']}")
            print(f"      pantalla:  {d['en_pantalla']}")

    print(f"\n{len(resultados)} archivos, {total_bloques} bloques, "
          f"{len(sucios)} con barras que se pierden")

    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "escapes.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON en {SALIDA / 'escapes.json'}")

    return 1 if sucios else 0


if __name__ == "__main__":
    raise SystemExit(main())
