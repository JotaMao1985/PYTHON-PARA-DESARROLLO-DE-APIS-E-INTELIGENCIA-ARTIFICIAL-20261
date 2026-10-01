---
modulo: ../../11_Python_para_APIS_IA_Contenedores_y_Docker.html
agenda: si
---

<!--
  Semana 11 · Contenedores y Docker. Rehecha el 2026-10-01 sobre el capítulo revisado
  (numeración 2.x…12.x, Dockerfile sin --chown ni useradd --system, tamaños medidos).
  Exposición (60 min del reparto): del entorno virtual al contenedor 10, contenedores
  frente a VM 8, Dockerfile e imagen base 14, multietapa 8 y buenas prácticas 20.
  El reparto deja el contexto y la caché de capas como consulta; aquí van en buenas
  prácticas, a pedido. El ejemplo guiado (lección 10) abre la práctica guiada de 180 min:
  se hace en vivo, paso a paso.
  Código verificado: pytest y uvicorn en un entorno con las versiones fijadas del
  material (FastAPI 0.111.0, Uvicorn 0.30.1, Pydantic 2.7.4); la imagen del ejemplo,
  construida y ejecutada con Docker 29 (OrbStack, arm64), y la comparación con diff
  del apartado 10.11, que da «Respuestas idénticas».
-->

# Del entorno virtual al contenedor {seccion=repaso}

> ¿Cómo se entrega la API a otra máquina sin que la regresión devuelva otros números por culpa de otra versión de NumPy?

???
Unos 10 minutos. Es la pregunta con que abre el capítulo (lección 2). Aquí se cierra el adelanto de la semana 1, que solo pedía saber cuándo elegir un contenedor; el `Dockerfile` que salga de hoy es el que se despliega en la semana 12.

## `venv` y `requirements.txt` fijan los paquetes, no la máquina

| Pregunta | ¿La resuelve `venv` + `requirements.txt`? |
|---|---|
| ¿Qué versión de Python corre? | **Solo en parte.** Se puede declarar, pero `venv` usa la de cada máquina |
| ¿Qué bibliotecas del sistema hay (`libopenblas`, `tzdata`)? | **No.** Dependen de cada computador |
| ¿En qué orden arrancan Uvicorn y la base de datos? | **No.** Es cosa del despliegue |

La imagen responde las dos primeras; la tercera es de un orquestador como Docker Compose.

???
Recordar la semana 10: fijar versiones, semillas y configuración resuelve la reproducibilidad dentro de una misma máquina. La tabla es la de la lección 3: un `.python-version` puede declarar y verificar la versión, pero no la provee. Lo que queda abierto es justo lo que no vive en Python.

## El `Dockerfile` es a la imagen lo que `requirements.txt` al entorno virtual

| Entorno virtual | Docker |
|---|---|
| `requirements.txt`: declara las dependencias | `Dockerfile`: declara la imagen |
| `python -m venv .venv`: crea el entorno | `docker build`: crea la imagen |
| `source .venv/bin/activate`: lo activa | `docker run`: lanza un contenedor |
| La carpeta `.venv/` | La imagen: inmutable, identificada por un *hash* |
| Una terminal con el entorno activo | Un contenedor en ejecución |

???
La «Analogía conceptual» de la lección 3: si `requirements.txt` describe cómo reconstruir un entorno, el `Dockerfile` describe cómo reconstruir una máquina, capa por capa. El material advierte que el paralelismo es útil pero no exacto: un entorno virtual se puede modificar; una imagen, no.

## Una imagen es la clase; un contenedor, su instancia {.idea}

La imagen es una plantilla que no cambia. Cada `docker run` crea una instancia nueva, como un objeto de una clase o una muestra extraída de una distribución.

???
Es la «Idea central» de la lección 3. Preguntar: si dos personas lanzan la misma imagen, ¿comparten el contenedor? No: cada una tiene su instancia.

## Mismo `requirements.txt`, distinto Python: ¿mismo entorno? {.pregunta tipo=E2}

Usted trabaja con Python 3.11.9; su compañero, con 3.12. Los dos corren `pip install -r requirements.txt`, con todas las versiones fijadas con `==`.

¿Obtienen el mismo entorno?

::: respuesta No
`venv` usa el Python que tenga cada máquina, y `requirements.txt` no dice nada del intérprete ni de las bibliotecas del sistema. La imagen sí: los dos ejecutarían `python:3.11.9-slim-bookworm`.
:::

???
Es la primera fila de la tabla de la lección 3, puesta como caso. Si alguien responde «sí, porque las versiones están fijadas»: los paquetes pedidos coinciden, el intérprete no, y pip descarga *wheels* distintas para 3.12. Además, `==` no fija las dependencias de esas dependencias (apartado 10.7).

## Producción ejecuta, byte a byte, la imagen que construyó el flujo

::: flujo
1. **git push** — el código y su `Dockerfile`
2. **Integración continua** — pytest sobre el código y, si pasa, `docker build`
3. **Registro** — la imagen, etiquetada con el *hash* del commit
4. **Producción** — descarga esa misma imagen y la ejecuta
:::

La misma imagen en el portátil, en el servidor de pruebas y en producción.

???
El flujo de la lección 5 (5.2); la integración continua llega en la semana 12, hoy basta con la idea de paridad. Lo que Docker no resuelve (5.3): no corrige un modelo mal especificado, no reemplaza a pytest ni al README, y no congela lo que no se fijó.

# Contenedores frente a máquinas virtuales {seccion=vms}

> Las dos aíslan aplicaciones en un mismo computador. La diferencia está en dónde se traza la línea.

???
Unos 8 minutos.

## La VM carga un kernel por aplicación; el contenedor comparte el del anfitrión

::: html
<div class="grid grid-cols-2 gap-10 max-w-5xl mx-auto mb-6">
  <div class="rounded-xl overflow-hidden border border-slate-200 divide-y divide-slate-200 text-center text-lg font-medium [&>div]:px-4">
    <div class="bg-navy text-white font-semibold py-2">Máquinas virtuales</div>
    <div class="bg-white text-slate-800 py-2">App 1 + dependencias</div>
    <div class="bg-gold text-slate-900 py-2">SO huésped 1 (kernel completo)</div>
    <div class="bg-white text-slate-800 py-2">App 2 + dependencias</div>
    <div class="bg-gold text-slate-900 py-2">SO huésped 2 (kernel completo)</div>
    <div class="bg-secondary text-white py-2">Hipervisor (VMware, KVM, Hyper-V)</div>
    <div class="bg-slate-600 text-white py-2">Sistema operativo anfitrión</div>
    <div class="bg-slate-800 text-white py-2">Hardware físico</div>
  </div>
  <div class="rounded-xl overflow-hidden border border-slate-200 divide-y divide-slate-200 text-center text-lg font-medium [&>div]:px-4">
    <div class="bg-navy text-white font-semibold py-2">Contenedores</div>
    <div class="bg-white text-slate-800 py-2">App 1</div>
    <div class="bg-teal text-white py-2">Contenedor 1 (binarios + libs)</div>
    <div class="bg-white text-slate-800 py-2">App 2</div>
    <div class="bg-teal text-white py-2">Contenedor 2 (binarios + libs)</div>
    <div class="bg-primary text-white py-2">Motor de contenedores (Docker Engine)</div>
    <div class="bg-slate-600 text-white py-2">Sistema operativo anfitrión (kernel único)</div>
    <div class="bg-slate-800 text-white py-2">Hardware físico</div>
  </div>
</div>
:::

La VM virtualiza el hardware; el contenedor, solo el espacio de usuario.

???
Es la figura 4.1 del material, con sus colores y su orden. La contracara está en la tabla 4.3: el aislamiento del contenedor es fuerte pero menor, porque una vulnerabilidad del kernel compartido afecta a todos los contenedores.

## Arranque, disco y memoria: la distancia es de órdenes de magnitud

![Contenedor: medido con la imagen del ejemplo. VM: valores típicos](recursos/m11/chart-vms.json){alto=430}

???
Figura 4.2. El contenedor está medido con la imagen del ejemplo integrador (Apple Silicon, Docker 29): responde en ≈ 0,5 s, ocupa ≈ 260 MB y usa ≈ 60 MB de RAM. La VM, con valores típicos: ≈ 45 s, ≈ 4 GB de disco y ≈ 1 GB de RAM.

## Los namespaces aíslan lo que el proceso ve; los cgroups limitan lo que consume

::: tarjetas {columnas=2}
### Namespaces: lo que ve
Cada contenedor tiene su propia vista de procesos (PID), red (NET), montajes (MNT) y usuarios (USER). No ve los procesos de otro.
### cgroups: lo que consume
Ponen techo a CPU, memoria, disco y número de procesos. Docker no los aplica por defecto: se piden con `--memory` y `--cpus`.
:::

::: info En macOS y Windows
Hay una pequeña VM Linux por debajo. Y un Mac con procesador Apple construye imágenes `arm64`: para un servidor x86, `docker build --platform linux/amd64`.
:::

???
Lección 4, 4.2. Las dos primitivas son del kernel de Linux; por eso, fuera de Linux, hay una VM de por medio. Lo de la arquitectura importa en la semana 12: la mayoría de los servidores en la nube son `amd64`, y una imagen sirve para una sola arquitectura.

## ¿Máquina virtual o contenedor? {.pregunta tipo=E8}

1. Correr Windows en el servidor Linux del laboratorio
2. Reproducir exactamente el experimento de un compañero
3. Aislar en la misma nube los sistemas de dos organizaciones

::: respuesta VM · contenedor · VM
Otro sistema operativo exige otro kernel (1); reproducir un entorno es justo lo que hace una imagen (2); separar organizaciones pide el aislamiento fuerte de un kernel propio (3).
:::

???
Los tres casos son los de la lección 4 (4.4). Cerrar con la caja «Convivencia, no exclusión»: en la nube, las VM hospedan decenas de contenedores; las dos tecnologías viven en capas distintas.

# El Dockerfile y su imagen base {seccion=dockerfile}

> Un `Dockerfile` es un manual de cocina: cada paso recibe el resultado del anterior y le agrega algo encima.

???
Unos 14 minutos: el centro de la exposición. Incluye la lección 7, la imagen base.

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
La versión didáctica mínima de la lección 6 (6.1), sin el comentario inicial. El archivo se llama `Dockerfile`, sin extensión. `FROM` es la primera instrucción: solo un `ARG` puede ir antes.

## `ENV` persiste, `ARG` no sale de la construcción y `EXPOSE` no publica nada

| Instrucción | Qué hace |
|---|---|
| `ENV PYTHONUNBUFFERED=1` | Variable que persiste en la imagen **y** en el contenedor |
| `ARG APP_VERSION=0.1.0` | Variable que existe **solo** mientras se construye |
| `EXPOSE 8000` | **Documenta** el puerto; publicarlo es `docker run -p` |
| `USER appuser` | Cambia el usuario de lo que sigue y del proceso final |
| `HEALTHCHECK CMD …` | Marca el contenedor `healthy` o `unhealthy`; **no** lo reinicia |

???
Son las filas de la tabla 6.2 que más se confunden; `FROM`, `WORKDIR`, `COPY`, `RUN` y `CMD` ya salieron en la diapositiva anterior, y `ENTRYPOINT` queda para la lectura. La de `EXPOSE` es la que se pregunta enseguida.

## `EXPOSE 8000` y sin `-p`: ¿responde la API? {.pregunta tipo=E2}

La imagen del ejemplo declara `EXPOSE 8000`. Usted la lanza así:

```shell Terminal
docker run --rm regresion-api:0.1.0
```

Desde otra terminal pide `curl http://localhost:8000/health`. ¿Qué obtiene?

::: respuesta Nada: no hay conexión
`EXPOSE` solo **documenta** el puerto. Hacen falta dos cosas: publicarlo con `docker run -p 8000:8000` y que Uvicorn escuche en `0.0.0.0`, que es lo que hace el `--host` del `CMD`.
:::

???
Es la caja «Del contenedor al navegador» de la lección 6. Comprobado con la imagen del ejemplo: sin `-p`, curl no conecta; con `-p` pero con Uvicorn en `127.0.0.1` (su valor por defecto), curl recibe una respuesta vacía; con las dos cosas, `{"status":"ok"}`.

## Cada instrucción con contenido agrega una capa inmutable

::: flujo
1. **FROM** — la imagen base
2. **WORKDIR** — `/app`
3. **COPY** — las dependencias
4. **RUN** — `pip install`
5. **COPY** — el código
6. **Contenedor** — capa de escritura; se va con `docker rm`
:::

Docker calcula un *hash* de la entrada de cada capa. Si coincide con uno guardado, **reutiliza** la capa en vez de reconstruirla.

???
La figura 6.1 de la lección 6 (6.3): `ENV`, `USER`, `EXPOSE` y `CMD` solo anotan metadatos. La capa del contenedor explica por qué lo que se escribe dentro se pierde con `docker rm` (vuelve en el apartado 10.12, con SQLite). La consecuencia del *hash*, el orden de las instrucciones, es la primera buena práctica.

## `python:3.11.9-slim-bookworm` se lee en cuatro partes

| Parte | Qué fija |
|---|---|
| `python` | El repositorio oficial, con CPython instalado |
| `3.11.9` | La versión exacta, mayor, menor **y parche**: la del curso |
| `slim` | Una variante recortada: Python y `pip`, sin extras de Debian |
| `bookworm` | Debian 12: hoy *oldstable*, con soporte hasta junio de 2028 |

???
Tabla 7.1 (lección 7). El repositorio `python` lo mantiene la comunidad de Docker; CPython es de la Python Software Foundation. `slim` deja fuera compiladores (`gcc`, `build-essential`), cabeceras y herramientas como `git` o `curl`: si una dependencia exige compilar, eso se resuelve con multi-stage.

## `slim` pesa un séptimo de la imagen completa y conserva las *wheels* científicas

![](recursos/m11/chart-imagen-base.json){alto=370}

`alpine` es aún más pequeña, pero usa `musl`: scikit-learn o PyTorch no publican *wheels* para ella, y hay que compilar.

???
Tabla 7.2 y figura 7.1: tamaños descomprimidos para `linux/amd64`. Docker Hub anuncia el comprimido, mucho menor (unos 50 MB para `slim`), y en un Mac con procesador Apple la imagen es `arm64` y algo mayor (unos 170 MB para `slim`).

# Construcción multietapa {seccion=multistage}

> Los compiladores que hacen falta para construir no tienen nada que hacer en producción.

???
Unos 8 minutos.

## Construir necesita compiladores; ejecutar, no

::: tarjetas {columnas=2}
### builder: construir
`build-essential`, cabeceras, la caché de `apt` y la de `pip`. Se usan para instalar y se descartan.
### runtime: ejecutar
El intérprete, el entorno virtual con los paquetes y el código. Es lo único que se entrega.
:::

Sin compiladores en producción: menos **superficie de ataque**, y menos peso cuando hubo que compilar.

???
Lección 9, 9.2: cinco ventajas; aquí van las dos que más pesan. Las otras tres: dependencias de construcción y de ejecución separadas, una etapa builder que alimenta varias imágenes (API, *worker*, job batch) y construcción en paralelo con BuildKit.

## Cada `FROM` abre una etapa, y solo la última se entrega

```dockerfile Dockerfile {resaltar=2,6-7}
# Etapa 1: builder — todo lo que solo hace falta durante la construcción
FROM python:3.11.9-slim-bookworm AS builder
# ... instalar compiladores, descargar dependencias, compilar wheels ...

# Etapa 2: runtime — la imagen final que se entrega a producción
FROM python:3.11.9-slim-bookworm AS runtime
COPY --from=builder /opt/venv /opt/venv
# ... copiar el código y arrancar la aplicación ...
```

La imagen final es la base de su etapa más lo que se copia con `COPY --from`: aquí, el entorno virtual.

???
El esquema general de la lección 9 (9.1). Para depurar, `docker build --target builder` construye hasta esa etapa y permite abrir una shell dentro sin tocar la imagen de producción (9.5).

## Dejar el compilador fuera de la imagen ahorra unos 300 MB

![](recursos/m11/chart-multistage.json){alto=400}

Sin nada que compilar, un mono-etapa pesa lo mismo: el multi-stage permite compilar sin cargar con el compilador.

???
Tabla 9.4 y figura 9.1: estimados para `linux/amd64` con numpy, scipy y scikit-learn. Medido con el ejemplo integrador en un Mac (`arm64`, suma de `docker history`): mono-etapa con compilador ≈ 560 MB, sin compilador ≈ 235, multi-stage ≈ 260 (hoy dio 262). El multi-stage se mantiene por la separación entre construir y ejecutar, no porque adelgace siempre.

## ¿Qué se queda en el builder y no llega a la imagen final? {.pregunta tipo=E2}

En el ejemplo del curso, el builder instala `build-essential` con `apt-get` y crea el entorno virtual en `/opt/venv`; el runtime copia ese entorno y el código.

¿Qué parte del trabajo del builder llega a la imagen final?

::: respuesta Solo /opt/venv
Todo lo demás se descarta con la etapa, en particular `build-essential`: el compilador y sus cabeceras. Menos tamaño y menos superficie de ataque.
:::

???
Es el ejercicio 11.5 de la autoevaluación. Su solución advierte que borrar `/var/lib/apt/lists/` o instalar con `--no-cache-dir` es otra técnica, ortogonal: ahorra espacio dentro de una misma etapa.

# Buenas prácticas {seccion=cierre}

> Una imagen que construye y responde todavía no es una imagen que se pueda entregar.

???
Unos 20 minutos. Reúne las prácticas que el material reparte entre las lecciones 6 a 9 con las «Buenas prácticas de seguridad» de la lección 12 (12.2). Los tiempos que se citan son de la imagen del ejemplo, construida con OrbStack en un Mac.

## Ordene las instrucciones por estabilidad decreciente {.idea etiqueta="Regla de oro"}

Lo que cambia rara vez va arriba; lo que cambia varias veces al día, abajo. Así, un cambio en el código no reinstala las dependencias.

???
La regla de oro de la lección 6 (6.4): las dependencias cambian cada semanas o meses; el código, varias veces al día.

## Dependencias primero, código después: un cambio de código no reinstala nada {columnas=1:1}

```dockerfile Anti-patrón
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
```

Cualquier cambio en `app/` invalida `COPY . .` y todo lo que sigue.

|||

```dockerfile Patrón
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
```

Medido con el ejemplo: tras cambiar `main.py`, la reconstrucción tardó **1 s**; solo el `pip install`, de 20 s a 2.5 min según la red.

???
El código de la lección 6 (6.4); es también el ejercicio 11.3. En la segunda construcción, todas las capas hasta `pip install` salieron `CACHED`; solo se rehízo la copia de `app/`. Con el anti-patrón, cada cambio de código paga de nuevo la instalación entera.

## Fije la versión exacta y, si puede, el *digest*

```dockerfile {resaltar=5}
# No recomendado: la versión flota.
FROM python:3.11-slim

# Recomendado: versión exacta.
FROM python:3.11.9-slim-bookworm

# Reproducibilidad máxima: hash criptográfico de la imagen.
FROM python:3.11.9-slim-bookworm@sha256:abc123...def
```

Son alternativas: un `Dockerfile` real lleva **una** sola línea `FROM`. Y fijar no es congelar: la base fijada no recibe parches.

???
Lección 7 (7.4). El *hash* de la última línea es ilustrativo; el real se obtiene con `docker inspect … --format='{{index .RepoDigests 0}}'`. El material pide subir la versión de forma deliberada cada cierto tiempo, con las pruebas en verde y tras escanear la imagen. Lo mismo vale para `requirements.txt`: `==`, no `>=`.

## Lo que no se ignora viaja al *daemon*, y puede quedar en una capa

```shell Terminal
docker build -t regresion-api:0.1.0 .
#> => transferring context: 482.31kB
```

`docker build .` empaqueta la carpeta, el **contexto**, y la envía al *daemon*. `.dockerignore` decide qué no viaja.

::: warn Un .env copiado no se borra
Queda en una capa permanente: un `RUN rm` posterior no lo quita. Si un secreto hace falta al construir, `RUN --mount=type=secret`, nunca `ARG` ni `ENV`.
:::

???
Lección 8 (8.1 a 8.3): velocidad, seguridad y caché. Con el `.dockerignore` del ejemplo, el contexto medido fue de 9.3 kB. Para auditar qué llega al *daemon*, el apartado 8.4 trae un `docker build -f -` que lista el contexto real (`tar --exclude-from` no sirve: no entiende `**` ni `!`). En ejecución, las credenciales llegan como variables de entorno.

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
Lección 6 (6.5); el material ya cita estos tiempos. Medido con la imagen del ejemplo y su `CMD` completo: con la forma exec, el proceso 1 del contenedor es Uvicorn; con la forma shell, es `sh -c`, y Docker espera los 10 s de gracia antes de matarlo con `SIGKILL`. Una API que no atiende `SIGTERM` deja peticiones a medias y conexiones abiertas.

## Si la plataforma decide el puerto, un shell con `exec` conserva la señal

```dockerfile Dockerfile
CMD ["sh", "-c", \
     "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

La forma exec no expande variables: `"$PORT"` llegaría literal a Uvicorn. Con `exec`, Uvicorn sigue siendo el proceso principal y recibe `SIGTERM`.

???
La caja «Cuando el puerto lo decide la plataforma» de la lección 6 (6.5), con la línea partida en dos. Render o Railway, en la semana 12, asignan el puerto en `$PORT`. El mismo patrón sirve para aplicar las migraciones antes de arrancar: `sh -c "alembic upgrade head && exec uvicorn …"`. Si el puerto cambia, el `HEALTHCHECK` debe sondear ese mismo puerto (10.12).

## El proceso corre como `appuser` y el código es de `root`: no lo puede modificar

```dockerfile {resaltar=2,4-5}
RUN groupadd --system --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --create-home appuser
WORKDIR /app
COPY app/ ./app/
USER appuser
```

Sin `--chown`, el código queda de solo lectura para `appuser`: quien comprometa el proceso no puede cambiar la aplicación.

???
Ejercicio 11.6 y la caja «Lo nuevo en este Dockerfile» de la lección 10. Comprobado en el contenedor: `id` da `uid=1001(appuser)` y un `touch` dentro de `app/` da `Permission denied`. La consecuencia práctica: `appuser` solo escribe en `/tmp`, en su `$HOME` y en los directorios que se le entreguen, así que una base SQLite necesita uno propio (10.12).

## Para ampliar: escanear, actualizar a propósito y restringir

::: tarjetas {columnas=3}
### Escanear
`docker scout`, `trivy` o `grype` revisan las capas y reportan CVE conocidas
### Actualizar
Subir la base y las dependencias de forma deliberada, con pruebas y escaneo
### Restringir
`docker run --read-only` o `--cap-drop=ALL`, si la aplicación lo permite
:::

Y una sola responsabilidad por imagen: sin `curl` ni `git` en producción.

???
La lección 12 (12.2) separa cuatro prácticas mínimas —no correr como root, no copiar secretos, fijar versiones, reducir la superficie de ataque— de estas tres, «para ampliar, cuando el proyecto lo pida». Hoy no se practican.

## Este `Dockerfile` construye sin errores. ¿Qué buenas prácticas incumple? {.pregunta tipo=E3}

```dockerfile
FROM python:3.11.9-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

::: respuesta Dos, por lo menos
`COPY . .` antes de `pip install`: cada cambio en `app/` reinstala todo. Y no hay `USER`: el proceso corre como `root`. Sin `.dockerignore`, además, `COPY . .` se lleva el `.env`.
:::

???
Es el ejercicio 11.3, que pregunta solo por la caché; lo del usuario y el `.env` sale de las prácticas mínimas de la lección 12. La corrección de la caché está en la solución comentada 11.3.

# Ejemplo guiado paso a paso: regresion-api {seccion=integrador}

> Una API que sirve una regresión lineal, empaquetada en dos etapas, sin `root` y con sondeo de salud.

???
Este bloque abre la práctica guiada: se hace en vivo, con el grupo escribiendo a la par. Todo el código es el de la lección 10 y se comprobó: las 4 pruebas pasan con las versiones fijadas, la imagen se construye y el contenedor responde exactamente lo mismo que la API local.

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
├── requirements-dev.txt
├── .dockerignore
└── Dockerfile
```

|||

- **Pasos 1–2** · El modelo y sus esquemas
- **Pasos 3–4** · La API y sus pruebas
- **Paso 5** · Dependencias y contexto
- **Pasos 6–7** · El `Dockerfile`, en dos etapas
- **Pasos 8–10** · Construir, comparar y verificar

???
La estructura de la lección 10 (10.1), sin los comentarios de los dos `requirements`: el de producción va en la imagen; el de desarrollo, no. El modelo se entrenó fuera de línea: en un proyecto real, el JSON lo produciría un script de entrenamiento versionado.

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
Recortado: sin imports, docstrings ni la línea `RUTA_MODELO = Path(__file__).parent / "modelo.json"` (10.2 y 10.3). Un JSON no admite comentarios: por eso la explicación de los coeficientes va fuera del archivo. Si alguien le pone un `#`, `json.load` falla y toda predicción da 500 aunque `/health` siga en verde.

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
Apartado 10.4, sin las descripciones de los dos últimos campos. La caja «Dos rangos, dos propósitos»: `[-1000, 1000]` protege a la API de entradas absurdas y da 422; `[-10, 10]` es el dominio de entrenamiento, y salirse de él es válido pero se avisa. El primero es de FastAPI; el segundo, del estadístico.

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
Apartado 10.5, sin la creación de `app` ni el `/health`. `cargar_modelo` con `@lru_cache` hace de *provider* (semana 8): lee el JSON la primera vez y después lo reutiliza.

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
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
#> 4 passed
```

`requirements-dev.txt` incluye `requirements.txt` y suma `pytest`, que la imagen no lleva.

???
Una de las cuatro pruebas de 10.6; las otras comprueban `/health`, la extrapolación con `x = 50` y el 422 con `x = 5000`. Comprobado con las versiones fijadas: 4 pasan, con dos avisos de deprecación de la librería, inofensivos. Según la caja «Dependencias de desarrollo aparte», `httpx` llega a la imagen de todos modos, porque `fastapi==0.111.0` lo trae.

## Paso 5 · Versiones fijadas y un contexto sin secretos {columnas=1:1}

```text requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
```

`==` fija los tres paquetes pedidos, no sus dependencias: para congelar el árbol, `pip freeze` o `pip-compile`.

|||

```text .dockerignore
.git
.venv
**/__pycache__
**/*.pyc
**/.env
**/.env.*
**/*.db
tests/
Dockerfile
.dockerignore
```

???
Apartados 10.7 y 10.8; el `.dockerignore` completo tiene además cachés, claves, documentación y carpetas de IDE. Los patrones con `**/` valen a cualquier profundidad: sin él, `__pycache__` solo excluiría el de la raíz, y los de `app/` entrarían con el `COPY app/`. `**/*.db` deja fuera la base de desarrollo.

## Paso 6 · La etapa builder deja las dependencias en `/opt/venv`

```dockerfile Dockerfile · etapa 1 {resaltar=12-13,16-17}
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
RUN pip install -r requirements.txt
```

???
Apartado 10.9, sin los comentarios. `build-essential` solo haría falta si alguna *wheel* debiera compilarse; aquí todas vienen compiladas, así que no se usa, y se descarta con la etapa. El entorno virtual se puede copiar a la otra etapa porque las dos usan la misma base y la misma ruta: un `venv` no es reubicable.

## Paso 7 · La etapa runtime copia el entorno, baja privilegios y arranca

```dockerfile Dockerfile · etapa 2 {resaltar=8,10,12}
FROM python:3.11.9-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
RUN groupadd --system --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --create-home appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Entre `EXPOSE` y `CMD`, el material declara un `HEALTHCHECK` que consulta `/health` cada 30 s.

???
Apartado 10.9, sin comentarios ni líneas en blanco. Cada línea resaltada es una buena práctica: un solo `COPY --from`, `USER` antes del `CMD` y forma exec. El `HEALTHCHECK` completo está en el material: marca el contenedor `healthy` o `unhealthy` (se ve en `docker ps`), pero no lo reinicia. Comprobado: `healthy` a los pocos segundos.

## Paso 8 · Construir, lanzar y pedir una predicción

```shell Terminal 1
docker build -t regresion-api:0.1.0 .
docker run --rm -p 8000:8000 --name regresion regresion-api:0.1.0
```

```shell Terminal 2
curl -s -w '\n' http://localhost:8000/health
#> {"status":"ok"}
curl -s -w '\n' -X POST http://localhost:8000/predicciones \
  -H 'Content-Type: application/json' \
  -d '{"x": 2.0}'
#> {"y_hat":6.3,"extrapolado":false,"version_modelo":"0.1.0"}
```

???
Apartado 10.10; las dos salidas son las que dio el contenedor. La primera construcción tarda lo que tarde `pip install` con la red del aula. La documentación interactiva queda en `http://localhost:8000/docs`, y necesita Internet: carga sus recursos desde un CDN.

## Dentro del contenedor, ¿qué responde con `x = 50`? ¿Y con `x = 5000`? {.pregunta tipo=E2}

El modelo se entrenó con `x` entre −10 y 10; la validación admite de −1000 a 1000.

::: respuesta 200 con aviso, y 422
`x = 50` es válido pero extrapola: **200** con `"extrapolado": true`. `x = 5000` viola el validador: **422**. Igual que en las pruebas: el contenedor no cambia lo que hace FastAPI.
:::

???
Comprobado con curl contra el contenedor: con 50, `y_hat` sale 116.69999999999999 (buena ocasión para hablar del redondeo en coma flotante) y `extrapolado` true; con 5000, 422. La diapositiva siguiente lo comprueba de forma sistemática.

## Paso 9 · Las mismas peticiones a la API local y al contenedor: `diff` no ve diferencias

```shell Terminal 3 · la API local, en otro puerto
uvicorn app.main:app --port 8001
```

```shell Terminal 2
peticiones() {
  for x in 2.0 50.0 5000.0; do
    curl -s -w ' [HTTP %{http_code}]\n' -X POST \
      "http://localhost:$1/predicciones" \
      -H 'Content-Type: application/json' -d "{\"x\": $x}"
  done
}
diff <(peticiones 8001) <(peticiones 8000) && echo "Respuestas idénticas"
#> Respuestas idénticas
```

???
Apartado 10.11, con la línea del `curl` partida en tres. Es lo que pide la práctica: comprobar que la API se comporta igual dentro del contenedor. Comprobado con las versiones fijadas: «Respuestas idénticas». Antes conviene verificar que los dos responden en `/health`, porque con los dos apagados `diff` también sale «idéntico». Los `<( … )` requieren `bash` o `zsh`.

## Paso 10 · Verificar que el proceso corre sin privilegios

```shell Terminal 2
docker exec regresion id
#> uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup)
docker stop regresion
```

`appuser`, no `root`. Y `docker stop` cierra en menos de un segundo: la forma exec hace su trabajo.

???
La verificación del apartado 10.10. El material también mide el tamaño con `docker history` (≈ 260 MB en Apple Silicon, ≈ 200–220 en x86); `docker images` puede mostrar otra cifra según la versión de Docker (con containerd, ≈ 330 MB de disco y ≈ 73 MB comprimidos).

## En su proyecto: estructura, variables, SQLite y puerto

::: tarjetas {columnas=2}
### Estructura
Con `main.py` en la raíz: `COPY main.py .` y `"main:app"`. Copiar también lo que se lee al arrancar: modelos, migraciones
### Variables
La imagen no lleva `.env`: `docker run --env-file .env`, con `CLAVE=valor` sin comillas
### SQLite
Un directorio propio para `appuser` (`/data`) y un volumen, `-v datos:/data`, para que los datos sobrevivan
### Puerto y migraciones
El `CMD` con `sh -c` y `exec`; el `HEALTHCHECK`, sondeando el mismo puerto
:::

???
Apartado 10.12, «De este ejemplo a tu proyecto»: los ajustes que suele exigir el proyecto propio. El material trae las órdenes completas, incluido el volumen que sobrevive a `docker rm` y un `docker-compose.yml` mínimo. Es la base de la tarea autónoma del 10.11.

## Cada decisión del `Dockerfile` responde a una buena práctica

| Decisión | Buena práctica |
|---|---|
| `python:3.11.9-slim-bookworm` | Versión exacta y base ligera |
| Builder y runtime separados | Sin compiladores ni cabeceras en la imagen final |
| Entorno virtual en `/opt/venv` | Un solo `COPY --from`, con la misma base y la misma ruta |
| `appuser` con UID 1001 | Menor privilegio: no puede modificar el código |
| `HEALTHCHECK` | `docker ps` muestra `healthy` o `unhealthy` |
| Forma exec en `CMD` | `SIGTERM` llega a Uvicorn: cierre limpio |

???
La tabla 10.13 del material. Reiniciar un contenedor `unhealthy` es cosa de un orquestador o de la plataforma. Buen momento para que el grupo use la tabla como lista de verificación del `Dockerfile` de su propio proyecto.

# Cierre y práctica {icono=Award}

## Lo que se llevan hoy {.cierre}

- La imagen es la clase; el contenedor, su instancia
- El contenedor comparte el kernel: órdenes de magnitud más liviano que una VM
- Instrucciones por estabilidad decreciente: dependencias arriba, código abajo
- Multi-stage: se compila en el builder y se entrega sin compilador
- Versión exacta, `.dockerignore`, forma exec y `USER`: las prácticas mínimas

???
El `Dockerfile` de hoy es el que se despliega en la semana 12.

## Práctica guiada: el Dockerfile del proyecto

::: flujo
1. **Escribir** — el `Dockerfile` y el `.dockerignore` del proyecto
2. **Construir** — `docker build -t <nombre>:0.1.0 .`
3. **Ejecutar** — `docker run --rm -p 8000:8000 --env-file .env`
4. **Comprobar** — las mismas peticiones, local y en el contenedor, con `diff`
:::

::: info Para practicar la redacción
Los ejercicios 11.7 (mono-etapa) y 11.8 (multi-stage) de la autoevaluación, con su solución comentada.
:::

???
Los 180 minutos de práctica, según el reparto de «Antes de empezar»: escribir el `Dockerfile` (lección 10), construir y ejecutar (lecciones 10 y 11) y comprobar la equivalencia (apartado 10.11). Sugerencia: pedir que construyan dos veces, cambiando una línea del código entre una y otra, para que vean la caché en acción.
