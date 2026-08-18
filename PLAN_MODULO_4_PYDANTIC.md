# Plan de revisión — Módulo 4 · Pydantic: validación declarativa

**Asignatura:** Python para Desarrollo de APIs e IA · USTA · Estadística · 2026-II
**Fecha:** 2026-08-17
**Archivo:** [`4_Python_para_APIS_IA_Pydantic.html`](4_Python_para_APIS_IA_Pydantic.html) · 3 066 líneas
**Fuente de remontaje:** [`heredado/4_Python_para_APIS_IA_Pydantic.html`](heredado/4_Python_para_APIS_IA_Pydantic.html)
**Entorno de verificación:** Python 3.10.14 · Pydantic 2.12.5 · pandas 2.3.3

---

## 0. Lo que se encontró, y cómo se comprobó

No se auditó leyendo el código: se levantó el módulo en `http://localhost:8137`, se leyó el
DOM sección por sección y se **ejecutaron los nueve bloques** extrayéndolos tal como los
cuece el navegador, no como están escritos en el archivo. La distinción no es teórica: dos
de los tres defectos bloqueantes **solo existen después de que JavaScript toca el texto**, y
leyendo el archivo se ven correctos.

### 0.1 Inventario

| | Cantidad |
|---|---|
| Secciones | 10 |
| Bloques de código | 9 (8 Python + 1 shell) |
| Preguntas de autoevaluación | 5 |
| Prosa | ~7 900 caracteres |
| Usos de `Box` en el contenido | 1 |
| Figuras, diagramas o gráficas | **0** |

### 0.2 Los tres bloqueantes — CERRADOS el 2026-08-17

**B1 · Las dos expresiones regulares se publicaban mutiladas.** El literal de plantilla de
JavaScript se come la barra invertida antes de que el texto llegue a la pantalla:

| En el archivo | Lo que veía el estudiante |
|---|---|
| `pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"` | `pattern=r"^[w.-]+@[w.-]+.w+$"` |
| `pattern=r"^\d{5}$"` | `pattern=r"^d{5}$"` |

No era cosmético. El «Ejemplo 4: Pattern inválido» quiere enseñar que falla el código
postal; ejecutado tal como se publicaba lanzaba **dos** errores, y el segundo rechazaba
`paciente@hospital.com`, un correo válido. Enseñaba lo contrario de lo que decía. Y la
página se contradecía a sí misma en pantalla: cuatro párrafos más arriba, la tarjeta «Email
válido» sí mostraba `r"^\S+@\S+\.\S+$"` intacta, porque ahí es texto JSX y no literal de
plantilla.

*Arreglo:* duplicar la barra en el origen (`\\w`, `\\d`), que es como ya estaban escritos
los `\\n` del mismo bloque. *Comprobado:* el DOM muestra las dos regex correctas y el
Ejemplo 4 lanza un error, el del código postal.

**B2 · El bloque de apertura no daba un promedio malo: reventaba.**
`TypeError: unsupported operand type(s) for +: 'float' and 'str'`. El comentario prometía
`# ¡Incorrecto!` —un número plausible pero falso, que es justo la lección de *garbage in,
garbage out*— y lo que salía era una traza.

*Arreglo:* el bloque ahora demuestra las dos formas de fallar y las distingue, que es la
lección real. El fallo silencioso (un peso negativo que nadie comprueba) da 48,57 kg frente
a los 75,35 kg reales; el ruidoso (números escritos como texto) se captura y se enseña.
*Comprobado:* corre limpio e imprime las tres líneas.

**B3 · El bloque «Fuentes Consultadas» estaba marcado como Python y contenía `pip install`.**
No compilaba (`SyntaxError`) y se resaltaba con la gramática equivocada.

*Arreglo:* pasa a `lang="shell"`. **Ojo con la clave:** LP-CORE mapea `shell → bash` en
`GRAMATICA` (línea 1015); poner `lang="bash"` no da error, simplemente deja el bloque **sin
resaltar**. Se intentó primero con `bash`, se vio en el DOM que salían 0 tokens y se
corrigió. *Comprobado:* 9 tokens de resaltado en el DOM.

**Estado tras la Fase 0:** los 8 bloques Python compilan y corren con exit 0; el bloque
shell pasa `bash -n`; las salidas declaradas en los comentarios `# Output:` de los bloques
3, 5 y 6 coinciden carácter por carácter con la salida real; las 10 secciones montan y la
consola no emite un solo error.

**B1 y B2 se llevaron también al heredado**, para que un remontaje no los deshaga; sus nueve
bloques se volvieron a extraer y ejecutar desde allí. **B3 no se puede llevar**: el heredado
guarda el código en un campo llamado `pythonCode` y el guion fija el lenguaje a fuego. Es la
razón de ser de T11, y hasta entonces el módulo 4 no debe remontarse.

### 0.2.1 El defecto de la barra invertida era exclusivo del módulo 4

El detector vive ya en
[`scripts/auditoria/escapes.py`](scripts/auditoria/escapes.py), con las convenciones del
resto de la cadena. Barre los 13 módulos y `heredado/` —27 archivos, 228 bloques— y trae una
autoprueba de 13 casos (`--autoprueba`), porque un detector que sólo se ha visto callar sobre
archivos limpios es indistinguible de uno roto. Sale con código 1 si encuentra algo, así que
sirve en una comprobación automática.

**Resultado del barrido: sólo el módulo 4 lo tenía.** Los otros tres de su familia —el 3, el
6 y el 13— están limpios.

> Escribir el detector costó **tres** intentos y conviene dejar dichos los dos fallos, porque
> los dos consistían en parecer que todo estaba bien.
>
> El primero marcaba como defecto toda línea en la que el texto cocido difiere del escrito, y
> eso incluye las que están **bien**: `\\w` tiene que cocerse a `\w`. Daba 18 falsos positivos
> en el módulo 13 —cada continuación de línea de un Dockerfile— y marcaba como rotas las dos
> líneas que se acababan de arreglar. La regla correcta no mira si el texto cambió, sino si
> una racha **impar** de barras precede a un carácter que JavaScript no reconoce como escape.
>
> El segundo recortaba el bloque con `` `(.*?)` ``, que se para en el primer acento grave
> **aunque esté escapado**. En `heredado/3` había un `` \` `` a mitad de bloque: el detector
> cortaba ahí, se inventaba un defecto en el corte y —esto es lo grave— dejaba de mirar todo
> lo que venía después. El cuerpo se toma ahora con `` (?:[^`\\]|\\.)* ``, y hay cinco casos
> de autoprueba que lo vigilan.

### 0.3 Lo que está bien y no se toca

La sección 7 —del `ValidationError` al 422— es la mejor del módulo: es la única escrita con
la voz del curso y no con la del artículo de origen, y explica bien por qué 422 y no 400. El
caso sutil `diagnostico_previo: str | None = Field(...)` («obligatorio pero nulable») está
correctamente planteado. Los bloques 2, 3, 5, 6, 7 y 8 son correctos.

---

## 1. La decisión de arquitectura que gobierna este plan

**Un remontaje borra todo lo que se corrija sólo en el archivo publicado.**

El módulo 4 pertenece a la familia «React con `curriculum` de datos» y se monta con
`convertir_react.py` a partir de `heredado/4_…html`. El README advierte que **cada cambio de
LP-CORE obliga a volver a montar estos capítulos**. Los tres bloqueantes existen también en
el heredado (líneas 512-513, 771 y 788), así que un remontaje los reintroduce.

Y hay un segundo filo, peor, porque no se arregla editando el heredado:
`convertir_react.py` **fija `lang="python"` a fuego** (línea 345) y lee el campo
`pythonCode`. El arreglo B3 no puede sobrevivir a un remontaje sin tocar el guion.

**Regla de este plan:** toda corrección de contenido se aplica **en los dos archivos**, y la
del lenguaje del bloque exige además abrir una vía en el guion. Nada se da por hecho hasta
verlo en el DOM.

---

## 2. Las decisiones del docente (2026-08-17)

| | Pregunta | Decisión |
|---|---|---|
| **D1** | El archivo dice seguir «el hilo financiero: crédito de libre inversión» y los ejemplos hablan de pacientes y experimentos | **Se conserva el hilo clínico-estadístico.** Se corrige el comentario que miente |
| **D2** | El módulo declara `stack: "Pydantic v2"` y enseña el estilo `Field(...)` que la documentación v2 ya no pone primero | **Añadir `Annotated` como estilo moderno**, junto al actual. Sin `model_validator`: la semana 7 profundiza |
| **D3** | Cero figuras y un solo uso de `Box` frente a los 13 de los módulos 1 y 2 | **Las tres cosas:** convertir las tarjetas a `Box`, añadir el diagrama del flujo de validación y la gráfica del sesgo |
| **D4** | Orden de trabajo | **Bloqueantes primero.** Hechos y verificados antes de escribir este plan |

---

## 3. Fase 1 — Verdad técnica y actualización a Pydantic v2 · CERRADA el 2026-08-17

### T1 · Borrar el comentario del hilo financiero — NO PROCEDE

**El comentario no es del módulo 4.** Sale de `lp-base.html`, la plantilla que este curso
comparte con Lógica de Programación Financiera, donde encabeza el `const EJ_INTERES` de
**aquel** curso —cuyo hilo sí es un crédito de libre inversión colombiano—. El montaje se
lleva `EJ_INTERES` pero deja el encabezado huérfano, y por eso lo traen **los 13 módulos**,
idéntico.

Es un comentario de JavaScript: el estudiante no lo ve nunca. Borrarlo sólo aquí lo desharía
el siguiente remontaje y dejaría mintiendo a los otros doce. Corregirlo es un cambio de
LP-CORE en el otro repositorio, con remontaje de los trece; queda anotado en §8 como asunto
transversal, no como tarea de este módulo.

### T2 · Sección 2: el ejemplo dice que valida el correo, y no lo valida

El texto afirma que crear la persona «con datos inválidos lanza error» señalando
`email="correo-invalido"`. El error lo lanza la edad. `email` es `str` pelado y no se valida:
comprobado, `'esto-no-es-un-correo-en-absoluto'` pasa sin queja. Es una afirmación falsa en
la segunda sección del módulo, y encima desaprovecha el mejor puente hacia la sección 4:
*el tipo solo no basta, y por eso existe `Field`*.

- **Criterios:** el ejemplo demuestra que el correo inválido **entra**; el texto lo nombra como el problema que `Field(pattern=…)` resuelve más adelante.
- **Verificación:** el bloque corre y su salida enseña el correo aceptado; el DOM muestra el texto nuevo.
- **Dependencias:** ninguna · **Archivos:** publicado + heredado · **Tamaño:** S

### T3 · Sección 4: `Annotated` como estilo moderno (D2)

Ni una aparición de `Annotated`, `model_validator`, `ConfigDict` ni `EmailStr` en todo el
módulo. Por D2 entra sólo `Annotated`: una tarjeta que enseñe `Field(...)` y
`Annotated[int, Field(ge=0)]` lado a lado, diciendo cuál recomienda hoy la documentación y
por qué el material usa el otro.

- **Criterios:** las dos formas aparecen juntas y se declara cuál es la recomendada; el bloque de código sigue compilando y corriendo.
- **Verificación:** ejecutar el bloque; leer la tarjeta en el DOM.
- **Dependencias:** ninguna · **Archivos:** publicado + heredado · **Tamaño:** M

### T4 · Sección 5: `None` no es `NaN`

La tarjeta «Nullable» dice que el dato «puede ser explícitamente `None` (NaN)». En un módulo
cuya tesis es no confundir ausencia con valor, y para un pregrado en Estadística, equiparar
los dos es justo el error que se está enseñando a evitar. `None` es ausencia en Python; `NaN`
es un float del IEEE 754 que pandas usa para representarla en una columna numérica.

- **Criterios:** el texto distingue los dos y explica en una línea cómo se relacionan al pasar por pandas.
- **Verificación:** leer la tarjeta en el DOM.
- **Dependencias:** ninguna · **Archivos:** publicado + heredado · **Tamaño:** S

### T5 · Sección 8: «Big Data» con `iterrows()` sobre tres filas

El bloque se titula «Integración con Pandas para Big Data» y usa `iterrows()`, que es
exactamente lo que no se hace con volumen. El patrón fila-a-fila es correcto para enseñar la
idea; el título promete otra cosa.

- **Criterios:** el título deja de prometer volumen; una nota explica que `iterrows()` sirve para aprender el patrón y no escala, y qué se hace cuando sí hay volumen.
- **Verificación:** el bloque sigue corriendo; el DOM muestra la nota.
- **Dependencias:** ninguna · **Archivos:** publicado + heredado · **Tamaño:** S

### ✅ Punto de control 1 — PASADO

- [x] Los 8 bloques Python compilan y corren con exit 0; el noveno pasa `bash -n`
- [x] Las salidas declaradas de los bloques 3, 5 y 6 coinciden con las reales
- [x] Las 10 secciones montan, la consola está limpia y no hay desborde horizontal a 375 px
- [x] El heredado corre sus 9 bloques salvo el de bibliografía, que es T11
- [x] `escapes.py` da 0 en los dos archivos

### 3.1 Una trampa de JSX que apareció al escribir, y que la Fase 3 va a repetir

Las tres tareas de prosa introdujeron un defecto de composición que **el código no delata y
el navegador no denuncia**: JSX borra el espacio en blanco que toca un salto de línea, de
modo que esto

```jsx
recomienda hoy otra forma, con
<code>Annotated</code>, y te la vas a encontrar
```

se lee en pantalla como «**conAnnotated**». Salieron cuatro así, y el primer arreglo —mover
la palabra a la línea siguiente— trasladó el problema al otro lado: `<code>None</code>` +
salto + `en` da «**Noneen**».

**La regla:** una etiqueta en línea y la palabra que la acompaña van en la **misma** línea
del archivo, a ambos lados. Nunca un salto de línea entre texto y `<code>`.

Se comprobó recorriendo las diez secciones en el DOM y mirando los nodos de texto vecinos de
cada `<code>` fuera de un `<pre>`. Queda una aparición, en la sección 7, que **no es de esta
tanda**: el autor la sorteó metiendo el espacio dentro de la etiqueta
(`<code> ValidationError</code>`). Se ve bien; se recoge en T6.

---

## 4. Fase 2 — Redacción y ortografía · CERRADA el 2026-08-17

### T6 · Pasada de ortografía y estilo sobre la prosa — HECHA

Se volcaron las diez secciones desde el DOM (11 554 caracteres de prosa renderizada) y se
leyeron enteras. **51 sustituciones** en cada archivo, aplicadas con una lista cerrada de
cadenas exactas y un número de apariciones esperado por cada una: si algo no cuadra, no se
escribe nada. Un patrón falló en el ensayo —`Strings:` llevaba un `className` que yo no había
previsto— y por eso el ensayo existe.

| Dónde | Qué | Cómo quedó |
|---|---|---|
| 7 títulos de bloque y 10 rótulos | *Title Case* inglés | Solo mayúscula inicial |
| Bloque 4 | `múltiple_of` | `multiple_of` — es un identificador |
| Bloque 7 | «anios», «Numero», «Peticion», «Asi» | Con sus tildes |
| §3 | «Type Hints» | «Anotaciones de tipo», que ya se declara en §2 |
| §4 | «Strings», «requerido», «Email válido» | «Cadenas de texto», «obligatorio», «Correo electrónico válido» |
| §5 | «Required», «Optional (Default)», «Nullable», «el input» | «Obligatorio *(required)*», «Con valor por defecto *(optional)*», «Anulable *(nullable)*», «la entrada» |
| §2 | «parsear» | «convertir» |
| Quiz | «coaccionar», «Data Cleaning», «string» ×3, «pipeline», «(default)» | Traducidos |
| Todo | «sólo» ×2 frente a «solo» ×5 | «solo», sin tilde |
| §1, §3, §6, §10 | Comillas rectas en texto citado | «…» |

### 4.1 El cuestionario enseñaba acentos graves

Al releerlo en el DOM apareció algo que no estaba en el inventario: dos preguntas y una
opción venían escritas con acentos graves de Markdown —``preferimos `int | None = None`
sobre `int = 0` ``— y **`Quiz` pinta el enunciado con `{q.pregunta}`**, texto plano, sin
marcado. El estudiante veía los acentos graves tal cual. Se quitaron: sin forma de marcar
código en ese componente, la notación no marcaba nada y solo estorbaba.

Se comprobó respondiendo el cuestionario en la página, porque **las justificaciones no
existen en el DOM hasta que se contesta**: leerlas exigía jugar, y ahí es donde se ven
«coaccionar» y «Data Cleaning» ya corregidos.

### ✅ Punto de control 2 — PASADO

- [x] Los 8 bloques Python del publicado corren; el noveno pasa `bash -n`
- [x] El heredado corre 8 de 9; el de bibliografía es T11
- [x] `escapes.py` da 0 en los dos archivos y su autoprueba pasa 13/13
- [x] Ningún espacio comido por JSX en las diez secciones
- [x] Consola limpia; sin desborde horizontal a 375 px en §4 y §8
- [x] Cero rastros de los 12 términos corregidos, en los dos archivos
- [ ] **Lectura del docente** antes de pasar a la Fase 3

---

## 5. Fase 3 — Componentes y figuras (D3) · CERRADA el 2026-08-17

> **Dónde viven las figuras, y por qué no donde decía este plan.** T8 y T9 declaraban
> `build/migracion/m4/graficas.jsx` entre sus archivos. Es un sitio equivocado: `build/` **no
> se versiona**, lo rehace `graficas.py` a partir del Plotly del heredado, y el heredado del
> módulo 4 no tiene ninguno —de ahí que el módulo llegara sin figuras—. Lo escrito a mano va
> en `scripts/migracion/componentes/modulo_4.jsx`, que sí se versiona y que **nombra la
> receta**; es el mismo mecanismo con el que el módulo 3 conserva su Constructor IA.
>
> El enganche usa lo que ya existía: `interactiveType` en la entrada del heredado, que
> `ACOMPANANTES` traduce a la etiqueta del componente. Se añadieron dos entradas —`sesgo_cero`
> y `flujo_422`—, que es una tabla de datos, no un cambio del conversor. El mecanismo coloca
> el componente **antes del bloque de código** —`seccion_jsx` añade el acompañante y después
> el `CodeBlock`—, y ahí están las dos en el publicado. Este plan dijo primero lo contrario;
> lo corrigió el primer `diff` de T11. Leído en la página funciona mejor así: la figura
> resume lo que el texto acaba de explicar y el código lo demuestra a continuación.

### T7 · Convertir las tarjetas de Tailwind a `Box` — REPLANTEADA

El diagnóstico de §0.1 («usa `Box` una vez, los módulos 1 y 2 lo usan 13») era cierto pero
sacaba la conclusión equivocada. **`convertir_react.py` ya convierte `div.tip-box` → `Box`
solo.** Que aquí salga uno y allí trece no es descuido: el guion se salta a propósito las
cajas que son celda de una rejilla, porque `Box` es un aviso de ancho completo con sus
`px-5 py-4` y `my-4`, y meterlo en un `grid` descabala la fila. Es el tropiezo del módulo 3
(commit `1bec2ab`), ya documentado dentro del propio guion. El módulo 4 tiene casi todas sus
cajas dentro de `grid md:grid-cols-2`; de ahí el uno.

Así que la tarea no es «convertir las tarjetas», que sería deshacer una decisión correcta.
Lo que queda es más pequeño y de otra clase:

1. **Las llamadas de atención de ancho completo que no son `tip-box`** —los dos
   `bg-yellow-50 border-l-4` de la sección 5 y el `bg-blue-50` de la 10— sí deberían ser
   `Box`, y el guion no las ve porque no llevan esa clase. Se marcan como `tip-box` en el
   heredado y el guion hace el resto.
2. **Las tarjetas de rejilla se quedan**, y su CSS lo rescata `estilos.py`. No se tocan.

Lo escrito en la Fase 1 ya sigue esta regla: el aviso de `Annotated` y el del volumen se
escribieron como `tip-box` en el heredado y como `Box` en el publicado, con el rótulo en
`<strong>` para que el guion saque el mismo `label`, y con `type="info"`/`"warn"` elegidos
según la tabla `PALABRAS_CAJA` para que un remontaje reproduzca exactamente lo mismo.

- **Hecho.** Las tres pasan a `Box`: «Cuidado con el 0» (`warn`), «None no es NaN» (`info`) y «Sobre esta adaptación» (`info`). Las celdas de rejilla no se tocaron.
- **Verificado importando el conversor** y pasándole los tres fragmentos del heredado: devuelve `<Box type="warn" label="Cuidado con el 0">`, `<Box type="info" label="None no es NaN">` y `<Box type="info" label="Sobre esta adaptación">`, que es exactamente lo que hay en el publicado. El `type` no se elige a mano: sale de `PALABRAS_CAJA` leyendo el rótulo, y por eso el primero se rotuló «Cuidado con el 0» —«cuidado» es la palabra que dispara `warn`— en vez de «Nota estadística», que habría caído en `info`.

### T8 · Diagrama del flujo de validación (sección 7) — HECHO

`FlujoValidacion422`, un `Pipeline` de cuatro pasos: llega el JSON → el modelo comprueba →
`ValidationError` → respuesta 422. Los rótulos son los mismos términos que usa el texto, en
el mismo orden. Verificado en el DOM: los cuatro pasos con sus flechas, y sin desborde a
375 px.

### T9 · Gráfica del sesgo por rellenar con 0 (sección 5) — HECHO

`SesgoPorCero`, con `usePlotly` + `ChartFrame`. Doce encuestados, ocho contestaron cuántos
cigarrillos fuman: rellenar con 0 los cuatro huecos baja la media de 13,13 a 8,75, **un 33 %
menos**. Es el mismo ejemplo de la justificación 3 del cuestionario, y se eligió porque tiene
la trampa dentro: dos de los que sí contestaron respondieron 0, y ese 0 es un dato. Los
números los calcula el componente, así que el pie no puede desmentir a la gráfica.

Verificado: SVG presente, 320 px de alto, las dos barras con sus etiquetas, rango del eje
`[0, 13.82]` —la etiqueta de la barra alta no se recorta— y 301×320 a 375 px.

### T10 · Iconos de sección — HECHO, y solo uno

Se revisaron los diez contra el resto del curso, y solo uno estaba mal: `Workflow` para
«Referencia bibliográfica», que significa un flujo de proceso. La convención de la casa es
`Table` (6 de 9 módulos con bibliografía), pero aquí la tiene con razón la sección 8, que va
de DataFrames; y `BookOpen`, el otro precedente, está reservado a la primera sección en **los
13 módulos**. Queda `FileCode`, que es lo más cercano a un documento entre los libres.

Los otros nueve se dejaron como estaban. Cambiarlos habría sido churn: `ArrowDownUp` para
obligatorios/opcionales/nulos no es brillante, pero ningún icono libre lo mejora.

### ✅ Punto de control 3 — PASADO

- [x] Las 10 secciones montan, ninguna vacía, consola limpia
- [x] El diagrama y la gráfica pintan; sin desborde a 375 px en §5 ni en §7
- [x] Los 8 bloques Python corren y el noveno pasa `bash -n`
- [x] `escapes.py` da 0 y ningún espacio comido por JSX en las diez secciones
- [x] La receta es JSON válido, apunta a un `componentes` que existe, y sus diez iconos están definidos en la plantilla

---

## 6. Fase 4 — Que las correcciones sobrevivan

### T11 · Abrir el lenguaje del bloque — HECHO

Dos cambios, y no en la receta como decía este plan: **el conversor no la lee**, sólo recibe
un archivo y un `--salida`. El lenguaje es una propiedad del bloque, así que se declara donde
vive el bloque.

1. **`convertir_react.py`** deja de emitir `lang="python"` a fuego. Lee un campo opcional
   `codeLang` junto al `pythonCode` y usa Python por omisión, que cubre los otros 24 bloques
   de los tres módulos de esta familia. El heredado del 4 declara `codeLang: 'shell'` en su
   bibliografía.
2. **`montar.py` es la puerta.** Lee `const GRAMATICA = {…}` de la plantilla —la lista de
   verdad— y aborta si algún bloque declara una clave que no está. No se repitió la lista en
   el conversor a propósito: dos listas se separan, y entonces la comprobación empieza a
   rechazar bloques buenos.

**Criterios, los tres cumplidos:**

- [x] El heredado declara `shell` y sobrevive al remontaje
- [x] **Remontar el módulo 4 reproduce el publicado sin una sola diferencia.** Para llegar ahí hubo que montar de verdad: el archivo publicado tenía mi formato a mano —`<Box>` con el contenido en la línea siguiente— y el guion lo emite en la misma línea. El texto visible es idéntico carácter por carácter antes y después; lo que cambió fue formato y la colocación de las dos figuras
- [x] Una clave inventada aborta y **no escribe nada**. Probado con `bash` —el error exacto que cometí— y con una clave absurda

> **Corrección: las figuras van ANTES del bloque de código, no después.** Lo dije al revés en
> §5 y en el comentario de `componentes/modulo_4.jsx`. `seccion_jsx` añade el acompañante y
> *después* el `CodeBlock`. Lo enseñó el primer `diff` de este trabajo. Leído en la página
> funciona mejor así: el diagrama resume el camino y el código lo demuestra.

### 6.1 Lo que encontró la auditoría de T11

**Un agujero en mi propia comprobación, del mismo tipo que ya me había mordido.** La primera
versión del gate iba de `<CodeBlock` a `lang` con un patrón acotado por el acento grave.
Funciona en los módulos 3, 4 y 6, donde el conversor emite `title, lang, code`. Pero
`deduplicar.py` —el del módulo 13— emite `title, code, …, lang`, con el programa entero en
medio: el patrón se paraba en el acento y leía **cero** de sus 26 bloques. No fallaba: daba
por buenos 26 bloques sin mirar ninguno.

Se vio al pasar el gate por los 13 y ver un `0` donde tenía que haber un número. Ahora
`lenguajes_de` quita primero el literal y luego lee los atributos, y lee los 26. **La lección
es la de siempre en este trabajo: una comprobación que sólo se ha visto callar no está
comprobada.**

**Y un defecto vivo en otro módulo.** Barridos los 13 con el gate corregido, todos declaran
`lang` en todos sus bloques —cero omisiones— y sólo uno usa una clave que no existe:

| Módulo | Clave | Consecuencia |
|---|---|---|
| **2 · HTTP** | `lang="bash"` | El bloque se publica **sin resaltar**. La clave es `shell` |

Es el mismo error que el módulo 4 tenía en su bibliografía. El arreglo es una palabra en
`heredado/2_…html`, pero es otro módulo y otra decisión: **no se tocó**. Queda anotado en §8.
El gate ya lo cazará solo el día que alguien remonte el 2.

**Sin regresión en los hermanos.** Los módulos 3 y 6 comparten `convertir_react.py` y
`montar.py`: los dos se remontaron y reproducen su archivo publicado sin diferencias.

### T12 · Cierre

Actualizar `ESTADO_HALLAZGOS.md` y el apartado de estado del `README.md`; un commit por
fase, nunca dos módulos en el mismo.

- **Dependencias:** T11 · **Tamaño:** S

### ✅ Punto de control final

- [ ] Remontar el módulo 4 no cambia ni una línea del archivo publicado
- [ ] `python3 scripts/auditoria/verificar_codigo.py --ejecutar` pasa el módulo 4
- [ ] `python3 scripts/auditoria/hallazgos.py --abiertos` no deja nada nuevo abierto

---

## 7. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Un remontaje borra las correcciones | **Alto** | T11, y hasta que esté: no remontar el 4. B1 y B2 ya están en el heredado; B3 no puede estarlo |
| ~~El defecto de la barra invertida está en otros módulos~~ | — | **Descartado.** El detector se pasó al 3, al 6 y al 13: limpios (§0.2.1) |
| `ChartFrame` sin precedente en este curso | Medio | T9 va la última; si se atasca, se corta sin bloquear lo demás |
| `Box` dentro de rejillas (el tropiezo del módulo 3) | Bajo | Verificar en el DOM a 375 px, no leyendo el JSX |
| Divergencia publicado ↔ heredado | Medio | Cada tarea toca los dos, y el punto de control 1 lo comprueba |

---

## 8. Preguntas abiertas

1. ~~El comentario del hilo financiero.~~ **RESUELTO en `lp-base.html`** (2026-08-17). No se
   borró ni se hizo genérico a medias: se le abrió el alcance. En LPF el comentario era
   **correcto** —encabeza su `EJ_INTERES`, el crédito de libre inversión en cuatro
   lenguajes—, así que borrarlo habría empeorado aquel curso. Ahora dice qué va ahí
   —contenido, no librería—, que el hilo lo pone cada curso, y que en un capítulo montado
   desde material heredado la poda se lleva las constantes y el encabezado queda solo. Es
   verdad en los dos cursos y en los dos casos.

   **Propagado a los 13** (decisión del docente). Se remontaron los doce restantes y se
   comparó cada uno contra su versión anterior: **once cambiaron exactamente 14 líneas, todas
   del comentario**; el módulo 2 cambió 16 —esas 14 más las dos de su `lang`—. Hoy los 13
   traen el comentario nuevo y ninguno el viejo.

   El cambio vive en `lp-base.html`, en el repositorio de Lógica de Programación Financiera, y
   se deja **sin confirmar**, como todo lo de esta sesión. Los capítulos de aquel curso lo
   tomarán cuando se remonten.

2. ~~La bibliografía descansa en un solo artículo de Medium.~~ **AMPLIADA** (2026-08-17).
   La sección 10 pasa de tres enlaces genéricos —la raíz de Towards Data Science, la raíz de
   Kaggle— a una bibliografía con fuente primaria, tres lecturas atribuidas y una tarea:

   | | Fuente | Por qué esa |
   |---|---|---|
   | Primaria | Documentación de Pydantic, *Concepts* | La referencia de la que salen las demás |
   | Wong, K. J. (17 jul 2024) | *Validations in Pydantic V2* | Continúa las secciones 4 y 6, y trae el `model_validator` que D2 dejó fuera |
   | Huls, M. (6 feb 2026) | *Pydantic Performance: 4 Tips…* | Responde con números al aviso de la sección 8; su primer consejo es preferir `Annotated`, que es justo lo que añadió T3 |
   | Henderson, C. (14 ago 2024) | *How to Easily Validate Your Data with Pandera* | Nombra la herramienta que la sección 8 mencionaba sin nombrar |

   Las tres se abrieron y se comprobaron: existen, son de lectura libre y tratan lo que dicen
   tratar. **El artículo base también estaba bien**: `WebFetch` devolvía 403, pero abierto en
   el navegador carga entero y sin muro de pago —era bloqueo de robots, no un enlace muerto—.
   Se le añadió el autor, Shivam Dattatray Shinde, que faltaba.

3. ~~El módulo 2 tiene el mismo defecto que tenía el 4.~~ **ARREGLADO** (2026-08-17). Su
   heredado declaraba `language: "bash"` en el bloque «Flujo de Trabajo Profesional», y
   `convertir_datos.py` pasa ese campo tal cual: el bloque se publicaba sin resaltar. Se
   corrigió en la fuente (`bash` → `shell`) y no normalizando el alias en el conversor, que
   habría dejado la clave mala en el heredado y ciego al gate. Comprobado en la página: el
   bloque pasa de 0 a **20 tokens** de resaltado.

   Fue el gate quien lo encontró, y de la peor manera posible para el defecto: al ensayar el
   remontaje de los doce, once salieron y **el 2 abortó**. Es exactamente para lo que se
   escribió.

4. ~~El bloque sugiere «Busca en GitHub: pydantic-examples-data-science».~~ **QUITADO**
   (2026-08-17). No se verificó que existiera, y mandar a buscar algo que quizá no está es
   peor que no mandar. En su sitio va `pip install pandera`, que sí existe —comprobado en
   PyPI, versión 0.32.1— y que es la herramienta de la lectura de Henderson.
