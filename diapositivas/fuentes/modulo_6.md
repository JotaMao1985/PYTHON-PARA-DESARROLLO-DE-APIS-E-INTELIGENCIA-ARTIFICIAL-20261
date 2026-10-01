---
modulo: ../../6_Python_para_APIS_IA_Fast_API.html
salida: ../6_Python_para_APIS_IA_Fast_API.html
agenda: si
---

<!--
  Semana 6 · FastAPI: de script a servicio.
  Cubre los 60 min de exposición del reparto del material («Antes de empezar»);
  la práctica guiada de 180 min se presenta al final, no se desarrolla.
-->

# Del script al servicio {seccion=fundamentals}

> Su modelo ya funciona en su computador. La pregunta de hoy es cómo lo usa alguien que no tiene su computador.

???
Arrancar con la pregunta, no con la definición. Dejar que respondan: «le mando el notebook», «le mando el .pkl»… y preguntar qué pasa cuando el modelo cambie.

## Una API es el camarero entre el cliente y la cocina

::: tarjetas
### Cliente
Pide «quiero una predicción». **No entra a la cocina**: no ve su código ni sus datos.
### API
Toma el pedido, lo lleva y vuelve con el resultado. Es la **única puerta** entre el mundo y su lógica.
### Servidor
Donde ocurre el trabajo de verdad: el modelo, la consulta a la base de datos, el cálculo.
:::

::: revelar
::: idea
WSGI: el camarero espera en la cocina hasta que el plato esté listo. ASGI: entrega la orden y atiende otra mesa mientras tanto.
:::
:::

???
La analogía del material (Fundamentos, caja «Concepto básico»). La segunda parte —el camarero que espera o no— se revela al final: es el puente con la sección de arquitectura, no hace falta desarrollarla aquí.

## REST: la URL nombra el recurso, el verbo dice qué hacer {columnas=5:4}

- **URL = dirección del recurso**: `/predicciones`, `/usuarios/42`
- **Verbo HTTP = acción**: GET consulta, POST crea, PUT actualiza, DELETE borra
- **JSON = el idioma**: legible para personas y para máquinas

REST es un **estilo**, no una norma: no hay documento que se cumpla o se incumpla, como sí lo hay con HTTP.

|||

```text Una petición y su respuesta
GET /usuarios/42 HTTP/1.1
Host: api.ejemplo.co

HTTP/1.1 200 OK
Content-Type: application/json

{"id": 42, "nombre": "Ana"}
```

???
Recordar la semana 2 (HTTP): esto no es nuevo, es la misma petición vista desde el lado del servidor.

## El decorador define el soporte de la aplicación {.idea}

Cada URL válida es un evento del espacio muestral. Pedir una que no está es un evento de probabilidad cero: **404 Not Found**.

???
Es la analogía estadística del material («el espacio de muestreo de las URL»). Funciona muy bien con estadísticos: dejarla en el aire unos segundos.

## Cinco líneas y ya hay un servicio {columnas=3:2}

```python main.py {resaltar=5-7}
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}
```

|||

```shell Terminal
pip install fastapi uvicorn
uvicorn main:app --reload
```

- `http://127.0.0.1:8000` → el JSON
- `http://127.0.0.1:8000/docs` → la documentación, **que nadie escribió**

???
Hacerlo en vivo. Abrir /docs y detenerse: esa página es el tema de la semana. El `módulo:variable` del comando ya se vio en la semana 5; no repetirlo.

# Quién atiende la petición {seccion=architecture}

> Entre el navegador y su función hay tres programas. Saber cuál es cuál es lo que le permite diagnosticar un fallo en producción.

## Tres piezas entre el navegador y su código

::: flujo
1. **Cliente** — navegador, app móvil o `curl`
2. **Servidor web** — Nginx: SSL, caché, balanceo
3. **Servidor de aplicación** — Uvicorn (ASGI) o Gunicorn (WSGI)
4. **Su código** — FastAPI o Flask, el modelo, NumPy
:::

En desarrollo, **Uvicorn hace de servidor web y de aplicación a la vez**. En producción se pone Nginx delante.

???
El diagrama ASCII del material («Flujo completo de una petición web») cuenta lo mismo con más detalle; aquí basta la cadena.

## WSGI es un contrato de 2003, y es síncrono

```python Aplicación WSGI pura {resaltar=1,13-14}
def mi_app_wsgi(environ, start_response):
    ruta = environ['PATH_INFO']
    metodo = environ['REQUEST_METHOD']

    if ruta == '/' and metodo == 'GET':
        status = '200 OK'
        body = b'{"mensaje": "Hola desde WSGI puro"}'
    else:
        status = '404 Not Found'
        body = b'{"error": "Ruta no encontrada"}'

    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    return [body]
```

Nadie escribe esto a mano: Flask y Django lo hacen por usted. Pero **la función devuelve la respuesta completa antes de soltar el hilo**.

???
PEP 333 (2003), PEP 3333 (2010). Lo único que importa retener es la última frase: de ahí sale toda la diferencia con ASGI.

## WSGI retiene el hilo; ASGI lo suelta mientras espera

::: tarjetas
### WSGI · Flask
- Cada petición ocupa su hilo **de principio a fin**, también mientras espera
- Más usuarios a la vez → más *workers* o más hilos
- Como una sesión de R en consola
### ASGI · FastAPI
- Durante la espera de I/O **el hilo queda libre** y atiende a otro
- El mismo *worker* sirve a varios usuarios que esperan
- Como Shiny con *promises*
:::

::: warn Comparación justa
Los dos con **un worker y un hilo**. Con cuatro workers, WSGI atiende cuatro a la vez; lo que nunca hace es aprovechar la espera.
:::

???
El material tiene el diagrama interactivo «Comparación de flujos de ejecución» (sección 3). Si hay tiempo, abrirlo desde el enlace del divisor.

## ¿Cuánto espera el usuario B? {.pregunta tipo=E2}

Un servidor con **un worker y un hilo**. El usuario A pide un endpoint que consulta una base de datos durante 10 s. El usuario B llega en el segundo 5 y pide algo instantáneo.

1. Con **Flask (WSGI)**: ¿cuándo empieza a atenderse B?
2. Con **FastAPI (ASGI)** y la consulta con `await`: ¿y ahora?

::: respuesta
WSGI: en el segundo **10**, cuando A suelta el hilo. ASGI: en el segundo **5**, en el hueco de la espera de A.
:::

???
Pedir que lo escriban antes de revelar. El error típico es decir «ASGI usa varios hilos»: no, es el mismo hilo, que no se queda mirando.

# Flask frente a FastAPI {seccion=flask-debate}

## La misma tarea, dos filosofías {columnas=1:1}

```python Flask — a mano
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    # Sin validación automática
    # Sin documentación generada
    return jsonify({"resultado": 42})
```

|||

```python FastAPI — declarativo {resaltar=6-7,9-10}
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    x: float  # ← validación

@app.post("/predict")  # ← /docs gratis
def predict(data: Input):
    return {"resultado": 42}
```

???
La diferencia está en las líneas resaltadas: el tipo `x: float` hace dos trabajos a la vez, validar y documentar.

## Cuándo elegir cada uno

| | Flask | Django | FastAPI |
|---|---|---|---|
| Protocolo | WSGI | WSGI / ASGI | ASGI |
| Validación | Con extensión | Forms / Serializers | **Automática (Pydantic)** |
| Documentación de la API | Con extensión | Django REST Framework | **Swagger UI, sin configurar** |
| Ideal para | Prototipos, apps simples | Aplicaciones web completas | **APIs de ML e IA** |

La tabla **no da peticiones por segundo** a propósito: sin declarar endpoint, hardware, *workers* y tipo de carga, esa cifra no significa nada.

???
Insistir en la última línea: es una lección de estadística, no de frameworks. Los TechEmpower Benchmarks publican método y máquina.

# Routing y CRUD {seccion=crud}

> Una ruta conecta una URL con una función. El tipo que anota en la función decide qué entra.

## Anatomía de una ruta

```text
@app.get("/usuarios/{user_id}")
 ─┬──  ─┬─  ──────┬──────────
  │     │         └─ RUTA: la URL que activa la función
  │     └─ VERBO: GET, POST, PUT, DELETE
  └─ DECORADOR: registra la función en el mapa de rutas
```

::: tarjetas {columnas=3}
### Estática
`/about` — siempre el mismo recurso
### De ruta
`/usuario/{user_id}` — FastAPI extrae y **convierte** el valor
### De consulta
`/buscar?campo=edad&limite=5` — lo que va después del `?`
:::

???
Los tres tipos de la sección 5. Las de consulta sin valor por defecto son obligatorias; con valor por defecto, opcionales.

## ¿Qué responde FastAPI? {.pregunta tipo=E2}

```python
@app.get("/analisis/{id}")
def ver(id: int):
    ...
```

Un cliente pide **`/analisis/ultimo`**.

::: respuesta 422 Unprocessable Entity
La anotación `id: int` es el contrato: FastAPI intenta convertir «ultimo» **antes de ejecutar una sola línea** de la función, falla y responde 422 diciendo qué campo. El 404 es tentador, pero para llegar a él la función tendría que ejecutarse.
:::

???
Pregunta del cuestionario del material (sección 7). Muy buena para discutir: casi todos dicen 404.

## Cada verbo tiene su código de estado

| Verbo | Análogo en R | En la API | Éxito |
|---|---|---|---|
| GET | `summary(df)` | Consultar | **200 OK** |
| POST | `predict()` | Crear | **201 Created** |
| PUT | `df[i] <- val` | Actualizar | **200 OK** |
| DELETE | `rm(obj)` | Borrar | **204 No Content** |

Y dos de error que conviene distinguir: **404**, el recurso no existe; **409**, la petición es válida pero **choca con lo que ya hay**.

## El 201 y el 409 hay que declararlos {.codigo-grande}

```python API de Registro de Experimentos {resaltar=1,4}
@app.post("/experimentos", status_code=201, response_model=Experimento)
def crear_experimento(exp: Experimento):
    if exp.id in db:
        raise HTTPException(status_code=409, detail="Ese id ya está registrado")
    db[exp.id] = exp
    return exp
```

Sin `status_code=201`, FastAPI responde **200** y el cliente no distingue «lo creé» de «ahí lo tienes».

???
El CRUD completo está en el material (sección 5): mostrarlo en /docs en vez de recorrerlo en diapositivas.

# Concurrencia {seccion=concurrency}

## `async def` no acelera nada por sí solo {.idea}

Solo aporta si dentro hay un `await` sobre una librería asíncrona. Con una bloqueante dentro, **todas** las peticiones esperan.

???
Es la «Regla de Oro» de la sección 6. Leerla despacio.

## Los cuatro casos de `async def`

```python {resaltar=4-7}
@app.post("/stats")                  # 1 · CPU: def, va a un hilo aparte
def calcular(datos: DatosInput): ...

@app.get("/clima-mal")               # 2 · EL ERROR
async def clima_mal():
    r = requests.get(URL)            #   bloquea el bucle de eventos
    return r.json()                  #   y con él, a TODOS

@app.get("/clima-bien")              # 3 · async + await de verdad
async def clima_bien():
    async with httpx.AsyncClient() as c:
        r = await c.get(URL)
    return r.json()
```

**La prueba:** si la llamada no lleva `await` delante, es bloqueante, y el endpoint va con `def`.

???
El cuarto caso del material —`def` con `requests`— es el aceptable: FastAPI lo manda al threadpool. Mencionarlo de palabra.

## ¿`def` o `async def`? {.pregunta tipo=E8}

::: tarjetas {columnas=3}
### A
Calcula la media y la varianza de 10 000 valores con NumPy.
### B
Consulta una base de datos con `asyncpg`.
### C
Llama a una API externa con `requests`.
:::

::: respuesta
**A**: `def` (CPU). **B**: `async def`, con `await`. **C**: `def`: `requests` no sabe esperar.
:::

## Responder primero, trabajar después

```python {resaltar=5}
from fastapi import BackgroundTasks

@app.post("/trigger-retrain", status_code=202)
def iniciar(background_tasks: BackgroundTasks, n_iter: int = 1000):
    background_tasks.add_task(entrenar_modelo_pesado, n_iter)
    return {"mensaje": "Entrenamiento iniciado en segundo plano."}
```

::: warn El límite
La tarea corre **en el mismo proceso** y `--reload` la mata al guardar. Un reentrenamiento de horas pide una cola externa: Celery, RQ o ARQ.
:::

# Cierre y práctica {seccion=evaluation}

## Lo que se llevan hoy {.cierre}

- El **tipo** anotado en la función valida la petición y escribe `/docs`
- ASGI no usa más hilos: **no se queda mirando** mientras espera
- `async def` solo con `await` dentro; si no, `def`
- 201 al crear, 204 al borrar, 404 si no existe, 409 si choca

???
Remitir al cuestionario de 8 preguntas de la sección 7 del material, para hacerlo antes de la próxima clase.

## Práctica guiada: su propia API de análisis {columnas=3:2}

::: flujo
1. **Dominio** — salud, deportes, clima, finanzas…
2. **Modelos** — `DatasetInput` y `StatsResult` con Pydantic
3. **Endpoints** — GET, POST y DELETE con sus códigos
4. **Evidencia** — capturas de la terminal y de `/docs`
:::

|||

::: info Política de IA
Puede usarla para sintaxis y depuración. El dominio es **suyo**, y el código idéntico al ejemplo o al de un compañero se penaliza.
:::

???
Los 180 min de práctica guiada. El enunciado completo, fase por fase, está en la sección 8 del material: proyectarlo desde ahí.
