---
modulo: ../../11_Python_para_APIS_IA_Contenedores_y_Docker.html
agenda: si
---

<!--
  Semana 11 · Contenedores y Docker.
  Exposición (60 min del reparto): del entorno virtual al contenedor 10, contenedores
  frente a VM 8, Dockerfile e imagen base 14, multietapa 9 y buenas prácticas 16.
  El reparto deja el caché de capas como consulta; aquí va en buenas prácticas, a pedido.
  El ejemplo guiado (sección 10 del material) abre la práctica guiada de 180 min:
  se hace en vivo, paso a paso.
  Código verificado: pytest con Python 3.11 (taller_corte2/build/venv) y la imagen del
  ejemplo construida y ejecutada con Docker 29 (OrbStack, arm64), con las versiones
  fijadas del material (FastAPI 0.111.0, Uvicorn 0.30.1, Pydantic 2.7.4).
-->

# Del entorno virtual al contenedor {seccion=repaso}

> ¿Cómo se entrega la API a otra máquina sin que la regresión devuelva otros números por culpa de otra versión de NumPy?

???
Unos 10 minutos. Es la pregunta con que abre el capítulo (sección 2). Aquí se cierra el adelanto de la semana 1, que solo pedía saber cuándo elegir un contenedor; la imagen que salga de hoy es la que se despliega en la semana 12.

## `venv` y `requirements.txt` fijan los paquetes, no la máquina

| Pregunta | ¿La resuelve `venv` + `requirements.txt`? |
|---|---|
| ¿Qué versión de Python corre? | **No.** `venv` hereda la del sistema |
| ¿Qué bibliotecas del sistema hay (`libopenblas`, `tzdata`)? | **No.** Dependen de cada computador |
| ¿En qué orden arrancan Uvicorn y la base de datos? | **No.** Es cosa del despliegue |

El contenedor lleva el aislamiento al sistema operativo completo.

???
Recordar la semana 10: fijar versiones, semillas y configuración resuelve la reproducibilidad dentro de una misma máquina. La tabla es la de la sección 3; lo que queda abierto es justo lo que no vive en Python.

## El `Dockerfile` es a la imagen lo que `requirements.txt` al entorno virtual

| Entorno virtual | Docker |
|---|---|
| `requirements.txt`: declara las dependencias | `Dockerfile`: declara la imagen |
| `python -m venv .venv`: crea el entorno | `docker build`: crea la imagen |
| `source .venv/bin/activate`: lo activa | `docker run`: lanza un contenedor |
| La carpeta `.venv/` | La imagen: inmutable, identificada por un *hash* |
| Una terminal con el entorno activo | Un contenedor en ejecución |

???
El material insiste en que el paralelismo es estricto y conviene tenerlo presente toda la unidad (sección 3, «Analogía conceptual»): si `requirements.txt` describe cómo reconstruir un entorno, el `Dockerfile` describe cómo reconstruir una máquina, capa por capa.

## Una imagen es la clase; un contenedor, su instancia {.idea}

La imagen es una plantilla que no cambia. Cada `docker run` crea una instancia nueva, como un objeto de una clase o una realización de un mismo modelo.

???
Es la «Idea central» de la sección 3, que también la compara con un molde estadístico y una realización muestral. Preguntar: si dos personas lanzan la misma imagen, ¿comparten el contenedor? No: cada una tiene su instancia.

## Mismo `requirements.txt`, distinto Python: ¿mismo entorno? {.pregunta tipo=E2}

Usted trabaja con Python 3.11.9; su compañero, con 3.12. Los dos corren `pip install -r requirements.txt`, con todas las versiones fijadas con `==`.

¿Obtienen el mismo entorno?

::: respuesta No
`venv` hereda el intérprete de cada máquina, y `requirements.txt` no dice nada de Python ni de las bibliotecas del sistema. La imagen sí: los dos ejecutarían `python:3.11.9-slim-bookworm`.
:::

???
Es la primera fila de la tabla de la sección 3, puesta como caso. Si alguien responde «sí, porque las versiones están fijadas»: los paquetes coinciden, el intérprete no, y pip descarga *wheels* distintas para 3.12.

## Lo que se prueba es, byte a byte, lo que se despliega

::: flujo
1. **git push** — el código y su `Dockerfile`
2. **Integración continua** — `docker build` y pytest *dentro* del contenedor
3. **Registro** — la imagen, etiquetada con el *hash* del commit
4. **Producción** — descarga esa misma imagen y la ejecuta
:::

La misma imagen en el portátil, en las pruebas y en el servidor.

???
El flujo de la sección 5 (4.2); la integración continua llega en semanas posteriores, hoy basta con la idea de paridad. Lo que Docker no resuelve (misma sección, 4.3): no corrige un modelo mal especificado, no reemplaza a pytest ni al README.

# Contenedores frente a máquinas virtuales {seccion=vms}

> Las dos aíslan aplicaciones en un mismo computador. La diferencia está en dónde se traza la línea.

???
Unos 8 minutos.

## La VM carga un kernel por aplicación; el contenedor comparte el del anfitrión

::: html
<div class="grid grid-cols-2 gap-10 max-w-5xl mx-auto mb-6">
  <div class="rounded-xl overflow-hidden border border-slate-200 divide-y divide-slate-200 text-center text-lg font-medium [&>div]:px-4">
    <div class="bg-navy text-white font-semibold py-2">Máquinas virtuales</div>
    <div class="bg-slate-800 text-white py-2">Hardware físico</div>
    <div class="bg-slate-600 text-white py-2">Sistema operativo anfitrión</div>
    <div class="bg-secondary text-white py-2">Hipervisor (VMware, KVM, Hyper-V)</div>
    <div class="bg-gold text-slate-900 py-2">SO huésped 1 (kernel completo)</div>
    <div class="bg-white text-slate-800 py-2">App 1 + dependencias</div>
    <div class="bg-gold text-slate-900 py-2">SO huésped 2 (kernel completo)</div>
    <div class="bg-white text-slate-800 py-2">App 2 + dependencias</div>
  </div>
  <div class="rounded-xl overflow-hidden border border-slate-200 divide-y divide-slate-200 text-center text-lg font-medium [&>div]:px-4">
    <div class="bg-navy text-white font-semibold py-2">Contenedores</div>
    <div class="bg-slate-800 text-white py-2">Hardware físico</div>
    <div class="bg-slate-600 text-white py-2">Sistema operativo anfitrión (kernel único)</div>
    <div class="bg-primary text-white py-2">Motor de contenedores (Docker Engine)</div>
    <div class="bg-teal text-white py-2">Contenedor 1 (binarios + libs)</div>
    <div class="bg-white text-slate-800 py-2">App 1</div>
    <div class="bg-teal text-white py-2">Contenedor 2 (binarios + libs)</div>
    <div class="bg-white text-slate-800 py-2">App 2</div>
  </div>
</div>
:::

La VM virtualiza el hardware; el contenedor, solo el espacio de usuario.

???
Es la figura 3.1 del material, con sus colores. La contracara está en la tabla 3.3: el aislamiento del contenedor es fuerte pero menor, porque una vulnerabilidad del kernel compartido afecta a todos los contenedores.

## Arranque, disco y memoria: la distancia es de órdenes de magnitud

![Valores típicos, en escala logarítmica](recursos/m11/chart-vms.json){alto=430}

???
Figura 3.2: unas 50 veces más rápido en arranque, 20 veces menos disco y 16 menos memoria para servir una API equivalente. Son valores típicos, no medidos. El eje es logarítmico: cada marca es un factor de 10.

## Los namespaces aíslan lo que el proceso ve; los cgroups limitan lo que consume

::: tarjetas {columnas=2}
### Namespaces: lo que ve
Cada contenedor tiene su propia vista de procesos (PID), red (NET), montajes (MNT) y usuarios (USER). No ve los procesos de otro.
### cgroups: lo que consume
Ponen techo a CPU, memoria, disco y red. Sin ellos, un contenedor podría agotar la memoria del servidor.
:::

::: info En macOS y Windows
Docker Desktop corre una pequeña VM Linux por debajo, y los contenedores viven dentro de ella.
:::

???
Sección 4, 3.2. Las dos primitivas son del kernel de Linux; por eso, fuera de Linux, hay una VM de por medio. El estudiante ve la misma interfaz, pero conviene que sepa que hay un nivel más.

## ¿Máquina virtual o contenedor? {.pregunta tipo=E8}

1. Correr Windows en el servidor Linux del laboratorio
2. Reproducir exactamente el experimento de un compañero
3. Aislar en la misma nube los sistemas de dos organizaciones

::: respuesta VM · contenedor · VM
Otro sistema operativo exige otro kernel (1); reproducir un entorno es justo lo que hace una imagen (2); separar organizaciones pide el aislamiento fuerte de un kernel propio (3).
:::

???
Los tres casos son los de la sección 4 (3.4). Cerrar con la caja «Convivencia, no exclusión»: en la nube, las VM hospedan decenas de contenedores; las dos tecnologías viven en capas distintas.

# El Dockerfile y su imagen base {seccion=dockerfile}

> Un `Dockerfile` es un manual de cocina: cada paso recibe el resultado del anterior y le agrega algo encima.

???
Unos 14 minutos: el centro de la exposición. Incluye la sección 7 del material, la imagen base.

## Siete instrucciones describen la máquina entera {columnas=2:1}

```dockerfile Dockerfile
FROM python:3.11.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

|||

- `FROM`: de qué imagen se parte
- `WORKDIR`, `COPY`, `RUN`: qué se le agrega
- `CMD`: qué se ejecuta al lanzar el contenedor

???
La versión didáctica mínima de la sección 6 (5.1), sin el comentario inicial. El archivo se llama `Dockerfile`, sin extensión. `FROM` tiene que ser la primera instrucción no comentada.

## `ENV` persiste, `ARG` no sale de la construcción y `EXPOSE` no publica nada

| Instrucción | Qué hace |
|---|---|
| `ENV PYTHONUNBUFFERED=1` | Variable que persiste en la imagen **y** en el contenedor |
| `ARG APP_VERSION=0.1.0` | Variable que existe **solo** mientras se construye |
| `EXPOSE 8000` | **Documenta** el puerto; publicarlo es `docker run -p` |
| `USER appuser` | Cambia el usuario de lo que sigue y del proceso final |
| `ENTRYPOINT ["uvicorn"]` | Fija el ejecutable; `CMD` le pasa los argumentos |

???
Son las filas de la tabla 5.2 que más se confunden; `FROM`, `WORKDIR`, `COPY`, `RUN` y `CMD` ya salieron en la diapositiva anterior. La de `EXPOSE` es la que se pregunta enseguida.

## `EXPOSE 8000` y sin `-p`: ¿responde la API? {.pregunta tipo=E2}

La imagen del ejemplo declara `EXPOSE 8000`. Usted la lanza así:

```shell Terminal
docker run --rm regresion-api:0.1.0
```

Desde otra terminal pide `curl http://localhost:8000/health`. ¿Qué obtiene?

::: respuesta Nada: no hay conexión
`EXPOSE` solo **documenta** el puerto. Publicarlo en el anfitrión es `docker run -p 8000:8000`, como hace el ejemplo del material.
:::

???
Comprobado con la imagen del ejemplo: sin `-p`, curl no conecta (código 7); con `-p 8000:8000`, responde `{"status":"ok"}`. Vale la pena preguntarlo antes de la práctica guiada, que lanza el contenedor con `-p`.

## Cada instrucción agrega una capa inmutable encima de la anterior

::: flujo
1. **FROM** — la imagen base
2. **WORKDIR** — `/app`
3. **COPY** — `requirements.txt`
4. **RUN** — `pip install`
5. **COPY** — `app/`
:::

Docker calcula un *hash* de la entrada de cada capa. Si coincide con uno guardado, **reutiliza** la capa en vez de reconstruirla.

???
La pila de capas de la sección 6 (5.3); `EXPOSE` y `CMD` agregan solo metadatos. La consecuencia, el orden de las instrucciones, es la primera buena práctica: se ve más adelante, con tiempos medidos.

## `python:3.11.9-slim-bookworm` se lee en cuatro partes

| Parte | Qué fija |
|---|---|
| `python` | El repositorio oficial, con CPython instalado |
| `3.11.9` | La versión exacta, mayor, menor **y parche**: la del curso |
| `slim` | Una variante recortada: Python y `pip`, sin extras de Debian |
| `bookworm` | Debian 12, *stable* hasta aproximadamente 2028 |

???
Tabla 6.1 (sección 7). `slim` deja fuera compiladores (`gcc`, `build-essential`), cabeceras y herramientas como `git` o `curl`. Si una dependencia exige compilar, eso se resuelve con multi-stage, que viene enseguida.

## `slim` pesa un séptimo de la imagen completa y conserva las *wheels* científicas

![](recursos/m11/chart-imagen-base.json){alto=370}

`alpine` es aún más pequeña, pero usa `musl`: NumPy o scikit-learn tienen que recompilarse.

???
Tabla 6.2 y figura 6.1. La recomendación del material: para una API que dependa del ecosistema científico (NumPy, SciPy, pandas, scikit-learn, statsmodels), `slim-bookworm` es el equilibrio práctico.

# Construcción multietapa {seccion=multistage}

> Los compiladores que hacen falta para construir no tienen nada que hacer en producción.

???
Unos 9 minutos.

## Construir necesita compiladores; ejecutar, no

::: tarjetas {columnas=2}
### builder: construir
`build-essential`, cabeceras, la caché de `apt` y la de `pip`. Se usan para instalar y se descartan.
### runtime: ejecutar
El intérprete, el entorno virtual con los paquetes y el código. Es lo único que se entrega.
:::

Menos peso y menos **superficie de ataque**: sin compiladores, quien logre ejecutar código tiene menos herramientas.

???
Sección 9, 8.2: cinco ventajas; aquí van las dos que más pesan. Las otras tres: una etapa builder puede alimentar varias imágenes (API, *worker*, job batch), las dependencias de construcción y de ejecución quedan separadas, y BuildKit construye etapas independientes en paralelo.

## Cada `FROM` abre una etapa, y solo la última se entrega

```dockerfile Dockerfile {resaltar=2,6-7}
# Etapa 1: builder — todo lo que sólo hace falta durante la construcción
FROM python:3.11.9-slim-bookworm AS builder
# ... instalar compiladores, descargar dependencias, compilar wheels ...

# Etapa 2: runtime — la imagen final que se entrega a producción
FROM python:3.11.9-slim-bookworm AS runtime
COPY --from=builder /opt/venv /opt/venv
# ... copiar el código y arrancar la aplicación ...
```

`COPY --from=builder` trae **solo** lo que se nombra: aquí, el entorno virtual.

???
El esquema general de la sección 9 (8.1). Para depurar, `docker build --target builder` construye hasta esa etapa y permite abrir una shell dentro sin tocar la imagen de producción (8.5).

## Multi-stage lleva la imagen de ≈ 1 400 MB a ≈ 230 MB

![](recursos/m11/chart-multistage.json){alto=420}

???
Tabla 8.4 y figura 8.1: un proyecto con fastapi, uvicorn, pydantic, numpy, scipy y scikit-learn; los tamaños son aproximados. Cada decisión suma: `slim` recorta el sistema base, quitar compiladores baja otro tercio y separar etapas deja la imagen más pequeña.

## ¿Qué se queda en el builder y no llega a la imagen final? {.pregunta tipo=E2}

En el ejemplo del curso, el builder instala `build-essential` con `apt-get` y crea el entorno virtual en `/opt/venv`; el runtime copia ese entorno y el código.

Nombre dos cosas que la imagen final **no** contiene.

::: respuesta Los compiladores y la caché de apt
Ni `build-essential` ni `/var/lib/apt/lists/`: la etapa runtime solo trae `/opt/venv` y `app/`. Menos tamaño y menos superficie de ataque.
:::

???
Es el ejercicio 10.5 de la autoevaluación (sección 11). Comprobado con `docker history` sobre la imagen del ejemplo: encima de la base solo quedan el usuario, el entorno virtual (85 MB) y el código.

# Buenas prácticas {seccion=cierre}

> Una imagen que construye y responde todavía no es una imagen que se pueda entregar.

???
Unos 16 minutos. Reúne las prácticas que el material reparte entre las secciones 6 a 9 con la «Lista mínima de seguridad» de la sección 12. Los tiempos que se citan son de la imagen del ejemplo, construida con OrbStack en un Mac.

## Ordene las instrucciones por estabilidad decreciente {.idea etiqueta="Regla de oro"}

Lo que cambia rara vez va arriba; lo que cambia varias veces al día, abajo. Así, un cambio en el código no reinstala las dependencias.

???
La regla de oro de la sección 6 (5.4): las dependencias cambian cada semanas o meses; el código, varias veces al día.

## Dependencias primero, código después: reconstruir pasa de minutos a un segundo {columnas=1:1}

```dockerfile Anti-patrón
COPY . .
RUN pip install -r requirements.txt
```

Cualquier cambio en `app/` invalida `COPY . .` y repite la instalación.

|||

```dockerfile Patrón
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
```

Medido con el ejemplo: `pip install` tardó **2 min 32 s**; tras cambiar `main.py`, la reconstrucción tardó **1 s**.

???
El código de la sección 6 (5.4). En la segunda construcción, todas las capas hasta `pip install` salieron `CACHED`; solo se rehízo la copia de `app/`. Con el anti-patrón, cada cambio de código paga de nuevo los dos minutos y medio.

## Fije la versión exacta y, si puede, el *digest*

```dockerfile {resaltar=5}
# No recomendado: la versión flota.
FROM python:3.11-slim

# Recomendado: versión exacta.
FROM python:3.11.9-slim-bookworm

# Reproducibilidad máxima: hash criptográfico de la imagen.
FROM python:3.11.9-slim-bookworm@sha256:abc123...def
```

`3.11` apunta al último parche: reconstruir meses después puede traer `3.11.12`.

???
Sección 7 (6.4). El *hash* de la última línea es ilustrativo; el real se obtiene con `docker inspect … --format='{{index .RepoDigests 0}}'`. El que resolvió hoy la construcción del ejemplo fue `sha256:8fb09919…c317`. Lo mismo vale para `requirements.txt`: `==`, no `>=`.

## Lo que no se ignora viaja al *daemon*, y puede quedar en una capa

```shell Terminal
docker build -t regresion-api:0.1.0 .
#> => transferring context: 482.31kB
```

`docker build .` empaqueta la carpeta, el **contexto**, y la envía al *daemon*. `.dockerignore` decide qué no viaja.

::: warn Un .env copiado no se borra
Queda en una capa permanente. Un `RUN rm` posterior no lo quita: la capa anterior lo conserva.
:::

???
Sección 8 (7.1 a 7.3): velocidad, seguridad y caché. Con el `.dockerignore` del ejemplo, el contexto medido fue de 9.3 kB. Los secretos se inyectan como variables de entorno al ejecutar, con `python-dotenv`; nunca se copian.

## Forma *exec* en `CMD`: el proceso recibe `SIGTERM` y cierra limpio {columnas=1:1 .codigo-grande}

```dockerfile Forma exec
CMD ["uvicorn", "app.main:app"]
```

`docker stop` tardó **0.3 s**: la señal llega a Uvicorn.

|||

```dockerfile Forma shell
CMD uvicorn app.main:app
```

`docker stop` tardó **10.2 s**: la señal llega a `/bin/sh`, no a Uvicorn.

???
Sección 6 (5.5). Medido con la imagen del ejemplo y su `CMD` completo: con la forma exec, el proceso 1 del contenedor es Uvicorn; con la forma shell, es `sh -c`, y Docker espera los 10 s de gracia antes de matarlo. Una API que no atiende `SIGTERM` deja peticiones a medias y conexiones de base de datos abiertas.

## El proceso corre como `appuser`: quien lo comprometa no hereda `root`

```dockerfile {resaltar=1-2,5}
RUN groupadd --system --gid 1001 appgroup \
 && useradd  --system --uid 1001 --gid appgroup --create-home appuser
WORKDIR /app
COPY --chown=appuser:appgroup app/ ./app/
USER appuser
```

`USER` va antes del `CMD` final; `--chown` le da el código a `appuser`.

???
Ejercicio 10.6: aunque las pruebas pasen igual con `root`, un atacante que ejecute código hereda los permisos del proceso. Al construir, `useradd` avisa que el UID 1001 supera `SYS_UID_MAX` (999): es inofensivo, conviene anticiparlo en la práctica.

## Y antes de publicar: escanear, actualizar y restringir

::: tarjetas {columnas=3}
### Escanear
`docker scout`, `trivy` o `grype` revisan las capas y reportan CVE conocidas
### Actualizar
Reconstruir y republicar cuando salgan parches de Debian o de CPython
### Restringir
`docker run --read-only` o `--cap-drop=ALL`, si la aplicación lo permite
:::

Y una sola responsabilidad por imagen: sin `curl` ni `git` en producción.

???
Completan la «Lista mínima de seguridad» de la sección 12 (11.2). Hoy no se practican; están para que el grupo sepa que existen.

## Este `Dockerfile` construye sin errores. ¿Qué buenas prácticas incumple? {.pregunta tipo=E3}

```dockerfile
FROM python:3.11.9-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app"]
```

::: respuesta Dos, por lo menos
`COPY . .` antes de `pip install`: cada cambio en `app/` reinstala todo. Y no hay `USER`: el proceso corre como `root`. Sin `.dockerignore`, además, `COPY . .` se lleva el `.env`.
:::

???
Es el ejercicio 10.3 (sección 11), que pregunta solo por la caché; lo del usuario sale de la lista de seguridad. OJO: este `CMD` no pasa `--host 0.0.0.0`, así que Uvicorn escucha en 127.0.0.1 dentro del contenedor y, aun con `-p`, no responde desde fuera (comprobado: curl recibe una respuesta vacía). La solución comentada 10.3 del material conserva ese `CMD`: ver la nota de entrega.

# Ejemplo guiado paso a paso: regresion-api {seccion=integrador}

> Una API que sirve una regresión lineal, empaquetada en dos etapas, sin `root` y con sondeo de salud.

???
Este bloque abre la práctica guiada: se hace en vivo, con el grupo escribiendo a la par. Todo el código es el de la sección 10 del material y se comprobó: las 4 pruebas pasan, la imagen se construye y el contenedor responde lo mismo que la API fuera de él.

## El objetivo: `POST /predicciones` devuelve ŷ = 1.7 + 2.3x {columnas=1:1}

```text Estructura del proyecto
regresion-api/
├── app/
│   ├── __init__.py
│   ├── main.py            # Aplicación FastAPI
│   ├── modelo.py          # Carga y predicción
│   ├── schemas.py         # Modelos Pydantic
│   └── modelo.json        # Coeficientes
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
├── .dockerignore
└── Dockerfile
```

|||

- **Pasos 1–2** · El modelo y sus esquemas
- **Pasos 3–4** · La API y sus pruebas
- **Paso 5** · Dependencias y contexto
- **Pasos 6–7** · El `Dockerfile`, en dos etapas
- **Pasos 8–9** · Construir, ejecutar y verificar

???
La estructura de la sección 10 (9.1). El modelo se entrenó fuera de línea: en un proyecto real, el JSON lo produciría un script de entrenamiento versionado.

## Paso 1 · El modelo es un JSON y una clase inmutable {columnas=2:3}

```json app/modelo.json
{
    "version": "0.1.0",
    "intercepto": 1.7,
    "pendiente": 2.3,
    "x_min": -10.0,
    "x_max": 10.0
}
```

|||

```python app/modelo.py {resaltar=10,12}
@dataclass(frozen=True)
class ModeloRegresion:
    version: str
    intercepto: float
    pendiente: float
    x_min: float
    x_max: float

    def predecir(self, x: float) -> float:
        return self.intercepto + self.pendiente * x

@lru_cache(maxsize=1)
def cargar_modelo() -> ModeloRegresion:
    with RUTA_MODELO.open("r", encoding="utf-8") as f:
        datos = json.load(f)
    return ModeloRegresion(**datos)
```

???
Recortado: sin imports, docstrings ni la línea `RUTA_MODELO = Path(__file__).parent / "modelo.json"` (sección 10, 9.2 y 9.3). OJO: en el material, el bloque de `modelo.json` empieza con un comentario `# app/modelo.json — …`, y JSON no admite comentarios. Copiado tal cual, `json.load` falla y `/predicciones` responde 500. Aquí va sin esa línea; que el grupo la borre si copia del material.

## Paso 2 · Pydantic rechaza lo absurdo; el modelo avisa cuando extrapola

```python app/schemas.py {resaltar=7-8,13}
class EntradaPrediccion(BaseModel):
    x: float = Field(..., description="Variable explicativa")

    @field_validator("x")
    @classmethod
    def validar_rango(cls, valor: float) -> float:
        if not -1000.0 <= valor <= 1000.0:
            raise ValueError("x debe pertenecer a [-1000, 1000]")
        return valor

class SalidaPrediccion(BaseModel):
    y_hat: float = Field(..., description="Predicción del modelo")
    extrapolado: bool = Field(...)
    version_modelo: str = Field(...)
```

???
Sección 10 (9.4), sin las descripciones de los dos últimos campos. Son dos cotas con dos propósitos: `[-1000, 1000]` protege a la API de entradas absurdas y da 422; `[-10, 10]` es el dominio de entrenamiento, y salirse de él es válido pero se avisa. La primera es de FastAPI; la segunda, del estadístico.

## Paso 3 · El endpoint recibe el modelo por inyección de dependencias

```python app/main.py {resaltar=4,9}
@app.post("/predicciones", response_model=SalidaPrediccion)
def predecir(
    entrada: EntradaPrediccion,
    modelo: ModeloRegresion = Depends(cargar_modelo),
) -> SalidaPrediccion:
    y_hat = modelo.predecir(entrada.x)
    return SalidaPrediccion(
        y_hat=y_hat,
        extrapolado=not (modelo.x_min <= entrada.x <= modelo.x_max),
        version_modelo=modelo.version,
    )
```

Además, `GET /health` devuelve `{"status": "ok"}`: es lo que consultará el `HEALTHCHECK`.

???
Sección 10 (9.5), sin la creación de `app` ni el `/health`. `cargar_modelo` con `@lru_cache` hace de *provider*: lee el JSON la primera vez y después lo reutiliza.

## Paso 4 · Las pruebas pasan antes de pensar en Docker {columnas=3:2}

```python tests/test_api.py
def test_prediccion_consistente_con_los_coeficientes():
    respuesta = cliente.post("/predicciones", json={"x": 2.0})
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    # y = 2.3 * 2.0 + 1.7 = 6.3
    assert abs(cuerpo["y_hat"] - 6.3) < 1e-9
    assert cuerpo["extrapolado"] is False
```

|||

```shell Terminal
pytest -q
#> 4 passed
```

`pytest` y `httpx` van aparte, en `requirements-dev.txt`: la imagen no los necesita.

???
Una de las cuatro pruebas de la sección 10 (9.6); las otras comprueban `/health`, la extrapolación con `x = 50` y el 422 con `x = 5000`. pytest también muestra dos avisos de deprecación de la librería: son inofensivos. OJO: con `fastapi==0.111.0`, `httpx` llega a la imagen de todos modos, como dependencia de FastAPI (ver la nota de entrega).

## Paso 5 · Versiones fijadas y un contexto sin secretos {columnas=1:1}

```text requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
```

`==`, no `>=`: dos construcciones separadas por meses instalan lo mismo.

|||

```text .dockerignore
.git
.venv
__pycache__
.pytest_cache
.env
.env.*
tests/
notebooks/
Dockerfile
.dockerignore
```

???
Sección 10 (9.7 y 9.8); el `.dockerignore` completo tiene además cachés, documentación y carpetas de IDE. `tests/` se excluye porque la imagen final no lleva pruebas; si se quiere una etapa *tester*, hay que quitar esa línea.

## Paso 6 · La etapa builder deja las dependencias en `/opt/venv`

```dockerfile Dockerfile · etapa 1 {resaltar=12-13,16-18}
FROM python:3.11.9-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt
```

???
Sección 10 (9.9), sin los comentarios. `build-essential` solo hace falta si alguna *wheel* debe compilarse, y se descarta con la etapa. OJO: el material abre este archivo con `# Dockerfile` antes de `# syntax=docker/dockerfile:1.7`, y así la directiva se ignora; comprobado, BuildKit solo usa el frontend 1.7 cuando `# syntax=` es la primera línea. No impide construir.

## Paso 7 · La etapa runtime copia el entorno, baja privilegios y arranca

```dockerfile Dockerfile · etapa 2 {resaltar=8,10,12}
FROM python:3.11.9-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
RUN groupadd --system --gid 1001 appgroup \
 && useradd  --system --uid 1001 --gid appgroup --create-home appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup app/ ./app/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Entre `EXPOSE` y `CMD`, el material declara un `HEALTHCHECK` que consulta `/health` cada 30 s.

???
Sección 10 (9.9), sin comentarios ni líneas en blanco. Cada línea resaltada es una buena práctica: un solo `COPY --from`, `USER` antes del `CMD` y forma exec. El `HEALTHCHECK` completo está en el material; con la imagen construida, `docker inspect` lo mostró `healthy` a los pocos segundos.

## Paso 8 · Construir, lanzar y pedir una predicción

```shell Terminal 1
docker build -t regresion-api:0.1.0 .
docker run --rm -p 8000:8000 --name regresion regresion-api:0.1.0
```

```shell Terminal 2
curl -s http://localhost:8000/health
#> {"status":"ok"}
curl -s -X POST http://localhost:8000/predicciones \
     -H 'Content-Type: application/json' \
     -d '{"x": 2.0}'
#> {"y_hat":6.3,"extrapolado":false,"version_modelo":"0.1.0"}
```

???
Sección 10 (9.10); las dos salidas son las que dio el contenedor. La primera construcción tardó casi 3 minutos, casi todo en `pip install`. La documentación interactiva queda en `http://localhost:8000/docs`.

## Dentro del contenedor, ¿qué responde con `x = 50`? ¿Y con `x = 5000`? {.pregunta tipo=E2}

El modelo se entrenó con `x` entre −10 y 10; la validación admite de −1000 a 1000.

::: respuesta 200 con aviso, y 422
`x = 50` es válido pero extrapola: **200** con `"extrapolado": true`. `x = 5000` viola el validador: **422**. Igual que en las pruebas: el contenedor no cambia lo que hace FastAPI.
:::

???
Comprobado con curl contra el contenedor: con 50, `y_hat` sale 116.69999999999999 (buena ocasión para hablar del redondeo en coma flotante) y `extrapolado` true; con 5000, 422. Es lo que pide la práctica: comprobar que la API se comporta igual dentro del contenedor.

## Paso 9 · Verificar que el proceso corre sin privilegios

```shell Terminal 2
docker exec regresion id
#> uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup)
docker stop regresion
```

`appuser`, no `root`. Y `docker stop` cierra en menos de un segundo: la forma exec hace su trabajo.

???
La verificación de la sección 10 (9.10). El material también mide el tamaño con `docker images … --format "{{.Size}}"` y da 187 MB; aquí salió distinto (ver la nota de entrega), así que la cifra no se proyecta: que cada quien mida la suya.

## Cada decisión del `Dockerfile` responde a una buena práctica

| Decisión | Buena práctica |
|---|---|
| `python:3.11.9-slim-bookworm` | Versión exacta y base ligera |
| Builder y runtime separados | Sin compiladores en producción |
| Entorno virtual en `/opt/venv` | Un solo `COPY --from=builder` |
| `appuser` con UID 1001 | Menor privilegio |
| `HEALTHCHECK` | El orquestador reinicia si la API deja de responder |
| Forma exec en `CMD` | `SIGTERM` llega a Uvicorn: cierre limpio |

???
La tabla 9.11 del material. Buen momento para que el grupo la use como lista de verificación del `Dockerfile` de su propio proyecto.

# Cierre y práctica {icono=Award}

## Lo que se llevan hoy {.cierre}

- La imagen es la clase; el contenedor, su instancia
- El contenedor comparte el kernel: órdenes de magnitud más liviano que una VM
- Instrucciones por estabilidad decreciente: dependencias arriba, código abajo
- Multi-stage: se construye con compiladores y se entrega sin ellos
- Versión exacta, `.dockerignore`, forma exec y `USER`: la lista mínima

???
La imagen de hoy es la que se despliega en la semana 12.

## Práctica guiada: el Dockerfile del proyecto

::: flujo
1. **Escribir** — el `Dockerfile` y el `.dockerignore` del proyecto
2. **Construir** — `docker build -t <nombre>:0.1.0 .`
3. **Ejecutar** — `docker run --rm -p 8000:8000`
4. **Comprobar** — la API responde igual que fuera del contenedor
:::

::: info Para practicar la redacción
Los ejercicios 10.7 (mono-etapa) y 10.8 (multi-stage) de la autoevaluación, con su solución comentada.
:::

???
Los 180 minutos de práctica, según el reparto de «Antes de empezar». Sugerencia: pedir que construyan dos veces, cambiando una línea del código entre una y otra, para que vean el caché en acción.
