# Estado de los hallazgos de la auditoría

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II  
**Generado:** 2026-08-07 por `scripts/auditoria/hallazgos.py --markdown`

> **No edites esta tabla a mano.** El registro vive en `scripts/auditoria/hallazgos.py`,
> y 39 de los 52 hallazgos llevan una prueba que se ejecuta contra los
> archivos: si el estado escrito y el archivo dejan de coincidir, el script lo dice y sale
> con código 1. Las cifras de esta página se calculan, no se escriben.

```bash
python3 scripts/auditoria/hallazgos.py             # tabla completa y comprobación
python3 scripts/auditoria/hallazgos.py --abiertos  # sólo lo que queda por hacer
```

---

## Resumen

| Estado | | Qué significa |
|---|---|---|
| ✔ Cerrado | **40** | Corregido y verificado |
| ◐ Parcial | **4** | Cerrado en unos módulos y abierto en otros |
| ✘ Abierto | **7** | Sigue ahí, con motivo declarado |
| · Nota | **1** | Corrección a un informe, no un defecto |
| | **52** | |

Por fase de origen: Fase 1 → 26 · Fase 2 → 23 · Fase 3 → 3.

---

## Lo que queda por hacer

| ID | Módulos | Hallazgo | Estado | Por qué sigue así |
|---|---|---|---|---|
| **I11** | 4, 6, 7 | 4 referencias bibliográficas tras el muro de pago de Medium | ✘ abierto | Hace falta buscar alternativas de acceso abierto: es trabajo de contenido |
| **C3** | 5, 7, 8, 9 | 89 KB de Font Awesome para 1 o 2 iconos | ✘ abierto | Cosmético y sin efecto visible |
| **C4** | 10–13 | Plotly 3.5.0 frente al 2.35.2 del syllabus | ✘ abierto | Cambiar de versión mayor sin verificar las 37 gráficas es peor negocio |
| **C5** | 6, 7 | Referencias a «2025» | ◐ parcial | Quedan 3 referencias a «2025» en el módulo 6 |
| **C7** | 7, 13 | Bloques de código que continúan a otro sin decirlo | ✘ abierto | Requiere leer los bloques en contexto, uno a uno |
| **C9** | 11 módulos | Font Awesome 6.0.0 frente al 6.5.2 del syllabus | ✘ abierto | La Fase 1 demostró que no rompe ningún icono |
| **P6** | 7 | 128 min de prosa contra un presupuesto de 60 | ◐ parcial | El bloque de reparto ya separa exposición de consulta; falta volver a medir la prosa |
| **P14** | 1, 7, 13 | No se dirigen al estudiante ni una vez | ◐ parcial | El módulo 7 sigue sin dirigirse al estudiante |
| **Q2** | 1, 4 | Aperturas que indexan en vez de motivar | ◐ parcial | El módulo 4 sigue abriendo con un índice |
| **Q4** | 7 | El módulo más pesado del curso no tiene ni una gráfica | ✘ abierto | Añadir gráficas es contenido nuevo, no corrección |
| **F2** | 8, 9 | Marcado desbalanceado: un `<main>` que nunca se cierra *(preexistente)* | ✘ abierto | Preexistente. Tocar marcado desbalanceado en 166 y 222 KB es más arriesgado que dejarlo |

---

## Registro completo

| ID | Fase | Gravedad | Módulos | Hallazgo | Estado | Cerrado en | Commit |
|---|---|---|---|---|---|---|---|
| B1 | 1 | bloqueante | 7 | «IMPLEMENTACIÓN CORRECTA» no compila: IndentationError | ✔ cerrado | Fase 1 | `94eaa09` |
| B2 | 1 | bloqueante | 7 | Error de sintaxis no intencionado en el ejemplo del error metodológico | ✔ cerrado | Fase 1 | `94eaa09` |
| B3 | 1 | bloqueante | 7 | Rama `else` sin indentar | ✔ cerrado | Fase 1 | `94eaa09` |
| B4 | 1 | bloqueante | 4 | `print("` partido por un `\n` que resolvió JavaScript | ✔ cerrado | Fase 1 | `deb0686` |
| B5 | 1 | bloqueante | 9 | 4 literales de correo destruidos por Cloudflare | ✔ cerrado | Fase 1 | `ba5b159` |
| B6 | 1 | bloqueante | 8 | Cadena de conexión con credencial destruida por Cloudflare | ✔ cerrado | Fase 1 | `70c5499` |
| I1 | 1 | importante | 1, 12, 13 | El `<title>` declara una semana que no es la suya | ✔ cerrado | Fase 3 | `4e31026` |
| I2 | 1 | importante | 3–9 | Ningún `<title>` declara semana | ✔ cerrado | Fase 3 | `4e31026` |
| I3 | 1 | importante | 8, 9 | 3 peticiones 404 en consola a `/cdn-cgi/` | ✔ cerrado | Fase 1 | `ba5b159` |
| I4 | 1 | importante | 1 | Desborda 58 px a 375 px | ✔ cerrado | Fase 3 | `e9dfeb2` |
| I5 | 1 | importante | 2 | Desborda 12 px a 375 px | ✔ cerrado | Fase 3 | `f2a65fc` |
| I6 | 1 | importante | 3, 4, 6, 13 | React en build de desarrollo y `@babel/standalone` sin pinear | ✔ cerrado | Fase 3 | `35412a2` |
| I7 | 1 | importante | 3–9 | Python 3.11.9 no se menciona nunca *(= P16)* | ✔ cerrado | Fase 3 | `7d69b57` |
| I8 | 1 | importante | 5 | Enseña Flask donde el proyecto exige FastAPI *(= P4)* | ✔ cerrado | Fase 3 | `1bb8eb7` |
| I9 | 1 | importante | 12 | Enseña Railway y Render en paralelo *(= P13)* | ✔ cerrado | Fase 3 | `7d69b57` |
| I10 | 1 | importante | 3 | Sin `description`, sin autor y sin Open Graph | ✔ cerrado | Fase 3 | `35412a2` |
| I11 | 1 | importante | 4, 6, 7 | 4 referencias bibliográficas tras el muro de pago de Medium | ✘ abierto | — | — |
| C1 | 1 | cosmético | 7 | El comentario dice «MathJax» sobre una carga de KaTeX | ✔ cerrado | Fase 3 | `7d69b57` |
| C2 | 1 | cosmético | 8 | Carga los 3 archivos de KaTeX y renderiza 0 fórmulas | ✔ cerrado | Fase 3 | `7d69b57` |
| C3 | 1 | cosmético | 5, 7, 8, 9 | 89 KB de Font Awesome para 1 o 2 iconos | ✘ abierto | — | — |
| C4 | 1 | cosmético | 10–13 | Plotly 3.5.0 frente al 2.35.2 del syllabus | ✘ abierto | — | — |
| C5 | 1 | cosmético | 6, 7 | Referencias a «2025» | ◐ parcial | Fase 3 (sólo el 7) | `7d69b57` |
| C6 | 1 | cosmético | todos | Ningún módulo declara el periodo 2026-II | ✔ cerrado | Fase 3 | `4e31026` |
| C7 | 1 | cosmético | 7, 13 | Bloques de código que continúan a otro sin decirlo | ✘ abierto | — | — |
| C8 | 1 | cosmético | 2, 10, 11 | Semana correcta pero en tres notaciones distintas | ✔ cerrado | Fase 3 | `4e31026` |
| C9 | 1 | cosmético | 11 módulos | Font Awesome 6.0.0 frente al 6.5.2 del syllabus | ✘ abierto | — | — |
| P1 | 2 | bloqueante | 13 | La rúbrica evalúa «Tablero (frontend)» (3 %) y ningún módulo lo prepara | ✔ cerrado | Fase 3 | `2f385db` |
| P2 | 2 | bloqueante | 3 | No nombra `dataclasses`, Pydantic, SQLAlchemy ni FastAPI | ✔ cerrado | Fase 3 | `35412a2` |
| P3 | 2 | bloqueante | 3 | Envía la API Key del estudiante **en la URL** | ✔ cerrado | Fase 3 | `35412a2` |
| P4 | 2 | bloqueante | 5 | Enseña Flask donde el proyecto se evalúa en FastAPI | ✔ cerrado | Fase 3 | `1bb8eb7` |
| P5 | 2 | importante | 7 | Celery/RabbitMQ/DLQ: 70 menciones que el syllabus no cita | ✔ cerrado | Fase 3 | `7d69b57` |
| P6 | 2 | importante | 7 | 128 min de prosa contra un presupuesto de 60 | ◐ parcial | Fase 3 (declarado, no medido) | `7d69b57` |
| P7 | 2 | importante | 2 | Declara 120 min en cabecera; sus lecciones suman 170 | ✔ cerrado | Fase 3 | `f2a65fc` |
| P8 | 2 | importante | 1, 2 | Radar «Competencias» con datos inventados y duplicado | ✔ cerrado | Fase 3 | `f2a65fc` |
| P9 | 2 | importante | 2 | 40 min a Pydantic, que es la semana 4 | ✔ cerrado | Fase 3 (D3: se declara) | `f2a65fc` |
| P10 | 2 | importante | 1 | 25 min a Docker, que es la semana 11 | ✔ cerrado | Fase 3 (D3: se declara) | `e9dfeb2` |
| P11 | 2 | importante | 11 módulos | No declaran ninguna duración | ✔ cerrado | Fase 3 | `4e31026` |
| P12 | 2 | importante | todos | Ningún módulo separa exposición de material de consulta | ✔ cerrado | Fase 3 | `4e31026` |
| P13 | 2 | importante | 12 | Compara Railway y Render donde el proyecto exige Render | ✔ cerrado | Fase 3 | `7d69b57` |
| P14 | 2 | importante | 1, 7, 13 | No se dirigen al estudiante ni una vez | ◐ parcial | Fase 3 (1 y 13; falta el 7) | `e9dfeb2` |
| P15 | 2 | importante | 6 | Único módulo que trata de **usted** | ✔ cerrado | Fase 3 | `7d69b57` |
| P16 | 2 | importante | 3–9 | Python 3.11.9 no se menciona nunca *(= I7)* | ✔ cerrado | Fase 3 | `7d69b57` |
| Q1 | 2 | cosmético | 10 | El `<title>` dice «Semana 10» y la cabecera «Semana X» | ✔ cerrado | Fase 3 | `7d69b57` |
| Q2 | 2 | cosmético | 1, 4 | Aperturas que indexan en vez de motivar | ◐ parcial | Fase 3 (sólo el 1) | `e9dfeb2` |
| Q3 | 2 | cosmético | 1 | Gráfica de barras sin fuente citada | ✔ cerrado | Fase 3 | `e9dfeb2` |
| Q4 | 2 | cosmético | 7 | El módulo más pesado del curso no tiene ni una gráfica | ✘ abierto | — | — |
| Q5 | 2 | cosmético | 2 | «Bonus: Funciones en Python», por debajo del nivel de la semana | ✔ cerrado | Fase 3 (D3: se declara) | `f2a65fc` |
| Q6 | 2 | cosmético | 3 | Termina en un generador de clases con IA, no en el puente | ✔ cerrado | Fase 3 | `35412a2` |
| F1 | 3 | importante | 1 | `TypeError` en consola cada 60 s, en el primer módulo del curso | ✔ cerrado | Fase 3 | `5e17c40` |
| F2 | 3 | importante | 8, 9 | Marcado desbalanceado: un `<main>` que nunca se cierra *(preexistente)* | ✘ abierto | — | — |
| F3 | 3 | nota | 7 | El módulo **sí** tiene 82 fórmulas: corrige al informe de la Fase 2 §7.3 | · nota | Fase 3 | `7d69b57` |
| R1 | 2 | importante | 4 | El syllabus asigna el error HTTP 422 y el módulo no lo mencionaba | ✔ cerrado | Fase 3 | `278175c` |

---

## Una corrección de aritmética a la Fase 2

El informe de la Fase 2 cierra su §6 con «**4 bloqueantes, 16 importantes, 6
cosméticos**», y **su propia tabla de importantes tiene 12 filas**, de P5 a P16. El 16
sale de leer el identificador más alto como si fuera un recuento, olvidando que P1–P4
son los bloqueantes. La Fase 2 encontró **22** hallazgos, no 26, y el «26 hallazgos
abiertos» que suma con la Fase 1 arrastra el mismo error.

No cambia ninguna conclusión —los cuatro bloqueantes siguen siendo cuatro—, pero es
justo el tipo de cifra que esta tabla existe para no repetir.

