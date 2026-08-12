#!/usr/bin/env python3
"""Verificacion del codigo Python del material (T1.2, criterio C7).

Tres pasadas, de la mas barata a la mas cara:

  1. SINTAXIS   — `ast.parse` sobre cada bloque de Python. Un bloque que no
                  compila es un defecto visible para el estudiante.
  2. IMPORTS    — que dependencias exige cada bloque y cuales estan instaladas.
                  Determina que es ejecutable y que no, sin darlo por bueno.
  3. EJECUCION  — corre los bloques ejecutables en un directorio temporal, con
                  limite de tiempo, y compara la salida real con la declarada.

Los bloques no ejecutables se listan aparte con el motivo. Nunca se dan por
buenos en silencio.

Uso:
    python3 scripts/auditoria/verificar_codigo.py
    python3 scripts/auditoria/verificar_codigo.py --ejecutar     # incluye la pasada 3
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path

SALIDA = Path(__file__).resolve().parent / "salida"
RAIZ = Path(__file__).resolve().parents[2]

STDLIB = set(sys.stdlib_module_names)

# Un bloque que llama a esto no se ejecuta: efectos fuera del directorio temporal
# o procesos que no terminan.
PELIGROSO = [
    (r"\bsubprocess\b", "lanza subprocesos"),
    (r"\bos\.(system|remove|unlink|rmdir|removedirs)\b", "borra o ejecuta en el sistema"),
    (r"\bshutil\.rmtree\b", "borra arboles de directorios"),
    (r"\buvicorn\.run\b|\bapp\.run\(", "arranca un servidor que no termina"),
    (r"\bwhile\s+True\b", "bucle potencialmente infinito"),
    (r"\brequests\.(get|post|put|delete)\b|\bhttpx\.", "hace peticiones de red"),
    (r"\binput\s*\(", "espera entrada por teclado"),
    (r"\bcelery\b|\bCelery\(", "necesita un broker de mensajes en marcha"),
]


def clasificar_fallo(stderr: str, codigo_bloque: str, anteriores: str) -> str:
    """Distingue el defecto real del bloque que continua a otro.

    Un NameError sobre un nombre que SI se define en un bloque anterior del
    mismo modulo es una continuacion legitima; sobre un nombre que no aparece
    en ninguna parte, es un fallo del material.
    """
    m = re.search(r"NameError: name '([^']+)' is not defined", stderr)
    if m:
        nombre = m.group(1)
        if re.search(rf"^\s*{re.escape(nombre)}\s*=|^\s*(def|class)\s+{re.escape(nombre)}\b|"
                     rf"import\s+\w+\s+as\s+{re.escape(nombre)}\b", anteriores, re.M):
            return "continua un bloque anterior del mismo modulo"
        return f"DEFECTO: usa '{nombre}' sin definirlo ni importarlo en ningun bloque"
    if "FileNotFoundError" in stderr:
        return "depende de un artefacto que produce un bloque anterior"
    if "ModuleNotFoundError" in stderr:
        return "dependencia no instalada"
    return "DEFECTO: falla en ejecucion"

# Fragmentos deliberadamente incompletos: no son errores de sintaxis del autor.
MARCAS_FRAGMENTO = [r"^\s*\.\.\.\s*$", r"#\s*\.\.\.", r"^\s*# resto", r"^\s*# \(\.\.\.\)"]


def modulos_importados(arbol: ast.AST) -> set[str]:
    mods: set[str] = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            mods.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods.add(n.module.split(".")[0])
    return mods


def instalado(mod: str) -> bool:
    if mod in STDLIB:
        return True
    try:
        return find_spec(mod) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def motivo_no_ejecutable(codigo: str, faltantes: set[str]) -> str | None:
    if faltantes:
        return f"dependencias no instaladas: {', '.join(sorted(faltantes))}"
    for patron, razon in PELIGROSO:
        if re.search(patron, codigo):
            return razon
    if re.search(r"@app\.(get|post|put|delete|patch)\b", codigo):
        return "define endpoints; requiere cliente de pruebas, no salida por consola"
    if not re.search(r"\bprint\s*\(|^>>> ", codigo, re.M):
        return "no imprime nada: no hay salida que comparar"
    return None


def ejecutar(codigo: str, tiempo: int = 20) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "bloque.py"
        f.write_text(codigo, encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(f)], cwd=tmp, timeout=tiempo,
                               capture_output=True, text=True)
            return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-2000:]}
        except subprocess.TimeoutExpired:
            return {"rc": None, "stdout": "", "stderr": f"TIMEOUT tras {tiempo}s"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ejecutar", action="store_true", help="ejecuta los bloques ejecutables")
    args = ap.parse_args()

    # Este script NO extrae: consume el bloques.json que produce extraer_codigo.py.
    # Si alguien edita un modulo y verifica sin volver a extraer, obtiene un verde
    # que no corresponde al archivo que tiene delante. Paso durante la Fase 3 y
    # costo dos commits con una cifra equivocada, asi que ahora se comprueba.
    ruta_bloques = SALIDA / "bloques.json"
    if not ruta_bloques.exists():
        print("Falta bloques.json. Ejecuta antes: python3 scripts/auditoria/extraer_codigo.py")
        return 2
    mtime_json = ruta_bloques.stat().st_mtime
    desfasados = [
        p.name for p in sorted(RAIZ.glob("[0-9]*_*.html"))
        if p.stat().st_mtime > mtime_json
    ]
    if desfasados:
        print("bloques.json es mas antiguo que estos modulos, asi que verificarlo "
              "no dice nada del archivo actual:")
        for nombre in desfasados:
            print(f"    {nombre}")
        print("\nEjecuta antes: python3 scripts/auditoria/extraer_codigo.py")
        return 2

    bloques = json.loads(ruta_bloques.read_text(encoding="utf-8"))
    python = [b for b in bloques if b["lenguaje"] == "python"]
    print(f"{len(python)} bloques de Python de {len(bloques)} bloques totales.\n")

    resultados = []
    for b in python:
        r = {k: b[k] for k in ("id", "modulo", "archivo", "linea", "origen", "lineas_codigo")}
        r["auditable_por_salida"] = b["salida"]["auditable"]
        r["salida_declarada"] = b["salida"]["comentarios"]
        try:
            arbol = ast.parse(b["codigo"])
            r["sintaxis"] = "ok"
            imports = modulos_importados(arbol)
        except SyntaxError as e:
            es_fragmento = any(re.search(p, b["codigo"], re.M) for p in MARCAS_FRAGMENTO)
            r["sintaxis"] = "fragmento" if es_fragmento else "ERROR"
            r["error"] = f"linea {e.lineno}: {e.msg}"
            r["linea_error"] = (b["codigo"].splitlines()[e.lineno - 1].strip()
                                if e.lineno and e.lineno <= len(b["codigo"].splitlines()) else "")
            imports = set()
        r["imports"] = sorted(imports)
        r["imports_faltantes"] = sorted(m for m in imports if not instalado(m))
        if r["sintaxis"] in ("ok", "fragmento"):
            r["no_ejecutable"] = motivo_no_ejecutable(b["codigo"], set(r["imports_faltantes"]))
        else:
            r["no_ejecutable"] = "no compila"
        resultados.append(r)

    # --- pasada 1: sintaxis
    errores = [r for r in resultados if r["sintaxis"] == "ERROR"]
    print("=== 1. SINTAXIS ===")
    print(f"  compilan: {sum(1 for r in resultados if r['sintaxis'] == 'ok')}  "
          f"fragmentos declarados: {sum(1 for r in resultados if r['sintaxis'] == 'fragmento')}  "
          f"ERRORES: {len(errores)}")
    for r in errores:
        print(f"  [{r['id']}] {r['archivo']}:{r['linea']}  {r['error']}")
        print(f"        -> {r['linea_error'][:110]}")

    # --- pasada 2: dependencias
    print("\n=== 2. DEPENDENCIAS ===")
    faltan: dict[str, int] = {}
    for r in resultados:
        for m in r["imports_faltantes"]:
            faltan[m] = faltan.get(m, 0) + 1
    if faltan:
        print("  paquetes que el material importa y no estan en este entorno:")
        for m, n in sorted(faltan.items(), key=lambda x: -x[1]):
            print(f"    {m:<24} en {n} bloques")
    else:
        print("  todas las dependencias importadas estan disponibles")

    ejecutables = [r for r in resultados if not r["no_ejecutable"]]
    print(f"\n  ejecutables sin dependencias externas: {len(ejecutables)}")
    motivos: dict[str, int] = {}
    for r in resultados:
        if r["no_ejecutable"]:
            clave = re.sub(r":.*", "", r["no_ejecutable"])
            motivos[clave] = motivos.get(clave, 0) + 1
    for m, n in sorted(motivos.items(), key=lambda x: -x[1]):
        print(f"    no ejecutable ({n}): {m}")

    # --- pasada 3: ejecucion
    if args.ejecutar:
        print("\n=== 3. EJECUCION ===")
        indice = {b["id"]: b for b in bloques}
        for r in ejecutables:
            res = ejecutar(indice[r["id"]]["codigo"])
            r["ejecucion"] = res
            estado = "OK " if res["rc"] == 0 else "FALLA"
            print(f"  [{estado}] {r['id']} {r['archivo']}:{r['linea']}")
            if res["rc"] != 0:
                previos = "\n".join(
                    b["codigo"] for b in bloques
                    if b["modulo"] == r["modulo"] and b["linea"] < r["linea"])
                r["diagnostico"] = clasificar_fallo(res["stderr"], indice[r["id"]]["codigo"], previos)
                ultima = res["stderr"].strip().splitlines()[-1][:130] if res["stderr"].strip() else "sin stderr"
                print(f"        {ultima}")
                print(f"        -> {r['diagnostico']}")
            elif r["salida_declarada"]:
                coincide = all(
                    re.sub(r"^#\s*(Output|Salida|Resultado)\s*:?\s*", "", d, flags=re.I).strip()
                    in res["stdout"] for d in r["salida_declarada"])
                r["salida_coincide"] = coincide
                print(f"        declara: {r['salida_declarada']}")
                print(f"        imprime: {res['stdout'].strip()[:200]!r}")
                print(f"        -> {'COINCIDE' if coincide else 'DIFIERE'}")
        fallan = [r for r in ejecutables if r["ejecucion"]["rc"] != 0]
        defectos = [r for r in fallan if r.get("diagnostico", "").startswith("DEFECTO")]
        comparados = [r for r in ejecutables if "salida_coincide" in r]
        print(f"\n  {len(ejecutables) - len(fallan)}/{len(ejecutables)} corren sin error")
        print(f"  {len(fallan)} fallan, de los cuales {len(defectos)} son defectos del material")
        print(f"  {sum(1 for r in comparados if r['salida_coincide'])}/{len(comparados)} "
              f"salidas declaradas coinciden con la real")

    (SALIDA / "verificacion_codigo.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON en {SALIDA / 'verificacion_codigo.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
