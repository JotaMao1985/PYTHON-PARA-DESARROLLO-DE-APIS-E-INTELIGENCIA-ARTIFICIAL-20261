# Plan de mejora — Módulo 5 · La aplicación: qué es y cómo se levanta

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-09-07
**Archivo principal:** [`5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`](5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html) · 3 080 líneas
**Archivo secundario:** [`6_Python_para_APIS_IA_Fast_API.html`](6_Python_para_APIS_IA_Fast_API.html) · sección «🚀 ¿Cómo Ejecutar los Ejemplos?» (líneas 2409–2503)
**Rama:** `migracion/modulos-3-5-7-8-9`

---

## Estado · cómo retomar esto en otra conversación

**Al 2026-09-07: hechas T1, T2, T3 y T4. Pasados los puntos de control A y B. Falta T5.**

T1–T4 están **confirmadas** en la rama `migracion/modulos-3-5-7-8-9`, en un solo commit
—`feat(modulo-5): la aplicación aparecía por primera vez…`— con dos archivos: el módulo 5
(+255 −25) y este plan. **Sin publicar a `main`**, así que los estudiantes todavía no lo ven.

Lo demás que aparezca en `git status` ya estaba antes de empezar y no es de este trabajo.

**Lo que queda, por orden de importancia:**

- **T6 (§3, fase 4) — decisión antes que trabajo.** Todo lo hecho vive sólo en el archivo
  publicado, y un remontaje con `montar.py` lo borraría entero: la sección, los dos ejercicios
  y los cinco retoques de T3. El camino duradero está probado en el módulo 4 y descrito en T6.
  **Es lo primero que hay que decidir**, porque cuanto más crezca el trabajo a mano, más caro
  es llevarlo a la receta.
- **T5 (§3, fase 3)** — reducir la guía «🚀 ¿Cómo Ejecutar los Ejemplos?» del módulo 6 a un
  recordatorio que remita a la semana 5. Dos avisos antes de abrir ese archivo:

  1. **Edición manual, nunca `montar.py`.** El módulo 6 arrastra el problema de sangría conocido.
  2. **Hay algo que mirar de paso:** `verificar_codigo.py` marca **7 bloques del módulo 6 rotos**
   con `unexpected indent`. Es preexistente. Falta comprobar en el DOM si el estudiante los ve
   mal sangrados o si es un artefacto del extractor. Si es lo primero, es un defecto aparte de
   T5 y merece su propio plan, no arreglarlo de tapadillo aquí.

**Cómo verificar cualquier cosa en este material** —y esto no es opcional, es lo que ha cazado
todos los defectos de este plan—:

```bash
python3 -c "
import io,re,ast
s=io.open('5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html',encoding='utf-8').read()
for t,c in re.findall(r'<CodeBlock title=\"([^\"]*)\" lang=\"python\" code=\{\`([^\`]*)\`\}',s):
    try: ast.parse(c); print('OK ',t)
    except SyntaxError as e: print('FALLA',t,e)
"
```

Y la página, servida y leída en el navegador: `preview_start` con `piloto-lpcore` (puerto
8137) y luego `http://localhost:8137/5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`.
Con el panel oculto, `read_page` devuelve vacío: leer con `javascript_tool` sobre el DOM.

---

## 0. El hallazgo

El módulo 5 es **la primera vez en todo el curso** que aparece una aplicación. No es una
impresión: los cuatro módulos anteriores no contienen ni una sola aparición de `FastAPI()`,
`@app.` ni `uvicorn`.

| Archivo | `FastAPI()` | `@app.` | `uvicorn` |
|---|---|---|---|
| `1_Python_para_APIS_IA.html` | 0 | 0 | 0 |
| `2_..._HTTP.html` | 0 | 0 | 0 |
| `3_..._POO_Clases.html` | 0 | 0 | 0 |
| `4_..._Pydantic.html` | 0 | 0 | 0 |
| **`5_..._Del_Modelo_al_Servicio_Web.html`** | **3** | **9** | **7** |

Y en esa primera aparición —línea 2396, `app = FastAPI()`— el material no dice qué es ese
objeto ni qué hay que teclear para que exista un servicio. Tres huecos concretos:

**H1 · El puente que no se cruza.** La sección 1.2 muestra la aplicación WSGI cruda
(`def app(environ, start_response)`, líneas 2255–2266) y cierra diciendo que «nadie escribe
aplicaciones así» y que «lo que acabas de ver es lo que *no* vas a tener que escribir nunca».
Dos secciones más abajo aparece `app = FastAPI()` sin que nadie diga que **es la misma pieza**,
construida por el framework en vez de a mano. El puente conceptual está a una frase de
distancia y no se da: el estudiante ve dos cosas llamadas `app` que no sabe que son la misma.

**H2 · El comando huérfano.** El único comando del módulo es `uvicorn app.main:app --reload`
(línea 2273). No se explica la sintaxis `módulo:variable`, y los bloques de código se titulan
`routing.py` (2394, 2419), `app_flask.py` (2468) y `app_fastapi.py` (2499). Ningún estudiante
puede mapear `app.main:app` con ningún archivo que tenga delante. Falta además todo lo demás
del primer arranque: qué imprime uvicorn, a qué URL ir, cómo se para, qué hacer si falla.

**H3 · La sesión promete lo que el material no enseña.** La tabla de apertura (línea 2180)
reparte 180 min de práctica guiada que **empiezan** por «Levantar un servidor mínimo con
uvicorn --reload». Y el taller evaluativo del corte I —que examina justamente los módulos 1
a 5— entrega una semilla cuyo README exige `uvicorn main:app --reload` (`taller_corte1/semilla/README.md`).
El estudiante tiene que ejecutar en el taller un comando que el material nunca le enseñó.

**Dónde sí está.** El módulo 6 tiene una guía «🚀 ¿Cómo Ejecutar los Ejemplos?» con cinco
pasos correctos y completos. Llega una semana tarde, después del taller.

---

## 1. Decisiones tomadas

| # | Decisión | Por qué |
|---|---|---|
| D1 | **Sección propia** en la barra lateral, entre «El servidor web y WSGI» y «Routing básico» | Queda en el menú, se puede volver a ella durante el taller y llega después de saber qué es un servidor web pero antes de la primera ruta |
| D2 | **El 5 enseña, el 6 recuerda**: la guía del módulo 6 se reduce a un recordatorio con remisión a la semana 5 | Una sola fuente de verdad; dos versiones del mismo procedimiento divergen |
| D3 | **`main.py` plano y `uvicorn main:app` como canónico**; `app.main:app` se explica como la variante de paquete | Es exactamente lo que exige la semilla del taller de corte I. `app.main:app` es lo que usa `Proyecto_I` y el Dockerfile de la semana 11, así que se enseña, pero después |
| D4 | La aplicación **no se ejecuta, se importa** — se dice explícitamente | El estudiante viene de `python script.py`. `python main.py` no imprime nada, y ése es el tropiezo del primer día |

---

## 2. Grafo de dependencias

```
Sección nueva escrita (T1)
      │
      ├── Registrada en `curriculum` + renumeración de la barra (T2)  ← bloquea todo lo visual
      │        │
      │        ├── Coherencia interna del módulo 5 (T3)   — remite a la sección nueva
      │        └── Actividades interactivas (T4)          — viven dentro de la sección
      │
      └── Reducción de la guía del módulo 6 (T5)          — independiente del 5, se puede paralelizar
```

T5 no depende de T1–T4 en el código, pero sí en el contenido: el recordatorio del módulo 6
remite a la sección nueva, así que su texto se fija cuando T1 está escrita.

---

## 3. Tareas

### Fase 1 — La sección nueva

#### Tarea 1: Escribir `ArrancarSection` — **HECHA el 2026-09-07**

**Descripción.** Un componente nuevo en el bloque `=== SECCIONES ===` del módulo 5, con
cuatro subsecciones que van del objeto al comando, del comando a la pantalla y de la pantalla
al error. Se inserta después de `ServidorWebSection` y antes de `RoutingSection`.

Contenido, subsección por subsección:

- **2.1 `app` es la pieza que ya viste.** Retoma literalmente el callable WSGI de 1.2: aquella
  función `app` *era* la aplicación; `app = FastAPI()` es esa misma pieza construida por el
  framework. Tres afirmaciones explícitas: (a) es un **objeto**, no un archivo ni un proceso;
  (b) `@app.get("/health")` **no ejecuta nada** — registra una ruta en ese objeto; (c) es lo
  que el servidor **importa**. Cierra con D4: `python main.py` no levanta nada, y por qué.
  Un `Pipeline` o diagrama corto: `main.py` → objeto `app` → uvicorn → puerto 8000.
- **2.2 De archivo a servicio.** Un `main.py` completo de ~10 líneas (dos rutas: `/` y
  `/health`, coherente con la buena práctica que el propio módulo recomienda en la línea 2748)
  y, justo debajo, `uvicorn main:app --reload` desmontado en tabla: `main` = el archivo sin
  `.py`, `app` = la variable dentro del archivo, `--reload` = releer al guardar, sólo en
  desarrollo. Después, la variante: cuando el código vive en `app/main.py`, el comando es
  `uvicorn app.main:app` — que es la línea que ya está en 1.3 y la que irá en el Dockerfile
  de la semana 11.
- **2.3 Qué ve en pantalla.** La salida literal de uvicorn (`INFO: Uvicorn running on
  http://127.0.0.1:8000 (Press CTRL+C to quit)`), las tres URL (`/`, `/health`, `/docs`), el
  `curl` equivalente —que engancha con el módulo 2— y `Ctrl+C` para parar. En `/docs` se
  cierra el círculo del módulo 4: los tipos que ya escribió están documentados sin hacer nada.
- **2.4 Cuando no arranca.** Los cuatro fallos del primer arranque, con el mensaje literal:

  | Mensaje | Causa |
  |---|---|
  | `Error loading ASGI app. Could not import module "main"` | La terminal no está en la carpeta de `main.py` |
  | `Error loading ASGI app. Attribute "app" not found in module "main"` | La variable se llama de otra forma |
  | `[Errno 48] Address already in use` | Hay otro uvicorn vivo; `--port 8001` o cerrarlo |
  | `ModuleNotFoundError: No module named 'fastapi'` | Entorno virtual sin activar |

**Criterios de aceptación:**
- [ ] La sección responde, con esas palabras, a «¿qué es `app`?» y a «¿qué tecleo?»
- [ ] Cita el callable WSGI de 1.2 de forma explícita: el estudiante sabe que son la misma pieza
- [ ] `uvicorn main:app --reload` aparece desmontado término a término
- [ ] Los cuatro mensajes de error son los literales de uvicorn, no paráfrasis

**Verificación:**
- [ ] `python3 scripts/auditoria/verificar_codigo.py` — el `main.py` nuevo compila
- [ ] El `main.py` del bloque, guardado y ejecutado con `uvicorn main:app`, responde en `/health`
- [ ] Ningún literal de plantilla pierde una barra invertida (ver R3)

**Dependencias:** ninguna
**Archivos:** `5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`
**Alcance:** M (1 archivo, ~120 líneas nuevas → 174 reales, sólo inserciones)

**Lo que se comprobó y lo que salió:**
- El `main.py` del material se extrajo del HTML, se levantó con `uvicorn main:app --reload`
  y respondió **200** en `/`, `/health` y `/docs`, con exactamente el JSON que el texto promete.
- La salida real de uvicorn 0.41 dice `using WatchFiles`, no `using StatReload`, porque este
  equipo tiene `watchfiles`. Con el `pip install` de los prerrequisitos sale `StatReload`. El
  bloque conserva `StatReload` y la prosa avisa de que esa línea varía.
- La sección se numera **2.1–2.4**, así que T2 tiene que renumerar los encabezados de contenido
  de las tres secciones siguientes (2.x→3.x en Routing, 3.x→4.x en Frameworks, 4.x→5.x en
  Asincronía) y la remisión «(sección 3)» de la tabla de apertura.
- **El icono `Terminal` no existe.** `Icons` no es lucide completo: LP-CORE trae 17 iconos
  escritos a mano (`BookOpen`, `Binary`, `Cpu`, `Calculator`, `Award`, `ChevronLeft`,
  `ChevronRight`, `Workflow`, `ArrowDownUp`, `GitBranch`, `Repeat`, `FileCode`, `Grid`,
  `FunctionSquare`, `Bug`, `Table`, `Layers`) y `renderIcon` devuelve `null` en silencio con
  cualquier otro nombre — en la verificación la entrada salió **sin icono**. T2 usa `FileCode`,
  que está libre. No añadir iconos a LP-CORE: ese bloque se genera con `ensamblar.py`.

#### Tarea 2: Registrar la sección y renumerar la barra — **HECHA el 2026-09-07**

**Descripción.** Añadir la entrada al array `curriculum` (líneas 2903–2913) entre `modulo-1` y
`modulo-2`, y renumerar a mano los títulos de las lecciones siguientes, que llevan el número
dentro del string («4. Routing básico…» pasa a ser la 5, y así hasta la 11). Elegir un icono
que exista en el paquete: `renderIcon` devuelve `null` en silencio si el nombre no está, así
que un icono inventado no da error, simplemente no se ve.

**Criterios de aceptación:**
- [ ] La barra lateral muestra 11 lecciones numeradas del 1 al 11, sin saltos ni repetidos
- [ ] El icono de la sección nueva se pinta (no hueco en blanco)
- [ ] `storageKey` cambia a `usta_2026i_apis_cap05_v2` (ver R1)

**Verificación:**
- [ ] Abrir el archivo en el navegador: la lección nueva aparece en el menú y navega
- [ ] Consola del navegador sin errores de Babel
- [ ] «Anterior / Siguiente» recorre las 11 sin salto

**Dependencias:** T1
**Archivos:** `5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`
**Alcance:** S (1 archivo: el array, la clave de reanudación, 12 encabezados y 1 remisión)

**Lo que se cambió, además del array:**
- Icono `FileCode` (el `Terminal` que se pensó en T1 no existe en LP-CORE).
- `storageKey` → `usta_2026i_apis_cap05_v2`.
- Los encabezados de contenido bajan un número: Routing 2.x→3.x, Frameworks 3.x→4.x,
  Asincronía 4.x→5.x. La sección nueva ocupa el hueco de 2.x.
- La remisión de la tabla de apertura, «Flask frente a los frameworks modernos (sección 3)»,
  pasa a «(sección 4)». Era la única de todo el módulo que apuntaba a una sección renumerada.

### Punto de control A — la página se levanta · **PASADO el 2026-09-07**

- [x] El módulo 5 abre en el navegador sin pantalla en blanco
- [x] La sección nueva renderiza completa, con sus bloques de código y sus tablas
- [x] Consola limpia — tras recorrer las once lecciones, cero errores
- [x] La barra lista 11 lecciones numeradas del 1 al 11, sin saltos ni repetidos, **todas con icono**
- [x] La numeración del contenido corre 1.1–1.4 · 2.1–2.4 · 3.1–3.4 · 4.1–4.3 · 5.1–5.5
- [x] A 375 px el cuerpo no desborda: las dos tablas anchas se desplazan dentro de su caja
- [ ] **Revisión del docente antes de seguir**

### Fase 2 — Coherencia y práctica

#### Tarea 3: Coser la sección nueva con el resto del módulo — **HECHA el 2026-09-07**

**Descripción.** Cuatro retoques que hacen que el módulo deje de contradecirse:

1. **Títulos de los bloques.** `routing.py` (2394, 2419) pasa a `main.py`: son aplicaciones
   completas y ejecutables, y el título debe ser el nombre que el comando espera. En la
   sección 3, `app_flask.py` y `app_fastapi.py` se quedan —ahí el contraste exige dos
   archivos— pero cada uno gana en comentario su línea de arranque (`# uvicorn app_fastapi:app --reload`,
   `# flask --app app_flask run`).
2. **Sección 1.3.** Hoy muestra `app.main:app` cien líneas antes de que exista la explicación.
   Añadir la remisión a la sección nueva, o simplificar el bloque de desarrollo a
   `uvicorn main:app --reload` dejando `app.main:app` sólo en la línea de producción.
3. **Tabla de apertura (2180).** «Levantar un servidor mínimo con uvicorn --reload» pasa a
   citar la sección nueva por su nombre.
4. **Errores comunes (2748).** Añadir «Ejecutar `python main.py` esperando que arranque el
   servidor» — el tropiezo de D4, en la lista donde el estudiante lo va a buscar.

**Criterios de aceptación:**
- [ ] Ningún bloque de código ejecutable tiene un título que el comando no pueda encontrar
- [ ] La primera aparición de `app.main:app` está explicada o remitida
- [ ] La tabla de la sesión y la barra lateral nombran la misma sección

**Verificación:**
- [ ] Búsqueda de `routing.py` en el archivo: cero apariciones
- [ ] Leer en el DOM las secciones 1.3, apertura y cierre: la remisión existe y el nombre coincide

**Dependencias:** T2
**Archivos:** `5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`
**Alcance:** S (1 archivo, 5 puntos)

**Cómo quedó cada punto:**
1. `routing.py` desaparece del archivo: los dos bloques pasan a `main.py` —son alternativas,
   se escribe una **o** la otra en ese archivo— y cada uno estrena una primera línea que dice
   con qué comando se levanta. `app_flask.py` y `app_fastapi.py` se quedan con su nombre y
   ganan la misma línea. Como los cuatro bloques nacen plegados (más de doce líneas), esa
   primera línea es justo la que queda a la vista sin desplegar.
2. En 1.3 no se tocó el bloque ya revisado: se añadió un párrafo que reconoce el galimatías
   de `app.main:app`, remite a 2.2 y deja claro que allí se levanta el primer servicio.
3. La fila de práctica de la tabla de apertura cita ahora «(sección 2)».
4. «Ejecutar `python main.py` esperando que arranque el servidor» encabeza los errores comunes.

**Verificado ejecutando, no leyendo:**
- Los nueve bloques de Python del módulo compilan (`ast.parse`).
- Los dos bloques de routing, guardados como `main.py`, arrancan **con el comando que ellos
  mismos anuncian** —`uvicorn main:app --reload` y `flask --app main run`, este último contra
  Flask 3.1.3 en un entorno aparte— y responden 200 en `/health` y en `/filter`.
- Los cinco cambios se leyeron en el DOM, recorriendo las lecciones 1, 3, 5, 6 y 9. Consola limpia.
- **La semilla del taller del corte I arranca con el comando que ahora enseña 2.2**:
  `uvicorn main:app --reload` en `taller_corte1/semilla/` responde 200 en `/ping`. Es el hueco
  H3 cerrado de punta a punta.

#### Tarea 4: Dos actividades sobre el arranque — **HECHA el 2026-09-07**

**Descripción.** La sección nueva es prosa y comandos; conviene que el estudiante haga algo.
Usar componentes que LP-CORE ya trae en el capítulo, sin código nuevo de librería:

- **`OrdenaPasos`** con la secuencia del primer arranque: crear el entorno → activarlo →
  `pip install fastapi uvicorn` → guardar `main.py` → `uvicorn main:app --reload` → abrir `/docs`.
- **`DetectaError`** con un `main.py` de seis líneas donde la variable se llama `api` y el
  comando dice `main:app`, para que el fallo se diagnostique en vez de memorizarse.

**Criterios de aceptación:**
- [ ] Las dos actividades cargan y responden a la interacción
- [ ] La explicación del `DetectaError` nombra el mensaje literal de uvicorn

**Verificación:**
- [ ] En el navegador: ordenar los pasos y comprobar que valida; marcar la línea del error y comprobar el diagnóstico

**Dependencias:** T2
**Archivos:** `5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`
**Alcance:** S (1 archivo, ~45 líneas)

**Cómo quedaron:**
- **`OrdenaPasos` al final de 2.3** — seis pasos de terminal con el orden *forzado*: nada se
  instala donde debe hasta que el entorno está activado, y nada responde en el 8000 hasta que
  hay alguien escuchando. El `main.py` ya escrito se da por supuesto en el enunciado, para que
  no haya ningún paso cuyo sitio sea discutible: `OrdenaPasos` califica por posición exacta.
- **`DetectaError` al final de 2.4** — un `main.py` válido que no arranca porque la variable se
  llama `api` y el comando dice `main:app`. El comando se declara intocable en el enunciado
  («es el que exige el taller»), y así la única respuesta defendible es la línea 5. La
  explicación enseña a distinguir los dos mensajes de la tabla de 2.4 — «no encontré el
  archivo» frente a «el archivo está, falta lo de dentro»— y el impacto dice por qué el curso
  arregla siempre la variable y no el comando.

**Resueltos los dos por el navegador**, no leídos: la secuencia responde «¡Secuencia correcta!»
con los seis pasos en su sitio, y el diagnóstico «¡Diagnóstico correcto!» con la línea 5 y el
tipo «Error de nombre». Consola limpia después de interactuar.

### Punto de control B — el módulo 5 está completo · **PASADO el 2026-09-07**

- [x] Los nueve bloques de Python del módulo 5 compilan (`ast.parse` sobre lo que publica el HTML)
- [x] Las once secciones se recorren en el navegador con la consola limpia
- [x] Un estudiante que lea sólo la sección nueva puede levantar la semilla del taller —
      comprobado ejecutándola
- [ ] **Revisión del docente**

**Hallazgo sobre el instrumental, que afecta a este punto de control.**
`verificar_codigo.py` **no ve los módulos migrados**. `extraer_codigo.py` sólo entiende los
bloques `<pre>` del formato heredado, así que de los trece módulos extrae **7 bloques, todos
del módulo 6, y cero del módulo 5**. El plan daba por hecho que ese guion era la red de
seguridad y no lo es: la verificación de sintaxis real es el barrido con `ast.parse` sobre los
`CodeBlock` del archivo, que es lo que se hizo. Enseñar al extractor a leer `CodeBlock` es
trabajo aparte y no de este plan.

De paso, los 7 bloques que sí ve —los del módulo 6— **fallan los 7** con errores de sangría
(`unexpected indent`). Es preexistente, es el problema de sangría conocido del módulo 6, y no
lo ha causado nada de este plan. Queda por comprobar si el estudiante los ve mal sangrados en
pantalla o si es un artefacto del extractor; el sitio natural para mirarlo es T5, que ya abre
ese archivo.

### Fase 3 — El módulo 6

#### Tarea 5: Reducir la guía del módulo 6 a un recordatorio — **HECHA el 2026-09-09**

**Descripción.** Las líneas 2409–2503 de `6_Python_para_APIS_IA_Fast_API.html` repiten el
procedimiento completo. Se sustituyen por un recordatorio de tres o cuatro líneas que remita a
la semana 5, conservando lo que sí es propio del módulo 6: el consejo de reemplazar el
contenido de `main.py` para cada ejemplo, y las URL específicas (`/bernoulli`).

**Criterios de aceptación:**
- [ ] El módulo 6 ya no enseña el procedimiento, lo recuerda y remite
- [ ] Sigue siendo utilizable por alguien que abra el módulo 6 suelto (el comando aparece, aunque sin los cinco pasos)
- [ ] No se toca nada más de ese archivo

**Verificación:**
- [ ] El módulo 6 abre en el navegador sin pantalla en blanco y sin errores de consola
- [ ] `git diff --stat` sobre el módulo 6 muestra un solo tramo de cambios

**Dependencias:** T1 (para fijar el texto de la remisión)
**Archivos:** `6_Python_para_APIS_IA_Fast_API.html`
**Alcance:** S (1 archivo: 94 líneas sustituidas por 21 — +13 −86 en el diff)

**Cómo quedó.** Los cinco pasos se van; queda un recordatorio que remite a **dos** sitios, no
a uno: el arranque a la semana 5, y el entorno virtual a la **semana 1**, que es el módulo de
entornos y ya enseña `venv` con la activación de Windows y la de Mac/Linux. Se conservan el
`pip install` y el `uvicorn main:app --reload` —para que el módulo 6 siga sirviendo a quien lo
abra suelto—, las tres direcciones propias del módulo (`/`, `/docs`, `/bernoulli`), el `Ctrl +
C` y el consejo de reemplazar el contenido de `main.py` en cada ejemplo.

Edición manual, sin `montar.py`. Un solo tramo de cambios en el archivo, líneas 2408–2504.

**Verificado:** el módulo 6 abre con sus ocho lecciones y la consola limpia; el recordatorio se
leyó renderizado; no queda ningún «Paso N —» ni ningún paseo por `venv` en esa lección.

**Descartada una preocupación por el camino:** parecía que borrar el paso 1 dejaría al curso
sin la activación de Windows, porque `venv\Scripts\activate` sólo salía en el módulo 6. Es
falso: el módulo 1 la tiene, con las dos plataformas, y es su sitio. No se duplicó nada.

### Fase 4: Que el trabajo sobreviva a un remontaje

#### Tarea 6: Llevar la sección a la receta y a los componentes

**Descripción.** Todo lo hecho en T1–T4 vive **sólo en el archivo publicado**, y `montar.py`
regenera ese archivo entero desde `heredado/` y `recetas/modulo_5.json`. Hoy, un remontaje del
módulo 5 borra la sección nueva, los dos ejercicios y los cinco retoques de T3.

No es una hipótesis: los dos arreglos recientes del material lo hicieron de las dos maneras, y
sólo una sobrevive.

| Commit | Qué tocó | ¿Sobrevive a un remontaje? |
|---|---|---|
| `60a7caa` fix(modulo-4) | el publicado **+** `heredado/` + `recetas/modulo_4.json` + `componentes/modulo_4.jsx` | **Sí** |
| `c2bf2cb` fix(modulo-5) | sólo el publicado | No |
| T1–T4 de este plan | sólo el publicado | No |

El mecanismo duradero ya existe y está probado en el módulo 4: la receta admite una clave
`componentes` que apunta a un `.jsx` escrito a mano y versionado, y su lista `secciones`
—con `id`, `componente`, `titulo`, `icono`— es la que genera el `curriculum`.

**Qué habría que hacer:**
1. Mover `ArrancarSection`, con sus dos ejercicios, a `scripts/migracion/componentes/modulo_5.jsx`.
2. Añadir a `recetas/modulo_5.json` la clave `"componentes"`, la entrada de la sección nueva en
   `secciones` (cuarta, icono `FileCode`) y la renumeración de los `titulo` siguientes.
3. Cambiar `config.storageKey` a `usta_2026i_apis_cap05_v2` en la receta.
4. Llevar los cinco retoques de T3 —que son contenido de sección— a
   `heredado/5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html`.
5. Montar a un destino temporal y comparar con el publicado antes de sustituir nada.

**Criterios de aceptación:**
- [ ] Montar la receta a un temporal produce un archivo equivalente al publicado hoy
- [ ] El diff contra el publicado no pierde ni la sección, ni los ejercicios, ni los retoques de T3

**Verificación:**
- [ ] `diff -w` entre el montado temporal y el publicado, revisado línea a línea
- [ ] El temporal se abre en el navegador con las once lecciones y la consola limpia

**Dependencias:** T1–T4
**Archivos:** `scripts/migracion/componentes/modulo_5.jsx` (nuevo), `scripts/migracion/recetas/modulo_5.json`, `heredado/5_…html`
**Alcance:** M

**Decisión pendiente del docente:** T6 puede hacerse ahora o no hacerse nunca. No hacerla es
defendible —el módulo 5 lleva desde el 19 de agosto con un arreglo que tampoco sobrevive, y
nadie ha remontado— pero entonces conviene que el comentario que ya lleva el archivo sea la
única advertencia, y asumir que remontar el 5 significa rehacer esto a mano.

### Punto de control C — cierre · **PASADO el 2026-09-09**

- [x] Los dos módulos abren y navegan sin errores, con la consola limpia
- [x] El procedimiento de arranque está escrito una sola vez, en el módulo 5
- [x] T1–T4 confirmadas en un commit; T5 pendiente de confirmar

---

## 3 bis. Lo que T5 dejó confirmado y sin arreglar

El plan pedía comprobar si los bloques que `verificar_codigo.py` marca rotos en el módulo 6 son
un defecto real o un artefacto del extractor. **Son un defecto real, y el estudiante lo ve.**

Nueve bloques del módulo 6 —los de formato heredado, `<pre><code>{`…`}</code></pre>`, no los
`CodeBlock` de LP-CORE— se publican con **16 espacios de más en todas las líneas menos la
primera**. Medido en el DOM, no en el archivo: en la lección 2, bajo un `from flask import …`
a ras de margen, la línea siguiente se pinta como `                app = Flask(__name__)`. Lo
que el estudiante copia con el botón «Copiar» no corre: da `IndentationError`.

Es el defecto que `indentar_jsx` arregló en `montar.py` y que el módulo 6 nunca recibió, porque
nunca se remontó. Los `CodeBlock` del mismo módulo están bien (sangría extra 0), así que el
defecto es exactamente de los bloques heredados.

**No se arregló aquí, a propósito.** Es ajeno a este plan, toca nueve bloques de cuatro
lecciones y tiene dos salidas —convertir esos `<pre>` a `CodeBlock`, o remontar el módulo con
el arreglo de sangría— que son decisiones de otro tamaño. Merece su propio plan.

---

## 4. Riesgos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R1 | `storageKey` guarda el **índice** de la lección. Al insertar una sección, quien iba por la 7 aterriza en otra | Medio | Cambiar la clave a `usta_2026i_apis_cap05_v2`: la reanudación vuelve a la primera lección en vez de a una equivocada |
| R2 | Babel compila en el navegador: un JSX mal cerrado deja la **página en blanco**, sin aviso en el archivo | Alto | Abrir la página tras cada tarea y leer la consola. Nunca dar por buena una edición sin verla renderizada |
| R3 | Los literales de plantilla se comen la barra invertida antes de llegar a la pantalla — es el bloqueante B1 documentado en `PLAN_MODULO_4_PYDANTIC.md`. Afecta a `venv\Scripts\activate` y a cualquier ruta de Windows | Alto | Doblar la barra (`venv\\Scripts\\activate`), como ya hace el módulo 6, y **verificar en el DOM**, no en el archivo |
| R4 | El módulo 6 tiene un problema de sangría conocido que impide remontarlo con `montar.py` | Alto | T5 es una **edición manual** del HTML. No ejecutar el remontaje sobre el módulo 6 |
| R6 | La sección **no existe en `heredado/`**: `montar.py` regenera todo lo que hay entre los centinelas, así que un remontaje del módulo 5 la borraría | Alto | Queda un comentario en el propio archivo avisándolo. Si hay que remontar, la sección se recupera del control de versiones |
| R5 | La renumeración de los títulos es manual y se hace en diez strings | Bajo | Comprobar la numeración leyendo la barra lateral renderizada, no el array |

---

## 5. Verificación final

- [ ] Cada tarea tiene sus criterios cumplidos
- [ ] La comprobación se hizo **contra la página**, no leyendo el código
- [ ] `python3 scripts/auditoria/verificar_codigo.py` sin regresiones
- [ ] El estudiante que termina el módulo 5 puede levantar la semilla del taller de corte I sin material adicional

---

## 6. Preguntas abiertas

Ninguna bloqueante. Dos que se resuelven al escribir y conviene revisar en el punto de
control A:

- El `main.py` de 4.2 lleva dos rutas (`/` y `/health`). Si se prefiere una sola, la que se
  queda es `/health`, porque es la que el módulo ya recomienda como buena práctica.
- La sección 1.3 puede quedarse como está (con una remisión) o simplificarse. La segunda
  opción es más limpia pero toca un bloque que ya estaba revisado.
