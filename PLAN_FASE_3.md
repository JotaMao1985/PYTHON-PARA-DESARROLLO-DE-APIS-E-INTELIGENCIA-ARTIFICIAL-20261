# Plan de ejecución — Fase 3 (correcciones)

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-08 · **La semana 1 empieza hoy.**
**Deriva de:** `PLAN_AUDITORIA_MODULOS.md` §2 (Fase 3) · `INFORME_AUDITORIA_TECNICA.md` · `INFORME_AUDITORIA_PEDAGOGICA.md`

---

## 0. Las cuatro decisiones que abren esta fase

Estaban en §9 del informe pedagógico y son la razón de que la Fase 3 no empezara antes.

| | Pregunta | Decisión del docente (2026-08-08) |
|---|---|---|
| **D1** | Alcance | **Opción A revisada completa**, incluida la reorientación del módulo 5 de Flask a FastAPI |
| **D2** | Criterio 14 «Tablero (frontend)», 3 % | **Añadir material de tablero al módulo 13.** La rúbrica no se toca |
| **D3** | Adelantos de Docker (25 min, semana 1) y Pydantic (40 min, semana 2) | **Deliberados: se conservan y se declaran** como adelanto, con el destino explícito |
| **D4** | Celery / RabbitMQ / DLQ en el módulo 7 | **Cortar.** Queda recuperable en el `.bak` |

Y una confirmación heredada de la Fase 1, que sigo leyendo como un sí y que aún puedes
corregir porque el módulo 12 es de la semana 12: **podar Railway y dejar Render**.

---

## 1. La decisión de arquitectura que gobierna toda la fase

Los 13 módulos están construidos sobre **cinco stacks distintos** (informe pedagógico §1).
Cualquier cosa que haya que añadir a los trece —y hay dos: el bloque de reparto 60/180 y
los metadatos— tiene que sobrevivir a los cinco.

**Regla:** todo lo que se inyecte en los 13 va en **HTML plano con estilos en línea**.

Sin Tailwind, porque los módulos 10, 11 y 12 no lo cargan. Sin React, porque nueve de los
trece no lo usan. Sin clases CSS propias, porque cada módulo tiene su hoja y colisionarían.
Es más verboso, y es la única forma de que el mismo bloque se vea igual en los trece sin
tocar el CSS de ninguno.

Segunda regla, heredada del riesgo §4 del plan: **un módulo por commit, nunca dos**, con
`.bak` antes de tocar y verificación en navegador antes de pasar al siguiente.

---

## 2. La convención que los 13 módulos van a cumplir

### 2.1 Título

```
Semana N — <título del syllabus> · Python para APIs e IA
```

El título sale del syllabus (`SEMANAS[n].titulo`, línea 1949 y siguientes), **no se
inventa**, para que la pestaña del navegador y el cronograma digan lo mismo:

| N | Título canónico | N | Título canónico |
|---|---|---|---|
| 1 | Del script al entorno de producción | 8 | Inyección de dependencias y configuración |
| 2 | Serialización y el protocolo HTTP | 9 | SQLAlchemy y persistencia |
| 3 | Programación orientada a objetos y clases | 10 | Testing y reproducibilidad |
| 4 | Pydantic: validación declarativa | 11 | Contenedores y Docker |
| 5 | Del modelo estadístico al servicio web | 12 | Despliegue, PaaS y CI/CD |
| 6 | FastAPI: de script a servicio | 13 | Modelos de ML en producción |
| 7 | Validación avanzada de datos | | |

Arábigos en los trece. Se acaban los «Clase II», «Semana XI», «Semana V» y «Semana X».

### 2.2 Metadatos

Los cinco que hoy faltan en unos u otros: `description`, `author`, `og:title`,
`og:description`, y el periodo **2026-II**, que hoy no declara ningún módulo.

### 2.3 El bloque de reparto 60/180

Es el hallazgo P11/P12 y el segundo de la lista de prioridades: **once módulos no declaran
ninguna duración**, y ninguno de los trece separa lo que se expone de lo que se consulta.
Sin eso ningún docente puede planear la sesión.

Cada módulo declara, justo debajo de su cabecera:

- **60 min de exposición** — qué secciones, nombradas
- **180 min de práctica guiada** — qué secciones
- **Material de consulta** — lo que no se expone en clase y el estudiante lee por su cuenta

El reparto sale de `CONFIG.minutosTeoria: 60` y `CONFIG.minutosPractica: 180` del syllabus
(línea 1911), así que no hay dos fuentes de verdad. El módulo 4 es la excepción declarada:
el syllabus lo define como estudio autónomo y su bloque dice eso, no finge una sesión.

---

## 3. Las tareas, en el orden del cronograma

El orden lo fijaste tú: cronograma, no gravedad. Lo que se dicta antes se arregla antes.

| # | Tarea | Módulo | Hallazgos que cierra | Tamaño |
|---|---|---|---|---|
| T0 | Convención y script de apoyo | — | contrato de T1–T13 | S |
| T1 | Módulo 1 | 1 | I1, I4, P8, P10, P14, Q2, Q3, P11 | M |
| T2 | Módulo 2 | 2 | I5, P7, P8, P9, Q5, C8, P11 | M |
| T3 | Módulo 3 | 3 | **P2, P3** (bloqueantes), I2, I6, I10, P16, Q6 | M |
| T4 | Módulo 4 | 4 | I2, I6, P16, Q2, cobertura 422 | S |
| T5a | Módulo 5 · núcleo a FastAPI | 5 | **P4** (bloqueante) | **L** |
| T5b | Módulo 5 · autoevaluación y cierre | 5 | I2, P16, cobertura ciclo petición-respuesta | M |
| T6 | Módulo 6 | 6 | P15, I2, I6, I11, P16, C5 | M |
| T7a | Módulo 7 · cortar Celery | 7 | **P5** | M |
| T7b | Módulo 7 · presupuesto y registro | 7 | P6, I2, P14, P16, Q4, C1, C3 | **L** |
| T8 | Módulo 8 | 8 | C2, C3, I2, P16 | S |
| T9 | Módulo 9 | 9 | I2, P16, C3 | S |
| T10 | Módulo 10 | 10 | **Q1**, C4, cobertura modos de fallo | S |
| T11 | Módulo 11 | 11 | C8, C4 | S |
| T12 | Módulo 12 | 12 | **P13/I9** (podar Railway), I1, C4 | M |
| T13 | Módulo 13 | 13 | **P1** (bloqueante, tablero), I1, I6, P14, C4 | **L** |
| T14 | Checkpoint 3 | los 13 | verificación en verde | M |
| T15 | Informe y auto-auditoría | — | documentación | M |

**Dependencias:** T1–T13 dependen todas de T0 (la convención) y de ninguna otra. T5b
depende de T5a; T7b depende de T7a. T14 depende de las trece. T15 depende de T14.

### 3.1 Criterios de aceptación comunes a T1–T13

Cada módulo, antes de pasar al siguiente:

- [ ] `.bak` creado antes de la primera edición
- [ ] Título con su semana en arábigo y el texto del syllabus
- [ ] `description`, `author`, Open Graph y periodo 2026-II presentes
- [ ] Bloque de reparto 60/180 visible y coherente con el contenido real del módulo
- [ ] Los hallazgos de su fila, cerrados
- [ ] Consola sin errores, servido por HTTP
- [ ] Sin desborde horizontal a 375 px, en todos los estados del módulo
- [ ] Los bloques de Python siguen compilando (`verificar_codigo.py`)
- [ ] Commit propio, con el módulo y los hallazgos en el mensaje

### 3.2 Checkpoints

> **Checkpoint 3.1 — tras T2.** Los dos módulos que se dictan estas dos semanas quedan
> corregidos y verificados. Es el mínimo entregable antes de la primera sesión.

> **Checkpoint 3.2 — tras T5b.** Los cuatro bloqueantes pedagógicos cerrados (P1 queda
> para T13 por ser del módulo 13). El corte I cae en la semana 5.

> **Checkpoint 3 — tras T14.** El barrido completo de la Fase 1 repetido en verde.

---

## 4. Riesgos propios de esta fase

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Reescribir el módulo 5 rompe un material que hoy funciona | Alto | `.bak`, y conservar la sección 3 como bisagra: es la única que ya está bien situada |
| Cortar Celery del módulo 7 deja referencias colgando en el índice y en la navegación | Medio | Verificar la navegación por secciones y el recuento tras el corte, no sólo que el bloque desapareció |
| El bloque de reparto se ve distinto en cada stack | Medio | Estilos en línea, sin dependencias; verificación visual módulo a módulo |
| El tablero del módulo 13 es contenido nuevo, no una corrección | Medio | Es el único añadido de alcance; se acota a lo que el criterio 14 evalúa, no a un curso de frontend |
| Trece módulos en una sesión agotan el contexto | Alto | Un commit por módulo: el trabajo cerrado sobrevive a cualquier corte |

---

## 5. Lo que esta fase NO hace

Para que quede dicho antes y no se lea como omisión:

- **No homogeneiza el stack** (Opción B) ni migra a LP-CORE (Opción C). Sigue habiendo
  cinco formas de renderizar. Esa decisión sigue siendo para el semestre.
- **No toca el syllabus.** El reparto 60/180 ya está en él y es la fuente de verdad.
- **No toca la rúbrica.** D2 resuelve el criterio 14 añadiendo material, no cambiando pesos.
- **No verifica accesibilidad por teclado ni contraste** (limitación L3 de la Fase 1).
