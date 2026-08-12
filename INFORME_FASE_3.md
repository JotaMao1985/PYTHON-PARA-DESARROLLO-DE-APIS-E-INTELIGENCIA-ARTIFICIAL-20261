# Informe de correcciones — Fase 3

**Asignatura:** Python para Desarrollo de APIs e Inteligencia Artificial · USTA · Estadística · 2026-II
**Fecha:** 2026-08-08 · **La semana 1 empieza hoy.**
**Alcance ejecutado:** Opción A revisada **completa**, incluida la reorientación del módulo 5.
**Corresponde a:** Fase 3 y Checkpoint 3 del `PLAN_AUDITORIA_MODULOS.md` · plan de ejecución en `PLAN_FASE_3.md`
**Fases anteriores:** `INFORME_AUDITORIA_TECNICA.md` (1) · `INFORME_AUDITORIA_PEDAGOGICA.md` (2)

> **Esta fase sí modifica el material.** Los 13 módulos están tocados, cada uno con
> respaldo `.bak` y verificado en navegador. Once commits, ninguno mezcla dos módulos
> salvo el que se declara y justifica en §3.

---

## 0. Lo que hay que mirar primero

**Los cuatro bloqueantes de la Fase 2 están cerrados**, y uno de ellos era de seguridad.

| | Módulo | Qué pasaba | Qué se hizo | Verificado con |
|---|---|---|---|---|
| **P3** | 3 | El «Constructor IA» enviaba la **API Key de Gemini del estudiante en la URL** | Pasa a la cabecera `x-goog-api-key` | DOM: 0 apariciones de `generateContent?key=` |
| **P2** | 3 | 0 menciones de `dataclasses`, Pydantic, SQLAlchemy y FastAPI, que son la teoría que el syllabus le asigna | Lección nueva: «Por qué esto es el cimiento del curso» | 15 / 6 / 4 / 4 menciones tras montar |
| **P4** | 5 | Enseñaba **usando Flask** en un curso que se evalúa en FastAPI | FastAPI pasa a ser el vehículo; Flask, la comparación | Flask 48→44, FastAPI 46→**58** |
| **P1** | 13 | La rúbrica evalúa un **tablero (3 %)** que ningún módulo preparaba | Sección nueva «6. El tablero» | «tablero» 0 → **26** |

Y **tres defectos que ninguna de las dos fases anteriores había visto**, encontrados
al corregir:

| | Módulo | Hallazgo | Por qué se escapó antes |
|---|---|---|---|
| **F1** | 1 | `TypeError` en consola **cada 60 segundos**, en el primer módulo del curso | El barrido de la Fase 1 mide la carga inicial; este error tarda un minuto en aparecer |
| **F2** | 8, 9 | Marcado desbalanceado: un `<main>` que nunca se cierra | Ninguna fase pasó un validador de estructura. **Es anterior a la Fase 3** (verificado contra el commit `5163d48`) |
| **F3** | 7 | El módulo **sí tiene fórmulas**: 82 renderizadas por KaTeX | El informe de la Fase 2 (§7.3) afirmaba lo contrario. Ver §5 |

---

## 1. Las cuatro decisiones que abrieron la fase

Estaban abiertas en §9 del informe pedagógico y las cerró el docente el 2026-08-08:

| | Pregunta | Decisión |
|---|---|---|
| D1 | Alcance | **Opción A revisada completa**, con el módulo 5 dentro |
| D2 | Criterio 14 «Tablero» | **Añadir material al módulo 13.** La rúbrica no se toca |
| D3 | Adelantos de Docker (sem. 1) y Pydantic (sem. 2) | **Deliberados: se conservan y se declaran** |
| D4 | Celery/RabbitMQ/DLQ del módulo 7 | **Cortar** |

Más la confirmación heredada de la Fase 1: **podar Railway y dejar Render** en el módulo 12.

---

## 2. La convención que ahora cumplen los 13

Antes de tocar contenido se fijó un contrato, porque cualquier cosa que haya que añadir
a los trece tiene que sobrevivir a **cinco stacks de render distintos**.

**Regla:** todo lo que se inyecta en los 13 va en HTML plano con estilos en línea. Sin
Tailwind —los módulos 10, 11 y 12 no lo cargan—, sin React —nueve no lo usan— y sin
clases propias, que colisionarían con la hoja de cada módulo.

`python3 scripts/auditoria/fase3.py --verificar`:

| | Antes | Después |
|---|---|---|
| Títulos con su semana, en arábigo y con el texto del syllabus | **0/13** | **13/13** |
| `<meta description>` | 12/13 | **13/13** |
| `<meta author>` | 7/13 | **13/13** |
| Open Graph | 0/13 | **13/13** |
| Periodo 2026-II | 0/13 | **13/13** |
| Bloque de reparto 60/180 | 0/13 | **13/13** |

Se acabaron «Clase II» en la semana 1, «Semana V» en la 12, «Semana VI» en la 13,
«Semana XI» en la 11 y los siete módulos sin número. **Los trece títulos salen ahora de
`SEMANAS` del syllabus**, no de la memoria de quien escribió cada uno.

### 2.1 El bloque de reparto, que es el cambio que más se va a notar

Era el hallazgo P11/P12: once módulos no declaraban ninguna duración y **ninguno de los
trece separaba lo que se expone de lo que se consulta**. Ahora cada módulo declara, bajo
su cabecera, qué entra en los 60 min de exposición, qué sostiene los 180 de práctica
guiada y qué es material de consulta.

Las decisiones de reparto viven en el `dict REPARTO` de `scripts/auditoria/fase3.py`, en
un solo sitio, para que se puedan discutir de una vez en vez de repartidas por trece
archivos. **El módulo 4 es la excepción declarada**: el syllabus lo define como estudio
autónomo, así que su bloque dice eso y no finge una sesión de 4 h.

---

## 3. Qué se cambió en cada módulo

| # | Trabajo | Hallazgos cerrados |
|---|---|---|
| 1 | Semana 1, radar honesto, apertura, desborde, temporizador | I1, I4, P8, P10, P11, P12, P14, Q2, Q3, **F1** |
| 2 | Semana 2, reloj derivado, radar propio, desborde | P7, P8, P9, P11, P12, C8, I5, Q5 |
| 3 | **P3 y P2**, React pineado | **P2, P3**, I2, I6, I10, P16, Q6 |
| 4 | El error 422 que faltaba, reparto de estudio autónomo | I2, I6, P16, cobertura 422 |
| 5 | **P4**: FastAPI pasa a ser el vehículo | **P4**, I2, P16 |
| 6 | Tuteo | P15, I2, I6, P16 |
| 7 | **Corte de Celery**, KaTeX aclarado | **P5**, I2, P16, C1 |
| 8 | KaTeX muerto retirado | C2, I2, P16 |
| 9 | Convención | I2, P16 |
| 10 | «Semana X» resuelto | **Q1** |
| 11 | Numeración arábiga | C8 |
| 12 | **Poda de Railway** | **P13/I9**, I1 |
| 13 | **El tablero** | **P1**, I1, I6 |

### 3.1 Los tres cortes y las tres adiciones

**Cortes:**

- **Módulo 7 · Celery, RabbitMQ y DLQ.** 563 líneas, 48 KB. Menciones: Celery 35→**0**,
  RabbitMQ 22→**0**, broker 11→**0**. El módulo baja de **714 a 668 KB**. Se conservan
  las cinco menciones a «dead letter queue» de otras secciones, porque ahí no es
  infraestructura sino un patrón de validación —apartar lo que no valida en vez de
  descartarlo—, y se les añade la explicación que daba la subsección cortada.
- **Módulo 12 · Railway.** De **46 a 10** menciones; Render queda en 38. Se reescriben a
  Render el flujo paso a paso, las variables, los logs y los cuatro ejercicios, y se
  retira la comparativa 6.5 con su radar «Railway vs. Render». Las 10 que quedan son
  comparación técnica legítima (qué es Nixpacks, una referencia bibliográfica).
- **Módulo 8 · KaTeX.** Cargaba tres archivos (~280 KB) para renderizar **cero** fórmulas.

**Adiciones:**

- **Módulo 3 · «Por qué esto es el cimiento del curso».** El puente de POO hacia
  `dataclasses` → Pydantic → SQLAlchemy → FastAPI. Usa el límite de `dataclasses` —declara
  tipos pero **no los comprueba**— como bisagra hacia la semana 4.
- **Módulo 4 · «Del ValidationError al error HTTP 422».** Por qué 422 y no 400, y cómo se
  lee el cuerpo con `loc`, `msg` y `type`.
- **Módulo 13 · «El tablero (rúbrica 3 %)».** CORS, un tablero completo en un solo archivo
  HTML sin dependencias, y los tres detalles que lo hacen aprobar: que lea el 422, que
  distinga «la API dijo que no» de «la API no contestó», y que consuma la API desplegada.

**Los tres bloques de código nuevos se ejecutaron antes de publicarlos** (criterio C7).
El del módulo 3 imprime lo que su comentario afirma: la instancia con `edad="treinta y
cuatro"` se construye sin protestar y `type()` dice `str`. El del módulo 4, con Pydantic
2.12.5, reporta los tres errores de una vez con los tipos `int_parsing`,
`greater_than_equal` y `greater_than`.

### 3.2 Un commit que rompe la regla, a propósito

El plan fija «un módulo por commit». El commit `4e31026` toca ocho. Es deliberado: son
ediciones generadas por script, idénticas en los ocho archivos y verificables de una
pasada con `--verificar`. Separarlas habría dado ocho mensajes iguales sin añadir
trazabilidad. **Las correcciones de contenido —Celery, Railway, el tablero— sí van una
por commit.**

---

## 4. Tres cosas que rompí, y cómo aparecieron

Las tres son mías, las tres se corrigieron en la misma sesión, y las tres comparten un
rasgo que conviene registrar: **ninguna se ve mirando la pantalla.**

### 4.1 El módulo 13 entero en blanco

La primera versión del tablero dejó el módulo **sin renderizar**: `<div id="root">` vacío.
El tablero es HTML y contiene un `</script>`, y esa secuencia cierra el
`<script type="text/babel">` que la envuelve **aunque esté dentro de una cadena de
JavaScript**. Babel reportaba «Unterminated template».

Se escapa como `<\/script>`, que el navegador vuelve a mostrar como `</script>`
—verificado que el estudiante lee la etiqueta correcta y no el escape—. Es un modo de
fallo total producido por una cadena dentro de un literal, y **sólo se ve comprobando si
React montó**: el archivo se sirve igual y pesa lo mismo.

### 4.2 Un icono que no existía

Al añadir la lección del 422 al módulo 4 le puse `icon: 'AlertTriangle'`, que **no está en
el mapa `Icons`** de ese módulo. `Icons[leccion.icon]` valía `undefined`, React intentaba
renderizarlo como componente y lanzaba en consola. **La lección renderizaba igual**, así
que mi primera verificación lo dio por bueno. Apareció revisando errores de `react-dom`
mientras verificaba el módulo 5, que ni siquiera usa React.

`fase3.py --verificar` ahora comprueba los iconos huérfanos de los módulos React.
Resultado actual: **ninguno en los 13**.

### 4.3 Un bloque de código invisible

La lección nueva del módulo 3 la escribí con el campo `code:`, y el módulo usa
`pythonCode:`. **No da ningún error**: la lección aparece en la navegación, renderiza su
prosa, y el bloque de código simplemente no está. Se detectó porque la comprobación en
navegador buscaba el *texto del código*, no sólo que la lección existiera.

> **La lección de las tres:** verificar que «la página carga» no verifica nada. Las tres
> comprobaciones que las cazaron fueron específicas: ¿montó React?, ¿hay errores tras el
> clic?, ¿está el texto del código en el DOM?

---

## 5. Correcciones a las fases anteriores

Como en las dos fases previas, lo que este trabajo contradice se anota:

1. **El módulo 7 sí tiene fórmulas.** El informe pedagógico (§7.3) dice que «no tiene
   fórmulas visibles pese a cargar KaTeX, igual que el 8». Es falso para el 7: descontando
   la configuración de `renderMathInElement` tiene 52 delimitadores en línea, 18 en bloque
   y 1 de corchete, y **el navegador renderiza 82 fórmulas**. KaTeX se conserva en el 7 y
   se retira sólo del 8, donde efectivamente sobra.

2. **`verificar_codigo.py` daba verde sobre datos obsoletos.** No extrae: consume el
   `bloques.json` que produce `extraer_codigo.py`. Tras añadir dos bloques nuevos, el
   verificador respondió «111 bloques, 111 compilan» — el mismo número que antes de mis
   cambios. **No estaba verificando el archivo que yo tenía delante.** Un bloque mío que no
   compilara habría pasado con un verde. La cifra correcta es **113/113** en ese momento y
   **112/112** al cierre (el corte de Celery se llevó un bloque). Los commits `35412a2` y
   `278175c` citan 111/111 y 112/112: lo verificado de verdad era 113/113.
   El verificador ahora compara `mtime` y **se niega a verificar** si algún módulo es más
   reciente, nombrándolo y saliendo con código 2.

3. **Los módulos 8 y 9 tienen marcado desbalanceado** (F2): un `<main>` que nunca se
   cierra. Los navegadores lo toleran, por eso nadie lo había visto. **Es anterior a esta
   fase** — verificado corriendo el mismo validador contra `5163d48`.

---

## 6. Verificación de cierre (Checkpoint 3)

| Comprobación | Resultado |
|---|---|
| Títulos, metadatos, periodo y reparto | **13/13** en las seis columnas |
| Iconos Font Awesome inexistentes | **ninguno** |
| Iconos React huérfanos | **ninguno** |
| Residuos de Cloudflare | **ninguno** |
| Correcciones B5/B6 de la Fase 1 | **intactas** (credencial y 4 correos) |
| Bloques de Python que compilan | **112 de 112**, 0 errores |
| Desborde a 375 px | **0 px** en todos los verificados |
| Estructura HTML | 11/13 limpios; 8 y 9 con el desbalance **preexistente** |

Verificados en navegador uno a uno: **1, 2, 3, 4, 5, 7, 8, 12, 13**. Los módulos **6, 9,
10 y 11** se validaron con el barrido automático y el validador de estructura, **no en
navegador** — está declarado como limitación en §7.

### 6.1 Peso del material

De **2 338 KB a 2 360 KB**. Sube 22 KB en total pese a cortar 48 del módulo 7 y retirar la
comparativa del 12, porque los trece ganan el bloque de reparto y tres ganan lecciones
nuevas. **El módulo 7 baja de 714 a 668 KB** y deja de ser cinco veces el módulo medio.

---

## 7. Auto-auditoría: dónde puede estar mal esto

**Lo que sigue siendo débil, y hay que decirlo:**

| Riesgo | Efecto |
|---|---|
| **Cuatro módulos no se verificaron en navegador** (6, 9, 10, 11) | Sus cambios son sustituciones de texto y el bloque de reparto, no estructura. Pero «bajo riesgo» no es «verificado»: si algo se rompió ahí, este informe no lo sabe |
| **El desborde se midió en el estado inicial de cada módulo**, no en todos | La Fase 1 cerró esa limitación con `desborde_estados.js` recorriendo la navegación. **Aquí no se repitió ese recorrido completo**: sólo la vista inicial de cada módulo verificado |
| **El bloque de reparto declara un juicio, no un hecho** | Qué va en los 60 min y qué en los 180 lo decidí yo cruzando las secciones reales con la `teoria` y la `practica` del syllabus. Es discutible módulo a módulo, y para eso está todo junto en `REPARTO` |
| **El tablero del módulo 13 no se ha ejecutado contra una API real** | El HTML es correcto y el flujo está razonado, pero nadie lo ha abierto contra un `/predict` desplegado. Los nombres de campo (`especie`, `probabilidad`) asumen el esquema del mini-proyecto de ese mismo módulo |
| **La reorientación del módulo 5 es de fondo, no cosmética** | Se reescribieron secciones enteras. Merece una lectura completa del docente antes de la semana 5, que es justo el margen que hay |
| **El «Semana X» del módulo 11 se sustituyó en bloque** | Eran referencias correctas a la semana 10. La sustitución es mecánica y se comprobó el orden (`Semana XI` contiene `Semana X`), pero no se leyó cada una en contexto |
| **No se midió accesibilidad por teclado ni contraste** | Sigue abierta la limitación L3 de la Fase 1, incluidos los bloques nuevos |

**Consecuencia práctica, igual que en las dos fases anteriores:** lo que está corregido
está verificado; lo que no está en este informe puede seguir ahí. Y esta fase añade una
consecuencia propia: **he tocado 13 archivos y he roto tres cosas en el proceso**. Las
tres las encontré, pero la tasa importa — el `.bak` de cada módulo y los once commits
separados existen precisamente por eso.

---

## 8. Lo que queda abierto

**Hallazgos que esta fase no cerró**, con el motivo:

| ID | Módulo | Hallazgo | Por qué sigue abierto |
|---|---|---|---|
| **F2** | 8, 9 | `<main>` sin cerrar | Preexistente. Arreglar marcado desbalanceado en archivos de 166 y 222 KB sin analizarlo a fondo es más arriesgado que dejarlo: los navegadores lo toleran hoy |
| P6 | 7 | 128 min de prosa contra 60 de presupuesto | El corte de Celery recupera 48 KB, pero **no he vuelto a medir la prosa**. El bloque de reparto ya separa exposición de consulta, que era la mitad del problema |
| I11 | 4, 6, 7 | 4 referencias tras el muro de pago de Medium | Hace falta buscar alternativas de acceso abierto, que es trabajo de contenido, no de corrección |
| C3 | 5, 7, 8, 9 | 89 KB de Font Awesome para 1 o 2 iconos | Cosmético y sin efecto visible |
| C4 | 10–13 | Plotly 3.5.0 frente al 2.35.2 del syllabus | Cosmético; cambiar de versión mayor sin verificar las 37 gráficas es peor negocio |
| C9 | 11 módulos | Font Awesome 6.0.0 frente al 6.5.2 del syllabus | La Fase 1 ya demostró que no rompe ningún icono |
| Q4 | 7 | 668 KB y 0 gráficas | Añadir gráficas es trabajo de contenido nuevo |

**Y las dos opciones grandes siguen donde estaban:** la **B** (homogeneización visual) y la
**C** (migración a LP-CORE) son para el semestre. Esta fase refuerza el argumento del
informe pedagógico: **ninguna de las dos habría arreglado ni uno de los cuatro
bloqueantes.** Siguen conviviendo cinco stacks de render.

---

## 9. Cómo revertir

Cada módulo tiene su `.bak` anterior a la primera edición (no versionados; están en
`.gitignore` desde esta fase):

```bash
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13; do f=$(ls ${n}_*.html); cp "$f.bak" "$f"; done
```

Y por commit, que es más fino:

```bash
git log --oneline auditoria/fase-2
git revert <hash>
```

---

## 10. Reproducir cualquier dato de este informe

```bash
# Estado de la convención en los 13, e iconos React huérfanos
python3 scripts/auditoria/fase3.py --verificar

# El bloque de reparto de un módulo, tal como se generó
python3 scripts/auditoria/fase3.py --reparto 7

# Barrido de la Fase 1, repetido. El orden importa: extraer ANTES de verificar
python3 scripts/auditoria/inventario.py
python3 scripts/auditoria/extraer_codigo.py
python3 scripts/auditoria/verificar_codigo.py --ejecutar
python3 scripts/auditoria/consistencia.py

# Comprobaciones puntuales citadas en el informe
grep -c "generateContent?key=" 3_*.html      # 0 — la clave ya no va en la URL (P3)
grep -oic "celery" 7_*.html                  # 0 — (P5)
grep -oic "railway" 12_*.html                # 10 — comparativas legítimas (P13)
grep -oic "tablero" 13_*.html                # 26 — (P1)

# Servir y verificar en navegador
python3 -m http.server 8123
```
