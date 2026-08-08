# Piloto de migración a LP-CORE — módulo 11

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-08
**Decisión que lo motiva:** Opción B ya + Opción C por bloques durante el semestre, empezando por
un piloto en el módulo 11 para medir antes de comprometer trece migraciones.
**Artefacto:** `_piloto_11_lpcore.html` — **no es material del curso.** El módulo 11 real
(`11_Python_para_APIS_IA_Contenedores_y_Docker.html`) **no se ha tocado**.

---

## 0. El resultado en una línea

**LP-CORE funciona en este curso, y le falta una pieza concreta y barata: el resaltador no
conoce Dockerfile, YAML ni SQL.** Son 25 de los 212 bloques de código del material, y 22 de
esos 25 son Dockerfiles concentrados justo en los módulos 11 y 13.

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

| Declarado en `GRAMATICA` | Gramática de Prism | ¿lo necesita este curso? |
|---|---|---|
| `pseudo` | `pseudo` | no — es de Lógica de Programación |
| `python` | `python` | **sí, 112 bloques** |
| `r` | `r` | no |
| `vba` | `visual-basic` | no |
| `shell` | `bash` | **sí, 32 bloques** |
| `text` | *(sin resaltar)* | sí, salidas |

Y lo que falta:

| Lenguaje | Bloques en el material | Dónde |
|---|---|---|
| **Dockerfile** | **22** | módulos 11 y 13 |
| **YAML** | 2 | módulo 12 (GitHub Actions, `render.yaml`) |
| **SQL** | 1 | módulo 9 |

En el piloto esto se ve así: pedí `lang="docker"`, el código **se muestra correctamente pero sin
un solo token resaltado** — `GRAMATICA` no tiene la clave, así que cae a `escaparHtml` y la
etiqueta pasa a «Salida». No falla, no avisa: simplemente se degrada en silencio.

**Coste de arreglarlo:** tres entradas en `GRAMATICA`, tres en `LANG_META` y cargar tres
componentes de Prism, que existen de serie (`prism-docker`, `prism-yaml`, `prism-sql`).

**Pero no se parchea aquí.** `GRAMATICA` vive dentro de los centinelas `LP-CORE INICIO/FIN`, que
`migrar.py` reescribe entero en cada estampado: un arreglo a mano en este archivo se pierde en la
siguiente pasada. Va en `lp-core-extra.jsx`, se regenera con `ensamblar.py` y se re-estampa. Y
como la librería es compartida, **el cambio llega también al material de Lógica de Programación**
—sin romperle nada, porque sólo añade claves— pero conviene saberlo antes de tocarla.

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
