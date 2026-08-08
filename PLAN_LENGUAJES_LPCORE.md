# Plan — cerrar el hueco de lenguajes de LP-CORE

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-08
**Origen:** [`PILOTO_LPCORE.md`](PILOTO_LPCORE.md) §2 y §5 — «antes de migrar nada más, cerrar el
hueco de Dockerfile/YAML/SQL».
**Vía elegida:** parchear la librería compartida de Lógica de Programación Financiera
(`lp-core-extra.jsx` + el `<head>` del capítulo 01) y portarle el guardarraíl de gramáticas que
Teoría del Riesgo ya tiene.

---

## 0. Qué cambió respecto del piloto

El piloto acertó en el diagnóstico y se quedó corto en el alcance. Al comprobarlo contra los
archivos aparecieron cuatro cosas.

### 0.1 El inventario estaba mal contado

El conteo del piloto sólo vio bloques `<pre>`. Cinco de los catorce archivos (módulos 3, 4, 6, 13
y el syllabus) son React y usan `<CodeBlock code={variable}>`: el módulo 13, con 26 bloques, entró
como si tuviera uno.

| | Piloto | Real |
|---|---|---|
| Bloques totales | 212 | **186** |
| Dockerfile | 22 — módulos 11 y 13 | **14** — mód. 11 (8), 13 (4), **12 (2)** |
| YAML | 2 — módulo 12 | **3** — todos en el 12 |
| SQL | 1 — módulo 9 | **0** — ver abajo |
| Python | 112 | **~88** |

Aparece además un lenguaje que no estaba inventariado: **TOML, 3 bloques** (`pytest.ini` y
`pyproject.toml` en el módulo 10, `[tool.ruff]` en el 9). Y quedan 48 bloques sin clasificar
automáticamente —shell con la primera línea comentada, salidas y diagramas ASCII—, así que la
cifra de shell es un suelo, no un total.

> **Corrección sobre la primera versión de esta tabla, que decía «SQL: 2».** Era el mismo error
> de conteo que se le señala al piloto, cometido aquí. Los dos bloques resultaron ser falsos
> positivos de un `^SELECT` con `re.M`: uno es Python (`select(models.Autor)`) y el otro TOML
> (`select = ["E", "F", …]` dentro de `[tool.ruff]`). **No hay ningún bloque de SQL autónomo en
> el material**: el SQL del módulo 9 vive dentro de cadenas de Python, en `text("SELECT …")`. Se
> declara `sql` igualmente — ver §1.6.

La conclusión de fondo aguanta, con una corrección operativa: **el módulo 12 también tiene
Dockerfiles**, no sólo el 11 y el 13.

### 0.2 Falta una gramática más, y es la segunda más usada

`GRAMATICA` declara `shell: 'bash'`, pero **`prism-bash` no está cargado en ningún head** y el
core de Prism 1.29 sólo trae markup, css, clike y javascript (comprobado sobre el bundle de
cdnjs). Los bloques de shell nunca se han resaltado, en ninguno de los dos cursos.

El piloto no lo vio porque sólo probó `lang="docker"`. Es el mismo defecto que ya había
diagnosticado, actuando sobre una clave que sí existía.

### 0.3 El arreglo son dos cambios, no uno

El piloto lo describe como «tres entradas en `GRAMATICA`, tres en `LANG_META` y cargar tres
componentes de Prism». Las dos primeras van en `lp-core-extra.jsx` y las propaga `migrar.py`. La
tercera va en el `<head>` — y **`migrar.py` no estampa el head**, ni en LPF ni en Teoría del
Riesgo. En LPF el head se extrae del capítulo 01 (`ensamblar.py:41`, `ANCLA_FIN_HEAD`).

Importa porque `resaltar()` cae al mismo `escaparHtml` cuando la clave existe en `GRAMATICA` pero
`Prism.languages[nombre]` es `undefined`. **Media reparación se ve exactamente igual que ninguna.**

### 0.4 Teoría del Riesgo ya resolvió esto

`Usta 2026II/Teoría del riesgo/Material html/_plantilla/` tiene `tr-core-extra.jsx`,
`tr-head.html` y `tr-base.html` propios, con `GRAMATICA = {python, r, shell, text}` —sin `pseudo`
ni `vba`—. Y su `ensamblar.py:75` trae el guardarraíl que aquí falta, con este comentario:

> Sin ellas el código sale sin resaltar, que es un defecto silencioso: se ve feo pero no falla
> nada, así que puede llegar al aula sin que nadie lo note.

Es decir: el precedente del taller no es parchear la librería compartida, es forkear por curso con
head propio. **Se descartó forkear aquí y ahora** porque `verificar.py` son 30 KB que codifican la
pedagogía de LPF (cuotas E1–E8, `CodeTabs` de cuatro lenguajes) y decidir qué aplica a este curso
es un proyecto aparte, no un arreglo. Queda anotado en §5.

---

## 1. Decisiones de arquitectura

1. **`GRAMATICA` se queda en una sola línea.** Partirla en varias terminaría en una línea
   `        };` con ocho espacios de sangría, que es justo el patrón que `cierre_de()` busca en
   `ensamblar.py:67` y `migrar.py:72`. En un capítulo ya estampado, `GRAMATICA` cae después de
   `const Termino`, así que un cierre nuevo con esa sangría puede adelantarse al que el guion
   busca. `LANG_META` sí es multilínea y ya termina así, pero eso funciona hoy porque el cierre de
   `Termino` aparece antes; añadirle entradas no mueve ese orden.

2. **Se aceptan `docker` y `dockerfile` como claves.** `prism-docker.min.js` registra las dos
   (comprobado sobre el bundle). El piloto escribió `lang="docker"`, pero el módulo 13 ya usa
   `lang="dockerfile"` en cinco bloques. Aceptar ambas cuesta una entrada y evita una pasada de
   normalización sobre material ya escrito.

3. **El guardarraíl se deriva de `GRAMATICA`, no de una lista fija.** Teoría del Riesgo comprueba
   una tupla escrita a mano (`"prism-python", "prism-r"`), que hay que acordarse de actualizar. Si
   en vez de eso se leen los valores de `GRAMATICA` y se comprueba que cada uno tenga su
   `prism-<valor>` en el head, la comprobación se mantiene sola: añadir una clave sin su
   componente pasa a ser imposible. Necesita dos exenciones — `pseudo`, que se registra en JS
   dentro de `lp-core-extra.jsx`, y las cuatro gramáticas que trae el core de Prism.

4. **No se toca `PREFIJO_SALIDA`.** Hoy no tiene entrada para `shell`, así que las líneas de
   salida de una terminal no se marcan como salida. Es un defecto real y adyacente, pero cambiarlo
   altera el aspecto de LPF además del de este curso. Va aparte (§5).

5. **No se toca ningún módulo del curso.** Este plan cambia la librería, no el material. Los 13
   módulos siguen exactamente como los dejó la Fase 3.

6. **Se declara `sql` aunque el material no tenga ningún bloque suelto.** Es la única clave que
   se añade «de más». La alternativa —no declararla— deja la trampa armada: el primer bloque con
   `lang="sql"` que alguien escriba caería en la misma degradación silenciosa, porque el
   guardarraíl de la Tarea 3 sólo comprueba las claves declaradas, no las que faltan. El módulo 9
   es de SQLAlchemy, así que ese bloque llegará. Cuesta un componente de 2 KB.

7. **Los tokens de Prism se fijan a `display: inline` dentro de `.lp-code-pre`.** Añadido durante
   la Tarea 5, no estaba previsto. Prism nombra sus tokens con palabras que Tailwind usa como
   utilidades: la gramática de TOML marca `[pytest]` como `token table` y `.table{display:table}`
   lo convertía en una tabla CSS, partiendo la línea en tres. La regla vive en el `<head>`, junto
   al resto del CSS de LP-CORE.

---

## 2. Tareas

### Fase 1 — La librería

#### Tarea 1: Extender `GRAMATICA` y `LANG_META`

**Descripción:** Añadir a la librería las cinco gramáticas que el material necesita y que hoy no
declara —`docker`/`dockerfile`, `yaml`, `sql`, `toml`— más los metadatos (etiqueta, icono, color)
con que `CodeBlock` rotula la cabecera del bloque. `shell` ya está declarado y no se toca aquí:
lo suyo es la Tarea 2.

**Criterios de aceptación:**
- [ ] `GRAMATICA` sigue siendo **una sola línea** e incluye `docker`, `dockerfile`, `yaml`, `sql`
      y `toml`, con los nombres de gramática de Prism verificados (`docker`, `docker`, `yaml`,
      `sql`, `toml`).
- [ ] `LANG_META` tiene una entrada por cada clave nueva, con iconos que existan en Font Awesome
      6.5.2 (`fab fa-docker`, `fas fa-file-code`, `fas fa-database`, `fas fa-gears`).
- [ ] Ninguna clave preexistente cambia de valor.

**Verificación:**
- [ ] `grep -c "^        const GRAMATICA = " lp-core-extra.jsx` devuelve 1.
- [ ] La Tarea 3 falla si esta tarea se hace sin la 2 — esa es la prueba de que el guardarraíl sirve.

**Dependencias:** ninguna
**Archivos:** `Usta 2026II/Logica de programacion/Material html/_plantilla/lp-core-extra.jsx`
**Tamaño:** XS

---

#### Tarea 2: Cargar las gramáticas en el `<head>`

**Descripción:** Añadir los cinco `<script>` de Prism que faltan. Cuatro son de las claves nuevas;
el quinto es **`prism-bash`, que corrige un defecto preexistente** (§0.2) y es el de mayor efecto
inmediato, porque shell es el segundo lenguaje del material.

**Criterios de aceptación:**
- [ ] El head de `01_LPF_Introduccion.html` carga `prism-bash`, `prism-docker`, `prism-yaml`,
      `prism-sql` y `prism-toml`, todos de cdnjs 1.29.0, junto a los tres que ya estaban.
- [ ] El comentario que precede al bloque explica por qué está cada uno, en el estilo del que ya
      hay ahí.
- [ ] `window.Prism.manual = true` sigue **antes** de `prism.min.js`.

**Verificación:**
- [ ] Los cinco devuelven HTTP 200 en cdnjs (ya comprobado; repetir tras editar por si hay una
      errata en la URL).
- [ ] En el navegador, `Object.keys(Prism.languages)` incluye `bash`, `docker`, `dockerfile`,
      `yaml`, `sql` y `toml`.

**Dependencias:** ninguna (puede ir en paralelo con la 1)
**Archivos:** `…/Material html/01_LPF_Introduccion.html` (sólo el head, líneas 24-31)
**Tamaño:** XS

---

#### Tarea 3: Guardarraíl derivado en `ensamblar.py`

**Descripción:** Que el ensamblado falle cuando una gramática declarada en `GRAMATICA` no tenga su
componente cargado en el head. Es la pieza que impide que el defecto vuelva: sin ella, la próxima
clave que alguien añada se degradará en silencio igual que `shell` lleva degradándose. Se deriva
de `GRAMATICA` en lugar de una tupla fija (§1.3).

**Criterios de aceptación:**
- [ ] `ensamblar.py` lee los valores de `GRAMATICA` desde `lp-core-extra.jsx` y comprueba que cada
      uno no exento aparezca como `prism-<valor>` en el head.
- [ ] Exenciones explícitas y comentadas: `pseudo` (se registra en JS) y las gramáticas del core
      de Prism.
- [ ] El mensaje de error dice qué falta y en qué archivo arreglarlo, como hace el de Font Awesome.
- [ ] Sale con código 1 y **no escribe `lp-base.html`**.

**Verificación:**
- [ ] Quitar a mano `prism-sql` del head → `ensamblar.py` falla nombrando `prism-sql`, y
      `lp-base.html` conserva su fecha de modificación anterior. Restaurar.
- [ ] Añadir una clave falsa a `GRAMATICA` → falla nombrándola. Quitarla.
- [ ] Con todo en su sitio → sale 0.

**Dependencias:** Tareas 1 y 2
**Archivos:** `…/_plantilla/ensamblar.py`
**Tamaño:** S

---

### ✅ Punto de control A — la librería

- [ ] `ensamblar.py` sale 0 y regenera `lp-base.html`.
- [ ] Los dos ensayos de fallo de la Tarea 3 fallan como deben.
- [ ] `git diff` toca exactamente tres archivos: `lp-core-extra.jsx`, `01_LPF_Introduccion.html`
      y `ensamblar.py`.

---

### Fase 2 — Propagar y comprobar

#### Tarea 4: Re-estampar y verificar LPF

**Descripción:** El único capítulo que existe hoy en LPF es el 01, que además es la fuente del
head. Re-estamparlo cierra el ciclo y demuestra que el cambio no le rompe nada — que es la
condición que el piloto puso para tocar una librería compartida.

**Criterios de aceptación:**
- [ ] `migrar.py` estampa el capítulo 01 sin fallos y el SHA de LP-CORE coincide con el de la
      plantilla (lo comprueba él mismo, `migrar.py:182`).
- [ ] `verificar.py` no reporta ningún hallazgo **nuevo** respecto de su salida antes del cambio.
- [ ] En particular, la comprobación 10 (contraste) no se queja de los colores nuevos de
      `LANG_META`.

**Verificación:**
- [ ] Guardar la salida de `verificar.py` **antes** de tocar nada y compararla con la de después.
      Sin la línea base, «no hay hallazgos nuevos» no es comprobable.
- [ ] Abrir el capítulo 01 en el navegador: 0 errores en consola, los bloques de `CodeTabs`
      siguen resaltando pseudocódigo, Python, R y VBA.

**Dependencias:** Punto de control A
**Archivos:** `01_LPF_Introduccion.html` (regenerado, con `.bak`)
**Tamaño:** S

---

#### Tarea 5: Rehacer el piloto con los cinco lenguajes

**Descripción:** Reconstruir `_piloto_11_lpcore.html` desde el `lp-base.html` nuevo, con un bloque
real de cada lenguaje tomado del material —Dockerfile del módulo 11, YAML del 12, SQL del 9, TOML
del 10, shell del 11— y comprobar que se resaltan. Es la prueba de que el hueco quedó cerrado; sin
ella sólo se sabe que los archivos cambiaron.

**Criterios de aceptación:**
- [ ] El piloto monta con 0 errores en consola.
- [ ] Los cinco bloques muestran tokens resaltados, no texto plano.
- [ ] La cabecera de cada bloque muestra su etiqueta correcta —«Dockerfile», no «Salida», que es
      justo el síntoma que describe el piloto.
- [ ] 0 px de desborde horizontal, como en la medición anterior.

**Verificación:**
- [ ] `python3 -m http.server 8123` y captura de pantalla de los cinco bloques.
- [ ] En consola: `document.querySelectorAll('.lp-code-pre .token').length > 0` para cada bloque.

**Dependencias:** Tarea 4
**Archivos:** `_piloto_11_lpcore.html`
**Tamaño:** S

---

### ✅ Punto de control B — el hueco cerrado

- [ ] Captura con los cinco lenguajes resaltados.
- [ ] LPF capítulo 01 sin regresiones.
- [ ] Revisión antes de seguir.

---

### Fase 3 — Dejar constancia

#### Tarea 6: Corregir `PILOTO_LPCORE.md` y actualizar el README

**Descripción:** El piloto es el documento que justifica la decisión de migrar o no, así que sus
cifras tienen que ser las correctas. Corregir las tablas de §2, añadir los cuatro hallazgos de §0
de este plan y actualizar el «siguiente paso» del README.

**Criterios de aceptación:**
- [ ] La tabla de §2 del piloto lleva las cifras reales y dice que el módulo 12 también tiene
      Dockerfiles.
- [ ] Queda escrito que `shell` estaba roto desde antes, que `migrar.py` no estampa el head, y
      que Teoría del Riesgo tiene fork propio.
- [ ] El README ya no dice que el hueco esté abierto, y apunta a este plan.
- [ ] La frase «coste de arreglarlo: tres entradas…» pasa a decir lo que realmente costó.

**Verificación:**
- [ ] Releer §0 y §2 del piloto sin este plan al lado y comprobar que se entienden solos.

**Dependencias:** Punto de control B
**Archivos:** `PILOTO_LPCORE.md`, `README.md`
**Tamaño:** XS

---

### ✅ Punto de control C — cerrado

- [ ] Los seis criterios de aceptación de arriba, cumplidos.
- [ ] Commit en `auditoria/fase-2`, o rama nueva si prefieres separarlo.
- [ ] La cola de migración (módulos 11, 12, 13) ya no está bloqueada.

---

## 3. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El cambio en la librería compartida rompe LPF | **Alto** — es material de otra asignatura | Sólo se añaden claves, ninguna cambia. Línea base de `verificar.py` antes y después (Tarea 4). `migrar.py` deja `.bak` |
| `GRAMATICA` multilínea confunde a `cierre_de()` | Medio — el ensamblado saldría mal cortado | Decisión §1.1: se queda en una línea. El guardarraíl de la Tarea 3 no cubre esto |
| Los colores nuevos de `LANG_META` disparan la comprobación de contraste | Bajo | Se detecta en la Tarea 4; hay válvula (`contraste-ok`) documentada en `verificar.py:377` |
| Cinco CDN más en el head de LPF | Bajo — ~18 KB, y LPF no usa ninguno | Aceptado al elegir la Vía 1. Se revierte solo si algún día se forkea (§5) |
| Los 48 bloques sin clasificar esconden otro lenguaje | Bajo | El guardarraíl no lo detectaría: sólo comprueba las claves declaradas, no las que faltan. Se revisan al migrar cada módulo |

---

## 4. Lo que este plan no hace

- **No migra ningún módulo.** El piloto sigue siendo lo único construido sobre LP-CORE, y las
  tres incógnitas de su §3 —`ChartFrame` con las gráficas de Plotly, las 8 tablas, y las 8
  secciones sin migrar del módulo 11— siguen sin medir.
- **No toca `PREFIJO_SALIDA`** (§1.4): las líneas de salida de shell siguen sin marcarse.
- **No normaliza `lang="docker"` frente a `lang="dockerfile"`** en el material: se aceptan las dos.
- **No forkea la librería** (§0.4).

---

## 5. Después de esto

Tres cosas quedan anotadas, ninguna bloqueante:

1. **Portar el guardarraíl derivado a Teoría del Riesgo.** Su versión es una tupla escrita a mano;
   la de la Tarea 3 se mantiene sola. Es copiar una función.
2. **Decidir si este curso forkea `py-core`.** La divergencia con LPF ya es mutua y no
   hipotética: este curso no quiere `pseudo`/`r`/`vba` ni sus componentes de Prism, y LPF no
   quiere Docker/YAML/SQL. El coste real está en `verificar.py`, no en la librería.
3. **Terminar de medir el módulo 11**, que es lo que el piloto dejó a medias y la única forma de
   estimar los doce restantes con algo que no sea una corazonada.
