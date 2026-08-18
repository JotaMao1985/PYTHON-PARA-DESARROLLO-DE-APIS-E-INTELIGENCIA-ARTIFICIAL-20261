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
├── 1_…  …  13_…                # Materiales numerados por sesión — es lo que se publica
├── heredado/                   # La versión previa de los ya migrados: fuente de scripts/migracion/
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

**Al 2026-08-10: cinco módulos migrados y en producción.** Se suman el 1 y el 2, con una
segunda boca de entrada —`convertir_datos.py`— y un verificador de contenido, `auditar.py`.
La cadena de montaje y el formato de receta no cambiaron.

**Al 2026-08-12: nueve módulos migrados.** Se suman el 5, el 7, el 8 y el 9, con una tercera
boca de entrada, `convertir_plano.py`. La cadena de montaje y el formato de receta siguen sin
cambiar. Lo que se encontró por el camino, y que la tabla de familias no anunciaba:

- **Sí tenían secciones.** Un `<article id="modulo-N">` por cada `<h2>`, que la navegación
  propia enseñaba y escondía. El troceo salió casi gratis; el trabajo estaba en los 231
  diagramas y sus 1 822 atributos con guion.
- **Los cuestionarios había que convertirlos, no copiarlos.** Los 28 de estos cuatro módulos
  marcaban la respuesta correcta con una clase que su guion de barajado quitaba al cargar. Sin
  ese guion —y no se lleva— la solución se habría visto en negrita antes de contestar. Van a
  `Quiz`, que además califica.
- **Tres diagramas del módulo 7 venían dentro de un `<pre>`**, con la tarjeta oscura de los
  bloques de código. Tomados por código se aplanaban a sus rótulos y el dibujo se perdía.
- **Las fórmulas cambiaron de delimitador**: el heredado usa KaTeX (`$x$`) y LP-CORE compone
  con MathJax (`\(x\)`). Sin traducir no fallaban: salían como texto con dólares.

Y un defecto de la poda de `montar.py`, que venía de antes: se comía el comentario que abre el
bloque generado. Los cinco módulos ya publicados estaban sin su `=== GRÁFICAS INICIO ===`. Al
corregirlo, volver a montarlos cambia exactamente esa línea y ninguna otra.

**Al 2026-08-12: diez módulos migrados.** Se suma el 3, con una cuarta boca de entrada,
`convertir_react.py`. Es la familia barata: el módulo ya era una aplicación de React con Babel
—el mismo montaje que LP-CORE— y su contenido ya vivía en un `const curriculum = [...]`, así que
el JSX se copia literal. Dos cosas que decidir, y las dos quedan documentadas:

- **El «Laboratorio de Datos» no se migró, porque no se veía.** El heredado trae un panel
  interactivo completo —media, mediana, varianza poblacional y muestral— gobernado por seis
  valores de `interactiveType`, detrás de una condición que sólo cumple uno de ellos. Se
  comprobó en el DOM de la página publicada, sección por sección: cinco de los seis no pintan
  nada. Migrarlo habría sido publicar algo que nunca se publicó. Recuperarlo es una decisión
  pedagógica, no de migración, y entonces va como componente propio.
- **El Constructor IA sí, y a mano.** Genera clases con Gemini desde la clave que ponga el
  estudiante. Vivía en un panel lateral de 384 px que en LP-CORE no existe, así que cambia el
  marco —pasa a ser una tarjeta dentro de la sección— y el texto que mandaba «al panel derecho».
  La lógica no cambia: la clave sigue viajando en la cabecera y no en la URL, que es la regla
  que el propio módulo enseña. Vive en `scripts/migracion/componentes/modulo_3.jsx`.

**Al 2026-08-13: once módulos migrados.** Se suma el 4, de la misma familia que el 3 y sin
componentes que portar a mano: su cuestionario —cinco preguntas que viven fuera del
`curriculum`, en un array `quizQuestions`— se emite con el mismo `bloque_quiz` que ya usaban los
módulos 1 y 2. Dos hallazgos:

- **Un `<Icons.X />` dentro del contenido puede dejar la página en blanco.** El icono de una
  sección pasa por `renderIcon` y falla en silencio si no existe; escrito dentro del contenido,
  no: es `undefined` en posición de componente y React tira la página entera con un error
  minificado que no dice de dónde viene. Pasó con `Icons.Structure`. Ahora `montar.py` se niega
  a montar si queda alguno que la plantilla no define.
- **La felicitación se recorta también aquí.** El cuestionario del 4 sí enseñaba la
  justificación a todo el mundo, pero con un «Respuesta Incorrecta» encima que le quitaba el
  filo al «Correcto.» de después. LP-CORE no pone ese contrapeso.

**El capítulo migrado sustituye al heredado y conserva su nombre.** El heredado pasa a
[`heredado/`](heredado/), con el mismo nombre, y a partir de ahí sólo lo leen los guiones de
migración. Es lo que hace que el trabajo llegue a alguien: `.github/workflows/static.yml`
publica el repositorio tal cual desde `main`, de modo que mientras el capítulo montado no
se versionara, ningún estudiante podía verlo. Al conservar el nombre no hubo que tocar ni un
enlace de `index.html` ni del syllabus.

Se guarda el heredado, en vez de sobrescribirlo y confiar en el historial de git, porque
LP-CORE está vivo: cada cambio de la librería obliga a volver a montar estos capítulos, y sin
la fuente a mano habría que editarlos uno a uno.

**Al 2026-08-17: revisión a fondo del módulo 4**, y tres arreglos que salpican a los trece.
El plan, los hallazgos y cómo se comprobó cada uno están en
[`PLAN_MODULO_4_PYDANTIC.md`](PLAN_MODULO_4_PYDANTIC.md). Lo que conviene saber sin abrirlo:

- **Lo que el estudiante veía mal.** Dos expresiones regulares se publicaban mutiladas —el
  literal de plantilla de JS se come la barra invertida—, y por eso el ejemplo titulado
  «Pattern inválido» rechazaba un correo que es válido: enseñaba lo contrario de lo que decía.
  El bloque de apertura no daba un promedio falso, que era la lección: reventaba con un
  `TypeError`. Y la bibliografía estaba marcada como Python conteniendo `pip install`.
- **Un detector nuevo**, [`scripts/auditoria/escapes.py`](scripts/auditoria/escapes.py), para
  el defecto de la barra invertida, que a ojo es invisible: el archivo se ve correcto. Barre
  los 13 y `heredado/`, y trae autoprueba, porque una comprobación que sólo se ha visto callar
  no está comprobada. Costó tres intentos y los dos fallos están documentados en el guion.
- **El montaje ya no da por Python todo bloque.** El heredado puede declarar `codeLang`, y
  `montar.py` **aborta** si la clave no está en el `GRAMATICA` de la plantilla. Encontró de
  paso un defecto vivo en el módulo 2: un bloque de shell marcado `bash` —que no es la clave—
  se publicaba sin resaltar.
- **El encabezado de los ejemplos ya no anuncia el hilo de otro curso.** Venía de
  `lp-base.html`, donde encabeza el `EJ_INTERES` de Lógica de Programación Financiera; aquí la
  poda se lleva la constante y dejaba el encabezado mintiendo. Se le abrió el alcance en la
  plantilla —sigue siendo cierto allí— y **se remontaron los trece** para propagarlo.

> El cambio de `lp-base.html` está **sin confirmar** en el repositorio de Lógica de
> Programación Financiera. Sus capítulos lo tomarán cuando se remonten.

**Lo siguiente**, por orden de coste creciente:

| Familia | Módulos | Qué falta |
|---|---|---|
| React con `curriculum` de datos | 6 | la cadena ya existe (`convertir_react.py`); falta portar a mano el `ComparisonDiagram` y el `Tooltip` |
| React con secciones ya en componentes | 13 | no hay nada que convertir: hay que deduplicar. Trae su propio `Box`, `Pipeline`, `usePlotly` y `ChartFrame`, que es justo lo que LP-CORE pone |

> **Corrección, tres veces la misma.** Esta tabla describió mal tres familias, y siempre por no
> contarlas. Hasta el 10 de agosto llamaba a los módulos 1 y 2 «HTML plano, pequeños —2 y 3
> bloques de código—»: son aplicaciones de una sola página con el contenido en un objeto
> `courseData`, seis secciones y unos cuarenta bloques cada uno, y gráficas de Chart.js, no de
> Plotly. Decía que el 5, el 7, el 8 y el 9 eran «HTML plano, **sin secciones**»: sí las tienen,
> un `<article id>` por `<h2>`. Y metía en una sola fila al 3, 4, 6 y 13: los tres primeros
> guardan el contenido en un `curriculum` de datos y el 13 ya lo tiene en componentes, que es
> otro trabajo.

> **Dependencia con el otro curso.** La librería LP-CORE vive en el repositorio de Lógica de
> Programación Financiera, y este curso la comparte, así que las dos carpetas de curso tienen
> que seguir colgando del mismo directorio padre: `montar.py` busca `lp-base.html` ahí.
>
> Los cambios que necesitó este curso —las gramáticas de Prism y sacar el nombre de la
> asignatura del `App` a `CONFIG`— **ya están en `main` de aquel repositorio** (su PR #1); la
> rama `lp-core/gramaticas-de-resaltado` se fusionó y se borró.
>
> Sigue vivo, eso sí: va por el capítulo 3. **Si alguien cambia la librería allí, hay que volver
> a montar estos once capítulos**, y por eso el heredado se conserva en `heredado/`. Son tres o
> cuatro comandos por módulo, según la familia, documentados en
> [`scripts/migracion/README.md`](scripts/migracion/README.md).

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
