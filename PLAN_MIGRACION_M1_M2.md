# Plan de migración a LP-CORE — módulos 1 y 2

> Estado: **ejecutado y cerrado el 2026-08-10**. Redactado el 2026-08-09, al
> retomar la cola de migración que dejaron abiertos los módulos 10, 11 y 12.
> Lo que cambió respecto al plan está al final, en «Cómo salió».

## Corrección previa: los módulos 1 y 2 no son lo que dice el plan

`README.md` y `scripts/migracion/README.md` clasifican los módulos 1 y 2 como
**«HTML plano, pequeños»**, a los que sólo les faltaría que `convertir.py`
supiera «trocear por `<h2>` cuando no hay `<section id>`». Eso es falso, y
conviene corregirlo antes de escribir una línea, porque la herramienta que
describe no serviría.

Lo que hay de verdad en `1_Python_para_APIS_IA.html` y
`2_Python_para_APIS_IA_HTTP.html`:

| Se creía | Es |
|---|---|
| HTML estático troceable por `<h2>` | Una aplicación de una sola página: un objeto `courseData` con `modules[]` que se pinta con plantillas literales (`loadModule`, `renderNav`, `renderPipeline`, `renderChart`, `checkAnswer`, `startTimer`) |
| 2 y 3 bloques de código — «los más baratos» | 6 secciones por módulo, ~40 bloques de contenido cada uno |
| Gráficas de Plotly, como 10/11/12 | **Chart.js**: cero `Plotly.newPlot`, dos `new Chart(…)` por archivo, alimentados desde `content.chartData` |
| `<section>` = sección de contenido | Los `<section>` que hay son envoltorios de maquetación del armazón; el contenido no está en el HTML |

Las dos consecuencias:

1. **`convertir.py` no aplica.** Parte de `<section id="…">` y de sopa de HTML
   con `div.box` y `<pre>` resaltado a mano. Aquí no hay ni una cosa ni la otra.
2. **`graficas.py` no aplica.** Busca la salida de `plotly.io.to_html` y su
   `Plotly.newPlot`. Aquí las gráficas son Chart.js declaradas como datos.

La buena noticia es que esto es **más fácil**, no más difícil, que lo que se
había supuesto: el contenido ya está estructurado como datos, así que no hay
que analizar HTML — se lee el objeto y se emite JSX. Y las formas encajan casi
una a una con LP-CORE.

### La familia es exactamente de dos

Antes de invertir en herramienta, cuánto se amortiza. Clasificación medida
sobre los trece archivos:

| Patrón | Módulos | Estado |
|---|---|---|
| `<section id>` + Plotly | 10, 11, 12 | migrados |
| **`courseData` + Chart.js** | **1, 2** | **esto** |
| ReactDOM + Babel, navegación propia | 3, 4, 6, 13 | pendiente, otra familia |
| HTML plano, sin secciones ni gráficas | 5, 7, 8, 9 | pendiente, el troceo por `<h2>` que el README atribuía a 1 y 2 |

Un guion para dos módulos. Se hace igualmente, y no por elegancia: **el HTML
migrado no se versiona**. Todo el proceso descansa en que la salida se
regenera desde el heredado más la receta. Transcribir a mano los módulos 1 y 2
los dejaría fuera de esa invariante y habría que empezar a versionar dos
excepciones.

---

## Qué se construye

Un cuarto guion, `scripts/migracion/convertir_datos.py`, que **produce el
mismo contrato que ya consume `montar.py`**: `piezas/jsx/<id>.jsx` y
`piezas/graficas.jsx`. `montar.py`, el formato de receta y `estilos.py` no se
tocan. Sólo cambia la boca de entrada de la cadena.

```
courseData (JS)  ──node──▶  JSON  ──▶  convertir_datos.py  ──▶  jsx/*.jsx
                                                            └─▶  graficas.jsx
                                                                      │
                                        receta modulo_1.json ─────────┤
                                                                      ▼
                                                                 montar.py
                                                                      │
                                                          _migrado_1_lpcore.html
```

### El mapa de traducción

| `courseData` | LP-CORE | Nota |
|---|---|---|
| `content.concept.text` | prosa dentro de `.prose-lp` | ya viene con `<code>`, `<strong>`, `<br>` |
| `content.concept.analogy` | `Box type="tip"` | el original abre con «⚡ **Analogía:**» — pasa a `label` |
| `content.concept.warning` | `Box type="warn"` | ídem con «⚠️ **Error Común:**» |
| `content.code` `{title, snippet, output}` | `CodeBlock title lang="python"` | la salida, ver decisión abierta |
| `content.codeExplanation` `{title, steps[]}` | `Accordion` | sólo en el módulo 2 |
| `content.quiz` / `quizzes[]` | `Quiz preguntas={[…]}` | **encaje casi exacto**: `question→pregunta`, `options[]→opciones[{texto,correcta}]` vía el índice `correct`, `feedback→justificacion` |
| `content.comparison[]` `{title,pros,cons,bestFor}` | tabla en `.prose-lp` | `.prose-lp` ya estiliza tablas — se comprobó en el módulo 11 |
| `content.glossary` `{title,items[{term,definition}]}` | `Accordion`, y los términos como `Termino` | sólo módulo 2 |
| `content.resources[]` `{name,desc,url}` | lista de enlaces | sólo en `synth` |
| `content.chartData` `{type,labels,data,label,description}` | `usePlotly` + `ChartFrame` | traducción Chart.js → Plotly a nivel de datos |
| `duration`, `shortTitle` | — | metadatos del armazón heredado |

### Inventario real, para dimensionar

Extraído evaluando `courseData` con Node:

| | secciones | concept | code | quiz | comparison | codeExpl. | glossary | resources | chartData |
|---|---|---|---|---|---|---|---|---|---|
| Módulo 1 | 6 | 6 | 6 | 5 | 13 fichas | — | — | 5 | 2 |
| Módulo 2 | 6 | 6 | 6 | 14 preg. | 15 fichas | 5 | 4 | 5 | 1 |

Los identificadores internos son `m1…m5` + `synth` (módulo 1) y `m1…m4`, `m7`,
`synth` (módulo 2). El `m7` del módulo 2 se titula «Módulo 5 (Bonus)»: la
numeración interna ya venía rota y la receta la endereza.

---

## Decisiones de arquitectura

1. **`montar.py` y el formato de receta no se tocan.** Si el guion nuevo emite
   el mismo contrato de piezas, los módulos 1 y 2 se montan con el mismo
   comando que el 11. Una cadena, dos bocas de entrada.
2. **`courseData` se extrae con Node, no con una expresión regular.** Es un
   objeto JS con plantillas literales, comas finales y claves sin comillas: no
   es JSON y analizarlo a mano sería frágil. Node v26 está disponible y
   `eval` + `JSON.stringify` lo resuelve en una línea. Ya se comprobó que
   ambos archivos evalúan sin error.
3. **Cada `module` del `courseData` es una sección del `curriculum`**, con el
   título reescrito en la receta. Dejar «Módulo 1: Python Moderno» dentro de
   lo que ya es el Módulo 1 del curso duplica la palabra en la barra lateral.
4. **Se conserva el contenido, como en 10/11/12.** Regla ya establecida en
   `scripts/migracion/README.md`: esto es migrar, no editar. Los defectos
   heredados se conservan y se anotan.
5. **Chart.js → Plotly se traduce por datos, no por marcado.** `bar` y `radar`
   son los dos tipos presentes; `radar` es `scatterpolar` con `fill: 'toself'`.
   El `description` pasa a `caption` de `ChartFrame`, que es donde LP-CORE
   espera el pie.

---

## Lista de tareas

### Fase 1 · Cimientos y rebanada vertical

**Tarea 1 — Extraer `courseData` a JSON**
Descripción: subcomando o guion que localiza `const courseData = {…}`, lo
evalúa con Node y vuelca JSON a `build/migracion/m<N>/datos.json`.
Aceptación:
- [ ] Produce JSON válido para los módulos 1 y 2.
- [ ] Falla con mensaje claro si no hay `courseData` o si Node no está.
- [ ] No deja artefactos temporales.
Verificación: `python3 … --volcar | python3 -m json.tool > /dev/null` y el
recuento de `modules` es 6 en ambos.
Dependencias: ninguna · Archivos: `scripts/migracion/convertir_datos.py` · **S**

**Tarea 2 — Rebanada vertical: sólo `concept`, un módulo, hasta el navegador**
Descripción: emitir las 6 secciones del módulo 1 con únicamente `concept`
(prosa + `Box` de analogía y aviso), escribir `recetas/modulo_1.json`, montar
y abrir. Prueba la cadena entera, incluida la compatibilidad con `montar.py`.
Aceptación:
- [ ] `_migrado_1_lpcore.html` se genera con 6 secciones en el `curriculum`.
- [ ] Babel compila: consola del navegador sin errores.
- [ ] La barra lateral muestra los 6 títulos reescritos.
Verificación: montar, abrir en el panel del navegador, `read_console_messages`
sin errores, captura de una sección.
Dependencias: 1 · Archivos: `convertir_datos.py`, `recetas/modulo_1.json` · **M**

### Punto de control · Cimientos
- [ ] La cadena de cuatro guiones funciona con la boca de entrada nueva.
- [ ] `montar.py` no necesitó cambios. *Si los necesitó, parar y replantear.*

### Fase 2 · Los bloques de contenido

**Tarea 3 — `code`, `codeExplanation` y `bonus`**
Aceptación:
- [ ] `CodeBlock` con `title` y `lang="python"`; se reutiliza `detectar_lang`
      de `convertir.py` para los bloques que no sean Python.
- [ ] La salida se trata según la decisión abierta de más abajo.
- [ ] `codeExplanation.steps[]` sale como `Accordion`.
Verificación: los 12 bloques de código se resaltan (Prism aplica clases), y
ningún bloque queda con `lang="text"` sin justificación.
Dependencias: 2 · **S**

**Tarea 4 — `quiz` y `quizzes[]` → `Quiz`**
Aceptación:
- [ ] `correct` (índice) se convierte en `correcta: true` de la opción.
- [ ] `feedback` pasa a `justificacion`.
- [ ] Las 5 preguntas del módulo 1 y las 14 del 2 salen sin pérdida.
Verificación: responder mal y bien una pregunta en el navegador; el marcador y
la justificación aparecen.
Dependencias: 2 · **S**

**Tarea 5 — `comparison`, `glossary`, `resources`**
Aceptación:
- [ ] `comparison[]` sale como tabla legible sin CSS propio.
- [ ] `glossary.items[]` sale como `Accordion`.
- [ ] Los 5 enlaces de `resources` abren en pestaña nueva y ninguno está roto.
Verificación: comprobar los 5 destinos con una petición de cabecera.
Dependencias: 2 · **S**

**Tarea 6 — `chartData`: Chart.js → `usePlotly` + `ChartFrame`**
Aceptación:
- [ ] `bar` y `radar` se traducen; cualquier otro tipo aborta con aviso.
- [ ] `description` va a `caption`, no a un `<p>` suelto.
- [ ] Las etiquetas largas no se salen del lienzo (`automargin: true`) — el
      defecto que en el módulo 11 se conservó a propósito aquí no se hereda,
      porque la gráfica se genera de cero.
Verificación: captura de las tres gráficas; sin recortes.
Dependencias: 2 · **M**

**Tarea 7 — Portada del archivo heredado**
Descripción: la apertura («Hoy tu código deja de ser sólo tuyo») y el reparto
del tiempo viven fuera de `courseData`, en HTML estático. Se recogen en una
sección 0.
Aceptación:
- [ ] Ningún párrafo de la portada se pierde.
- [ ] La gráfica del reparto se conserva o se sustituye por la tabla de
      duraciones, que es el mismo dato.
Dependencias: 6 · **S**

### Punto de control · Módulo 1 completo
- [ ] Consola limpia, las 6 secciones navegan, el cuestionario puntúa.
- [ ] `diff` conceptual contra el original: ningún bloque de contenido perdido.
- [ ] **Revisión humana antes de seguir con el módulo 2.**

### Fase 3 · Módulo 2 y cierre

**Tarea 8 — `recetas/modulo_2.json` y ajuste de las diferencias**
Descripción: el módulo 2 añade `codeExplanation`, `glossary` y `quizzes[]` en
plural. Si las tareas 3–5 se hicieron bien, aquí sólo hay receta y depuración.
Aceptación:
- [ ] Se monta sin tocar `convertir_datos.py`. *Si hay que tocarlo, es señal
      de que el guion se ajustó al módulo 1 en vez de al patrón.*
Dependencias: 3, 4, 5, 6, 7 · **M**

**Tarea 9 — `estilos.py` sobre los dos módulos**
Descripción: comprobar si el `<style>` heredado tiene reglas propias que
LP-CORE no cubra. A diferencia de 10/11/12, aquí casi todo es Tailwind por
CDN, así que probablemente el CSS rescatado sea vacío o mínimo.
Aceptación:
- [ ] Se documenta qué se rescató y qué se descartó, o que no hizo falta nada.
Dependencias: 8 · **S**

**Tarea 10 — Documentación**
Aceptación:
- [ ] `scripts/migracion/README.md`: la familia `courseData`, el guion nuevo,
      el mapa de traducción y **la tabla de familias corregida**.
- [ ] `README.md`: estado al día y la clasificación arreglada — los módulos
      5, 7, 8 y 9 son los que necesitan el troceo por `<h2>`, no el 1 y el 2.
- [ ] Un commit por fase, no uno solo al final.
Dependencias: 9 · **S**

### Punto de control · Completo
- [ ] Los dos módulos se regeneran desde cero con los cuatro comandos.
- [ ] Ningún `_migrado_*.html` versionado.

---

## Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El guion se ajusta al módulo 1 y falla en el 2 | Medio | La tarea 8 es la prueba: si hay que tocar el guion, se ajustó de más |
| Prosa de `concept` con llaves o comillas que rompen JSX | Medio | Reutilizar `escapar_jsx` y `atributo` de `convertir.py`, ya probados en tres módulos |
| Chart.js radar sin equivalente limpio en Plotly | Bajo | `scatterpolar` + `fill: 'toself'`; es una gráfica |
| LP-CORE cambia en el repo de LPF | Bajo | Ya conocido; se re-ensambla y se vuelve a montar |
| Sección `synth` con forma distinta a las demás | Bajo | Ya inventariada: `comparison[5]` + `resources` + `chartData` |

## Supuestos

1. Los módulos 1 y 2 se **traducen**, no se reescriben — misma regla que 10/11/12.
2. Los títulos de sección se reescriben en la receta para no duplicar «Módulo».
3. El temporizador por módulo (`startTimer`, «25 min») y la barra de progreso
   `renderPipeline` son armazón, no contenido, y no se reproducen; la duración
   queda como dato en la tabla del reparto.
4. Las gráficas pasan a Plotly porque es lo que LP-CORE trae; no se añade
   Chart.js a la plantilla.

## Decisión cerrada · la salida del código

**El botón «Ejecutar simulación».** En el heredado, `code.output` está
precalculado y oculto tras un botón que lo revela (`runSimulation`). LP-CORE
no tiene ese componente.

**Resuelto el 2026-08-09: `Accordion` «Ver salida».** El botón desaparece —no
ejecutaba nada— pero el gesto de revelar se mantiene, que es lo que sostiene
el «predice antes de mirar». Es además la decisión que ya se tomó en
`convertir.py` al plegar las soluciones de los ejercicios, y por el mismo
motivo, así que el material no acaba con dos criterios.

```jsx
<CodeBlock title="Clasificación de outliers" lang="python" code={`…`} />
<Accordion items={[{ titulo: 'Ver salida', contenido: (<>
  <pre>Resultados: ['valido', 'outlier_severo', 'error', 'outlier_leve']</pre>
</>) }]} />
```

Se descartaron: la salida visible en un `CodeBlock title="Salida"` (sin
fricción, pero pierde la predicción) y el prefijo `#>` dentro del bloque (la
convención de LP-CORE en Lógica, pero los módulos 10/11/12 de este curso no la
siguen y convivirían dos estilos).

---

## Cómo salió

Las diez tareas están hechas. Los dos módulos se regeneran de cero con la
cadena, `montar.py` no necesitó ningún cambio para el contenido —sólo dos
comprobaciones nuevas de la receta— y `auditar.py` da **10 925 piezas de
contenido, cero perdidas** en las doce secciones.

|  | secciones | CodeBlock | Box | Accordion | tablas | gráficas |
|---|---|---|---|---|---|---|
| Módulo 1 | 7 | 16 | 18 | 7 | 7 | 2 |
| Módulo 2 | 7 | 17 | 18 | 15 | 12 | 1 |

Siete y no seis: la portada —la apertura y el reparto del tiempo, que viven
fuera de `courseData`— es la sección 1, y las del objeto pasaron a numerarse
de la 2 a la 7.

### Lo que el plan no vio

- **`code.output` no podía inyectarse como JSX.** Una salida del módulo 2 dice
  `🐍 Original: <class 'datetime.datetime'>`, y ese `<class …>` Babel lo abre
  como etiqueta y no lo cierra nunca: el módulo 2 no compilaba. Va en un
  `CodeBlock`, dentro de una plantilla literal. Lo encontró `auditar.py`, que
  el plan no contemplaba y acabó siendo la pieza que más valor dio.
- **`comparison` viene en dos formas**, no en una: `{tool,use,detail}` y
  `{title,pros,cons,bestFor}`. Cada una da una tabla distinta.
- **`glossary.conceptualExample`** es un antes/después de código, no prosa.
  `Comparador` de LP-CORE parecía el componente natural y no lo es: exige las
  cuatro versiones del código y una pregunta de opción múltiple.
- **El emoji de `analogy` y `warning` es información, no adorno.** La etiqueta
  cambia de sección a sección, así que no clasifica; el emoji sí.
- **Un componente no puede llamarse como algo que la plantilla ya declara.**
  `PortadaSection` existe en `lp-base.html`, y como la receta lo nombraba,
  `podar` lo daba por vivo y lo dejaba: dos declaraciones y página en blanco.

### Falsas alarmas, para que no se repitan

- **Los iconos de los módulos 10, 11 y 12 nunca estuvieron rotos.** Se
  concluyó que 19 de 27 no existían leyendo sólo el literal `const Icons = {…}`
  e ignorando el `Object.assign(Icons, {…})` que lo amplía. Son diecisiete y
  todos dibujan; comprobado contra la página. De ahí salió, eso sí, la
  comprobación de iconos de `montar.py`, porque un nombre mal escrito sí
  fallaba en silencio.
- **Tres versiones de `auditar.py` dieron pérdidas que no existían**, todas por
  intentar quitar «etiquetas» del JSX con una expresión regular. Está explicado
  en `scripts/migracion/README.md` para que la cuarta no se reescriba.

### Lo que queda abierto

Dos defectos menores de `montar.py`, ninguno bloqueante:

- `podar()` se lleva por delante el centinela `SECCIONES INICIO` cuando la
  constante que poda está justo antes. Le pasa al módulo 1.
- El docstring promete una idempotencia que no está implementada: dice que
  reutiliza el archivo de salida si tiene centinelas, pero siempre reconstruye
  desde `lp-base.html`. Es idempotente de hecho, así que el centinela perdido
  no rompe nada — pero lo que documenta no es lo que hace.

Y un hueco del material, no de la herramienta: **el módulo 2 no tiene
apertura.** El 1 abre con un gancho («Hoy tu código deja de ser sólo tuyo») y
el 2 entra directo al reparto del tiempo. Es decisión del docente si escribirla.
