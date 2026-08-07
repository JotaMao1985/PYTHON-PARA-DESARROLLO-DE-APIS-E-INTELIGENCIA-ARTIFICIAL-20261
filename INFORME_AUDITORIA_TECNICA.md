# Informe de auditoría técnica — Fase 1

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-06
**Alcance:** los 13 módulos HTML.
**Corresponde a:** T1.1, T1.2 y T1.3 del `PLAN_AUDITORIA_MODULOS.md` · Checkpoint 1

> **Estado tras la revisión del docente (2026-08-06).** Se autorizó corregir de inmediato
> los seis defectos bloqueantes: **están aplicados y verificados en navegador** (§12).
> Los módulos 4, 7, 8 y 9 quedaron modificados, con respaldo `.bak`. El resto del informe
> describe el estado **antes** de esa corrección, para que quede constancia de qué había.
> También se cerró la limitación L2 (§11.1). Todo lo demás sigue sin tocar.

---

## 0. Lo que hay que mirar primero

Seis defectos hacen que el estudiante lea código que **no funciona**, y los seis están
en material que se dicta en la primera mitad del semestre.

| | Módulo | Qué pasa | Verificado |
|---|---|---|---|
| **B1** | 7 | El bloque rotulado «**IMPLEMENTACIÓN CORRECTA**» no compila: `IndentationError` | `ast.parse` + HTML crudo |
| **B2** | 7 | El bloque «CÓDIGO CON ERROR METODOLÓGICO» tiene, además del error que enseña, un error de sintaxis que no enseña nada | ídem |
| **B3** | 7 | La rama `else` del ejemplo de validación jerárquica está sin indentar | ídem |
| **B4** | 4 | `print("` aparece partido en dos líneas: un `\n` que el autor escribió para Python se lo comió JavaScript | **navegador** |
| **B5** | 9 | Cuatro ejemplos muestran `[email protected]` donde debería ir un correo | **navegador** |
| **B6** | 8 | La cadena de conexión del ejemplo se muestra como `postgresql://admin:[email protected]:5432/…` — y es justo el ejemplo del antipatrón de credencial embebida | **navegador** |

Los seis son mecánicos de arreglar y los seis están fuera del alcance de cualquier
revisión que no ejecute el código. Es exactamente lo que el criterio C7 predecía.
**Los seis están ya corregidos y verificados** (§12); esta sección deja constancia de qué
había.

**Buena noticia, y no es menor:** de las salidas que el material declara, **3 de 3
coinciden** con lo que el código imprime de verdad. No hay ningún `#> 600000` como el
que apareció en el material de Lógica de Programación.

---

## 1. Qué se hizo, y qué no

Cuatro barridos, tres automáticos y uno en navegador. Todo reproducible:

```bash
python3 scripts/auditoria/inventario.py        # T1.1a  inventario técnico
python3 scripts/auditoria/enlaces.py           # T1.1b  enlaces vivos
python3 scripts/auditoria/extraer_codigo.py    # T1.2   extracción de bloques
python3 scripts/auditoria/verificar_codigo.py --ejecutar   # T1.2  sintaxis + ejecución
python3 scripts/auditoria/consistencia.py      # T1.3   mapa de menciones
```

Los datos crudos quedan en `scripts/auditoria/salida/*.json` (no versionados; se
regeneran con los comandos de arriba). El barrido de navegador está en
`salida/navegador.json`.

**Lo que este informe NO cubre**, y conviene tenerlo presente al leerlo:

- **L1 · Nada pedagógico.** Ni un juicio sobre si el contenido cubre el RA de su semana,
  si la apertura motiva o si las gráficas son honestas. Eso es la Fase 2.
- ~~**L2 · Sólo la vista inicial de cada módulo.**~~ **Cerrada** — ver §11.1. Se recorrieron
  todos los estados de los ocho módulos que ocultan contenido: el resultado no cambia.
- **L3 · Operabilidad por teclado y contraste no medidos.** El plan los pone bajo C5
  pero no en la lista de T1.1; quedan para la Fase 2 o para un barrido propio.
- **L4 · Cuatro enlaces sin veredicto.** Medium y sus publicaciones devuelven 403 a
  cualquier cliente que no sea un navegador con sesión. No están muertos ni vivos:
  están sin comprobar (§4).

---

## 2. Inventario técnico (T1.1)

| # | KB | Semana declarada | Render | Fórmulas | Gráficas | Font Awesome | Meta |
|---|---|---|---|---|---|---|---|
| 1 | 80 | ❌ Clase II | HTML plano | — | Chart.js 3.9.1 | 6.0.0 | D A · |
| 2 | 103 | ✅ Semana II | HTML plano | — | Chart.js 3.9.1 | 6.0.0 | D A · |
| 3 | 81 | ⚠️ sin semana | React **dev** + Babel | — | — | 6.0.0 | · · · |
| 4 | 72 | ⚠️ sin semana | React **dev** + Babel | — | — | 6.0.0 | D A · |
| 5 | 141 | ⚠️ sin semana | HTML plano | — | — | 6.0.0 | D A · |
| 6 | 180 | ⚠️ sin semana | React **dev** + Babel | — | — | 6.0.0 | D · · |
| 7 | **714** | ⚠️ sin semana | HTML plano | KaTeX 0.16.8 | — | 6.0.0 | D A · |
| 8 | 163 | ⚠️ sin semana | HTML plano | KaTeX 0.16.8 *(0 fórmulas)* | — | 6.0.0 | D A · |
| 9 | 219 | ⚠️ sin semana | HTML plano | — | — | 6.0.0 | D A · |
| 10 | 148 | ✅ Semana 10 | HTML plano | — | Plotly 3.5.0 | — | D · · |
| 11 | 149 | ✅ Semana XI | HTML plano | — | Plotly 3.5.0 | — | D · · |
| 12 | 159 | ❌ Semana V | HTML plano | — | Plotly 3.5.0 | 6.0.0 | D · · |
| 13 | 130 | ❌ Semana VI | React **dev** + Babel | — | Plotly 3.5.0 | 6.0.0 | D · · |

*Meta: **D**escripción · **A**utor · **O**pen Graph. Un punto es que falta.*
*Referencia: el syllabus (módulo 0) usa React 18 **producción** + Babel 7.26.4 pineado,
MathJax 3, Plotly 2.35.2, Prism 1.29.0 y Font Awesome 6.5.2.*

### 2.1 Numeración de semana — confirmado

Tres módulos declaran una semana que no es la suya (1, 12, 13) y siete no declaran
ninguna (3–9). Sólo tres están bien (2, 10, 11), y entre esos tres conviven arábigos
(«Semana 10») y romanos («Semana II», «Semana XI»).

### 2.2 React en modo desarrollo, y sin pinear — nuevo

Los módulos **3, 4, 6 y 13** cargan `react.development.js` + `react-dom.development.js`
y `@babel/standalone` **sin número de versión**. Tres consecuencias:

1. La consola del estudiante muestra dos avisos en cada carga («in-browser Babel
   transformer», «Download the React DevTools»).
2. El build de desarrollo es varias veces más pesado y más lento que el de producción.
3. `@babel/standalone` sin pinear significa que **el día que Babel publique una versión
   incompatible, los cuatro módulos dejan de renderizar sin que nadie toque nada.**
   El syllabus ya migrado lo tiene pineado a `7.26.4`; los módulos no.

### 2.3 Font Awesome 6.0.0 — hipótesis descartada

El plan (§0.2) advertía que los iconos posteriores a la versión 6.5 salen como huecos en
blanco. **Se comprobó y no ocurre.** De los **53 iconos distintos** que usan los once
módulos con FA 6.0.0, **los 53 existen** en el catálogo de 6.0.0 (2 138 iconos, leído del
propio CSS del CDN). Control negativo: `fa-bluesky`, `fa-square-x-twitter` y
`fa-arrow-turn-down-left` sí se reportan como ausentes, así que la comprobación funciona.

Subir a 6.5.2 sigue siendo deseable por homogeneidad con el syllabus, pero **no arregla
ningún defecto visible**: no es urgente.

### 2.4 Peso muerto

- Módulo **8**: carga los tres archivos de KaTeX (~280 KB) y renderiza **0 fórmulas**. No
  es que estén ocultas: los únicos `\(`, `$$` y `\[` del archivo están en la
  *configuración* de `renderMathInElement` (líneas 181–184). No hay una sola fórmula en
  todo el módulo.
- Módulos **5, 7, 8, 9**: cargan los 89 KB del CSS de Font Awesome para **1 o 2 iconos**.
- Módulo **7**: 714 KB, casi cinco veces el módulo medio. 7 026 nodos en el DOM inicial.

---

## 3. Barrido en navegador (T1.1c)

Servidos por HTTP en `localhost:8123`, viewport 375 × 812.

| # | Desborde a 375 px | Errores de consola | Observación |
|---|---|---|---|
| 1 | **+58 px**, 9 elementos | 0 | Indicador de pasos y caja «Tip Pedagógico» fija |
| 2 | **+12 px**, 3 elementos | 0 | Mismos dos culpables |
| 3–7 | 0 px | 0 | *(ver limitación L2)* |
| **8** | 0 px | **1 error** | 404 a `/cdn-cgi/scripts/…/email-decode.min.js` |
| **9** | 0 px | **2 errores** | mismo 404, dos veces |
| 10–13 | 0 px | 0 | 10 y 11 son los únicos con consola completamente limpia |

**Total de errores de consola en los 13 módulos: 3**, todos de la misma causa (§5.2).
El resto son avisos: `cdn.tailwindcss.com` en producción (módulos 1–9 y 13) y los dos de
React/Babel en los cuatro módulos de desarrollo (3, 4, 6, 13).

Los módulos **10, 11 y 12** no cargan Tailwind, ni React, ni Babel: son los únicos tres
que arrancan sin un solo mensaje en consola. Son también los que mejor puntúan en
consistencia (§6).

---

## 4. Enlaces (T1.1b)

**55 de 59 URL únicas responden 2xx/3xx.** Ningún enlace confirmadamente muerto.

Cuatro sin veredicto, todos de la familia Medium, que devuelve 403 a cualquier cliente
sin navegador (comprobado también con `curl` y user-agent de Chrome):

| Módulo | URL |
|---|---|
| 4 | `pub.towardsai.net/data-reliability-101-…` |
| 6 | `leapcell.medium.com/is-flask-dead-is-fastapi-the-future-…` |
| 6 | `saketgarodia.medium.com/from-zero-to-api-…` |
| 7 | `medium.com/data-policy/hierarchical-models-…` |

Hay que abrirlos a mano. Aviso aparte: **cuatro de las referencias bibliográficas del
curso están tras el muro de pago de Medium**, lo que es un problema de acceso para el
estudiante con independencia de si el enlace vive.

**Falsos positivos descartados** durante el barrido: `kaggle.com` y
`towardsdatascience.com` devuelven 404 a una petición `HEAD` y 200 a un `GET`; los
`<link rel="preconnect">` a `fonts.googleapis.com` y `fonts.gstatic.com` devuelven 404
en la raíz por diseño y no son enlaces navegables. El script ya los excluye.

### 4.1 Enlaces internos

Dos módulos (**8** y **9**) contienen rutas a `/cdn-cgi/…` que no existen. No son enlaces
que alguien escribiera: son residuo de Cloudflare (§5.2).

---

## 5. Código: extracción, sintaxis y ejecución (T1.2 · criterio C7)

### 5.1 Qué se extrajo

**210 bloques** de código en los 13 módulos, de las tres formas en que el material los
guarda: `<pre>` con resaltado (7 módulos), plantillas de JavaScript `pythonCode:` /
`const xCode =` (módulos 1, 2, 3, 4, 6, 13) y objetos de datos `snippet:`.

| Lenguaje | Bloques |
|---|---|
| Python | **111** |
| bash | 31 |
| Dockerfile | 22 |
| sólo comentarios | 20 |
| otros (YAML, SQL, diagramas en `<pre>`) | 26 |

Cobertura de los 111 bloques de Python:

| | Bloques | |
|---|---|---|
| Compilan | **107** | |
| **No compilan** | **4** | § 5.3 — son defectos reales |
| Ejecutados de verdad | **30** | 26 terminan con código 0 |
| Con salida declarada y comparada | **3** | **3 de 3 coinciden** |
| No auditables, y por qué | 77 | ver abajo |

Los 77 no auditables, **declarados, no dados por buenos**: 33 importan dependencias que
no están en el entorno (`app`, `pytest`, `flask`, `config`, `database`…), 27 no imprimen
nada que comparar, 14 definen *endpoints* y exigen un cliente de pruebas, 1 hace
peticiones de red, 1 espera entrada por teclado y 1 necesita un broker de mensajes.

Los 4 fallos de ejecución que no son defectos: dos bloques del módulo 7 continúan a un
bloque anterior del mismo módulo (`np` y `datos_demograficos_simulados` **sí** están
definidos antes), y dos del módulo 13 leen el `artifacts/model.joblib` que produce el
bloque de entrenamiento anterior. Legítimo, aunque el material no avisa de la dependencia.

### 5.2 Residuo de Cloudflare — módulos 8 y 9 (B5, B6)

Los módulos 8 y 9 se guardaron desde una página servida por Cloudflare, que reescribe
**cualquier** cadena con `@` para ocultar correos. El resultado: los literales de los
ejemplos quedaron destruidos y el script que los descifraba apunta a una ruta que en
local da 404.

Lo que el estudiante ve en pantalla, verificado en el navegador:

| Módulo | Debería decir | Dice |
|---|---|---|
| 8 | `postgresql://admin:SuperSecreto123@192.168.1.50:5432/encuestas_db` | `postgresql://admin:[email protected]:5432/encuestas_db` |
| 9 | `email="ada@mail.com"` (×2), `"ada@example.com"`, `"grace@example.com"` | `[email protected]` (×4) |

El caso del módulo 8 es el peor de los seis bloqueantes: el ejemplo existe **para
enseñar por qué no se embeben credenciales**, y la credencial es lo único que no se ve.

Los valores originales son recuperables (van cifrados en el atributo `data-cfemail`), así
que la corrección es mecánica. `scripts/auditoria/inventario.py` ya los descifra e imprime.

### 5.3 Los cuatro bloques que no compilan

Los cuatro se verificaron a mano contra el HTML crudo: **no son artefactos del extractor.**

**B1 · Módulo 7, `id="code-block-8"`, línea 3273** — rotulado «IMPLEMENTACIÓN CORRECTA»:

```python
# IMPLEMENTACIÓN CORRECTA
@field_validator('edad')
@classmethod
    def validar_edad(cls, v: int) -> int:     # ← IndentationError: unexpected indent
```

**B2 · Módulo 7, `id="code-block-7"`, línea 3226** — rotulado «CÓDIGO CON ERROR
METODOLÓGICO». El error que se quiere enseñar es el `abs(v)` que corrige en silencio;
el que hay además no enseña nada:

```python
def validar_edad(cls, v: int) -> int:
    # "Corregir" edades negativas aplicando valor absoluto
if v < 0:                    # ← IndentationError: expected an indented block
        return abs(v)
return v
```

**B3 · Módulo 7, línea 5168** (bloque de validación jerárquica, 139 líneas). En la línea
5304 del archivo, la rama `else` queda sin cuerpo indentado:

```python
    else:
print(f"   ❌ RECHAZADA")     # ← columna 0
```

**B4 · Módulo 4, línea 694** (lección «El Poder de "Field"»). En el archivo está escrito
correctamente:

```javascript
pythonCode: `
...
print("\n=== Ejemplo 2: Error de validación ===")
```

Pero eso es una **plantilla de JavaScript de varias líneas**: el `\n` lo resuelve el motor
de JS antes de que Python lo vea. Comprobado en el navegador, el estudiante lee:

```python
# 2. Error: desviación negativa
print("
=== Ejemplo 2: Error de validación ===")
```

> **Ojo con la corrección:** en el módulo **3** hay 25 `\n` dentro de una plantilla
> `pythonCode` y **están bien**, porque allí todo el bloque va en una sola línea física y
> el `\n` es el separador. La regla es: `\n` dentro de una plantilla de varias líneas es un
> error; dentro de una de una sola línea es lo correcto. No se pueden reemplazar a ciegas.

---

## 6. Consistencia transversal (T1.3 · criterio C6)

`python3 scripts/auditoria/consistencia.py` produce el mapa completo; lo que importa:

### 6.1 Python 3.11.9 — confirmado

Los módulos **3, 4, 5, 6, 7, 8 y 9 no mencionan `3.11.9` ni una vez**, siendo la versión
que el syllabus y el proyecto integrador fijan como obligatoria. Los módulos 10–13 sí lo
hacen, y con insistencia (el 11, 48 veces). El módulo 1 llega a mencionar 3.12, 3.10 y 3.9;
el 9 menciona 3.9 seis veces.

### 6.2 Railway frente a Render — **la premisa del plan era incorrecta**

El plan afirmaba «Railway 48 veces y Render 4». El conteo real en el módulo 12, con
frontera de palabra e ignorando mayúsculas:

| | Railway | Render |
|---|---|---|
| Total | **46** | **40** |
| En prosa (fuera del JSON de las gráficas) | 42 | 35 |
| Configuración concreta | `railway.json` 0 · `railway.app` 2 · `nixpacks` 2 | `render.yaml` 3 · `render.com` 2 |

El módulo **no enseña la plataforma equivocada**: enseña las dos en paralelo, y una de sus
gráficas es literalmente «Railway vs. Render: capacidades comparadas». El defecto real es
otro y es más leve: **el módulo compara dos plataformas donde el proyecto exige una**, lo
que gasta tiempo de clase y deja al estudiante sin saber cuál va a evaluarse. Es una
decisión pedagógica (Fase 2), no una corrección mecánica.

### 6.3 Flask en el módulo 5 — hallazgo nuevo, y probablemente el más importante de §6

| | FastAPI | Flask | Django |
|---|---|---|---|
| Módulo 5 | 46 | **48** | 0 |
| Módulo 6 | 102 | 58 | 11 |

En el módulo 6 las menciones a Flask son comparativas y están bien («Flask y Django
encapsulan…», «¿Flask está muerto?»). **En el módulo 5 no.** El módulo construye sobre
Flask: explica Werkzeug y Jinja2 como «las dos bibliotecas fundamentales» sobre las que se
trabaja, usa `app = Flask(...)` y `@app.route` (3 y 7 veces), habla del servidor de
desarrollo de Flask y **hasta la autoevaluación pregunta por él** («¿Por qué el servidor
de desarrollo de Flask…?»).

Un módulo titulado «Del Modelo Estadístico al Servicio Web» que enseña Flask, en un curso
cuyo proyecto se evalúa en FastAPI. Esto no se arregla cambiando una palabra: hay que
decidir en Fase 2 si el módulo se reorienta o si se declara explícitamente como una
comparativa histórica.

### 6.4 Otros

- **Pydantic**: v2 en todo el material que lo usa (`field_validator` en 7 módulos,
  `model_dump()` donde toca). **Cero** idiomas de v1 (`@validator`, `.dict()`, `parse_obj`).
  Esto está limpio.
- **FastAPI**: el módulo 13 usa `lifespan` 28 veces y `@app.on_event` 2. Se comprobó el
  contexto de las dos (línea 1204): son el contraste deliberado con la API obsoleta
  («Hasta hace pocas versiones, FastAPI usaba los decoradores…»). **Correcto, no es un
  hallazgo.**
- **«2025»** aparece en los módulos 6 (3 veces) y 7 (5 veces).
- **«2026-II»** sólo aparece en el syllabus. Ningún módulo declara el periodo.
- **Montserrat y la referencia a USTA** están en los 13 módulos. La identidad visual, dentro
  de lo desigual del stack, es lo más consistente que hay.

---

## 7. Tres premisas del plan que hay que corregir

Este barrido contradice al `PLAN_AUDITORIA_MODULOS.md` en tres puntos. Conviene anotarlo
antes de que las cifras se repitan en la Fase 3:

1. **Font Awesome 6.0.0 no está rompiendo ningún icono** (§2.3). Sube a 6.5.2 por
   coherencia, no por urgencia.
2. **El módulo 12 no es «Railway 48 / Render 4»**, es 46/40 y comparativo (§6.2). El
   problema existe pero es de pertinencia, no de plataforma equivocada.
3. **Los módulos 10, 11 y 12 no usan MathJax.** El plan los listaba así; la única mención
   es `window.PlotlyConfig = {MathJaxConfig: 'local'}`, que es configuración de Plotly. Los
   únicos módulos con fórmulas son el 7 y el 8, ambos con KaTeX. El «dos motores de
   fórmulas conviviendo» se reduce a **uno**, KaTeX, frente al MathJax del syllabus.

En cambio, **sí se confirma**: la numeración de semana rota, los cuatro stacks de render,
los tamaños dispares y la ausencia de Python 3.11.9 en los módulos 3–9.

---

## 8. Todos los hallazgos, por gravedad

### Bloqueantes — el estudiante lee o copia algo que no funciona · **los 6 corregidos, §12**

| ID | Módulo | Hallazgo | Corrección |
|---|---|---|---|
| B1 | 7 | «IMPLEMENTACIÓN CORRECTA» no compila (L3273) | Indentar el `def` |
| B2 | 7 | Error de sintaxis no intencionado en el ejemplo del error metodológico (L3226) | Indentar `if` y `return` |
| B3 | 7 | Rama `else` sin indentar (L5304) | Indentar el `print` |
| B4 | 4 | `print("` partido por un `\n` de JS (L780) | Escapar a `\\n` |
| B5 | 9 | 4 literales de correo → `[email protected]` | Restituir y borrar el `<script>` de Cloudflare |
| B6 | 8 | Cadena de conexión con credencial → `[email protected]` | ídem |

### Importantes — contradicen al syllabus o degradan la experiencia

| ID | Módulo | Hallazgo |
|---|---|---|
| I1 | 1, 12, 13 | El `<title>` declara una semana que no es la suya |
| I2 | 3–9 | Ningún `<title>` declara semana |
| I3 | 8, 9 | 3 peticiones 404 en consola (`/cdn-cgi/…`) — **corregido junto con B5/B6** |
| I4 | 1 | Desborda 58 px a 375 px (9 elementos) |
| I5 | 2 | Desborda 12 px a 375 px |
| I6 | 3, 4, 6, 13 | React en build de **desarrollo** y `@babel/standalone` **sin pinear** |
| I7 | 3–9 | Python 3.11.9 no se menciona nunca |
| I8 | 5 | Enseña Flask donde el proyecto exige FastAPI (§6.3) — **requiere decisión pedagógica** |
| I9 | 12 | Enseña Railway y Render en paralelo (§6.2) — **requiere decisión pedagógica** |
| I10 | 3 | Sin `<meta description>`, sin autor, sin Open Graph |
| I11 | 4, 6, 7 | 4 referencias bibliográficas tras el muro de pago de Medium |

### Cosméticos

| ID | Módulo | Hallazgo |
|---|---|---|
| C1 | 7 | El comentario dice «MathJax for LaTeX Rendering» sobre una carga de KaTeX |
| C2 | 8 | Carga los 3 archivos de KaTeX y renderiza 0 fórmulas |
| C3 | 5, 7, 8, 9 | 89 KB de Font Awesome para 1 o 2 iconos |
| C4 | 10–13 | Plotly 3.5.0 frente al 2.35.2 del syllabus |
| C5 | 6, 7 | Referencias a «2025» |
| C6 | todos | Ningún módulo declara el periodo 2026-II |
| C7 | 7, 13 | Bloques que continúan a otro sin decirlo |
| C8 | 2, 10, 11 | Semana correcta pero en tres notaciones (arábigo / romano) |
| C9 | 11 módulos | Font Awesome 6.0.0 frente al 6.5.2 del syllabus (sin efecto visible) |

**Total: 6 bloqueantes, 11 importantes, 9 cosméticos.**

---

## 9. Auto-auditoría de este informe

Dónde puede estar equivocado, y qué se hizo para reducirlo.

**Falsos positivos que se cazaron y eliminaron antes de publicar.** El extractor produjo
en su primera versión 14 errores de sintaxis; **10 eran míos, no del material**:

- 9 bloques del módulo 6 arrastraban el envoltorio JSX `{\`…\`}` como si fuera código.
- 1 bloque del módulo 7 era una caja de maquetación (un diagrama dentro de un `<pre>`)
  clasificada como Python.

Los 4 que quedan se verificaron **uno a uno contra el HTML crudo**, y el del módulo 4
además en el navegador. También se descartaron: dos «enlaces rotos» que sólo fallaban
ante `HEAD`, cuatro «404» que eran `preconnect`, y un «`np` no definido» del módulo 7 que
resultó estar importado en el bloque inmediatamente anterior — mi primer `grep` no lo vio
porque el `import` va partido por etiquetas `<span>` de resaltado.

**Errores en el borrador de este mismo informe, corregidos antes de entregarlo.** Al
verificar una a una las afirmaciones que había escrito de memoria aparecieron tres:

- Decía que Tailwind lo cargaban 11 módulos: son **10** (1–9 y 13).
- Decía que 10 y 11 eran los únicos con consola limpia: son **tres**, 10, 11 y **12**.
- Dejaba en duda el `@app.on_event` del módulo 13. Comprobado el contexto: es deliberado
  y está bien redactado. Lo he sacado de la lista de hallazgos.

**Comprobación de que el detector de iconos funciona.** El resultado «0 iconos rotos» es
sospechosamente limpio, así que se pasó un control negativo: tres iconos que Font Awesome
introdujo después de la 6.0 (`fa-bluesky`, `fa-square-x-twitter`,
`fa-arrow-turn-down-left`) se reportan correctamente como ausentes del catálogo. El
detector distingue; los 53 iconos del material simplemente existen todos.

**Lo que sigue siendo débil, y hay que decirlo:**

| Riesgo | Efecto |
|---|---|
| ~~Sólo se midió la vista inicial (L2)~~ | **Cerrado** en §11.1 |
| **El entorno de ejecución es el `base` de mambaforge con Python 3.10.14** | El material fija 3.11.9. Un bloque que aquí corre podría fallar en 3.11, y al revés. Los 30 bloques ejecutados no usan nada sensible a la versión, pero no está verificado en 3.11.9 |
| **La detección de «salida declarada» es de patrón** | Busca `# Output`, `#>`, `>>>` y similares. Si el material declara resultados en prosa o en una caja aparte del bloque, no se detectan. Sólo 3 bloques resultaron comparables: es poco, y parte de ese poco puede ser ceguera del detector |
| **Los 26 bloques «otros»** | Diagramas, texto de consola y fragmentos sueltos. No se auditaron |
| **Atribución de avisos de consola** | Los mensajes se acumulan entre navegaciones. Los **errores** (3) sí están atribuidos con certeza porque coinciden con los 404 estáticos; los avisos se atribuyeron por el stack de cada módulo, no por observación aislada |

**Consecuencia práctica:** el número «6 bloqueantes» es un **suelo, no un techo**. Lo que
está en la lista está verificado; lo que no está puede seguir ahí.

---

## 10. Decisiones tomadas y lo que sigue abierto

**Decidido el 2026-08-06:**

1. **Corregir ya los 6 bloqueantes.** Hecho y verificado — §12.
2. **Módulo 5: reorientar a FastAPI.** Es trabajo de Fase 3 y no es pequeño; el alcance
   está estimado en §12.2.
3. **Cerrar la limitación L2 antes de la Fase 2.** Hecho — §11.1.

4. **Módulo 12: podar Railway y dejar Render.** Trabajo de Fase 3. *(Leo así el «sí» a la
   pregunta; si la intención era conservar la comparación declarando cuál se evalúa,
   corrígeme antes de que toque el módulo 12 — no está hecho.)*
5. **El orden lo manda el cronograma**, no la gravedad: lo que se dicta antes se arregla
   antes. Aplica a las Fases 2 y 3.

6. **No hay módulos intocables.** Los 13 entran en la Fase 2.
7. **La sesión de 4 h se reparte en 60 min de teoría + 180 min de práctica guiada.**
   Coincide con lo que el syllabus ya declara (`CONFIG.minutosTeoria: 60`,
   `CONFIG.minutosPractica: 180`, línea 1911): **no hay que tocar el syllabus**. Lo que sí
   cambia es la Fase 2 — ver §10.2.

**Con esto no queda ninguna pregunta abierta**, salvo confirmar la lectura del punto 4.

### 10.1 Orden de trabajo que se deriva del cronograma

Con el criterio «cronograma, no gravedad», la Fase 2 audita en el orden 1 → 13, y la
Fase 3 corrige en ese mismo orden. Dos consecuencias que conviene ver ahora:

- Los **módulos 1 y 2** pasan al frente de la cola: son los únicos con desborde real a
  375 px (58 y 12 px) y se dictan las dos primeras semanas.
- El **módulo 5** (reorientación a FastAPI, §12.2) es el trabajo más pesado y le toca
  pronto. Su ficha de Fase 2 debería redactarse cuanto antes para no reescribirlo dos
  veces.

### 10.2 Lo que el reparto 60/180 añade a la Fase 2

Confirmado el reparto, cada ficha de módulo tiene que responder dos preguntas más, que
hasta ahora no estaban en los criterios C1–C4:

- **¿La teoría del módulo cabe en 60 minutos?** No es retórico. Los módulos pesan entre
  72 KB y **714 KB**: el 7 es diez veces el 4. Un módulo que necesita dos horas de
  exposición no se arregla puliéndolo, se parte o se reparte en trabajo autónomo.
- **¿El módulo aporta 180 minutos de práctica guiada?** Es el bloque grande de la sesión
  y es donde se preparan los criterios de rúbrica. Un módulo que sea todo exposición deja
  tres horas de clase sin material.

Esto convierte el desequilibrio de tamaños (§2.4) de una observación estética en un
criterio medible. La ficha de cada módulo debe estimar ambos tiempos y decir si cuadran.

---

## 11. Ampliaciones posteriores al informe inicial

### 11.1 Limitación L2 cerrada: desborde en todos los estados

Se recorrieron **todos** los estados de los ocho módulos que ocultan contenido, usando la
navegación de cada módulo (los botones «Siguiente» y de lección), y abriendo además todos
los `<details>`:

| Módulo | Mecanismo | Estados medidos | Desborde máximo |
|---|---|---|---|
| 3 | SPA React, botones de lección | 11 | **0 px** |
| 4 | SPA React, 9 lecciones | 12 | **0 px** |
| 5 | 8 secciones vía «Siguiente» | 9 | **0 px** |
| 6 | SPA React, botones de lección | 11 | **0 px** |
| 7 | 9 secciones vía «Siguiente» | 9 | **0 px** |
| 8 | 7 secciones + `<details>` abiertos | 8 | **0 px** |
| 9 | 11 secciones + `<details>` abiertos | 12 | **0 px** |
| 13 | SPA React, botones de lección | 8 | **0 px** |

**Conclusión: los únicos módulos que desbordan a 375 px siguen siendo el 1 (+58 px) y el
2 (+12 px).** El «0 px» de los demás ya es concluyente, no una limitación del método.

La rutina está en `scripts/auditoria/desborde_estados.js`, para volver a pasarla en el
Checkpoint 3.

> **Trampa que costó dos intentos y conviene no repetir.** El primer método revelaba las
> secciones ocultas forzando `style.display = 'block'`. Daba 231, 502, 436 y 163 px de
> desborde en cuatro secciones del módulo 7 — **todo falso**: saltarse la navegación del
> módulo produce un layout que ningún usuario ve. Recorriendo el botón «Siguiente», el
> desborde real de esas mismas cuatro secciones es 0. El aviso está escrito en la cabecera
> del script.

### 11.2 Mapa de secciones del módulo 5

Levantado al medir el desborde; sirve para dimensionar la reorientación a FastAPI:

| Sección | Título |
|---|---|
| `modulo-0` | Introducción: ¿Por qué necesitas saber esto? |
| `modulo-1` | Módulo 1: El Servidor Web y WSGI |
| `modulo-2` | Módulo 2: Routing Básico y Avanzado |
| `modulo-3` | Módulo 3: Flask vs Frameworks Modernos (FastAPI) |
| `modulo-4` | Módulo 4: Síncrono vs Asíncrono (Profundización) |
| `modulo-5` | Ejercicios de Autoevaluación |
| `modulo-6` | Resumen y Mejores Prácticas |
| `modulo-7` | Bibliografía y Fuentes Consultadas |

---

## 12. Correcciones aplicadas (2026-08-06)

Los seis bloqueantes, con respaldo `.bak` de cada archivo antes de tocarlo.

| ID | Archivo | Cambio |
|---|---|---|
| B1 | `7_…Data_Validation.html` | `code-block-8`: decoradores y cuerpo alineados a columna 0 |
| B2 | `7_…Data_Validation.html` | `code-block-7`: `if` y `return v` indentados 4 espacios |
| B3 | `7_…Data_Validation.html` | L5304: `print` de la rama `else` indentado 8 espacios |
| B4 | `4_…Pydantic.html` | L780, L791, L803: `\n` → `\\n` en la plantilla `pythonCode` |
| B5 | `9_…SQLAlchemy_BD.html` | 4 literales restituidos, 2 `<script>` muertos eliminados |
| B6 | `8_…DI_Configuracion.html` | 1 literal restituido, 1 `<script>` muerto eliminado |

B5 y B6 se aplicaron con `scripts/auditoria/corregir_cloudflare.py` (tiene `--simular`).
B1–B4 son ediciones puntuales.

**Verificación, doble:**

- **Barrido de sintaxis:** `verificar_codigo.py` pasa de 4 errores a **0**.
  **111 de 111 bloques de Python compilan.** `inventario.py` reporta **0 residuos de
  Cloudflare** y **0 rutas internas rotas** a `/cdn-cgi/`.
- **En el navegador**, a 375 px y con caché evitada:
  - Módulo 7: los tres bloques renderizan Python válido, y `code-block-7` **conserva** el
    `abs(v)` que corrige en silencio — el error metodológico que sí enseña sigue ahí.
  - Módulo 4: 3 `print("\n===` correctos, 0 partidos.
  - Módulo 8: `DATABASE_URL = "postgresql://admin:SuperSecreto123@192.168.1.50:5432/encuestas_db"`.
  - Módulos 8 y 9: 0 `[email protected]` en el DOM, 0 peticiones 404 en consola.
    **El material entero queda sin un solo error de consola.**

### 12.1 Cómo revertir

```bash
for n in 4 7 8 9; do f=$(ls ${n}_*.html); cp "$f.bak" "$f"; done
```

### 12.2 Lo que implica reorientar el módulo 5 a FastAPI

Decisión tomada, trabajo pendiente (Fase 3). Por el mapa de §11.2, no es un
buscar-y-reemplazar: las secciones 1 y 2 enseñan WSGI y *routing* **usando Flask como
vehículo** (`app = Flask` ×3, `@app.route` ×7, Werkzeug y Jinja2 presentados como «las dos
bibliotecas fundamentales»), y la autoevaluación pregunta por el servidor de desarrollo de
Flask. Hay que reescribir contenido, no sustituir nombres. La sección 3, «Flask vs
Frameworks Modernos (FastAPI)», es la única que ya está donde debe estar y sirve de
bisagra: puede quedarse como contraste histórico.

Sugerencia de orden, para no bloquear el arranque de clases: hacerlo **después** de la
Fase 2, cuando la ficha pedagógica del módulo 5 diga qué RA tiene asignado y qué criterios
de rúbrica prepara. Reescribir antes de saber eso es reescribir dos veces.

---

## 13. Reproducir cualquier dato de este informe

```bash
# Inventario, iconos y residuos de Cloudflare
python3 scripts/auditoria/inventario.py

# Enlaces (tarda ~1 min: hace una petición por URL)
python3 scripts/auditoria/enlaces.py

# Bloques de código: extracción y clasificación
python3 scripts/auditoria/extraer_codigo.py
python3 scripts/auditoria/extraer_codigo.py --ver 7      # volcar los del módulo 7

# Sintaxis, dependencias y ejecución
python3 scripts/auditoria/verificar_codigo.py --ejecutar

# Mapa de consistencia
python3 scripts/auditoria/consistencia.py
python3 scripts/auditoria/consistencia.py --detalle flask   # líneas exactas

# Restitución de los literales destruidos por Cloudflare (B5, B6)
python3 scripts/auditoria/corregir_cloudflare.py --simular

# Barrido en navegador (sirve el material y lo abre a 375 px)
python3 -m http.server 8123
# …y pegar scripts/auditoria/desborde_estados.js en la consola de cada módulo
```

Los resultados quedan en `scripts/auditoria/salida/`: `inventario.json`, `enlaces.json`,
`bloques.json`, `verificacion_codigo.json`, `consistencia.json` y `navegador.json`.
