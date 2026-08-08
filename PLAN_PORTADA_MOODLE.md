# Plan de implementación: Banner de portada Moodle — Python para APIs e IA (USTA 2026-I)

## Overview

Producir un **banner de cabecera de 1920×480 px (4:1)** para el aula Moodle del curso
*Python para APIs e IA*. La pieza se construye en **dos capas**: ComfyUI genera la
ilustración de fondo (red de datos abstracta, **sin texto**), y el título, el logo USTA y
la paleta institucional se componen encima en HTML/CSS y se exportan a PNG con Chrome
headless en la medida exacta.

## Decisiones de arquitectura

- **AD1 — Dos capas, no una.** Ni SDXL Turbo ni Flux schnell renderizan de forma fiable
  «Python para APIs e IA» con tildes correctas, y el logo USTA es imposible de generar.
  El fondo es raster generado; el texto y la marca son vectoriales/HTML. Consecuencia
  práctica: cambiar el semestre o el título después **no exige regenerar la imagen**.

- **AD2 — Concepto visual: red de datos abstracta.** Nodos luminosos conectados por hilos
  de luz, profundidad de campo, degradado morado→magenta sobre azul profundo. Elegido por
  riesgo bajo de artefactos (sin caras, manos ni texto) y porque admite una **zona
  tranquila a la izquierda** donde asentar el título.

- **AD3 — Render a 2× y downsample.** El HTML se captura a 3840×960 con
  `--force-device-scale-factor=2` y se reduce a 1920×480 con Pillow (Lanczos). El texto
  queda nítido; el fondo, deliberadamente suave.

- **AD4 — Flux genera a 1216×832 y se recorta a 4:1.** Flux schnell hace OOM por encima de
  ~1280×1280 en este equipo. Se genera en apaisado seguro y la composición HTML lo usa con
  `background-size: cover`, recortando en vertical (inocuo en una imagen abstracta). El
  upscale efectivo es 1.58×, tolerable en una composición atmosférica.

- **AD5 — El logo va sobre un chip claro.** `Logo_USTA.png` es **RGB sin canal alfa**, con
  fondo gris azulado `(236,242,246)`. En vez de hacer keying (que ensucia los bordes
  antialiaseados), se coloca sobre un rectángulo claro redondeado. El keying por tolerancia
  queda como plan B (Task 1).

---

## Hallazgos verificados que condicionan el plan

| # | Hallazgo | Evidencia |
|---|---|---|
| H1 | ComfyUI operativo, ambos modelos presentes | `sd_xl_turbo_1.0_fp16.safetensors`, `flux1-schnell-Q4_K_S.gguf`. Servidor apagado (auto-arranca). |
| H2 | `Logo_USTA.png` **no tiene transparencia** | 800×800, modo `RGB`. Esquinas = `(236,242,246)`. |
| H3 | **Conflicto de paleta.** El logo es azul `#00478C` + rojo `#DF040B`; el syllabus y los 13 módulos HTML usan morado `#3D008D` + magenta `#ED1E79` | Colores dominantes del PNG vs. `grep` de hex en `0_Syllabus_P_A_IA.html`. |
| H4 | Chrome y Pillow 12.1.0 disponibles para la composición headless | `/Applications/Google Chrome.app/...` OK. |
| H5 | No existe carpeta de assets en el repo | Se creará `assets/portada/`. |

---

## Task list

### Fase 1 — Fundación (tooling de composición)

#### Task 1: Preparar el activo del logo

**Description:** Dejar el logo listo para superponerse sobre fondo oscuro, resolviendo H2.
Ruta principal: recortar el margen muerto y generar `logo_usta_chip.png` (logo sobre chip
claro redondeado). Ruta B si el chip no convence visualmente: keying por tolerancia del
color de fondo a alfa.

**Acceptance criteria:**
- [ ] Existe `assets/portada/logo_usta_chip.png` sin franja de fondo sobrante alrededor del sello.
- [ ] El activo se lee correctamente al superponerse sobre `#001A4D` (sin halo ni caja gris visible).

**Verification:**
- [ ] `python3 -c "from PIL import Image; im=Image.open('assets/portada/logo_usta_chip.png'); print(im.size, im.mode)"` reporta modo `RGBA`.
- [ ] Inspección visual del PNG sobre fondo oscuro.

**Dependencies:** Ninguna
**Files:** `assets/portada/logo_usta_chip.png`, `scripts/portada/prep_logo.py`
**Scope:** S (1-2 archivos)

---

#### Task 2: Pipeline de composición HTML → PNG exacto

**Description:** Plantilla HTML de 1920×480 con el fondo como `background-image`, el bloque
de título a la izquierda, el logo a la derecha y la paleta USTA; más un script que la
captura con Chrome headless a 2× y la reduce a la medida exacta. Se construye y se valida
con un **fondo placeholder** (un degradado CSS plano), antes de que exista la ilustración.

**Acceptance criteria:**
- [ ] El PNG resultante mide exactamente 1920×480 px.
- [ ] El título se lee con tildes correctas y sin recortes a ningún ancho de la franja.
- [ ] Cambiar el texto del título en el HTML se refleja en el PNG sin tocar el script.

**Verification:**
- [ ] `python3 -c "from PIL import Image; print(Image.open('assets/portada/banner.png').size)"` → `(1920, 480)`.
- [ ] Zoom al 400 % sobre el título: bordes de letra limpios, sin escalonado.

**Dependencies:** Task 1
**Files:** `scripts/portada/banner.html`, `scripts/portada/render.py`
**Scope:** M (2-3 archivos)

---

### ✅ Checkpoint A — La composición funciona antes de gastar GPU
- [ ] `banner.png` sale a 1920×480 exactos con fondo placeholder.
- [ ] Texto nítido y logo bien asentado.
- [ ] **Revisión con el docente antes de seguir.**

> *Por qué este orden:* la composición es el punto donde más probable es descubrir que el
> texto no cabe o que el logo desentona. Descubrirlo con un degradado CSS cuesta segundos;
> descubrirlo después de 8 renders de Flux cuesta 10 minutos de GPU y obliga a regenerar.

---

### Fase 2 — Ilustración

#### Task 3: Bocetos rápidos con SDXL Turbo

**Description:** 3-4 prompts distintos de la misma dirección (red de datos abstracta),
`--batch 4` cada uno, a 768×768. Objetivo: elegir *dirección*, no calidad final —
densidad de nodos, cuánta profundidad de campo, cuán oscuro el fondo, dónde cae el vacío.

**Acceptance criteria:**
- [ ] Al menos 12 bocetos generados y presentados al docente.
- [ ] Se elige una dirección y se anota qué prompt la produjo.

**Verification:**
- [ ] Cada boceto se abre y se muestra inline.
- [ ] El script reporta seed y parámetros de la variante elegida.

**Dependencies:** Ninguna (paralelizable con Fase 1)
**Files:** salidas en `~/ComfyUI/output/`
**Scope:** S

---

#### Task 4: Render final con Flux schnell

**Description:** Traducir la dirección elegida a un prompt en lenguaje natural para Flux,
generar a 1216×832 con 2-3 semillas. Advertir del tiempo (~60-90 s por imagen; la primera
carga el modelo y tarda más).

**Acceptance criteria:**
- [ ] 2-3 renders a 1216×832 sin artefactos evidentes en la banda central (la que sobrevive al recorte 4:1).
- [ ] La franja izquierda queda oscura y sin detalle competitivo con el título.
- [ ] Seed y prompt registrados.

**Verification:**
- [ ] Recorte 4:1 de prueba con Pillow: la zona del título mantiene contraste suficiente.

**Dependencies:** Task 3
**Files:** `assets/portada/fondo_flux.png`
**Scope:** S

---

### ✅ Checkpoint B — Hay ilustración elegida
- [ ] Fondo seleccionado, sin texto, con zona tranquila a la izquierda.
- [ ] Reproducible (prompt + seed anotados).

---

### Fase 3 — Composición final y entrega

#### Task 5: Componer y exportar el banner

**Description:** Sustituir el placeholder por `fondo_flux.png`, ajustar el `object-position`
del recorte, calibrar el velo de contraste bajo el título y exportar.

**Acceptance criteria:**
- [ ] `assets/portada/banner_1920x480.png` existe, mide 1920×480 y pesa < 1.5 MB.
- [ ] Contraste texto/fondo ≥ 4.5:1 en el área del título.

**Verification:**
- [ ] Medición de contraste sobre los píxeles reales bajo el texto (script con Pillow).
- [ ] Vista previa a tamaño real y al 25 % (cómo se ve en la tarjeta de Moodle).

**Dependencies:** Task 2, Task 4
**Files:** `scripts/portada/banner.html`, `assets/portada/banner_1920x480.png`
**Scope:** S

---

#### Task 6: Documentar reproducibilidad

**Description:** Un `README.md` corto en `assets/portada/` con el prompt exacto, el modelo,
la seed, el tamaño y el comando para regenerar. Sin esto, dentro de seis meses la portada
es irreproducible.

**Acceptance criteria:**
- [ ] El README permite regenerar un fondo equivalente copiando y pegando un comando.
- [ ] Queda anotada la decisión de paleta (ver Q1).

**Verification:**
- [ ] Ejecutar el comando documentado reproduce el fondo con la misma seed.

**Dependencies:** Task 5
**Files:** `assets/portada/README.md`
**Scope:** XS

---

### ✅ Checkpoint C — Entrega
- [ ] Banner listo, verificado y reproducible.
- [ ] Aprobación del docente.

---

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Flux hace OOM por encima de ~1280 px | Medio | AD4: generar a 1216×832 y recortar. Fallback: turbo 768 + upscale Lanczos. |
| El upscale 1.58× suaviza el detalle del fondo | Medio | El concepto elegido es atmosférico y tolera el suavizado; la nitidez la aporta la capa de texto a 2×. |
| El logo sin alfa desentona sobre fondo oscuro | **Confirmado (H2)** | AD5: chip claro. Plan B: keying por tolerancia. |
| Choque de paleta morado/magenta vs. azul/rojo del logo | **Confirmado (H3)** | Decisión abierta Q1. |
| El 4:1 se recorta mal en la tarjeta de curso de Moodle | Medio | Ver Q3. Emitir además un 16:9 desde la misma composición cuesta una línea. |
| Iterar sobre el prompt sin criterio y no converger | Medio | Checkpoint A antes de tocar la GPU; Task 3 elige *dirección*, Task 4 solo *ejecuta*. |

---

## Estado: COMPLETADO (2026-08-06)

Las 6 tareas y los 3 checkpoints se ejecutaron. Entregables en `assets/portada/`, con
reproducibilidad documentada en `assets/portada/README.md`.

Desviaciones respecto al plan, y por qué:

- **Task 3 necesitó dos rondas, no una.** La primera tanda de 16 bocetos colapsó a magenta
  neón: SDXL Turbo ignoró el azul profundo y el resultado leía a banner de cripto. Se
  corrigió liderando el prompt con «dark midnight navy blue» y mandando `hot pink, fuchsia`
  al negativo. La segunda ronda (12 bocetos) dio la dirección buena.
- **La «zona tranquila a la izquierda» se abandonó como instrucción de prompt.** Ninguno de
  los 28 bocetos la respetó. Se resolvió en la capa de composición con el velo degradado,
  que además garantiza contraste independientemente de la ilustración.
- **AD5 revisada: el sello se enmascara por geometría, no por color.** El keying cromático
  planeado semitransparentaba los cuadrantes blancos de la cruz (distan solo ~25 del fondo)
  y el sello se veía gris sobre navy. Un disco antialiaseado lo resuelve exactamente.
- **Se añadió `scripts/portada/verificar.py`**, no previsto. Su primera versión medía el
  contraste sobre el PNG final e informaba 1.00:1 en todo: la región del título contiene el
  propio texto blanco. Corregido re-renderizando el fondo aislado con `--sin-texto`.

## Preguntas abiertas — resueltas

**Q1 — Paleta.** RESUELTA: opción (a), morado/magenta con el sello aislado.
**Q2 — Texto.** RESUELTO: `Python para APIs e IA` / `Facultad de Estadística · Universidad
Santo Tomás · 2026-II`, sin nombre del docente. Nota: **2026-II**, mientras el resto del
repo dice 2026-I.
**Q3 — Uso en Moodle.** RESUELTO: se emiten ambas piezas, 4:1 y 16:9.

<details>
<summary>Enunciado original de las preguntas</summary>

**Q1 — Paleta (bloqueante para Task 4).** El logo USTA es azul `#00478C` + rojo `#DF040B`;
el material del curso es morado `#3D008D` + magenta `#ED1E79`. Tres salidas:
  - **(a)** Mantener morado/magenta (coherente con los 13 módulos HTML) y aislar el logo en
    su chip claro, de modo que la separación se lea como co-branding intencional. *Recomendada.*
  - **(b)** Reorientar la ilustración al azul institucional `#00478C`/`#001A4D` con acentos
    rojos: más fiel a la marca USTA, pero rompe con el material existente del curso.
  - **(c)** Puente: fondo azul profundo con nodos morado→magenta. Concilia ambos, a costa de
    una paleta más cargada.

**Q2 — Texto exacto (bloqueante para Task 2).** ¿Qué debe decir el banner? Propuesta por
defecto, a confirmar o corregir:
  - Título: `Python para APIs e IA`
  - Bajada: `Facultad de Estadística · Universidad Santo Tomás · 2026-I`
  - ¿Se incluye el nombre del docente?

**Q3 — Uso real en Moodle (no bloqueante).** Un 4:1 es correcto como cabecera dentro de la
página del curso, pero si Moodle además lo usa como *imagen de resumen* en la tarjeta del
listado, el tema recorta a una proporción mucho más cuadrada y el título se pierde. Si ese
uso aplica, conviene emitir también la variante 16:9 desde la misma composición.

</details>
