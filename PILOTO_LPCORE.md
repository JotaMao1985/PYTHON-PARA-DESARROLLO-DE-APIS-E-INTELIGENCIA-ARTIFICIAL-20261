# Piloto de migración a LP-CORE — módulo 11

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-08
**Decisión que lo motiva:** Opción B ya + Opción C por bloques durante el semestre, empezando por
un piloto en el módulo 11 para medir antes de comprometer trece migraciones.
**Artefacto:** `_piloto_11_lpcore.html` — **no es material del curso.** El módulo 11 real
(`11_Python_para_APIS_IA_Contenedores_y_Docker.html`) **no se ha tocado**.

---

> **Estado al 2026-08-08 (tarde): el hueco de §2 está cerrado.** Lo que sigue es el piloto tal
> como se escribió, con las cifras corregidas en §2 y una nota de cierre en §5. El detalle del
> arreglo —que resultó ser mayor de lo que este documento suponía— está en
> [`PLAN_LENGUAJES_LPCORE.md`](PLAN_LENGUAJES_LPCORE.md).

## 0. El resultado en una línea

**LP-CORE funciona en este curso, y le falta una pieza concreta y barata: el resaltador no
conoce Dockerfile, YAML ni TOML.** Son 17 de los 186 bloques de código del material, y 14 de
esos 17 son Dockerfiles repartidos entre los módulos 11, 12 y 13.

---

## 1. Qué se construyó

Tres de las once secciones del módulo 11, sobre `lp-base.html`:

| Sección del piloto | Componentes LP-CORE que ejercita |
|---|---|
| Portada y objetivos | `CONFIG`, `Motivacion`, `Box` (info / aviso) |
| 5. Estructura del Dockerfile | `CodeBlock` ×2, `Accordion`, `Termino`, `Box` (tip) |
| Autoevaluación | `MCQ` simple y `MCQ` múltiple, con retroalimentación por opción |

**Verificado en navegador:** monta, la barra lateral y el progreso funcionan («Lección 1 de 3 ·
33 %»), la navegación entre secciones funciona, **0 errores en consola** y **0 px de desborde**.
La portada se compone sola a partir de `CONFIG`: número de capítulo, horas, RA y temas.

---

## 2. El hallazgo: los lenguajes que el resaltador no conoce

`CodeBlock` resuelve el resaltado con `GRAMATICA[lang]` sobre Prism. Lo que trae LP-CORE:

| Declarado en `GRAMATICA` | Gramática de Prism | ¿lo necesita este curso? | ¿cargada? |
|---|---|---|---|
| `pseudo` | `pseudo` | no — es de Lógica de Programación | sí (en JS) |
| `python` | `python` | **sí, ~88 bloques** | sí |
| `r` | `r` | no | sí |
| `vba` | `visual-basic` | no | sí |
| `shell` | `bash` | **sí, el segundo del material** | **NO** ⚠ |
| `text` | *(sin resaltar)* | sí, salidas | n/a |

Y lo que falta:

| Lenguaje | Bloques en el material | Dónde |
|---|---|---|
| **Dockerfile** | **14** | módulos 11 (8), 13 (4) y **12 (2)** |
| **YAML** | 3 | módulo 12 (GitHub Actions, `render.yaml`) |
| **TOML** | 3 | módulos 10 (`pytest.ini`, `pyproject.toml`) y 9 (`[tool.ruff]`) |
| **SQL** | 0 | el SQL del módulo 9 va dentro de `text("SELECT …")`, en Python |

> **Corrección del 2026-08-08.** Las cifras de arriba sustituyen a las primeras de este
> documento, que contaban 212 bloques, 22 Dockerfiles y 112 de Python. El conteo original sólo
> miraba etiquetas `<pre>`, y cinco archivos —módulos 3, 4, 6, 13 y el syllabus— son React y
> usan `<CodeBlock code={variable}>`: el módulo 13, con 26 bloques, entró como si tuviera uno.
> TOML no estaba inventariado, y los que se contaron como SQL eran falsos positivos (una línea
> `select(...)` de Python y un `select = [...]` de TOML).
>
> Y el hallazgo que este documento no vio: **`shell` estaba roto desde el principio.** La clave
> estaba declarada, pero `prism-bash` no se cargaba en ningún `head` y el núcleo de Prism sólo
> trae markup, css, clike y javascript. Es el mismo defecto silencioso descrito abajo, actuando
> sobre una clave que sí existía — y sobre el segundo lenguaje del material.

En el piloto esto se ve así: pedí `lang="docker"`, el código **se muestra correctamente pero sin
un solo token resaltado** — `GRAMATICA` no tiene la clave, así que cae a `escaparHtml` y la
etiqueta pasa a «Salida». No falla, no avisa: simplemente se degrada en silencio.

**Coste estimado entonces:** tres entradas en `GRAMATICA`, tres en `LANG_META` y cargar tres
componentes de Prism, que existen de serie (`prism-docker`, `prism-yaml`, `prism-sql`).

**Lo que costó de verdad:** cinco claves y cinco componentes —`bash` incluido—, una comprobación
nueva en `ensamblar.py` que deriva de `GRAMATICA` las gramáticas que el `head` debe cargar, y una
regla de CSS. Esta última no se veía venir: Prism etiqueta la cabecera de sección de TOML como
`class="token table"` y Tailwind tiene una utilidad `.table { display: table }` que la captura, de
modo que `[pytest]` se partía en tres líneas. Los tokens estaban ahí y el recuento daba bien; sólo
se vio mirando la página.

**Pero no se parchea aquí.** `GRAMATICA` vive dentro de los centinelas `LP-CORE INICIO/FIN`, que
`migrar.py` reescribe entero en cada estampado: un arreglo a mano en este archivo se pierde en la
siguiente pasada. Va en `lp-core-extra.jsx`, se regenera con `ensamblar.py` y se re-estampa. Y
como la librería es compartida, **el cambio llega también al material de Lógica de Programación**
—sin romperle nada, porque sólo añade claves— pero conviene saberlo antes de tocarla.

> **Lo que faltaba en ese razonamiento:** los `<script>` de Prism y el CSS **no** viven dentro de
> los centinelas, sino en el `<head>` — y `migrar.py` no estampa el `head`, ni aquí ni en Teoría
> del Riesgo. Se comprobó en vivo: tras arreglar el CSS y re-ensamblar, `migrar.py` respondió «ya
> estaba al día» en los dos archivos, y hubo que copiar la regla a mano al piloto. Así que cada
> migración tiene que llevarse el `head` aparte, junto al título y los metadatos que ya
> menciona §3.
>
> Y Teoría del Riesgo **no comparte esta librería**: tiene `tr-core-extra.jsx`, `tr-head.html` y
> `tr-base.html` propios, con `GRAMATICA = {python, r, shell, text}`. El precedente del taller no
> es parchear lo compartido, es forkear por curso. Se decidió no forkear ahora —el coste real
> está en `verificar.py`, no en la librería— pero queda como decisión abierta.

---

## 3. Lo que el piloto NO midió

Y es la mitad que más pesa, así que no conviene extrapolar desde aquí:

- **`ChartFrame` no se ejercitó.** El módulo 11 tiene 3 gráficas de Plotly y no las migré. Es la
  incógnita mayor: hay que ver si el JSON que exporta `plotly.io.to_html` encaja en el
  componente o hay que reconstruir las figuras.
- **Las 8 tablas tampoco.** LP-CORE no tiene componente de tabla en la lista de autoría; habrá
  que decidir si van como HTML dentro de un `Box` o si merecen componente propio.
- **El `<head>` no se adapta solo.** El piloto conserva el `<title>` de la plantilla —«Lógica de
  Programación Financiera — Plantilla base»— porque está fuera de la región que se sustituye.
  Cada migración tiene que rehacer título, metadatos y el periodo 2026-II, que es justo la
  convención que la Fase 3 dejó al 13/13.
- **8 de las 11 secciones** del módulo 11 siguen sin migrar, incluidas las dos más largas.

---

## 4. Lo que sí se puede afirmar

1. **La arquitectura encaja.** Contenido de un curso de APIs dentro de componentes escritos para
   uno de programación financiera, sin fricción: `Motivacion`, `Box`, `Accordion`, `Termino` y
   `MCQ` sirven tal cual.
2. **`migrar.py` no sirve para los módulos 1 y 2.** Reemplaza desde `const { useState…` hasta
   `const Termino`, y esos dos módulos no tienen ninguno de los dos: no cargan React. Para ellos
   la migración es reconstrucción desde `lp-base.html`, no estampado.
3. **`CodeTabs` no aplica aquí.** Es el componente de cuatro lenguajes en paralelo de LPF. Este
   curso es sólo Python: se usa `CodeBlock` y ya.

---

## 5. Recomendación

> **Cerrado el 2026-08-08.** El hueco ya no bloquea la cola: los cinco lenguajes resaltan y
> `ensamblar.py` falla si alguien vuelve a declarar una gramática sin cargarla. Lo verificado está
> en la sección «Banco de lenguajes» del propio piloto. Lo que sigue de esta sección es lo que
> queda por hacer, que no cambió.

**Antes de migrar nada más:** cerrar el hueco de Dockerfile/YAML/SQL en `lp-core-extra.jsx`. Si no,
los módulos 11, 12 y 13 —los tres primeros de la cola— salen con el código sin resaltar, que es
peor que lo que hay hoy.

**Después:** terminar el módulo 11 completo, con las gráficas y las tablas, que es lo que falta
por medir. Sólo con el módulo 11 entero cerrado tiene sentido estimar los doce restantes.

**Mientras tanto, la Opción B sigue teniendo valor propio**, y no es trabajo tirado: la
homogeneización visual sirve a los módulos que no lleguen a migrarse este semestre, y la
convención de título, metadatos y reparto de la Fase 3 ya está en los trece.

---

## 6. Reproducir

```bash
python3 -m http.server 8123
# y abrir http://localhost:8123/_piloto_11_lpcore.html
```

El artefacto se puede borrar sin consecuencias: no lo referencia nadie.
