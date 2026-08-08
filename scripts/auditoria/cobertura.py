#!/usr/bin/env python3
"""Cobertura del RA declarado y de la rubrica, modulo a modulo (T2.0b, criterios C1 y C2).

Solo lectura.

C1 pregunta «¿el modulo cubre el resultado de aprendizaje de su semana?». Eso se
puede medir sin opinar: el syllabus declara para cada semana un `ra`, una
`teoria`, una `practica` y un trabajo `autonomo` concretos. Aqui cada uno de esos
campos se descompone en TEMAS ATOMICOS y se busca cada tema en el modulo.

El juicio pedagogico sigue siendo mio; lo que este script aporta es la evidencia
de si el tema esta o no esta, con su conteo, para que la ficha no sea impresion.

AVISO sobre el metodo: un tema «presente» significa que el modulo lo NOMBRA, no
que lo ensene bien. Un 12/12 no absuelve al modulo; un 0/12 si lo condena. Es un
detector de ausencias, no de calidad.

Uso:
    python3 scripts/auditoria/cobertura.py
    python3 scripts/auditoria/cobertura.py --detalle 5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "salida"

# --- Temas que el syllabus declara para cada semana --------------------------
# Cada entrada: (etiqueta legible, patron, origen) donde origen indica de que
# campo del syllabus sale el tema: ra / teoria / practica / autonomo.
TEMAS: dict[int, list[tuple[str, str, str]]] = {
    1: [
        ("Python 3.11.9", r"3\.11\.9", "ra"),
        ("venv", r"\bvenv\b", "ra"),
        ("Git", r"\bgit\b", "ra"),
        ("conda (comparado con venv)", r"\bconda\b", "teoria"),
        ("decoradores", r"\bdecorador", "teoria"),
        ("type hinting", r"type hint|anotaci[oó]n de tipo|typing\b", "practica"),
        ("repositorio propio", r"\brepositorio\b|git init", "practica"),
        ("Pandas", r"\bpandas\b", "autonomo"),
        ("funciones puras", r"funci[oó]n(?:es)? pura", "autonomo"),
    ],
    2: [
        ("verbos HTTP", r"\bGET\b|\bPOST\b|\bPUT\b|\bDELETE\b", "teoria"),
        ("códigos de estado", r"c[oó]digo de estado|status code|\b(?:200|404|500)\b", "teoria"),
        ("cabeceras", r"\bcabecera|\bheader", "teoria"),
        ("JSON", r"\bJSON\b", "teoria"),
        ("Pickle", r"\bpickle\b", "teoria"),
        ("requirements.txt", r"requirements\.txt", "teoria"),
        ("Requests", r"\brequests\b", "ra"),
        ("serialización", r"serializ", "ra"),
    ],
    3: [
        ("clases", r"\bclase[s]?\b", "ra"),
        ("atributos", r"\batributo", "teoria"),
        ("métodos", r"\bm[eé]todo", "teoria"),
        ("composición vs herencia", r"composici[oó]n|herencia", "teoria"),
        ("métodos especiales (dunder)", r"__init__|__str__|__repr__|m[eé]todo[s]? especial|dunder", "teoria"),
        ("dataclasses", r"dataclass", "ra"),
        ("por qué lo exigen Pydantic/SQLAlchemy/FastAPI", r"pydantic|sqlalchemy|fastapi", "teoria"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    4: [
        ("modelos Pydantic", r"BaseModel|modelo[s]? pydantic", "ra"),
        ("campos / Field", r"\bField\b|\bcampo", "teoria"),
        ("coerción de tipos", r"coerci[oó]n|coerce|conversi[oó]n autom[aá]tica", "teoria"),
        ("serialización", r"serializ", "teoria"),
        ("deserialización", r"deserializ|parse|model_validate", "teoria"),
        ("error 422", r"\b422\b", "teoria"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    5: [
        ("servidor web", r"servidor web", "teoria"),
        ("WSGI", r"\bWSGI\b", "teoria"),
        ("ASGI", r"\bASGI\b", "teoria"),
        ("routing", r"\brouting\b|\bruta[s]?\b|\benrutamiento\b", "teoria"),
        ("Flask frente a modernos", r"\bflask\b", "teoria"),
        ("síncrono vs asíncrono", r"as[ií]ncrono|\basync\b", "teoria"),
        ("ciclo petición-respuesta", r"petici[oó]n[- ]respuesta|request[- ]response", "ra"),
        ("exponer la limpieza como endpoint", r"\bendpoint\b", "practica"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    6: [
        ("FastAPI", r"\bfastapi\b", "ra"),
        ("routers / organización modular", r"\bAPIRouter\b|\brouter", "teoria"),
        ("type hinting como contrato", r"type hint|anotaci[oó]n de tipo", "teoria"),
        ("OpenAPI", r"\bOpenAPI\b", "teoria"),
        ("Swagger UI", r"\bswagger\b", "teoria"),
        ("Redoc", r"\bredoc\b", "teoria"),
        ("async/await", r"async\s*/\s*await|\bawait\b", "teoria"),
        ("Uvicorn", r"\buvicorn\b", "ra"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    7: [
        ("validadores de campo", r"field_validator|validador de campo", "teoria"),
        ("tipos complejos / anotaciones", r"\bAnnotated\b|conint|constr|tipo[s]? complejo", "teoria"),
        ("modelos anidados", r"anidad", "teoria"),
        ("error 422", r"\b422\b", "teoria"),
        ("rango estadístico", r"\brango\b", "practica"),
        ("descripciones de campo", r"description\s*=|\bdescripci[oó]n de(?:l)? campo", "autonomo"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    8: [
        ("variables de entorno", r"variable[s]? de entorno|env var", "teoria"),
        ("inyección de dependencias", r"inyecci[oó]n de dependencia|\bDepends\b", "ra"),
        ("conexión a base de datos", r"conexi[oó]n a (?:la )?base de datos|get_db", "teoria"),
        ("carga de configuración", r"configuraci[oó]n|settings", "teoria"),
        ("python-dotenv", r"dotenv", "ra"),
        ("dependencia de parámetros comunes", r"par[aá]metro[s]? com[uú]n", "practica"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    9: [
        ("ORM frente a SQL crudo", r"\bORM\b", "teoria"),
        ("SQLAlchemy Core", r"sqlalchemy core|\bCore\b", "teoria"),
        ("SQLAlchemy ORM", r"sqlalchemy", "ra"),
        ("Alembic / migraciones", r"alembic|migraci[oó]n", "teoria"),
        ("SQLite", r"sqlite", "teoria"),
        ("histórico de predicciones", r"hist[oó]rico", "ra"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    10: [
        ("pirámide de testing", r"pir[aá]mide", "teoria"),
        ("pytest", r"\bpytest\b", "ra"),
        ("TestClient", r"TestClient", "teoria"),
        ("fixtures", r"\bfixture", "teoria"),
        ("reproducibilidad", r"reproducib", "ra"),
        ("httpx", r"\bhttpx\b", "ra"),
        ("modos de fallo", r"modo[s]? de fallo|caso[s]? de fallo|fallo previsto", "practica"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    11: [
        ("del entorno virtual al contenedor", r"entorno virtual", "teoria"),
        ("contenedores frente a VM", r"m[aá]quina[s]? virtual", "teoria"),
        ("Dockerfile", r"Dockerfile", "teoria"),
        ("python:3.11.9-slim-bookworm", r"3\.11\.9-slim-bookworm", "teoria"),
        ("construcción multietapa", r"multietapa|multi-stage|multistage", "teoria"),
        ("equivalencia con el entorno local", r"equivalen", "autonomo"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    12: [
        ("plataforma como servicio (PaaS)", r"\bPaaS\b|plataforma como servicio", "teoria"),
        ("Render", r"\brender\b", "practica"),
        ("entorno prod frente a dev", r"producci[oó]n.{0,40}desarrollo|desarrollo.{0,40}producci[oó]n", "teoria"),
        ("GitHub Actions", r"GitHub Actions", "teoria"),
        ("integración continua", r"integraci[oó]n continua|\bCI\b", "ra"),
        ("logs de producción", r"\blog[s]?\b", "teoria"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
    13: [
        ("entrenar", r"\bentrenar\b|\bentrenamiento\b|\.fit\(", "teoria"),
        ("serializar", r"serializ", "teoria"),
        ("cargar", r"\bcargar\b|\bload\b", "teoria"),
        ("predecir", r"\bpredic|\bpredict\b", "ra"),
        ("patrón Singleton", r"singleton", "teoria"),
        ("joblib", r"joblib", "ra"),
        ("coste de dependencias ML sobre la imagen", r"tama[nñ]o de la imagen|peso de la imagen", "teoria"),
        ("Scikit-Learn", r"scikit|sklearn", "ra"),
        ("consistencia con el entrenamiento", r"consistente|consistencia|skew", "ra"),
        ("Python 3.11.9", r"3\.11\.9", "ra"),
    ],
}

# --- Rubrica: que criterio prepara cada modulo, segun el syllabus -------------
# `esperado` es el mapeo que se deduce del cronograma; el script comprueba si el
# modulo menciona de verdad la materia del criterio.
RUBRICA = {
    10: ("Backend con FastAPI, Pydantic y SQLAlchemy", 12,
         r"fastapi|pydantic|sqlalchemy", [4, 6, 7, 8, 9]),
    11: ("Pipeline de ML, Singleton y endpoint de predicción", 8,
         r"singleton|joblib|predict", [13]),
    12: ("Pruebas con pytest y TestClient", 4, r"pytest|TestClient", [10]),
    13: ("Docker, despliegue en PaaS e integración continua", 7,
         r"docker|PaaS|GitHub Actions", [11, 12]),
    14: ("Tablero (frontend)", 3,
         r"\btablero\b|\bdashboard\b|streamlit|\bfrontend\b", []),
    15: ("Buenas prácticas: Git, venv, README y .env", 6,
         r"\bgit\b|\bvenv\b|README|\.env\b", [1, 8]),
}


def texto_modulo(n: int) -> str:
    """Prosa + codigo: se busca en TODO lo que el modulo contiene, no solo en la
    prosa, porque un tema puede estar solo en un bloque de codigo (`joblib`,
    `TestClient`) y eso cuenta como cubierto."""
    ruta = next(RAIZ.glob(f"{n}_*.html"))
    html = ruta.read_text(encoding="utf-8", errors="replace")
    # Se despoja de etiquetas para no contar nombres de clase CSS como temas.
    sin_estilo = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S)
    sin_attr = re.sub(r"\s(?:class|style|d|viewBox|stroke[a-z-]*|fill)=\"[^\"]*\"", " ", sin_estilo)
    return re.sub(r"<[^>]+>", " ", sin_attr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detalle", type=int, help="desglose de un modulo")
    args = ap.parse_args()

    resultados = {}
    print(f"{'#':>3}  {'cubiertos':>10}  temas ausentes")
    print("-" * 78)
    for n in range(1, 14):
        txt = texto_modulo(n)
        filas = []
        for etiqueta, patron, origen in TEMAS[n]:
            veces = len(re.findall(patron, txt, re.I))
            filas.append({"tema": etiqueta, "origen": origen,
                          "veces": veces, "presente": veces > 0})
        ausentes = [f["tema"] for f in filas if not f["presente"]]
        resultados[str(n)] = {"temas": filas, "ausentes": ausentes,
                              "cubiertos": len(filas) - len(ausentes),
                              "total": len(filas)}
        print(f"{n:>3}  {len(filas)-len(ausentes):>4}/{len(filas):<5}  "
              f"{', '.join(ausentes) if ausentes else '—'}")

        if args.detalle == n:
            print()
            for f in filas:
                marca = "✓" if f["presente"] else "✗"
                print(f"   {marca} [{f['origen']:<9}] {f['tema']:<45} {f['veces']:>4}")
            return 0

    print("\n=== Rúbrica: ¿algún módulo prepara cada criterio de ingeniería? ===")
    rub = {}
    for k, (nombre, peso, patron, esperados) in RUBRICA.items():
        halla = []
        for n in range(1, 14):
            veces = len(re.findall(patron, texto_modulo(n), re.I))
            if veces >= 5:          # umbral: mencion incidental no es preparar
                halla.append((n, veces))
        rub[str(k)] = {"criterio": nombre, "peso": peso,
                       "esperados": esperados,
                       "modulos_que_lo_tratan": [n for n, _ in halla]}
        marca = "✓" if halla else "✗ NINGUNO"
        print(f"  c{k:<3} {peso:>2}%  {nombre[:46]:<48} {marca} "
              f"{[n for n,_ in halla]}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "cobertura.json").write_text(
        json.dumps({"temas": resultados, "rubrica": rub},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {SALIDA}/cobertura.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
