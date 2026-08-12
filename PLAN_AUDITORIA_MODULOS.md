# Plan de auditoría de los 13 módulos del curso

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-06 · **Cerrado el 2026-08-08**
**Estado:** **EJECUTADO.** Las tres fases están hechas y los 13 módulos, corregidos.

> **Cierre (2026-08-08).** Fase 1 → `INFORME_AUDITORIA_TECNICA.md`, Fase 2 →
> `INFORME_AUDITORIA_PEDAGOGICA.md`, Fase 3 → `PLAN_FASE_3.md` + `INFORME_FASE_3.md`.
>
> El docente eligió la **Opción A revisada completa** (§3), con el módulo 5 dentro. Los
> **cuatro bloqueantes pedagógicos están cerrados** —P1 tablero, P2 y P3 del módulo 3, P4
> del módulo 5— además de los seis técnicos que ya se habían corregido en la Fase 1. Los
> 13 módulos cumplen ahora la convención de título, metadatos, periodo y reparto 60/180:
> **13/13 en las seis comprobaciones**, desde 0/13 en cuatro de ellas.
>
> Aparecieron **tres hallazgos que ninguna de las dos fases de sólo lectura había visto**
> (§0 del informe de la Fase 3), y quedan abiertos los cosméticos y las opciones **B** y
> **C**, que siguen siendo trabajo de semestre.

---

## 0. ¿Vale la pena? Sí, y la evidencia ya está sobre la mesa

Antes de proponer nada corrí un barrido de sólo lectura sobre los 13 módulos. Tres
hallazgos bastan para justificar la revisión.

### 0.1 Cinco convenciones de numeración y tres números equivocados

| Módulo | `<title>` actual | Problema |
|---|---|---|
| 1 | Python para APIs e IA — **Clase II** | Es la semana 1, y lo llama «Clase II» |
| 2 | **Semana II** — Ingeniería de Datos y Despliegue | El módulo enseña HTTP; el título anuncia otra cosa |
| 3–9 | *(sin número de semana)* | Siete módulos sin anclaje al cronograma |
| 10 | **Semana 10** — Testing y Reproducibilidad | Correcto, arábigo |
| 11 | **Semana XI** — Contenedores y Docker | Correcto, pero romano |
| 12 | **Semana V** — Despliegue, PaaS y CI/CD | **Debería ser semana 12** |
| 13 | **Semana VI** — Modelos de ML en Producción | **Debería ser semana 13** |

El título es lo que ve el estudiante en la pestaña y lo que indexa Google. Hoy tres
módulos declaran una semana que no es la suya y siete no declaran ninguna.

### 0.2 El material no es un material, son cuatro

| Módulo | Render | Matemáticas | Gráficas | Font Awesome |
|---|---|---|---|---|
| 1, 2 | React sin Babel | — | Chart.js | 6.0.0 |
| 3, 4, 6, 13 | React + Babel | — | — | 6.0.0 |
| 5, 9 | HTML plano | — | — | 6.0.0 |
| 7 | React sin Babel | KaTeX | — | 6.0.0 |
| 8 | HTML plano | KaTeX | — | 6.0.0 |
| 10, 11 | React sin Babel | MathJax | — | *(sin FA)* |
| 12 | HTML plano | MathJax | — | 6.0.0 |
| **0 (syllabus)** | **React + Babel** | **MathJax** | **Plotly** | **6.5.2** |

Dos motores de fórmulas distintos, tres formas de renderizar, y el syllabus ya
recién migrado a un cuarto stack. Para el estudiante esto se traduce en que cada
sesión se ve y se comporta distinto.

> **Nota sobre Font Awesome 6.0.0:** el material de Lógica de Programación
> documenta que los iconos introducidos después de 6.5 **aparecen como huecos en
> blanco, sin ningún error en consola**. Once módulos están en 6.0.0. Hay que
> comprobar si alguno usa iconos posteriores.

### 0.3 El contenido contradice al proyecto que se evalúa

El módulo 12 menciona **Railway 48 veces y Render 4**. El proyecto integrador exige
Render free-tier, y el syllabus ya declara Render como plataforma canónica. Un
estudiante que siga el módulo 12 al pie de la letra despliega en la plataforma
equivocada.

Además, los módulos 3 a 9 no mencionan **Python 3.11.9** ni una sola vez, cuando es
la versión que el syllabus y el proyecto fijan como obligatoria.

---

## 1. Los siete criterios de auditoría

Son los mismos que se aplicaron al syllabus, más uno que aporta el material de
Lógica de Programación y que es el que más defectos reales encuentra.

| # | Criterio | Qué se pregunta |
|---|---|---|
| C1 | **Coherencia con el syllabus** | ¿El módulo enseña lo que el cronograma dice que enseña esa semana? ¿El título declara la semana correcta? ¿Cubre el resultado de aprendizaje declarado? |
| C2 | **Pertinencia** | ¿El contenido sirve al RA de su semana y prepara los criterios de rúbrica que le tocan? ¿Sobra materia que nadie evalúa? ¿Falta materia que sí se evalúa? |
| C3 | **Calidad narrativa** | ¿Abre dando una razón para leer, o abre con un índice? ¿Registro dirigido al estudiante, sin notas internas de planeación? ¿Verbos de RA homogéneos? |
| C4 | **Gráficas y visualizaciones** | ¿Informan o decoran? ¿Los datos son reales y derivados, o inventados? ¿Tienen alternativa textual? |
| C5 | **Integridad técnica** | ¿Consola limpia? ¿Sin desborde horizontal a 375 px? ¿Operable por teclado? ¿Enlaces vivos? ¿CDNs coherentes? |
| C6 | **Consistencia transversal** | Python 3.11.9, Render como PaaS, paleta USTA, tipografía Montserrat, terminología compartida entre módulos |
| C7 | **Verificación del código ejecutado** | **Toda salida declarada tiene que haberse ejecutado.** Los bloques de Python del material se extraen, se corren y se compara su salida real con la declarada |

> **Por qué C7 es el más valioso.** En el material de Lógica de Programación esta
> regla cazó un `#> 600000` cuyo resultado real era 2 400 000: el código contradecía
> la clave de su propio ejercicio, y **no se veía en pantalla** — una cifra
> equivocada se lee igual que una correcta. Aquí el riesgo es el mismo: trece
> módulos llenos de código que nadie ha vuelto a ejecutar desde que se escribió.

---

## 2. Fases

Cada fase termina en un estado revisable. **Las fases 1 y 2 no modifican nada**: sólo
producen informes. Ninguna corrección empieza sin que apruebes el informe de la 2.

### Fase 1 — Barrido automático transversal (sólo lectura)

Un script que recorre los 13 módulos y produce una tabla de defectos objetivos. Es
barato, es exhaustivo y no depende de mi criterio.

**T1.1 · Inventario técnico**
- [ ] Título, número de semana declarado, tamaño, stack de render, versiones de CDN
- [ ] Errores de consola al cargar cada módulo, servidos por HTTP
- [ ] Enlaces rotos (internos y externos)
- [ ] Desborde horizontal a 375 px
- [ ] Iconos Font Awesome posteriores a 6.0.0 que no van a pintar
- **Verificación:** informe con una fila por módulo; cada defecto reproducible con un comando
- **Tamaño:** M

**T1.2 · Extracción y ejecución del código (C7)**
- [ ] Extraer todos los bloques de Python de los 13 módulos
- [ ] Ejecutar los que declaren salida y comparar con la declarada
- [ ] Listar por separado los no auditables, en vez de darlos por buenos en silencio
- **Verificación:** informe de salidas: coincide / difiere / no ejecutable, con el diff
- **Dependencias:** T1.1 · **Tamaño:** M

**T1.3 · Consistencia transversal (C6)**
- [ ] Mapa de menciones: Python 3.11.9, Railway/Render, Flask, versiones de librerías
- [ ] Terminología divergente entre módulos para el mismo concepto
- **Verificación:** tabla de discrepancias con archivo y línea
- **Tamaño:** S

> #### Checkpoint 1 — informe técnico
> Entrego `INFORME_AUDITORIA_TECNICA.md`. **Tú decides qué se corrige antes de seguir.**

### Fase 2 — Auditoría pedagógica módulo a módulo (sólo lectura)

Aquí sí hace falta leer el contenido. Un módulo por tarea, en el orden del
cronograma, contrastando contra el RA que el syllabus le asigna.

**T2.1 … T2.13 · Un módulo cada una**
Para cada módulo, contra los criterios C1–C4:
- [ ] ¿El contenido cubre el RA declarado en el syllabus para esa semana? ¿Qué falta y qué sobra?
- [ ] ¿Qué criterios de la rúbrica prepara, y los prepara de verdad?
- [ ] Apertura: ¿motiva o indexa?
- [ ] Notas internas filtradas, registro inconsistente, marcadores sin resolver
- [ ] Gráficas: pertinencia y honestidad de los datos
- **Verificación:** ficha por módulo con hallazgos clasificados en *bloqueante / importante / cosmético*
- **Dependencias:** Checkpoint 1 · **Tamaño:** S cada una (13 tareas)

> #### Checkpoint 2 — informe pedagógico y decisión de alcance
> Entrego `INFORME_AUDITORIA_PEDAGOGICA.md` con el total de hallazgos priorizados.
> **Aquí decides el alcance de la Fase 3** (ver §3: son tres opciones muy distintas
> en esfuerzo).

### Fase 3 — Correcciones (alcance por decidir)

Se ejecuta módulo a módulo, cada uno verificado en navegador antes de pasar al
siguiente, con respaldo `.bak` como se hizo con el syllabus. El orden lo fija la
prioridad del informe, no el número del módulo.

**T3.x · Un módulo por tarea**
- [ ] Correcciones aprobadas aplicadas
- [ ] Consola limpia, sin desborde a 375 px, enlaces vivos
- [ ] Salidas de código re-ejecutadas y coincidentes
- [ ] Captura antes/después
- **Tamaño:** S a L según el módulo y la opción elegida

> #### Checkpoint 3 — cierre
> Barrido de la Fase 1 repetido en verde sobre los 13 módulos.

---

## 3. Tres opciones de alcance para la Fase 3

Esta es la decisión que más cambia el trabajo. Van de menor a mayor.

### Opción A — Pasada de consistencia *(la que recomiendo empezar)*

No se toca la estructura ni el stack de ningún módulo. Se corrige:

- Títulos y numeración de semana (los tres equivocados y los siete ausentes)
- Metadatos: descripción, autor, Open Graph, periodo 2026-II
- Railway → Render en el módulo 12 y donde haga falta
- Versiones: Python 3.11.9 donde se declare versión, Font Awesome a 6.5.2
- Enlaces rotos, salidas de código equivocadas
- Enlace de vuelta al syllabus y al módulo siguiente en cada archivo

**Riesgo:** bajo. Cambios locales y verificables uno a uno.
**Resultado:** el material deja de contradecirse. Sigue viéndose distinto en cada sesión.

### Opción B — Consistencia + homogeneización visual

Todo lo de A, más unificar la capa de presentación sin reescribir contenido:
paleta USTA, Montserrat, un solo motor de fórmulas, Font Awesome único, cabecera y
pie comunes con navegación entre módulos.

**Riesgo:** medio. Tocar el CSS de trece archivos con cuatro stacks distintos puede
romper maquetaciones que hoy funcionan. Exige verificar cada módulo en navegador.
**Resultado:** el curso se ve como un curso.

### Opción C — Migración completa a LP-CORE

Los 13 módulos reconstruidos sobre `lp-base.html`, como se hizo con el syllabus.

**Riesgo:** alto, y quiero ser explícito: son **2,3 MB de contenido** en trece
archivos con cuatro arquitecturas distintas, y el módulo 7 solo pesa 714 KB. No es
una migración mecánica: hay que **reescribir el contenido dentro de los componentes**
de la librería. Es el mayor trabajo de todo lo que hemos hecho hasta ahora, con
diferencia, y no debería intentarse antes del inicio de clases.
**Resultado:** un material homogéneo, mantenible y verificable con las mismas
herramientas que LPF.

**Mi recomendación:** ejecutar Fases 1 y 2 completas (son baratas y no rompen nada),
y con el informe en la mano decidir. Probablemente **A ahora**, antes del 8 de
agosto, y **B o C por bloques** durante el semestre, empezando por los módulos que
el cronograma toca más tarde — que son los que dan margen.

---

## 4. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El curso empieza el 8 de agosto y la auditoría toca material en uso | Alto | Auditar en el orden del cronograma; corregir primero lo que se dicta antes. Las fases 1 y 2 no modifican nada, así que pueden correr con el curso en marcha |
| Tocar cuatro stacks distintos rompe algo que hoy funciona | Alto | `.bak` por archivo, verificación en navegador módulo a módulo, nunca dos módulos en el mismo commit |
| El módulo 7 (714 KB) desborda cualquier estimación | Medio | Tratarlo como tarea propia y decidir su alcance por separado |
| Ejecutar código del material tiene dependencias no instaladas | Medio | Entorno aislado; los bloques no ejecutables se **declaran** no auditados, no se dan por buenos |
| La auditoría encuentra más de lo que da tiempo a arreglar | Medio | Clasificar en bloqueante / importante / cosmético desde la primera ficha, y cerrar sólo lo bloqueante antes de clases |

---

## 5. Lo que necesito de ti antes de empezar

1. **¿Arranco por las Fases 1 y 2?** No modifican nada y producen los dos informes
   sobre los que se decide todo lo demás.
2. **¿Hay módulos intocables?** Alguno que ya hayas revisado y prefieras que no mire.
3. **¿El orden lo manda el cronograma o la gravedad?** Mi propuesta es el cronograma:
   lo que se dicta antes se arregla antes.
4. **Confirmar el reparto 60/180 de la sesión de 4 h** — sigue pendiente del plan
   anterior y afecta a lo que cada módulo debe cubrir en clase.
