# Python para Desarrollo de APIs e Inteligencia Artificial

> Universidad Santo Tomás · Pregrado en Estadística · **2026-II** · Código 28549 · 4 créditos

Materiales del curso *Python para Desarrollo de APIs e Inteligencia Artificial*.
El objetivo del curso es que los estudiantes transiten del análisis estadístico
en notebooks al diseño y despliegue de servicios web reales con FastAPI,
incorporando validación de datos, persistencia, contenedores, CI/CD y
modelos de machine learning en producción.

**16 semanas**, del 8 de agosto al 21 de noviembre de 2026, sin semanas de receso.
El [syllabus](0_Syllabus_P_A_IA.html) es la fuente de verdad del cronograma, la
evaluación y la rúbrica; este README sólo indexa los archivos.

| Corte | Peso | Se evalúa a más tardar | Semana |
| ----- | ---- | ---------------------- | ------ |
| I     | 30 % | sábado 5 de septiembre de 2026  | 5  |
| II    | 30 % | sábado 17 de octubre de 2026    | 11 |
| III   | 40 % | sábado 21 de noviembre de 2026  | 16 |

---

## Cómo navegar el material

- **En línea** — abre [`index.html`](index.html) directamente en el navegador
  (clonar el repo o, si está habilitado, vía GitHub Pages).
- **Localmente** — clona el repositorio y abre `index.html` en tu navegador.

```bash
git clone https://github.com/JotaMao1985/PYTHON-PARA-DESARROLLO-DE-APIS-E-INTELIGENCIA-ARTIFICIAL-20261.git
cd PYTHON-PARA-DESARROLLO-DE-APIS-E-INTELIGENCIA-ARTIFICIAL-20261
open index.html      # macOS
xdg-open index.html  # Linux
start index.html     # Windows
```

---

## Índice de módulos

Los módulos 1 a 13 corresponden **uno a uno** con las semanas 1 a 13. Las semanas 14
y 15 son talleres dirigidos de proyecto y la 16 es la sustentación final.

| Sem. | #  | Módulo                                                                                       | Tema                                  |
| ---- | -- | -------------------------------------------------------------------------------------------- | ------------------------------------- |
| —    | 0  | [Syllabus del curso](0_Syllabus_P_A_IA.html)                                                 | Cronograma, evaluación y rúbrica      |
| 1    | 1  | [Introducción a Python para APIs e IA](1_Python_para_APIS_IA.html)                           | Encuadre y herramientas               |
| 2    | 2  | [Protocolo HTTP](2_Python_para_APIS_IA_HTTP.html)                                            | Verbos, estados y diseño REST         |
| 3    | 3  | [POO y clases en Python](3_Python_para_APIS_IA_POO_Clases.html)                              | Programación orientada a objetos      |
| 4    | 4  | [Pydantic — Estudio autónomo](4_Python_para_APIS_IA_Pydantic.html)                           | Validación declarativa de datos       |
| 5    | 5  | [Del modelo estadístico al servicio web](5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html) | Del análisis al servicio HTTP         |
| 6    | 6  | [FastAPI — De script a servicio](6_Python_para_APIS_IA_Fast_API.html)                        | Routers, modelos y OpenAPI            |
| 7    | 7  | [Validación de datos en Python](7_Python_para_APIS_IA_Data_Validation.html)                  | Patrones de validación robustos       |
| 8    | 8  | [Inyección de dependencias y configuración](8_Python_para_APIS_IA_DI_Configuracion.html)     | DI y settings en FastAPI              |
| 9    | 9  | [SQLAlchemy y bases de datos](9_Python_para_APIS_IA_SQLAlchemy_BD.html)                      | Persistencia con SQLAlchemy           |
| 10   | 10 | [Testing y reproducibilidad](10_Python_para_APIS_IA_Testing_y_Reproducibilidad.html)         | Pruebas automatizadas y entornos      |
| 11   | 11 | [Contenedores y Docker](11_Python_para_APIS_IA_Contenedores_y_Docker.html)                   | Imágenes reproducibles                |
| 12   | 12 | [Despliegue, PaaS y CI/CD](12_Python_para_APIS_IA_Despliegue_PaaS_y_CI_CD.html)              | Publicación automatizada              |
| 13   | 13 | [Modelos de ML en producción](13_Python_para_APIS_IA_Modelos_ML_en_Produccion.html)          | Serialización y patrón Singleton      |

### Proyecto integrador — Teoría del Riesgo

Trabajo transversal del semestre: se avanza desde la semana 1 en el trabajo
independiente, y estas dos sesiones son los talleres dirigidos de revisión.

| Sem. | Sesión | Material                                                                                        |
| ---- | ------ | ------------------------------------------------------------------------------------------------ |
| 14   | II     | [Taller I — datos y modelo](Proyecto_Integrador_Riesgo_Python_CII.html)                          |
| 15   | III    | [Taller II — API e integración](Proyecto_Integrador_Riesgo_Python_CIII.html)                     |
| 16   | —      | Sustentación final (sin material propio)                                                          |

`Proyecto_Integrador_Riesgo_Python_CIII.html` es además la **especificación viva**
del proyecto: arquitectura en cinco capas, entregables y rúbrica.

---

## Stack del curso

`Python` · `FastAPI` · `Pydantic` · `SQLAlchemy` · `Scikit-Learn` · `Docker` · `GitHub Actions`

## Estructura del repositorio

```text
.
├── index.html                  # Portada con navegación a los módulos
├── 0_Syllabus_P_A_IA.html      # Syllabus
├── 1_…  …  13_…                # Materiales numerados por sesión
├── Proyecto_I/                 # Submódulo: solución de referencia del proyecto integrador
├── Examples/                   # Demos pedagógicas (FastAPI, Docker, IA) — ver Examples/README.md
├── app/                        # Pipeline de clasificación de documentos
├── data/                       # Datasets de apoyo (PDFs sintéticos)
└── *.ipynb / *.py              # Notebooks y scripts complementarios
```

### Clonar con submódulos

`Proyecto_I/` apunta al repo independiente
[proyecto-integrador-riesgo-2026I](https://github.com/JotaMao1985/proyecto-integrador-riesgo-2026I).

```bash
# Clonar el curso incluyendo el integrador
git clone --recurse-submodules https://github.com/JotaMao1985/PYTHON-PARA-DESARROLLO-DE-APIS-E-INTELIGENCIA-ARTIFICIAL-20261.git

# Si ya lo clonaste sin submódulos:
git submodule update --init --recursive
```

## Estado del trabajo y siguiente paso

**Al 2026-08-08:** las tres fases de auditoría están cerradas y los 13 módulos corregidos —
46 de 53 hallazgos cerrados, 6 abiertos y todos cosméticos.

El hueco de lenguajes de LP-CORE, que bloqueaba la cola de migración, **quedó cerrado el 8 de
agosto**: el resaltador ya conoce Dockerfile, YAML, SQL y TOML, y de paso se arregló `shell`, que
llevaba roto desde el principio sin que nadie lo notara. `ensamblar.py` ahora falla si alguien
declara una gramática sin cargarla, así que el defecto no puede repetirse. El plan, lo que se
midió y las cifras corregidas están en
[`PLAN_LENGUAJES_LPCORE.md`](PLAN_LENGUAJES_LPCORE.md).

**Al 2026-08-09: tres módulos migrados a LP-CORE** —el 10, el 11 y el 12— y la migración
convertida en un proceso de cuatro guiones con una receta por módulo, documentado en
[`scripts/migracion/README.md`](scripts/migracion/README.md). Las tres incógnitas que dejó el
piloto están resueltas: `ChartFrame` acepta la salida de `plotly.io.to_html` con una conversión
mecánica, las tablas no necesitan componente porque `.prose-lp` ya las estiliza, y el `<head>` lo
pone `montar.py`.

**Al 2026-08-10: cinco módulos migrados.** Se suman el 1 y el 2, con una segunda boca de
entrada —`convertir_datos.py`— y un verificador de contenido, `auditar.py`. La cadena de
montaje y el formato de receta no cambiaron.

El HTML migrado (`_migrado_*.html`) **no se versiona**: es salida derivada y se regenera con los
guiones a partir del módulo heredado y su receta, que sí están en el repositorio.

**Lo siguiente**, por orden de coste creciente:

| Familia | Módulos | Qué falta |
|---|---|---|
| HTML plano, sin secciones ni gráficas | 5, 7, 8, 9 | trocear por `<h2>` **y** pasar a camelCase 1 919 atributos con guion repartidos en 231 diagramas |
| ReactDOM con navegación propia | 3, 4, 6, 13 | no es conversión: hay que re-alojar sus componentes en el `curriculum` |

> **Corrección.** Hasta el 10 de agosto esta tabla clasificaba los módulos 1 y 2 como «HTML plano,
> pequeños —2 y 3 bloques de código—» a los que sólo les faltaba trocear por `<h2>`. Era falso en
> los tres datos: son aplicaciones de una sola página con el contenido en un objeto `courseData`,
> traen seis secciones y unos cuarenta bloques cada uno, y sus gráficas son de Chart.js, no de
> Plotly. Los que necesitan el troceo por `<h2>` son el 5, el 7, el 8 y el 9.

> **Dependencia con el otro curso.** La librería LP-CORE vive en el repositorio de Lógica de
> Programación Financiera, y este curso la comparte. Si alguien la cambia allí, hay que
> re-ensamblar y volver a montar estos módulos. Los cambios que necesitó este curso —las
> gramáticas de Prism y sacar el nombre de la asignatura del `App` a `CONFIG`— están en la rama
> `lp-core/gramaticas-de-resaltado` de aquel repositorio, todavía sin fusionar a `main`.

## Auditoría del material

Los 13 módulos se auditaron en tres fases (agosto de 2026). El estado de cada
hallazgo está en **[`ESTADO_HALLAZGOS.md`](ESTADO_HALLAZGOS.md)**, que se genera y se
comprueba contra los archivos:

```bash
python3 scripts/auditoria/hallazgos.py --abiertos
```

| Documento | Qué contiene |
|---|---|
| [`ESTADO_HALLAZGOS.md`](ESTADO_HALLAZGOS.md) | Los 52 hallazgos, su estado y qué queda por hacer |
| [`PLAN_AUDITORIA_MODULOS.md`](PLAN_AUDITORIA_MODULOS.md) | El plan de las tres fases y las opciones de alcance |
| [`INFORME_AUDITORIA_TECNICA.md`](INFORME_AUDITORIA_TECNICA.md) | Fase 1 · código, enlaces, consola, consistencia |
| [`INFORME_AUDITORIA_PEDAGOGICA.md`](INFORME_AUDITORIA_PEDAGOGICA.md) | Fase 2 · cobertura del RA, narrativa, gráficas, tiempos |
| [`PLAN_FASE_3.md`](PLAN_FASE_3.md) · [`INFORME_FASE_3.md`](INFORME_FASE_3.md) | Fase 3 · las correcciones y su auto-auditoría |

## Docente

**Javier Mauricio Sierra** — Universidad Santo Tomás

## Uso académico

Material elaborado con fines educativos para la asignatura.
Cualquier reutilización fuera del contexto del curso debe citar la fuente.
