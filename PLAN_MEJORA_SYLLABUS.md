# Plan de mejora — `0_Syllabus_P_A_IA.html`

**Asignatura:** Python para Desarrollo de APIs e Inteligencia Artificial · USTA · Estadística · 2026-I
**Fecha del diagnóstico:** 2026-08-06
**Estado del documento auditado:** 61.840 bytes, última modificación 2026-03-20

---

## 0. Veredicto

El syllabus tiene **una tesis pedagógica excelente** ("del script aislado al producto de datos desplegado") y una **secuencia de contenidos técnicamente correcta**. Como pieza de diseño instruccional el esqueleto es mejor que el de la mayoría de syllabi: cada semana declara resultado de aprendizaje, teoría, práctica guiada, trabajo autónomo y stack.

Pero **no es todavía un buen syllabus**, por tres razones de peso distinto:

1. **Está roto en el navegador** (verificado). Ningún estilo de Tailwind se aplica: la página se renderiza sin maquetación, en Times, con el encabezado ilegible.
2. **No describe el curso que realmente se dicta.** Hay divergencias mayores entre las 16 semanas del syllabus y los 13 módulos + proyecto integrador que existen en el repositorio.
3. **Las dos gráficas presentan como dato lo que es invención.** Una de ellas es demostrablemente falsa contra el propio contenido del curso.

Lo bueno es reparable sin rehacer nada: el `syllabusData` de JavaScript es una buena arquitectura de contenido y sobrevive intacto a todas las correcciones.

---

## 0.bis Decisiones del docente (2026-08-06)

Cuatro decisiones tomadas antes de ejecutar; el plan de §2 queda ajustado a ellas.

| # | Decisión | Efecto sobre el plan |
|---|---|---|
| D1 | **Se conservan las 16 semanas** y se mapea cada una a su módulo real. No se renumera el material existente. | T2.1 se ejecuta en modo "mapeo": algunos módulos ocupan 2 semanas y se declaran explícitamente las sesiones de taller/parcial/asesoría. |
| D2 | **El Proyecto Integrador de Teoría del Riesgo es EL proyecto del curso.** | T3.1 y T3.2 se ejecutan completos, sin vía alterna. Se asume matrícula paralela en Teoría del Riesgo. |
| D3 | **DL (S12) y LLMs (S14) se reclasifican como contenido opcional/de extensión**, con lectura asignada. No se produce material nuevo. | T2.3 opción (b). Elimina el mayor volumen de trabajo del plan. Obliga a recalcular la distribución del gráfico de IA (T4.1). |
| D4 | **Sí existe formato institucional obligatorio USTA**; el docente lo comparte. | Este HTML pasa a ser el **companion del estudiante**, no el documento oficial. La Fase 1 se reduce: bloque de identificación mínimo + enlace al documento oficial, sin duplicar todo el formato. Queda **en espera de la plantilla**. |
| D5 | **Migración completa al sistema de diseño LP-CORE** (`lp-base.html` del material de Lógica de Programación Financiera 2026-II). | El syllabus se reconstruye como documento React autocontenido de 5 secciones. Supersede las Fases 4-6 del plan original, que se cierran con los componentes de la librería. Ejecutada 2026-08-06. |
| D6 | **Los datos institucionales pendientes se infieren del material existente** y se presentan como borrador para corrección. | Lo que no puede inferirse honestamente se marca **visiblemente como pendiente** dentro del documento en lugar de inventarse. |
| D7 | **Datos institucionales entregados por el docente** (2026-08-06): código **28549**, **4 créditos**, **sin prerrequisitos**, correo `javiersierra@usta.edu.co`, atención lunes 18:00–20:00 y sábados 8:00–10:00. | Cerró el bloque de identificación. Solo quedan pendientes los cortes. |
| D8 | **La sesión semanal es de 4 h**, no de 3. | Resolvió una inconsistencia heredada: 4 créditos son 192 h; con 3 h de clase el trabajo independiente habría sido de 9 h/semana, contra las 8 h que declaraba el syllabus anterior. Con 4 h de clase cuadra en 64 h + 128 h, relación 1:2. El reparto interno (60 min de teoría + 180 min de práctica) lo fijó Claude y es editable en `CONFIG`. |
| D9 | **Sistema de evaluación** (2026-08-06): cortes I y II 30 % cada uno —actividades y entregas sustentadas en clase—, corte III 40 % —sólo el proyecto: entregables 20 %, sustentación 80 %—. En el corte I, la definición del proyecto pesa 5 % del corte. En el corte II, primera entrega equivalente al 30 % del proyecto, con justificación exigida. Equipos de máximo 2. | Cerró la sección de evaluación. Deriva: la sustentación vale **32 % de la definitiva** y el proyecto **47,5 %**. |
| D10 | **Cierre de la evaluación** (2026-08-06): primera entrega = **20 % del corte II**; fechas límite de evaluación **5 sep / 17 oct / 21 nov de 2026** (las tres en sábado); y **la rúbrica se modifica al esquema 20-80** — califica sólo los entregables, sin criterio de sustentación. | Resolvió la doble medición de la sustentación. Rúbrica reescalada de 16 a **15 criterios** (×100/85, mayor residuo; el empate del redondeo se resolvió contra el tablero, deliberadamente lo menos pesado). Nueva composición: Riesgo 60 % · Ingeniería 40 %. Con el corte III en la semana 16, la semana 1 es la del **8 de agosto de 2026** y los cortes caen en las semanas **5, 11 y 16** (supuesto sin recesos). Abre una tarea: sincronizar la rúbrica del spec `Proyecto_Integrador_Riesgo_Python_CIII.html` (chip creado). |

---

## 1. Hallazgos

### 1.1 Fallo técnico — la página no se estiliza (BLOQUEANTE, verificado)

Evidencia reproducida en navegador sobre el archivo tal como está:

```
[error] Uncaught ReferenceError: tailwind is not defined
        at 0_Syllabus_P_A_IA.html:65:9
```

```js
// Estado real del DOM con el archivo actual
{ tailwindConfigColors: "NO CONFIG",      // la paleta USTA nunca se registra
  body_font:            "Times",           // Montserrat se descarga y no se usa
  main_maxWidth:        "none",            // max-w-7xl no aplica
  grid_display:         "block",           // ningún grid se construye
  mobileMenu_bg:        "rgba(0,0,0,0)",   // bg-navy es transparente
  styleSheets:          [FontAwesome, GoogleFonts, <style> propio]  // ← sin hoja Tailwind
}
```

**Causa raíz** — línea 38:

```html
<script src="https://cdn.tailwindcss.com" defer></script>
```

Con `defer`, el script inline de la línea 64 (`tailwind.config = {...}`) se ejecuta **antes** de que exista el objeto `tailwind` → `ReferenceError` → la configuración muere. Y el propio CDN, diferido, no llega a inyectar su hoja de estilos.

**Verificación A/B en el mismo navegador** (inyectando el CDN sin `defer` en caliente):

| Propiedad | Con `defer` (actual) | Sin `defer` |
|---|---|---|
| `section.grid` → `display` | `block` | `grid` |
| `main` → `max-width` | `none` | `1280px` |
| Hojas de estilo | 3 | 4 |

**Consecuencias visibles para el estudiante:** todo el documento se ve como HTML plano en serif; el `<h1>` blanco queda sobre fondo azul-oscuro sin las utilidades que lo hacen legible; las tarjetas, el grid de dashboard y el layout de dos columnas del cronograma no existen; la identidad visual USTA (`#3D008D`, `#ED1E79`, `#001A4D`, `#FDB913`) declarada en el `tailwind.config` **nunca se aplica en ninguna parte**.

**Fallos técnicos menores:**
- `og:image` y `twitter:image` apuntan a `via.placeholder.com`, servicio discontinuado → previsualización social rota.
- `Logo_USTA.png` existe en el repositorio (sin trackear) pero el header usa un icono genérico de Font Awesome (`fa-network-wired`).
- Todo el contenido vive en JavaScript: sin JS no hay syllabus, y no es imprimible ni indexable.

### 1.2 Coherencia — el syllabus no coincide con el curso dictado

Contraste entre lo que promete el documento y lo que existe en el repositorio (verificado por grep sobre los 13 módulos + los tres HTML del proyecto integrador):

| Syllabus dice | Realidad del repositorio |
|---|---|
| **S3: Introducción a Flask** (sesión completa) | No hay sesión de Flask. El módulo 3 es **POO y Clases**, tema que el syllabus no menciona en ninguna semana. |
| **S12: Deep Learning con TensorFlow/Keras** | No existe material. `TensorFlow` sólo aparece como mención en el módulo 1 y en el spec del proyecto. `Deep Learning` aparece **únicamente en el syllabus**. |
| **S13: Procesamiento asíncrono / BackgroundTasks** | Sin material propio; sólo mención dentro del módulo 6 (FastAPI). |
| **S14: Integración de LLMs (OpenAI/HuggingFace)** | `OpenAI` y `HuggingFace` aparecen **únicamente en el syllabus**. Cero material. |
| **16 semanas** | 13 módulos numerados + proyecto integrador. El mapeo semana↔módulo no existe y no es 1:1. |
| **Railway** (16 menciones; Render: 0) | El proyecto real exige **Render free-tier** (13-14 menciones). El módulo 12 enseña Railway (48) y Render (5). |
| **Proyecto: "API de Datos con IA", dataset libre, individual** | **Proyecto Integrador de Teoría del Riesgo**: arquitectura de 5 capas, 16 endpoints mínimos, ≥5 activos con 2 años de histórico vía API, equipos de máx. 2, 20 días calendario. |
| **Rúbrica: 40% arquitectura / 30% reproducibilidad IA / 30% despliegue** | **16 criterios sobre 5.0**, con pesos que el syllabus no refleja: sustentación oral 15%, backend 10%, VaR+CVaR+Kupiec 7%, Markowitz 7%, ML+Singleton 7%, Docker+CI 6%, GARCH 6%, CAPM 6%, renta fija 6%… |
| **4 entregables** (repo, Dockerfile, URL, Swagger) | **6 entregables**, incluyendo dashboard frontend, informe ejecutivo PDF (≤5 pág) y sustentación oral de 20-25 min. |
| — | **Dashboard Streamlit/Shiny/Dash obligatorio**: ausente del syllabus. |
| — | **GitHub Actions / CI obligatorio**: ausente del syllabus. |
| — | **Política de uso de IA** explícita en el proyecto: ausente del syllabus. |
| — | Contenidos financieros que el proyecto evalúa (GARCH, Markowitz, CAPM, VaR, Black-Scholes, Nelson-Siegel): **ausentes del syllabus**, que no menciona la articulación con Teoría del Riesgo. |

El efecto neto: un estudiante que planifique su semestre con este syllabus **se prepara para un curso distinto del que va a cursar y para un proyecto distinto del que se le va a calificar**. Éste es el problema más grave del documento, por encima del fallo técnico.

### 1.3 Elementos formales ausentes

No aparecen en el syllabus, ni en ningún otro material del repositorio:

- **Identificación de la asignatura**: código, número de créditos, horas presenciales/autónomas oficiales, periodo académico, prerrequisitos, correquisitos.
- **Datos del docente**: nombre, correo institucional, horario de atención/tutoría.
- **Sistema de evaluación del curso completo**: sólo se detalla la rúbrica del proyecto final. No hay cortes, ni pesos por corte, ni cuánto vale el proyecto sobre la nota definitiva, ni qué otras evaluaciones existen.
- **Resultados de aprendizaje a nivel de asignatura** (los hay por semana, pero no agregados) ni vínculo con las competencias del programa de Estadística.
- **Calendario real**: fechas de inicio/fin, semanas de parciales, festivos, fecha límite de entrega del proyecto (el proyecto habla de 20 días calendario, sin anclaje al calendario).
- **Políticas**: asistencia, entregas tardías, integridad académica, uso de IA generativa.
- **Bibliografía formal**: hay 6 enlaces útiles, pero sin norma de citación, sin distinción entre bibliografía básica y complementaria, sin garantía de acceso abierto.
- **Marco institucional USTA** (identidad tomista / enfoque humanista), habitual en el formato institucional.

### 1.4 Gráficas — pertinencia y calidad (la parte más débil)

**Gráfico 1 — "Progresión de Complejidad" (líneas):**

- Los datos son literalmente inventados; el propio código lo admite: `// Estimated values`.
- El eje Y dice "Nivel (1-10)" **sin definición operativa**: no se sabe qué mide, ni respecto de qué, ni quién lo estimó.
- **Es internamente incoherente con el propio syllabus.** La complejidad cae a **5** en S15 —la semana de OAuth2, JWT, hardening de Docker y usuario no-root, discutiblemente la más difícil del curso— y salta a **9** en S16, que el `syllabusData` describe como `theory: "N/A - Sesión de Demos"`. La curva declara que la semana más compleja del semestre es la de presentaciones.
- "Autonomía Requerida" crece monótonamente de 1 a 10, pero la interfaz declara **trabajo autónomo constante de 8 h** en las 16 semanas. Las dos afirmaciones se contradicen dentro de la misma página.
- El `fill: true` sobre una escala ordinal inventada sugiere una precisión de medición que no existe.
- Sin alternativa textual: es un `<canvas>` inaccesible para lector de pantalla (WCAG 1.1.1).

**Gráfico 2 — "Distribución de Contenidos IA" (dona 60/30/10):**

- **Porcentaje ¿de qué?** El denominador no está definido: no son semanas, no son horas, no son créditos.
- **Es falso contra el propio curso.** Declara 30% Deep Learning y 10% LLMs, cuando no existe material de ninguno de los dos y la semana de DL está marcada como *"Opcional"* en su propio trabajo autónomo. Contado por semanas, S11/S12/S14 darían ≈33/33/33; contado por material existente, sería ≈100/0/0.
- Una dona de tres categorías comunica menos que una tabla o una barra apilada.
- Ninguno de los dos gráficos usa la paleta USTA declarada (usan indigo `#4F46E5`, ámbar, azul/púrpura/esmeralda) → choca con la identidad visual que el documento dice adoptar.

**Conclusión sobre las gráficas: son decorativas, no informativas.** Ocupan el lugar más valioso de la página (arriba, antes del cronograma) para no responder ninguna pregunta que un estudiante se haga realmente. Las preguntas que sí se hace —*¿qué necesito saber antes de qué? ¿en qué se me va el tiempo? ¿qué se me evalúa y cuándo?*— no tienen gráfico.

### 1.5 Calidad narrativa

- **Fortaleza real**: el párrafo de apertura tiene una tesis clara y bien dirigida ("estudiantes de estadística con sólidos conocimientos matemáticos pero sin experiencia en ingeniería de software"). Es el mejor texto del documento.
- A partir de la semana 5 la prosa degenera en **lista de temas separada por puntos**; se pierde la voz que promete el encabezado.
- **Notas internas filtradas al texto del estudiante**: `"N/A - Sesión de Demos"`, `"(la importancia sin Docker... aún)"`, `"Opcional: Si el proyecto usa DL..."`. Son anotaciones de planeación, no redacción dirigida a quien lee.
- **Falta el argumento más fuerte que tiene el curso**: por qué un estadístico —no un ingeniero— necesita esto. No hay conexión con empleabilidad, con investigación reproducible, ni con Teoría del Riesgo.
- **Falta una sección de "lo que este curso NO cubre"**, muy útil para gestionar expectativas (no es un curso de ML, no es un curso de frontend, no cubre Kubernetes…).
- **Los tooltips definen lo fácil y no lo difícil**: explican "ingeniería de software" y "FastAPI", pero no ASGI, WSGI, singleton, PaaS, ORM, CI/CD, event loop — que son los términos que un estadístico no conoce.
- Los verbos de los resultados de aprendizaje no siguen una taxonomía consistente (mezclan "Configurar", "Interpretar", "Asegurar", "Defender") — corregible con una pasada de homogeneización.

### 1.6 Accesibilidad y UX

- **Las tarjetas de semana son `<div>` con `click`**: no reciben foco, no responden a teclado, sin `role="button"` ni `tabindex`. Fallo WCAG 2.1.1 — el cronograma completo es inoperable sin ratón.
- Los botones de filtro no exponen estado (`aria-pressed`) y la lógica depende de `e.target`, frágil ante clics sobre nodos hijos.
- Tooltips sólo en `:hover`: inaccesibles por teclado y en táctil.
- `h-[800px]` fijo en el grid del cronograma: en pantallas pequeñas atrapa el scroll y comprime el detalle.
- Sin hoja de impresión: un syllabus se imprime y se convierte a PDF, y hoy saldría roto.
- Contraste dudoso en `text-white/70` sobre el degradado del header.

### 1.7 Mantenibilidad

- El índice del `README.md` (13 módulos) y el cronograma del syllabus (16 semanas) son **dos fuentes de verdad que ya divergieron**.
- **El syllabus no enlaza a ningún material del curso.** Cada tarjeta semanal debería abrir su módulo HTML; hoy el estudiante tiene que adivinar la correspondencia.

---

## 1.bis Estado tras la migración a LP-CORE (2026-08-06)

El syllabus se reconstruyó sobre `lp-base.html`. El archivo anterior quedó en
`0_Syllabus_P_A_IA.html.bak`. Qué cerró la migración, de los hallazgos de §1:

| Hallazgo | Estado |
|---|---|
| §1.1 Fallo de Tailwind, tipografía, identidad | **Cerrado** — LP-CORE carga Tailwind de forma síncrona y trae la paleta y Montserrat de fábrica |
| §1.2 S3 prometía Flask | **Cerrado** — la semana 3 es POO y Clases (módulo 3), con nota que explica el cambio |
| §1.2 S12 y S14 fantasma (DL, LLMs) | **Cerrado** — reclasificados como contenidos de extensión, con su salida en la bonificación |
| §1.2 Railway frente a Render | **Cerrado** — Render es el canónico en todo el documento |
| §1.2 Proyecto genérico | **Cerrado** — es el Integrador de Riesgo: 5 capas, 6 entregables, equipos de 2, 20 días |
| §1.2 Rúbrica 40/30/30 | **Cerrado con advertencia** — publicados los 16 criterios; ver riesgo de las tres rúbricas |
| §1.2 Sin enlace al material | **Cerrado** — 15 de 16 semanas enlazan a su módulo; la 16 es la sustentación |
| §1.4 Gráficas inventadas | **Cerrado** — las dos nuevas se calculan de los datos del propio documento |
| §1.5 Narrativa y notas internas | **Cerrado** — motivación por sección, apertura reescrita, sección «lo que no cubre» |
| §1.6 Cronograma inoperable por teclado | **Cerrado** — `Tabs` y `Accordion` de LP-CORE son botones nativos |
| §1.6 Tooltips solo con hover | **Cerrado** — `Termino` de LP-CORE |
| §1.3 Identificación institucional | **Cerrado** (2026-08-06) — código 28549, 4 créditos, sin prerrequisitos, correo y horario de atención. Las horas se derivan de los créditos |
| §1.3 Cortes y peso del proyecto | **Cerrado** (2026-08-06) — cortes I y II 30 % cada uno, corte III 40 % (entregables 20 %, sustentación 80 %). El aporte de cada componente a la definitiva se calcula, no se escribe |
| §1.6 Hoja de impresión | **Abierto** — LP-CORE no la trae; el documento es de pantalla |
| §1.7 Fuente única con el README | **Abierto** — el README sigue listando 13 módulos y el syllabus 16 semanas |

**Verificación ejecutada:** bloque LP-CORE idéntico byte a byte al de la plantilla
(SHA-256 `019f1df2…`); las 5 secciones montan con contenido; las 2 gráficas Plotly
dibujan; los 15 enlaces a material resuelven; a 375 px hay 367 px de contenido sin
desborde horizontal en ninguna sección; ningún componente usado sin definir; ningún
uso de color como texto sin confirmar; los 5 iconos existen en el catálogo.

---

## 2. Plan de mejora

Orden por dependencias: primero lo que impide leer el documento, luego lo que lo hace falso, luego lo que lo hace mejor.

> **Nota (2026-08-06).** Las Fases 2 a 6 quedaron absorbidas por la migración a
> LP-CORE (D5). La tabla de §1.bis dice qué cerró y qué sigue abierto. Lo que resta
> es la Fase 1 (bloqueada por el formato institucional) y los tres puntos abiertos.

### Fase 0 — Reparación técnica (bloqueante) — ✅ EJECUTADA 2026-08-06

**T0.1 · Restaurar el pipeline de Tailwind** — ✅
Quitado `defer` de `<script src="https://cdn.tailwindcss.com">`, dejando el `tailwind.config` inline después del CDN (patrón documentado del Play CDN). Se añadió comentario en el archivo explicando por qué no debe volver a diferirse.
- [x] La consola no reporta `ReferenceError`.
- [x] `window.tailwind.config.theme.extend.colors` contiene `primary`, `secondary`, `navy`, `gold` (`primary === '#3D008D'`).
- [x] `section.grid → display: grid` (antes `block`).
- [x] `main → max-width: 1280px` (antes `none`).
- [x] `body → font-family: Montserrat…` (antes `Times`).
- [x] `#mobileMenu → background: rgb(0,26,77)` — `bg-navy` ya resuelve a la paleta USTA (antes transparente).
- [x] Hojas de estilo: 4 (antes 3; faltaba la de Tailwind).

**T0.2 · Blindar la tipografía y el color base sin depender del CDN** — ✅
`font-family` declarada en `body`, más reglas de respaldo con `:where()` (**especificidad cero**, para que Tailwind siempre gane cuando sí carga) sobre `main`, el `h1` y el subtítulo del header. El escudo se dimensiona en CSS propio y no en clases de Tailwind.
- [x] Con la hoja de Tailwind desactivada, el documento sigue siendo legible: Montserrat, `main` contenido a 1280 px con padding, `h1` blanco sobre el degradado navy, subtítulo a 70 % de blanco, escudo a 44×44 px (no a 800 px).
- **Verificación ejecutada:** desactivada la hoja inyectada por el CDN en tiempo de ejecución y remedidas las propiedades computadas.

**T0.3 · Metadatos e identidad** — ✅
`og:image` y `twitter:image` apuntan ahora al escudo publicado en GitHub Pages, con `width`/`height`/`alt`. El icono genérico `fa-network-wired` del header se sustituyó por `Logo_USTA.png` en un recuadro `#ECF2F6` (el mismo fondo del PNG, para que se vea integrado sobre el header navy).
- [x] Ninguna referencia a `via.placeholder.com` en el documento.
- [x] El escudo carga y se renderiza a 44×44 px.
- [ ] **Pendiente del docente:** `Logo_USTA.png` sigue **sin trackear en git**. Si se hace push sin añadirlo, el escudo y la previsualización social se romperán en GitHub Pages.

> ### Checkpoint 0 — el documento se ve — ✅ SUPERADO
> Consola limpia · paleta USTA aplicada · 16 tarjetas de semana y vista de detalle renderizando · 2 gráficos dibujados · verificado en navegador.

### Fase 1 — Verdad institucional

> **Ajustada por D4.** Este HTML es el *companion* del estudiante; el formato institucional USTA es un documento aparte. La Fase 1 no duplica ese formato: extrae de él lo que el estudiante consulta a diario y enlaza al oficial para el resto. **En espera de la plantilla institucional.**

**T1.1 · Bloque de identificación de la asignatura (versión mínima)**
Añadir sección superior con: código, créditos, horas presenciales y autónomas oficiales, periodo, prerrequisitos, docente, correo institucional, horario de atención, y **enlace al syllabus institucional oficial**.
- [ ] Los datos coinciden con el documento institucional (no estimados).
- [ ] Las horas declaradas son consistentes con las que muestra el detalle semanal (hoy: 60 min teoría + 120 min práctica + 8 h autónomo → 48 h presenciales + 128 h autónomas = 176 h; **verificar contra los créditos reales** — si no cuadran, corregir el detalle semanal, no la identificación).
- [ ] Existe un enlace visible al formato oficial, de modo que el companion nunca se lea como fuente normativa.
- **Dependencias:** plantilla institucional (pendiente de entrega) · **Tamaño:** S

**T1.2 · Sistema de evaluación del curso completo**
Hoy sólo existe la rúbrica del proyecto. Documentar cortes, pesos y qué evaluación cae en cada uno; declarar el peso del proyecto integrador sobre la nota definitiva.
- [ ] Los porcentajes de todo el curso suman 100%.
- [ ] Cada evaluación tiene semana asignada en el cronograma.
- **Tamaño:** S

**T1.3 · Políticas**
Asistencia, entregas tardías, integridad académica y **uso de IA generativa** (alinear con la política ya redactada en el proyecto integrador: permitida y fomentada, con defensa oral obligatoria y sección "Uso de herramientas de IA" en el README).
- [ ] La política de IA del syllabus y la del proyecto no se contradicen.
- **Tamaño:** S

> ### Checkpoint 1 — revisión con coordinación académica antes de continuar

### Fase 2 — Coherencia con el curso realmente dictado

**T2.1 · Mapear las 16 semanas a los 13 módulos** *(D1: se conservan las 16 semanas)*
Añadir al `syllabusData` los campos `material` (ruta al HTML del módulo o `null`) y `tipo` (`sesion` | `taller` | `evaluacion` | `asesoria`). Los módulos que ocupan dos semanas se declaran como tales; las tres semanas sin módulo propio se tipifican explícitamente.
- [ ] Las 16 semanas tienen `material` apuntando a un archivo existente, o `tipo ≠ sesion` con justificación visible al estudiante.
- [ ] Ninguna semana promete un tema del que no exista material ni lectura asignada.
- [ ] La numeración de los 13 módulos **no cambia** (el material ya está distribuido y enlazado desde el README).
- **Verificación:** script que recorra `syllabusData` y compruebe que cada `material` resuelve a un archivo del repositorio.
- **Dependencias:** ninguna · **Tamaño:** M

**T2.2 · Corregir S3 y añadir POO**
Sustituir la sesión de Flask por **POO y Clases** (módulo 3 real); conservar Flask como comparación conceptual dentro de la semana de FastAPI.
- [ ] "POO / Clases" aparece como contenido con RA propio.
- [ ] Flask ya no figura como sesión completa.
- **Tamaño:** S

**T2.3 · Reclasificar Deep Learning (S12) y LLMs (S14) como extensión** *(D3)*
Reescribir ambas semanas como contenido **opcional / de extensión** con lectura asignada y sin promesa de sesión guiada. No se produce material nuevo. Las horas presenciales liberadas se reasignan (ver riesgo asociado) a despliegue, CI y acompañamiento del proyecto, que es donde está el peso real de la rúbrica.
- [ ] Ninguna semana "fantasma": todo tema prometido tiene material o lectura explícita.
- [ ] Ambas semanas quedan marcadas visualmente como extensión, no como sesión obligatoria.
- [ ] Se enlaza la bonificación del proyecto (LSTM/MLP, hasta +0.5) como salida natural para quien quiera profundizar.
- [ ] El destino de las horas presenciales liberadas queda declarado en el cronograma.
- **Dependencias:** T2.1 · **Tamaño:** S *(reducido de M por D3)*

**T2.4 · Unificar la plataforma PaaS**
Render como canónico (es lo que exige el proyecto y lo que se evalúa); Railway como alternativa mencionada. Hoy el syllabus dice Railway 16 veces y Render 0.
- [ ] Todas las menciones del syllabus nombran Render primero.
- [ ] Coherente con el módulo 12 y con el spec del proyecto.
- **Tamaño:** XS

**T2.5 · Enlazar cada semana con su material**
Añadir campo `material` al `syllabusData` y renderizar un botón "Abrir material de la sesión" en la vista de detalle.
- [ ] Las 16 tarjetas enlazan a su HTML o declaran que no hay.
- [ ] Ningún enlace roto (verificable con un script de comprobación de rutas).
- **Dependencias:** T2.1 · **Tamaño:** S

> ### Checkpoint 2 — trazabilidad completa
> Tabla semana → módulo → material verificada, sin huecos silenciosos.

### Fase 3 — Proyecto y rúbrica reales

**T3.1 · Reescribir la sección "Proyecto Final"** *(D2: el Integrador es EL proyecto)*
Sustituir la descripción genérica por el **Proyecto Integrador de Teoría del Riesgo**: 5 capas, 16 endpoints mínimos, ≥5 activos con 2 años de histórico vía API, equipos de máximo 2, 20 días calendario, stack obligatorio (Python 3.11.9, FastAPI, Pydantic v2, SQLAlchemy+SQLite, Docker, Render free-tier, GitHub Actions, Streamlit/Shiny/Dash).
- [ ] Los 6 entregables reales aparecen (backend, dashboard, Docker+URL+CI, repo, informe PDF ≤5 pág, sustentación 20-25 min).
- [ ] Las tres fases del semestre se re-anclan a los hitos reales del proyecto.
- [ ] Se declara la articulación con Teoría del Riesgo y la matrícula paralela que el proyecto supone.
- [ ] El syllabus enlaza al spec vivo (`Proyecto_Integrador_Riesgo_Python_CIII_Riesgo.html`) en vez de reproducirlo, para no crear una tercera fuente de verdad.
- **Tamaño:** M

**T3.2 · Sustituir la rúbrica 40/30/30**
Publicar los 16 criterios con sus pesos (o una agrupación fiel que los preserve), incluidas las bonificaciones (hasta +0.5).
- [ ] Los pesos publicados suman lo mismo que la rúbrica operativa.
- [ ] Se identifican los criterios de contenido nuevo (★) frente a los de cursos previos.
- **Dependencias:** T3.1 · **Tamaño:** S

**T3.3 · Matriz de alineación RA → semana → criterio de rúbrica**
Tabla que muestre qué semana habilita qué criterio evaluado. Es el artefacto que pide acreditación y el que más ayuda al estudiante.
- [ ] Todo criterio de la rúbrica tiene al menos una semana que lo prepara.
- [ ] Toda semana contribuye al menos a un criterio (o se justifica por qué no).
- **Dependencias:** T2.1, T3.2 · **Tamaño:** M

> ### Checkpoint 3 — un estudiante puede predecir su nota leyendo el syllabus

### Fase 4 — Gráficas: de decorativas a informativas

Principio rector: **ningún gráfico con datos inventados**. Todo dato visualizado debe derivarse del `syllabusData` o de la rúbrica, calculado en tiempo de render, no escrito a mano.

**T4.1 · Retirar la dona 60/30/10**
Sustituir por **distribución de horas presenciales por módulo** (Fundamentos / APIs / IA / Proyecto), calculada contando semanas × horas declaradas, con el denominador impreso ("sobre 48 h presenciales").
- [ ] Los porcentajes se calculan desde `syllabusData`, no se escriben a mano.
- [ ] El denominador es explícito en el subtítulo del gráfico.
- **Dependencias:** T2.1, T2.3 · **Tamaño:** S

**T4.2 · Reemplazar la curva de complejidad inventada**
Opción recomendada: **mapa de prerrequisitos / ruta de aprendizaje** (qué desbloquea qué: HTTP → Pydantic → FastAPI → DI → Persistencia → Tests → Docker → Deploy → ML). Responde la pregunta que el estudiante sí se hace.
Si se conserva una curva de carga, debe traer definición operativa publicada (p. ej. "horas estimadas de trabajo autónomo por semana", que además obliga a que el 8 h fijo deje de ser fijo).
- [ ] Cero valores marcados como "estimados" sin definición.
- [ ] Ninguna afirmación del gráfico contradice el `syllabusData` (test explícito: la semana de demos no puede ser la de mayor complejidad).
- **Dependencias:** T2.1 · **Tamaño:** M

**T4.3 · Línea de tiempo de hitos y entregables**
Gráfico o banda temporal con fechas reales: entregas parciales del proyecto, cortes, semana de sustentación.
- [ ] Las fechas coinciden con el calendario académico y con los 20 días del proyecto.
- **Dependencias:** T1.2, T3.1 · **Tamaño:** S

**T4.4 · Paleta y accesibilidad de los gráficos**
Aplicar la paleta USTA a los tres gráficos y añadir alternativa textual (tabla accesible o `aria-describedby`) a cada `<canvas>`.
- [ ] Ningún color fuera de la paleta declarada.
- [ ] Cada gráfico tiene equivalente textual navegable por lector de pantalla.
- [ ] Contraste de series verificado (≥3:1 entre series adyacentes).
- **Dependencias:** T0.1 · **Tamaño:** S

> ### Checkpoint 4 — cada gráfico responde una pregunta real y ningún dato es inventado

### Fase 5 — Narrativa

**T5.1 · Reescribir "Visión General"**
Tres párrafos: (1) por qué un **estadístico** necesita esto —empleabilidad, reproducibilidad, investigación—; (2) qué producto concreto tendrá al final y su articulación con Teoría del Riesgo; (3) qué **no** cubre el curso.
- [ ] Existe sección explícita "Lo que este curso no cubre".
- [ ] La articulación con Teoría del Riesgo se nombra en la apertura.
- **Tamaño:** S

**T5.2 · Bisagras narrativas por módulo**
Un párrafo de entrada por cada bloque (Fundamentos / APIs / IA / Proyecto) que explique por qué ese bloque viene después del anterior.
- [ ] Cuatro párrafos, uno por filtro de módulo, visibles al filtrar.
- **Tamaño:** S

**T5.3 · Limpieza de registro**
Eliminar notas internas del texto del estudiante (`"N/A - Sesión de Demos"`, `"(la importancia sin Docker... aún)"`, `"Opcional: Si..."`) y homogeneizar los verbos de los RA bajo una única taxonomía.
- [ ] Cero cadenas con marcas de planeación interna.
- [ ] Todos los RA empiezan por verbo observable del mismo nivel taxonómico.
- **Tamaño:** S

**T5.4 · Ampliar el glosario**
Tooltips para ASGI, WSGI, ORM, PaaS, singleton, event loop, CI/CD, contenedor.
- [ ] Todo acrónimo técnico tiene definición en su primera aparición.
- **Tamaño:** S

### Fase 6 — Accesibilidad, impresión y mantenibilidad

**T6.1 · Cronograma operable por teclado**
Convertir las tarjetas de semana en `<button>` (o `role="button"` + `tabindex="0"` + manejo de Enter/Espacio); añadir `aria-pressed` a los filtros y hacerlos robustos ante `e.target` hijo.
- [ ] Navegación completa del cronograma sólo con teclado.
- [ ] El estado activo se anuncia por lector de pantalla.
- **Tamaño:** S

**T6.2 · Tooltips accesibles**
Que se muestren también en `:focus-visible`.
- [ ] Todo tooltip alcanzable por teclado.
- **Tamaño:** XS

**T6.3 · Responsive e impresión**
Sustituir `h-[800px]` fijo por altura adaptativa; añadir hoja `@media print` que despliegue las 16 semanas en flujo lineal.
- [ ] En 375 px de ancho no hay scroll horizontal ni contenido atrapado.
- [ ] El PDF impreso contiene las 16 semanas completas, con logo y datos de identificación.
- **Tamaño:** S

**T6.4 · Bibliografía formal**
Convertir los 6 enlaces en bibliografía básica y complementaria con citación normalizada; verificar al menos un recurso de acceso abierto; revisar vigencia de todos los enlaces.
- [ ] Cero enlaces rotos.
- [ ] Distinción básica/complementaria explícita.
- **Tamaño:** S

**T6.5 · Fuente única de verdad**
Que la tabla de módulos del `README.md` y el cronograma del syllabus se deriven del mismo origen, o dejar nota de sincronización obligatoria en ambos.
- [ ] Un cambio de módulo obliga a un solo punto de edición, o el desajuste se detecta automáticamente.
- **Dependencias:** T2.5 · **Tamaño:** M

> ### Checkpoint final
> Consola limpia · navegación por teclado completa · impresión correcta · cero divergencias entre syllabus, README y proyecto · cero datos inventados en gráficos.

---

## 3. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Los datos institucionales (créditos, cortes) no coinciden con las 176 h implícitas del syllabus | Alto | Resolver T1.1 **antes** de T4.1: la distribución de horas depende de ellos. Si hay desajuste, se corrige el detalle semanal, no la identificación |
| El companion (este HTML) y el formato institucional divergen con el tiempo | Alto | T1.1 exige enlace visible al oficial y nota de precedencia normativa; ningún dato evaluativo se escribe sólo aquí |
| Las horas liberadas por D3 (S12 y S14) se perciben como relleno | Medio | T2.3 obliga a declarar su destino en el cronograma (despliegue, CI, acompañamiento de proyecto), no a dejarlas en blanco |
| El mapeo 16→13 deja semanas sin módulo que parezcan vacías | Medio | T2.1 tipifica cada semana (`taller`/`evaluacion`/`asesoria`) con justificación visible, en vez de dejarlas sin material y sin explicación |
| Publicar los 16 criterios abruma al estudiante en la primera lectura | Medio | Vista agrupada por defecto (4 bloques) con detalle desplegable |
| D2 asume matrícula paralela en Teoría del Riesgo; si algún estudiante no la cursa, queda sin proyecto viable | Medio | Verificar la lista de matriculados al inicio del semestre; si aparece el caso, activar la vía alterna descartada hoy |
| Dependencia total de CDNs externos en aula sin buena conectividad | Medio | T0.2 (degradación digna) + considerar vendorizar Tailwind/Chart.js localmente |

---

## 4. Preguntas abiertas

Resueltas el 2026-08-06: canon de 16 semanas (D1), proyecto integrador como único proyecto (D2), DL y LLMs como extensión (D3), existencia de formato institucional (D4).

Pendientes:

Resuelta en la migración: las 3 semanas sin módulo propio son dos talleres dirigidos
de proyecto (14 y 15, apoyados en los materiales de las sesiones II y III) y la
sustentación (16). **Su ubicación en el calendario real está por confirmar**: el
proyecto es transversal y los talleres son puntos de revisión, no su inicio.

1. **¿Cuál de las tres rúbricas gobierna la nota de esta asignatura?** El archivo más
   reciente (`..._CIII_Riesgo.html`, 10 criterios) elimina todos los criterios de
   ingeniería. El documento publica la de 16 con una advertencia visible.
   → **el más urgente**: es lo que los estudiantes leerán como su evaluación
Resueltos por D10: la doble medición de la sustentación (rúbrica 20-80, criterio 16
retirado), el peso de la primera entrega (20 % del corte II) y las semanas de los
cortes (5, 11 y 16, ancladas a las fechas límite).

Resueltos el 2026-08-06 (segunda tanda): el periodo es **2026-II** (corregido en
título, metas y `CONFIG`, 5 apariciones) y **no hay semanas de receso** — el anclaje
de calendario (semana 1 = 8 de agosto, cortes en 5/11/16) pasó de supuesto a dato
confirmado.

2. **Sincronizar la rúbrica del spec** `Proyecto_Integrador_Riesgo_Python_CIII.html`
   (aún muestra 16 criterios con sustentación al 15 %) — en curso en sesión aparte
   (chip iniciado por el docente).
3. **Confirmar el reparto de la sesión de 4 h** (hoy 60 min de teoría + 180 min de
   práctica guiada). Es un solo par de números en `CONFIG`; todo lo demás se recalcula.

Cerrado el 2026-08-06 (tercera tanda): **`README.md` e `index.html` sincronizados** —
periodo 2026-II, mapeo semana↔módulo, fechas de corte, talleres de proyecto en las
semanas 14 y 15. Las URLs del repositorio (`…-20261`) se dejaron intactas por ser
nombres reales de GitHub.

## 5. Continuación: auditoría de los 13 módulos

El syllabus está cerrado, pero **los módulos que describe nunca se han auditado**.
Un barrido de sólo lectura ya encontró tres módulos con el número de semana
equivocado en el `<title>`, cuatro stacks técnicos distintos conviviendo y el módulo
12 enseñando Railway (48 menciones) contra el Render que exige el proyecto.

Plan detallado en **`PLAN_AUDITORIA_MODULOS.md`**: siete criterios, tres fases y tres
opciones de alcance. Las fases 1 y 2 no modifican nada.
