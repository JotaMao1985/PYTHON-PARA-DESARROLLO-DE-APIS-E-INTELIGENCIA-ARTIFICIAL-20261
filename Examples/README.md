# Examples — demos pedagógicas del curso

Esta carpeta contiene scripts cortos que se usan como **demos en vivo** durante las clases. No son parte del [proyecto integrador](https://github.com/JotaMao1985/proyecto-integrador-riesgo-2026I) (que vive como submódulo en `Proyecto_I/`); son ejemplos didácticos que ilustran conceptos puntuales de cada módulo.

## Inventario

| Archivo | Líneas | Módulo | Qué demuestra |
| --- | --- | --- | --- |
| [`hellow_FAPI.py`](hellow_FAPI.py) | 5 | M6 — FastAPI | Endpoint mínimo `@app.get("/")` |
| [`Bernoulli_1.py`](Bernoulli_1.py) | 19 | M5 / M6 | Endpoint que ejecuta un experimento Bernoulli con NumPy |
| [`Experimentos_essay.py`](Experimentos_essay.py) | 44 | M6 — FastAPI | API de registro de experimentos (POST + GET con Pydantic) |
| [`A_Full_CRUD.py`](A_Full_CRUD.py) | 38 | M6 — FastAPI | CRUD completo (Movie Review API): POST / GET / PUT / DELETE con Pydantic + "DB" en dict |
| [`Constructor_Clases_IA.py`](Constructor_Clases_IA.py) | 79 | M3 — POO | Clase `GeneradorClases` que usa Gemini 2.5 Flash para generar código Python; muestra POO real, `system_instruction`, reintentos con backoff |
| [`convert_math.py`](convert_math.py) | 121 | (utilidad docente) | Limpieza de LaTeX en HTML — ⚠️ contiene ruta absoluta dura, no portable |
| [`Dockerfile`](Dockerfile) | 16 | M11 — Docker | Imagen Python 3.11-slim — ⚠️ espera `requirements.txt` en el build context |
| [`docker-compose.yml`](docker-compose.yml) | 12 | M11 — Docker | Servicio que monta `./app` y `./data` y se conecta a Ollama — ⚠️ pensado para ejecutarse desde la raíz del repo, no desde aquí |

## Advertencias importantes

Algunos archivos **no son portables tal cual** y requieren ajustes antes de ejecutarse:

- `convert_math.py` tiene una ruta absoluta a la máquina del docente. Cámbiala antes de usar.
- `Dockerfile` hace `COPY requirements.txt .` pero esta carpeta no tiene `requirements.txt`. Para construir desde aquí necesitas crear uno (sugerencia: `fastapi`, `uvicorn`, `pydantic`, `numpy`, `google-genai`, `python-dotenv`).
- `docker-compose.yml` monta `./app:/app` y `./data:/data`. Estas carpetas están en la **raíz del repo del curso**, no en `Examples/`. Si quieres usarlo, ejecútalo desde la raíz: `docker compose -f Examples/docker-compose.yml up`, o copia el compose a la raíz, o ajusta las rutas a `../app` y `../data`.

## Cómo correr una demo rápida

Para los scripts FastAPI (asumiendo `pip install fastapi uvicorn pydantic numpy`):

```bash
uvicorn Examples.hellow_FAPI:app --reload
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs  (Swagger UI auto-generado)
```

Reemplaza `hellow_FAPI` por el script que quieras servir (`A_Full_CRUD`, `Experimentos_essay`, `Bernoulli_1`).

## Para Constructor_Clases_IA.py

Necesita `GEMINI_API_KEY` exportada:

```bash
export GEMINI_API_KEY='tu_clave'
pip install google-genai python-dotenv
python Examples/Constructor_Clases_IA.py
```

> El SDK es `google-genai` (`from google import genai`). El antiguo
> `google-generativeai` quedó obsoleto el 30 de noviembre de 2025 y Google ya no
> lo mantiene; si un tutorial usa `genai.configure(...)` o `genai.GenerativeModel(...)`,
> está escrito para la librería vieja.

## ¿Qué cambió en mayo 2026?

Estos archivos vivían antes en `Proyecto_I/`. Se movieron a `Examples/` cuando `Proyecto_I/` pasó a ser submódulo del [proyecto integrador](https://github.com/JotaMao1985/proyecto-integrador-riesgo-2026I) (solución de referencia, no playground de demos).
