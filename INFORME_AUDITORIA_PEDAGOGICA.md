# Informe de auditoría pedagógica — Fase 2

**Asignatura:** Python para Desarrollo de APIs e Inteligencia Artificial · USTA · Estadística · 2026-II
**Fecha:** 2026-08-06
**Alcance:** los 13 módulos HTML, contra los criterios C1–C4 del plan más el reparto 60/180.
**Corresponde a:** T2.1 … T2.13 del `PLAN_AUDITORIA_MODULOS.md` · Checkpoint 2
**Fase anterior:** `INFORME_AUDITORIA_TECNICA.md` (Fase 1, Checkpoint 1)

> **Esta fase no ha modificado ningún módulo.** Sólo se han añadido tres scripts de
> lectura a `scripts/auditoria/`. Los seis bloqueantes de la Fase 1 siguen siendo las
> únicas correcciones aplicadas al material.

---

## 0. Lo que hay que mirar primero

La Fase 1 buscaba código que no compila. Ésta busca otra cosa: **materia que se
evalúa y nadie enseña, y materia que se enseña y nadie evalúa.** Aparecieron cuatro
casos del primer tipo y tres del segundo.

| | Módulo | Hallazgo | Verificado con |
|---|---|---|---|
| **P1** | — | **La rúbrica evalúa un «Tablero (frontend)» que vale 3 % y que no prepara ningún módulo.** 0 menciones de «tablero», «dashboard» o «streamlit» en los 13 | conteo en crudo sobre los 13 archivos |
| **P2** | 3 | El syllabus le asigna a la semana 3 explicar «por qué **Pydantic, SQLAlchemy y FastAPI** exigen entender esto primero», y **el módulo no nombra ninguno de los tres, ni `dataclasses`** — que su propio stack declara | `grep -oic` = 0, 0, 0, 0 |
| **P3** | 3 | El «Constructor IA» pide al estudiante su **API Key de Gemini y la envía en la URL**, que es exactamente lo que **el módulo 2 le prohíbe** una semana antes | endpoint + texto del módulo 2 |
| **P4** | 5 | Enseña **Flask** donde el proyecto se evalúa en FastAPI *(ya detectado en Fase 1; aquí se confirma el alcance pedagógico)* | Fase 1 §6.3 |
| **P5** | 2 | Dedica **40 min a Pydantic**, que es la semana 4 entera, y es su lección más larga junto con HTTP | `duration:` del propio módulo |
| **P6** | 7 | Una subsección completa sobre **Celery, RabbitMQ y Dead Letter Queues** (35 + 22 + 13 menciones) que **el syllabus no menciona en ninguna de sus 16 semanas** | conteo + `grep` sobre el syllabus |
| **P7** | 1 | Dedica **25 min a Docker**, que es la semana 11 entera | `duration:` del propio módulo |

Ninguno de los siete se ve leyendo el módulo por encima: los cuatro primeros exigen
tener el syllabus al lado, y los tres últimos exigen sumar los tiempos que el propio
material declara.

**Y una buena noticia que conviene registrar:** **cero notas internas de planeación
filtradas** al material del estudiante en los 13 módulos, y **cero anclas internas
rotas**. Se buscaron `TODO:`, `FIXME`, `lorem ipsum`, «pendiente», «diapositiva» y
nueve marcadores más, con control negativo. El material está limpio de residuo de
autoría.

---

## 1. Método, y por qué no es una lectura impresionista

Leer 13 módulos y opinar produce fichas desiguales: las primeras detalladas y las
últimas, cansadas. Para evitarlo, la fase empezó construyendo dos herramientas.

```bash
python3 scripts/auditoria/prosa.py       # texto que el estudiante lee, por módulo
python3 scripts/auditoria/cobertura.py   # cobertura del RA declarado y de la rúbrica
python3 scripts/auditoria/graficas.py    # datos reales de cada gráfica (C4)
```

**`prosa.py`** extrae el texto que el estudiante lee de verdad. No es trivial porque
la prosa vive en sitios distintos según el stack — y aquí aparece la **primera
corrección a la Fase 1**:

> **Los stacks son cinco, no cuatro.** La tabla §2 del informe técnico clasifica los
> módulos **1 y 2** como «HTML plano» y el plan original como «React sin Babel».
> Ninguna de las dos es cierta: **no cargan React** (`React.createElement` = 0,
> `useState` = 0) y su `<body>` sólo tiene 345 caracteres de texto. Todo el
> contenido vive en un objeto `courseData` dentro de un `<script>` sin `type`, con
> HTML incrustado en los literales. Es un quinto patrón, y es el único que **declara
> su propia duración por lección** — dato que resultó ser el más útil de toda la fase.

**`cobertura.py`** convierte C1 en algo medible. El syllabus declara para cada semana
un `ra`, una `teoria`, una `practica` y un trabajo `autonomo` concretos; el script los
descompone en temas atómicos y busca cada uno en su módulo.

> **Límite del método, y hay que decirlo:** que un tema esté «presente» significa que
> el módulo **lo nombra**, no que lo enseñe bien. Un 9/9 no absuelve a un módulo; un
> 0/4 sí lo condena. Es un detector de ausencias, no de calidad. Los juicios de
> calidad de este informe salen de leer el material, y están marcados como tales.

---

## 2. Cobertura del resultado de aprendizaje declarado (C1)

Temas que el syllabus asigna a cada semana, y cuántos aparecen en su módulo:

| # | Cobertura | Temas ausentes |
|---|---|---|
| 1 | **9/9** | — |
| 2 | **8/8** | — |
| 3 | **5/8** | `dataclasses`, «por qué lo exigen Pydantic/SQLAlchemy/FastAPI», Python 3.11.9 |
| 4 | 5/7 | error 422, Python 3.11.9 |
| 5 | 7/9 | ciclo petición-respuesta, Python 3.11.9 |
| 6 | 8/9 | Python 3.11.9 |
| 7 | 6/7 | Python 3.11.9 |
| 8 | 5/7 | dependencia de parámetros comunes, Python 3.11.9 |
| 9 | 5/7 | histórico de predicciones, Python 3.11.9 |
| 10 | 7/8 | modos de fallo |
| 11 | **7/7** | — |
| 12 | **7/7** | — |
| 13 | 9/10 | consistencia con el entrenamiento *(training/serving skew)* |

**Python 3.11.9 falta en los módulos 3 a 9**, los siete: confirma el hallazgo I7 de la
Fase 1 y le pone cifra. Descontando ese tema, que es transversal, **el único módulo
con un hueco de fondo es el 3**.

### 2.1 El módulo 3, en detalle

El syllabus declara para la semana 3:

> *teoría:* «Clases, atributos y métodos aplicados al modelado estadístico. Composición
> frente a herencia. Métodos especiales. **Por qué Pydantic, SQLAlchemy y FastAPI
> exigen entender esto primero**.» · *stack:* «Python 3.11.9 · POO · **dataclasses**»

El módulo cubre bien la primera mitad —clases, atributos, métodos, herencia y
polimorfismo— y **no cubre nada de la segunda**:

| | menciones en el módulo 3 |
|---|---|
| `dataclasses` | **0** |
| Pydantic | **0** |
| SQLAlchemy | **0** |
| FastAPI | **0** |
| `3.11.9` | **0** |

Esto importa más de lo que parece por una razón de diseño del curso: el syllabus
tiene una `nota` explícita en esta semana que dice que **la semana 3 sustituye a la
sesión de Flask** que anunciaban versiones anteriores. Es decir, la POO entró al
cronograma justificada como cimiento de lo que viene. **El módulo no construye ese
puente**: enseña POO genérica y termina en una sección de generación de clases con IA.

---

## 3. Lo que el curso evalúa y ningún módulo prepara (C2)

De los 15 criterios de la rúbrica adaptada, 9 son de Teoría del Riesgo y se cursan
en paralelo. Los 6 de ingeniería son los que este curso tiene que sostener:

| Criterio | Peso | ¿Qué módulos lo tratan? |
|---|---|---|
| c10 · Backend con FastAPI, Pydantic y SQLAlchemy | 12 % | 4, 6, 7, 8, 9 ✅ |
| c11 · Pipeline de ML, Singleton y endpoint de predicción | 8 % | 13 ✅ |
| c12 · Pruebas con pytest y TestClient | 4 % | 10 ✅ |
| c13 · Docker, despliegue en PaaS e integración continua | 7 % | 11, 12 ✅ |
| **c14 · Tablero (frontend)** | **3 %** | **ninguno** ❌ |
| c15 · Buenas prácticas: Git, venv, README y .env | 6 % | 1, 8 ✅ |

**El criterio 14 no lo prepara nadie.** Barrido en crudo sobre los 13 archivos:

| término | apariciones en los 13 módulos |
|---|---|
| «tablero» | **0** |
| «dashboard» | 7, todas incidentales (módulos 5, 6, 7, 12) |
| «streamlit» | **0** |
| «frontend» | 2 (módulos 2 y 7) |

Son 3 puntos de la nota de entregables por un artefacto que el material no explica
cómo construir. **Es una decisión tuya, no un defecto que yo pueda corregir**: o el
criterio sale de la rúbrica, o alguna sesión tiene que asumirlo. Está en §9 como
pregunta abierta.

### 3.1 Materia que se enseña y nadie evalúa

El caso simétrico. Tres bolsas de contenido que no sirven al RA de su semana ni a
ningún criterio de rúbrica:

| Módulo | Contenido | Tiempo declarado | Dónde vive de verdad |
|---|---|---|---|
| 1 | «Módulo 3: Docker vs Entornos Virtuales» | **25 min** | semana 11, entera |
| 2 | «Módulo 3: Validación con Pydantic» | **40 min** | semana 4, entera |
| 7 | Celery + RabbitMQ + Dead Letter Queues | no declarado | **ninguna semana** |

El del módulo 7 es el más claro: **35 menciones a Celery, 22 a RabbitMQ, 13 a «dead
letter» y 11 a «broker»**, y el syllabus **no nombra Celery ni RabbitMQ ni una sola
vez en sus 16 semanas**. Está además en el módulo más pesado del curso, que es
justamente el que menos margen tiene (§5).

Los del 1 y el 2 son más discutibles y no los llamo defecto sin matizarlos: un
adelanto deliberado puede ser buena pedagogía. Pero conviene verlos con el número
delante, porque **son 65 de los 315 minutos que esos dos módulos declaran**, en las
dos semanas donde el estudiante todavía está instalando Python.

---

## 4. Narrativa, registro y honestidad de las gráficas (C3, C4)

### 4.1 Aperturas: ¿motivan o indexan?

| Abren motivando | Abren indexando |
|---|---|
| **9** — «¿De qué trata esta guía?», «¿Qué es SQL?», «¿Y SQLite? ¿Por qué empezar con él?» | **1** — banner, objetivo declarado, y directo al contenido |
| **8** — «¿Por qué un estadístico necesita estos patrones?» | **4** — «Introducción: El Problema de los Datos» seguido de un ejemplo, sin decir a quién le duele |
| **5** — «Introducción: ¿Por qué necesitas saber esto?» | **10, 11, 12** — «1. Introducción» numerada, tono de manual |
| **7** — «Introducción: Arquitectura de Validación de Datos» | |

Los módulos 8 y 9 son los mejores del curso en esto y sirven de patrón para el resto.

### 4.2 Registro: a quién le habla el material

Conteo de marcas de segunda persona («puedes», «tienes», «debes», «necesitas»…),
de usted y de primera del plural:

| Módulo | tú | usted | nosotros |
|---|---|---|---|
| 9 | **20** | 0 | 3 |
| 3 | 17 | 0 | 10 |
| 5 | 11 | 0 | 0 |
| 8 | 9 | 0 | 0 |
| 4 | 5 | 0 | 1 |
| **6** | 4 | **7** | 1 |
| 2, 10, 11, 12 | 1–2 | 0 | 0 |
| **1, 7, 13** | **0** | 0–2 | **0** |

Dos cosas: **el módulo 6 es el único que trata de usted** al estudiante mientras el
resto lo tutea, y **los módulos 1, 7 y 13 no se dirigen al estudiante ni una vez**.
El 1 es el primero que el estudiante abre en el curso.

### 4.3 Gráficas: sólo hay 36, y las tres primeras son las que fallan

| Módulo | Gráficas | Motor | Veredicto |
|---|---|---|---|
| 1 | 2 | Chart.js | 1 informa · **1 inventada** |
| 2 | 1 | Chart.js | **inventada y además ajena** |
| 3–9 | **0** | — | el módulo 7, con 709 KB, no tiene ni una |
| 10 | 14 | Plotly | derivadas, con título de figura |
| 11 | 4 | Plotly | ídem |
| 12 | 15 | Plotly | ídem |
| 13 | 4 | Plotly | **las mejores**: pie de figura numerado y `~` marcando la aproximación |

**El caso del radar, que es el que hay que arreglar.** Los módulos 1 y 2 cierran su
sesión con un radar «Competencias Desarrolladas». Son **byte a byte el mismo
gráfico**:

```
labels: ['Rendimiento (Py3.11)', 'Aislamiento (Venv/Conda)', 'Contenedores (Docker)',
         'Control Versiones (Git)', 'Validación (Decoradores)']
data:   [85, 90, 70, 80, 85]
desc:   "Mapa de competencias técnicas cubiertas en este curso."
```

Tres problemas, de menor a mayor:

1. **Los números no significan nada.** 85 ¿de qué? No hay escala, ni fuente, ni
   método. Son cinco cifras puestas a ojo.
2. **La descripción es falsa.** Dice «cubiertas en **este curso**» y lo que lista son
   cinco temas de la semana 1, no los de las 16 semanas.
3. **En el módulo 2 los cinco ejes son de otra sesión.** El módulo 2 enseña HTTP,
   JSON/Pickle y Pydantic: **ninguno** de los cinco ejes del radar. El estudiante
   cierra la semana 2 viendo el mapa de competencias de la semana 1.

La gráfica de barras del módulo 1 (`Python 3.9 / 3.10 / 3.11` → `1.0 / 0.9 / 0.65`
de tiempo relativo) es distinta: **la forma es correcta** —3.11 es la mejora grande,
3.10 apenas movió la aguja— y coincide con lo que documenta CPython. Su defecto es
menor: **no cita de dónde sale**.

El contraste con el módulo 13 es instructivo y conviene copiarlo: sus cuatro figuras
llevan pie numerado («Figura 4.1 — Tamaño instalado de paquetes representativos de
ML…»), y los valores van marcados con `~` para declarar que son órdenes de magnitud,
no mediciones.

---

## 5. El criterio nuevo: ¿cabe en 60 min de teoría y aporta 180 de práctica?

Es el criterio que añadió el reparto confirmado de la sesión de 4 h. Y es el que
produce el hallazgo estructural de esta fase.

### 5.1 Sólo 2 de 13 módulos declaran cuánto duran

Los módulos **1 y 2** declaran una duración por lección. **Los otros once no dicen
nada**: el docente que los abre no sabe qué parte expone y qué parte es lectura.

Y el que declara, se contradice:

> **El módulo 2 anuncia «⏱️ 120 min» en su cabecera. Sus seis lecciones suman 170.**
> `40 + 30 + 40 + 20 + 25 + 15`. Cincuenta minutos de diferencia dentro del mismo
> archivo. Es el mismo tipo de defecto que el criterio C7 caza en el código —una
> cifra declarada que el propio material desmiente— aplicado al tiempo.

El módulo 1 declara `25+25+25+30+25+15` = **145 min** y no anuncia total, así que no
se contradice.

### 5.2 Leer la prosa en voz alta cabe; lo demás no se sabe

Estimación a 110 palabras/minuto (exposición técnica con pausas — es una estimación
declarada, no una medición):

| # | Palabras | Min de prosa | Líneas de código | Señales de práctica |
|---|---|---|---|---|
| 1 | 3 651 | 33 | 408 | 9 |
| 2 | 5 320 | 48 | 325 | 3 |
| 3 | 2 850 | 26 | 223 | 12 |
| 4 | 1 445 | **13** | 303 | 1 |
| 5 | 2 983 | 27 | 532 | 21 |
| 6 | 5 580 | 51 | 406 | 16 |
| **7** | **14 072** | **128** | **1 927** | 36 |
| 8 | 2 208 | 20 | 731 | 18 |
| 9 | 4 791 | 44 | 757 | 17 |
| 10 | 3 402 | 31 | 1 400 | 15 |
| 11 | 5 995 | 54 | 1 110 | 23 |
| 12 | 5 519 | 50 | 848 | 17 |
| 13 | 5 037 | 46 | 610 | 6 |
| | **62 853** | **571** | **9 580** | |

**Conclusión honesta, con sus dos mitades:**

- **La prosa cabe.** 571 minutos contra los 780 disponibles (13 × 60). **El único
  módulo que revienta su propia hora es el 7: 128 minutos, 2,1 veces su presupuesto.**
- **Sobre las 9 580 líneas de código no puedo pronunciarme, y ése es el hallazgo.**
  Si se explican en clase a un ritmo normal, el curso necesita cuatro veces las horas
  que tiene. Si son material de consulta para los 180 min de práctica, sobra tiempo.
  **El material no dice cuál de las dos cosas es**, y sin eso ningún módulo se puede
  planificar.

Ésa es la observación de fondo de la Fase 2: **los 13 módulos están escritos como
manuales de estudio completos, no como planes de una sesión de 4 h partida en 60 y
180.** No es que estén mal escritos; es que responden a otra pregunta.

### 5.3 Los dos extremos

- **Módulo 7 · 709 KB, 14 072 palabras, 1 927 líneas de código.** Cinco veces el
  módulo medio. La Fase 1 ya avisó de que desbordaba cualquier estimación; ahora
  tiene cifra. Es además donde vive la subsección de Celery que nadie evalúa (§3.1),
  y no tiene ni una gráfica.
- **Módulo 4 · 1 445 palabras, 13 min de prosa, 1 señal de práctica.** Es el más
  ligero con diferencia. **Pero aquí no hay defecto:** su título es «Estudio Autónomo:
  Validación de Datos con Pydantic» y el syllabus declara para la semana 4 exactamente
  eso — «Módulo de estudio autónomo: recorrer el material completo». **Es el único
  módulo cuyo tamaño coincide con el papel que el syllabus le da.**

---

## 6. Todos los hallazgos, por gravedad

### Bloqueantes — el curso evalúa algo que no enseña, o enseña algo que se contradice

| ID | Módulo | Hallazgo |
|---|---|---|
| **P1** | — | La rúbrica evalúa «Tablero (frontend)» (3 %) y **ningún módulo lo prepara** |
| **P2** | 3 | No nombra `dataclasses`, Pydantic, SQLAlchemy ni FastAPI, que es la teoría que el syllabus le asigna |
| **P3** | 3 | Envía la API Key del estudiante **en la URL**, que es lo que el módulo 2 prohíbe expresamente |
| **P4** | 5 | Enseña Flask donde el proyecto se evalúa en FastAPI *(confirmado de Fase 1 — decisión ya tomada: reorientar)* |

### Importantes — contradicen al syllabus, gastan tiempo de clase o engañan al lector

| ID | Módulo | Hallazgo |
|---|---|---|
| P5 | 7 | Celery/RabbitMQ/DLQ: 70 menciones de materia que el syllabus no cita en 16 semanas |
| P6 | 7 | 128 min de prosa contra un presupuesto de 60. El doble |
| P7 | 2 | Declara 120 min en cabecera; sus lecciones suman 170 |
| P8 | 1, 2 | Radar «Competencias» con datos inventados, **duplicado**, y en el módulo 2 con ejes de otra sesión |
| P9 | 2 | 40 min a Pydantic, que es la semana 4 |
| P10 | 1 | 25 min a Docker, que es la semana 11 |
| P11 | 11 módulos | No declaran ninguna duración: el docente no sabe qué expone y qué deja leer |
| P12 | todos | Ningún módulo separa exposición de material de consulta (§5.2) |
| P13 | 12 | Compara Railway y Render donde el proyecto exige Render *(confirmado: 46/40)* |
| P14 | 1, 7, 13 | No se dirigen al estudiante ni una vez. El 1 es el primero del curso |
| P15 | 6 | Único módulo que trata de **usted**; los demás tutean |
| P16 | 3–9 | Python 3.11.9 no se menciona nunca *(confirma I7 de Fase 1, con cifra)* |

### Cosméticos

| ID | Módulo | Hallazgo |
|---|---|---|
| Q1 | 10 | El `<title>` dice «Semana 10» y la cabecera «Semana X», en el mismo archivo. «Semana X» es además indistinguible de un marcador sin rellenar |
| Q2 | 1, 4 | Aperturas que indexan en vez de motivar |
| Q3 | 1, 2 | Gráfica de barras sin fuente citada |
| Q4 | 7 | 709 KB y 0 gráficas |
| Q5 | 2 | «Módulo 5 (Bonus): Funciones en Python», 25 min, por debajo del nivel de la semana 2 |
| Q6 | 3 | Termina en un generador de clases con IA, no en el puente hacia Pydantic |

**Total de la Fase 2: 4 bloqueantes, 16 importantes, 6 cosméticos.**
Sumados a la Fase 1 (6 bloqueantes ya corregidos, 11 importantes, 9 cosméticos):
**26 hallazgos abiertos de los que 4 son bloqueantes.**

---

## 7. Correcciones a las fases anteriores

Como en la Fase 1, lo que este barrido contradice se anota antes de que la cifra se
repita:

1. **Los stacks son cinco, no cuatro** (§1). Los módulos 1 y 2 no son «HTML plano»
   (informe técnico §2) ni «React sin Babel» (plan §0.2): no cargan React.
2. **`new Chart(` no cuenta gráficas, cuenta ramas del renderizador.** El módulo 2
   tiene **una** gráfica y dos `new Chart(`. La métrica del primer borrador de
   `prosa.py` decía 2 y era falsa; `graficas.py` cuenta definiciones de datos.
3. **El módulo 7 no tiene fórmulas visibles pese a cargar KaTeX**, igual que el 8
   (§C2 de la Fase 1). No se ha añadido como hallazgo nuevo porque ya estaba, pero
   la ausencia total de gráficas en el módulo más pesado sí lo es (Q4).

> **Salvedad del contador de gráficas.** `graficas.py` cubre dos de las tres formas
> en que el material define gráficas: el almacén de datos de Chart.js (módulos 1–2) y
> el JSON que `plotly.io.to_html` exporta (módulos 10–12). **El módulo 13 usa una
> tercera**, un hook `usePlotly(id, dataFn, layoutFn)` de React donde los datos salen
> de funciones, así que el script devuelve 0 para él. **Sus 4 gráficas están contadas
> a mano** —`chart-serializacion`, `chart-latencia`, `chart-pytorch`,
> `chart-docker-comp`— y sus datos leídos uno a uno. La cifra del informe es correcta;
> la del script, no. Queda anotado para el Checkpoint 3.

---

## 8. Auto-auditoría de este informe

Dónde puede estar equivocado, y qué se hizo para reducirlo.

**Falsos positivos cazados antes de publicar.** Fueron tres, y los tres habrían
llegado al informe:

- **`\bTODO\b` caza la palabra española «todo».** Daba 11 «notas internas filtradas»
  en el módulo 1 y 13 en el 9 — **todas falsas**. Peor: tampoco basta con exigir
  mayúsculas, porque el material escribe «Aísla TODO (SO, config, libs)» como énfasis.
  El detector definitivo exige `TODO:` o `TODO-`, y se validó con un control negativo
  (caza `TODO:`, `FIXME`, `lorem ipsum` y «diapositiva»; no caza «Aísla TODO»).
  **Resultado real: 0 notas internas en los 13 módulos.**
- **Las listas de clases de Tailwind se colaban como prosa.** «my-4 rounded-xl
  overflow-hidden border border-gray-700» pasa cualquier filtro ingenuo de «parece una
  frase». Inflaba el recuento de los cuatro módulos React y **con él la estimación de
  minutos**, que es justo lo que había que medir bien: el módulo 6 pasó de 7 422
  palabras a 5 580 y el 4 de 1 792 a 1 445. Se corrigió con un filtro de densidad.
- **Una «ancla rota» en el módulo 5 que no existía.** Llegué a escribir que el enlace
  «Preguntas de Sustentación» apuntaba a la bibliografía. Era mi regex, que sólo
  miraba `href="#modulo-N"`. El destino real es `#preguntas-sustentacion` y **existe**.
  Barrido completo: **0 anclas internas rotas en los 13 módulos.**

**Verificación una a una de las cifras publicadas.** Antes de entregar se volvieron a
comprobar contra el archivo **las 73 afirmaciones cuantitativas** de este informe:
conteos de menciones, duraciones declaradas, recuentos de palabras y de líneas, número
de gráficas, marcas de registro, cobertura del RA y el análisis de sensibilidad de §8.

**Resultado: 72 correctas, 1 equivocada.** La tabla de §5.2 sumaba **9 180 líneas de
código y son 9 580**; error de transcripción mío, ya corregido. No cambia ninguna
conclusión —la observación es que el volumen de código no está caracterizado, y 400
líneas más la refuerzan— pero queda constancia. La rutina de verificación es la que
aparece en §11.

**Lo que sigue siendo débil, y hay que decirlo:**

| Riesgo | Efecto |
|---|---|
| **Las 110 palabras/minuto son una estimación, no una medición** | Toda la tabla §5.2 se mueve con ese número. A 130 ppm el total baja de 571 a 483 min; a 90 sube a 698. **La conclusión «la prosa cabe» aguanta en todo el rango; el «módulo 7 = 2,1×» también** (128→108 min en el mejor caso, aún por encima de 60) |
| **«Señales de práctica» cuenta palabras, no ejercicios** | Busca «ejercicio», «autoevaluación», «implementa»… Un módulo con 21 señales no tiene 21 ejercicios. Sirve para ordenar módulos entre sí, no para afirmar que uno aporta 180 min |
| **La cobertura del RA detecta menciones, no calidad** | Declarado en §1. El 9/9 del módulo 1 no dice que la semana 1 esté bien enseñada; dice que no falta ningún tema |
| **El juicio «motiva o indexa» (§4.1) es mío** | Es el único apartado sin respaldo cuantitativo. Está separado a propósito para que se pueda discutir aparte |
| **No se verificó nada en navegador** | Esta fase es de lectura. Los hallazgos de renderizado siguen siendo los de la Fase 1 |
| **Los 9 criterios de Riesgo de la rúbrica no se auditaron** | Son de la asignatura paralela. Que ningún módulo los prepare es esperado, no un hallazgo |

**Consecuencia práctica, igual que en la Fase 1:** los 4 bloqueantes son un **suelo**.
Lo que está en la lista está verificado contra el archivo; lo que no está puede seguir ahí.

---

## 9. Lo que necesito decidido antes de la Fase 3

Tres preguntas de verdad y una confirmación pendiente. Ninguna la puedo resolver yo
porque las cuatro son decisiones de diseño del curso, no defectos.

1. **El criterio 14 «Tablero (frontend)», 3 %.** Ningún módulo lo prepara (P1). Tres
   salidas: (a) sacarlo de la rúbrica y redistribuir 3 puntos; (b) añadir un bloque de
   tablero al módulo 13 o al taller de la semana 15; (c) dejarlo y declarar
   explícitamente que se evalúa sobre trabajo autónomo. **Recomiendo (b)**: el taller
   de la semana 15 ya integra «modelo, API y tablero» según el syllabus, así que el
   hueco es sólo de material.

2. **El adelanto de Pydantic (40 min en la semana 2) y de Docker (25 min en la semana
   1).** ¿Fue deliberado —dar un anticipo motivador— o es sedimento de una versión
   anterior del cronograma? Si es deliberado no lo toco y lo declaro en el módulo; si
   no, son 65 minutos recuperables en las dos semanas más cargadas de instalación.

3. **El módulo 7 y su subsección de Celery.** Es el módulo más pesado del curso
   (2,1× su hora) y contiene 70 menciones de materia que el syllabus no cita.
   **Recomiendo cortarla** y recuperar el tiempo, pero si la usas como lectura de
   extensión, se marca como opcional y se queda.

4. **Confirmación pendiente de la Fase 1:** «módulo 12 → podar Railway, dejar Render».
   Sigue sin confirmar y sigue sin tocarse. El conteo se ha vuelto a verificar: 46/40.

---

## 10. Recomendación de alcance para la Fase 3

El plan ofrece tres opciones (§3 del `PLAN_AUDITORIA_MODULOS.md`). Con el informe
delante, **mantengo la recomendación de la Opción A ahora, pero con una corrección
de contenido**: la lista original de la Opción A era casi toda cosmética —títulos,
metadatos, versiones— y esta fase muestra que **lo que de verdad hay que arreglar
antes de clases no está en esa lista**.

**Opción A revisada, en el orden en que yo la haría:**

| Orden | Trabajo | Módulos | Por qué primero |
|---|---|---|---|
| 1 | Cerrar los 4 bloqueantes P1–P4 | 3, 5, rúbrica | Es materia que se evalúa y no se enseña |
| 2 | Declarar la duración de cada módulo y separar exposición de consulta | los 13 | Sin esto no se puede planear ninguna sesión (P11, P12) |
| 3 | Arreglar el radar duplicado y su descripción | 1, 2 | Se ven en la semana 1 y 2, y son falsos (P8) |
| 4 | Títulos, numeración de semana y Python 3.11.9 | 1, 3–9, 10, 12, 13 | Lo que ya traía la Opción A |
| 5 | Desborde a 375 px | 1, 2 | Único defecto de render verificado (Fase 1) |

**Las opciones B y C siguen siendo para el semestre, no para antes del 8 de agosto.**
Y añado un argumento nuevo a favor de aplazarlas: esta fase muestra que **el problema
grande del material no es visual, es de encaje con el cronograma**. Homogeneizar la
presentación (B) o migrar a LP-CORE (C) no arregla ni uno de los cuatro bloqueantes.

**Orden de ejecución:** el que fijaste — cronograma, no gravedad. Con una excepción
que propongo: **el módulo 3 antes que el 1 y el 2**, porque tiene dos de los cuatro
bloqueantes y se dicta la semana 3. Si prefieres el orden estricto, se hace 1 → 13
sin más.

---

## 11. Reproducir cualquier dato de este informe

```bash
# Prosa, secciones, registro, notas internas y estimación de minutos
python3 scripts/auditoria/prosa.py
python3 scripts/auditoria/prosa.py --ver 5           # volcar el texto del módulo 5
python3 scripts/auditoria/prosa.py --secciones       # árbol de secciones de los 13

# Cobertura del RA declarado y de la rúbrica
python3 scripts/auditoria/cobertura.py
python3 scripts/auditoria/cobertura.py --detalle 3   # desglose del módulo 3

# Gráficas y sus datos reales
python3 scripts/auditoria/graficas.py
python3 scripts/auditoria/graficas.py --detalle 13

# Comprobaciones puntuales citadas en el informe
grep -c "React.createElement" 1_*.html               # 0 — no es React (§1)
grep -oic "dataclass" 3_*.html                       # 0 — (§2.1)
grep -oic "celery" 7_*.html                          # 35 — (§3.1)
grep -oic "celery" 0_Syllabus_P_A_IA.html            # 0 — (§3.1)
grep -o 'duration: *"[0-9]* min"' 2_*.html           # suman 170, la cabecera dice 120
```

Salidas en `scripts/auditoria/salida/`: `prosa/NN.txt`, `prosa_metricas.json`,
`cobertura.json`, `graficas.json`.
