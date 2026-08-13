# Migración del material a LP-CORE

Convierte un módulo heredado en un capítulo de LP-CORE, la librería de
componentes que este curso comparte con Lógica de Programación Financiera.

**El capítulo montado sustituye al heredado y conserva su nombre.** El heredado
pasa a `heredado/`, con el mismo nombre, y a partir de ahí sólo lo leen estos
guiones.

```text
1_Python_para_APIS_IA.html            ← el capítulo LP-CORE: es lo que se publica
heredado/1_Python_para_APIS_IA.html   ← la fuente: sólo la leen los guiones
```

Así el capítulo montado **sí se versiona**, que es la única forma de que llegue
a los estudiantes: `.github/workflows/static.yml` publica el repositorio tal cual
desde `main`, e `index.html` y el syllabus enlazan por nombre. Al conservarlo, no
hubo que tocar ni un enlace.

El heredado se guarda —en vez de sobrescribirlo y confiar en el historial de
git— porque **LP-CORE está vivo**: vive en el repositorio de Lógica de
Programación Financiera, que sigue en desarrollo, y cada cambio de la librería
obliga a volver a montar estos capítulos. Sin la fuente a mano habría que
editarlos a mano, que es justo lo que la cadena evita.

Lo intermedio (`build/`) no se versiona: no lo lee nadie y se rehace en un
segundo.

Hay **dos bocas de entrada**, porque el material heredado no es homogéneo, y
una sola cadena de salida. Lo que cambia es de dónde se saca el contenido; el
contrato de piezas —`jsx/<id>.jsx` y `graficas.jsx`— y el montaje son los
mismos.

## Familias de módulos

| Familia | Módulos | Cómo se migra |
|---|---|---|
| `<section id>` + Plotly | 10, 11, 12 | `graficas.py` + `convertir.py` |
| `courseData` + Chart.js | 1, 2 | `convertir_datos.py` |
| Un `<article id>` por `<h2>`, con diagramas SVG | 5, 7, 8, 9 | `convertir_plano.py` |
| **React con `const curriculum = [...]` de datos** | **3**, 4, 6 | **`convertir_react.py`** |
| React con secciones ya en componentes | 13 | pendiente: no hay nada que convertir, hay que deduplicar |

> Esta tabla se ha equivocado dos veces, y las dos de la misma manera: dando por
> «HTML plano» un módulo que no lo era.
>
> Hasta agosto de 2026 decía que los módulos 1 y 2 eran «HTML plano, pequeños» a
> los que sólo les faltaba trocear por `<h2>`. Era falso: son aplicaciones de una
> sola página con todo el contenido en un objeto `courseData`, y sus gráficas son
> de Chart.js, no de Plotly.
>
> Y decía que el 5, el 7, el 8 y el 9 eran «HTML plano, **sin secciones**». Lo
> segundo también era falso, y en la dirección contraria: sí traen secciones
> —un `<article id="modulo-N">` por cada `<h2>` del temario, que la navegación
> propia enseña y esconde con `style.display`—, así que el troceo sale casi
> gratis. El trabajo estaba donde la tabla no miraba: en los 231 diagramas SVG.
>
> Y la última fila decía «ReactDOM con navegación propia: 3, 4, 6, 13», como si
> fueran una. No lo son: el 3, el 4 y el 6 guardan el contenido en un
> `const curriculum = [...]` **de datos**, y el 13 ya lo tiene repartido en
> componentes de sección. Al 13 no hay que convertirlo, hay que deduplicarlo:
> trae su propio `Box`, su `Pipeline`, su `usePlotly` y su `ChartFrame`, que es
> justo lo que LP-CORE ya pone.
>
> La lección, las tres veces, es la misma: **contar el material antes de escribir
> la herramienta.** Cuesta un `grep` y ahorra un guion entero.

## Cómo se migra un módulo

**Familia `<section id>`** (10, 11, 12):

```bash
N=11; F=heredado/$(ls heredado | grep "^${N}_Python")

python3 scripts/migracion/graficas.py  "$F" --salida build/migracion/m$N
python3 scripts/migracion/convertir.py "$F" --todas \
        --salida build/migracion/m$N/jsx --graficas build/migracion/m$N/graficas.json
python3 scripts/migracion/estilos.py   "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py    scripts/migracion/recetas/modulo_$N.json
```

**Familia `courseData`** (1 y 2). Un guion menos: las gráficas salen del mismo
objeto que el texto, así que no hay paso aparte.

```bash
N=1; F=heredado/$(ls heredado | grep "^${N}_Python")

python3 scripts/migracion/convertir_datos.py "$F" --salida build/migracion/m$N
python3 scripts/migracion/estilos.py         "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py          scripts/migracion/recetas/modulo_$N.json
python3 scripts/migracion/auditar.py $N
```

**Familia `<article id>`** (5, 7, 8 y 9). Tampoco hay paso de gráficas: estos
módulos no traen ninguna. Los diagramas son SVG escritos a mano y viajan dentro
del JSX.

```bash
N=7; F=heredado/$(ls heredado | grep "^${N}_Python")

PYTHONPATH=scripts/migracion \
python3 scripts/migracion/convertir_plano.py "$F" --salida build/migracion/m$N
python3 scripts/migracion/estilos.py         "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py          scripts/migracion/recetas/modulo_$N.json
```

`PYTHONPATH` hace falta porque el guion importa de `convertir.py` y de
`convertir_datos.py`, que están a su lado. Escribe además `titulos.json` con el
`<h2>` de cada artículo: es lo que hay que copiar —y numerar— en la receta.

**Familia `curriculum`** (3, 4 y 6). La misma forma, con `convertir_react.py`:

```bash
N=3; F=heredado/$(ls heredado | grep "^${N}_Python")

PYTHONPATH=scripts/migracion \
python3 scripts/migracion/convertir_react.py "$F" --salida build/migracion/m$N
python3 scripts/migracion/estilos.py         "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py          scripts/migracion/recetas/modulo_$N.json
```

El orden importa: `estilos.py` mira el JSX ya convertido para saber qué clases
siguen vivas, y `montar.py` necesita las piezas.

| Guion | Qué hace |
|---|---|
| `graficas.py` | `Plotly.newPlot` de `plotly.io.to_html` → `usePlotly` + `ChartFrame`. Descarta el `template` por defecto y la altura, que la fija la clase del marco. |
| `convertir.py` | Una `<section>` → un componente de sección. `div.box` → `Box`, `<pre>` con resaltado a mano → `CodeBlock`, `box solution` → `Accordion`. |
| `convertir_datos.py` | El objeto `courseData` → secciones y gráficas. Ver abajo. |
| `convertir_plano.py` | Un `<article id>` → un componente de sección. `.tip-box` → `Box`, `<details>` → `Accordion`, los radios de «Verificación de Comprensión» → `Quiz`, y los atributos de los SVG a camelCase. Ver abajo. |
| `convertir_react.py` | Una entrada del `curriculum` heredado → un componente de sección. El `content` se copia literal, porque ya es JSX; sólo `.tip-box` → `Box`. Ver abajo. |
| `estilos.py` | Rescata del `<style>` original sólo las reglas de los diagramas propios que LP-CORE no cubre, con las variables resueltas. |
| `montar.py` | Arma el archivo sobre `lp-base.html`: `<head>`, `CONFIG`, CSS, gráficas, secciones y `curriculum`. Poda lo que quede de la demo de LPF. |
| `auditar.py` | Comprueba que no se perdió contenido: cada palabra del origen, con su frecuencia, tiene que estar en el JSX. |

## La familia `courseData`

Los módulos 1 y 2 no son HTML estático: son una aplicación de una sola página.
El contenido vive en un objeto JavaScript con un `modules[]` y el armazón lo
pinta con plantillas literales. En el HTML no hay ni una `<section id>` de
contenido ni una caja `div.box`.

Sale **más barato**, no más caro: el contenido ya está estructurado, así que no
hay que analizar HTML. Cada `module` es una sección y las formas encajan casi
una a una:

| `courseData` | LP-CORE |
|---|---|
| `concept.text` | prosa; `<br><br>` pasa a corte de párrafo, el simple se queda (hace listas) |
| `concept.analogy` · `concept.warning` | `Box`, con el tipo que dice el emoji |
| `code` | `CodeBlock`, y `output` plegado en un `Accordion` «Ver salida» |
| `codeExplanation` | `Accordion`, un pliegue por paso |
| `quiz` · `quizzes[]` | `Quiz` |
| `comparison[]` | tabla — viene en dos formas, `{tool,use,detail}` y `{title,pros,cons,bestFor}` |
| `glossary` | `Accordion` con la tabla de términos |
| `bonus` | `Accordion`: es material de consulta fuera de sesión |
| `resources[]` | la lista de lecturas del cierre |
| `chartData` | `usePlotly` + `ChartFrame`; `bar` es `bar` y `radar` es `scatterpolar` cerrado sobre sí mismo |

Además hay contenido **fuera** de `courseData`: la apertura y el reparto del
tiempo son HTML estático marcado con `data-fase3`, delante del armazón. Salen
como una sección `portada`, con la apertura en un `Motivacion`. El módulo 2 no
trae apertura; sólo reparto.

### Por qué Node

`courseData` no es JSON y no hay forma honrada de fingir que lo es: trae
plantillas literales de varias líneas, comas finales y claves sin comillas. Lo
evalúa Node, que es quien conoce las reglas.

Contar llaves para encontrar dónde acaba el objeto **no funciona**: dentro hay
fragmentos de Python en plantillas literales, y esos traen llaves de diccionario
en la columna cero. En el módulo 2, el primer cierre plausible aparece 43 000
caracteres antes del verdadero. Así que se proponen los cierres candidatos y se
acepta el primero que Node consiga parsear como objeto con `modules`.

## La familia `<article id>`

El troceo es lo barato: cada `<h2>` del temario vive dentro de su
`<article id="modulo-N">`, así que la sección ya viene delimitada y el `<h2>`
da el título. Lo que hay que quitar de cada artículo es lo que LP-CORE ya
dibuja: la banda de título con su icono, y el «Anterior · 1 de 8 · Siguiente»
del pie, cuyos `href="#modulo-1"` además ya no llevan a ninguna parte.

Lo caro son los **231 diagramas**, con 1 822 atributos con guion. En una página
normal esto no se nota porque el analizador de HTML corrige los nombres al
entrar en contenido SVG; JSX no analiza HTML, así que ahí `stroke-width` es una
propiedad desconocida y el trazo no se dibuja. Lo mismo con `viewBox`, que el
módulo 7 escribe 27 veces en minúscula: en SVG el nombre distingue mayúsculas y
sin él el dibujo no escala. Se cambia **sólo el nombre del atributo, y sólo
dentro de un `<svg>`**: fuera, el guion es correcto —`data-language` se escribe
igual en JSX— y hay prosa que habla de `font-size` sin que eso sea un atributo.

Cuatro cosas de este material que costaron su rato:

- **Los cuestionarios hay que convertirlos, no copiarlos.** Los radios del
  heredado sólo funcionan con su guion de barajado, que es el que quita la
  clase `font-medium` de la opción correcta al cargar la página. Ese guion no
  se lleva —LP-CORE no tiene dónde ponerlo—, así que copiar el marcado tal cual
  dejaría **la respuesta correcta en negrita desde el principio**. Van a `Quiz`,
  que hace lo mismo y además califica. La insignia de dificultad («Nivel
  Medio») entra en el enunciado, porque `Quiz` no tiene campo para ella y es lo
  único que le dice al estudiante cuánto debería costarle.
- **Un `<pre>` con un `<svg>` dentro es un diagrama, no código.** El módulo 7
  mete tres diagramas grandes en la tarjeta oscura de los bloques de código,
  para reutilizar el estilo. Tratarlos como código los aplana: `texto_plano` se
  queda con los rótulos y tira el dibujo. Eran los tres avisos de «lang sin
  determinar» que soltaba el guion, y por eso ese aviso existe.
- **Las fórmulas cambian de delimitador.** El heredado carga KaTeX y escribe
  `$x$`; LP-CORE compone con MathJax, cuya configuración sólo reconoce `\(x\)`
  en línea. En bloque no hay problema: `$$…$$` lo entienden los dos. Sin
  traducir, las fórmulas no fallan —salen como texto con dólares, que es
  peor—. La pareja no puede cruzar una etiqueta ni pasar de 200 caracteres:
  es lo que impide que el `$` suelto de un precio (`"$1,500.00"`) se enganche
  con el siguiente de verdad y se trague el párrafo de en medio.
- **El `<` que no abre etiqueta.** Uno solo en los cuatro módulos, dentro de
  una fórmula (`$p < 0.05$`), y bastaba para que Babel no compilara la página
  entera. Se escapa cuando le sigue un espacio o una cifra, que es cuando no
  hay ambigüedad posible. Pegado a una letra no se toca: el analizador de HTML
  también lo leería como etiqueta, así que traducirlo sería cambiar el
  significado en vez de conservarlo.

## La familia `curriculum`

Es la más barata de las tres, y por un motivo que conviene decir claro: **el
JSX ya está escrito.** Los módulos 3, 4 y 6 son aplicaciones de React con Babel
en el navegador —el mismo montaje que LP-CORE— y su contenido vive en un
`const curriculum = [...]` cuya forma es casi la que LP-CORE espera:

```js
{ id, title, codeTitle, icon, content: (<div>…</div>), pythonCode: `…` }
```

De ahí sale una sección: el `content` **tal cual** más un `CodeBlock` con
`codeTitle` y `pythonCode`. Lo único que se traduce es `div.tip-box` → `Box`.

El `content` no pasa por `escapar_jsx` ni por `limpiar_jsx`, y eso es lo
importante: es JSX escrito a mano, con sus expresiones y sus comentarios
`{/* … */}`. Escaparle las llaves —que es lo correcto con el HTML de las otras
dos familias— lo rompería.

Para leer el `curriculum` se usa la **indentación**, no un analizador de
JavaScript: el `)` que cierra un `content` está siempre a dieciséis espacios.
Contar paréntesis obligaría a saber si el que se mira va dentro de una cadena,
y la prosa lleva comillas simples en castellano y en los ejemplos de código.

### Los componentes propios no los mueve el guion

Cada módulo de esta familia trae los suyos —el `AIClassBuilder` del 3, el
`Quiz` del 4, el `ComparisonDiagram` y el `Tooltip` del 6—. **Se portan a
mano**, a `componentes/modulo_N.jsx`, y la receta los nombra; `montar.py` los
estampa entre sus centinelas. No es pereza: adaptar un componente a un sitio
distinto del que se escribió es un juicio, no una transformación. El del
módulo 3 vivía en un panel lateral de 384 px con `h-full` y su propio scroll;
en LP-CORE la sección es una columna, así que `h-full` lo dejaría de altura
cero. Cambian el marco, `Icons.Sparkles` —que LP-CORE no tiene, y `renderIcon`
devuelve `null` en silencio para un nombre que no conoce— y el `lang` del
`CodeBlock`, que sin declarar cae en `pseudo`. La lógica, ni una línea.

### El laboratorio que no se migró, porque no se veía

El módulo 3 trae un «Laboratorio de Datos» entero —entrada de datos, media,
mediana, varianza poblacional y muestral, polimorfismo en vivo— gobernado por
seis valores de `interactiveType`. **No se ve nunca.** El panel derecho está
detrás de `interactiveType === 'ai_builder'` y dentro vuelve a preguntar lo
mismo, así que la rama del laboratorio es inalcanzable; de los seis valores,
cinco no pintan nada. Se comprobó en el DOM de la página publicada, sección por
sección, antes de decidir.

No se migra, porque migrarlo sería **publicar algo que nunca se publicó**: la
regla de esta cadena es conservar lo que el material hacía, no lo que su código
pretendía hacer. `convertir_react.py` lo dice en voz alta al terminar, para que
quien lea el heredado no crea que se quedó a medias. Si el laboratorio se
quiere de verdad, es una decisión pedagógica y va como componente propio, igual
que el `AIClassBuilder`.

## La receta

Un JSON por módulo en `recetas/`. Rutas relativas a la raíz del repositorio,
para que el resultado no dependa de desde dónde se invoque:

```jsonc
{
  "base":    "../../Usta 2026II/…/lp-base.html",  // la plantilla vive en el otro curso
  "piezas":  "build/migracion/m11",               // lo intermedio, no se versiona
  "salida":  "11_Python_para_APIS_IA_Contenedores_y_Docker.html",  // el nombre de siempre
  "componentes": "scripts/migracion/componentes/modulo_3.jsx",  // opcional: los propios
  "config":  { /* lo que el App lee: titulo, ra, horas, asignatura, lema… */ },
  "secciones": [ { "id": "vms", "componente": "VmsSection",
                   "titulo": "3. Contenedores vs máquinas virtuales",
                   "icono": "Layers" } ]
}
```

`componentes` sólo lo usa la familia `curriculum`, y es una ruta a un archivo
del repositorio, no de `build/`: lo que se escribe a mano tiene que versionarse.

`montar.py` comprueba dos cosas de la receta antes de montar, y las dos por el
mismo motivo: fallaban sin avisar.

- **Los iconos.** Salen del objeto `Icons`, que los declara en **dos** sitios:
  el literal `const Icons = {…}` y el `Object.assign(Icons, {…})` con que
  `lp-core-extra.jsx` lo amplía. Son diecisiete, no siete; mirar sólo el primero
  lleva a concluir que las recetas están llenas de nombres inventados, y no lo
  están. `renderIcon` devuelve `null` para un nombre que no conoce, así que un
  icono mal escrito dejaba la sección sin icono y sin error de consola.
- **El nombre del componente.** Si coincide con algo que la plantilla ya
  declara, sale declarado dos veces y Babel no compila la página. Y no basta
  con confiar en la poda: precisamente porque la receta lo nombra, `podar` lo
  da por vivo y no lo retira. Pasó con `PortadaSection`, que es una de las
  secciones de muestra de LPF.

La poda tenía además un defecto silencioso, corregido en agosto de 2026: cada
declaración muerta llegaba «hasta donde empieza la siguiente», y eso incluía el
comentario que abre el bloque generado. La última constante de la plantilla se
llevaba por delante el `=== GRÁFICAS INICIO ===` —los módulos 1, 2, 10, 11 y 12
estaban publicados sin él— y, en los módulos sin gráficas, el
`=== SECCIONES INICIO ===`. No rompía nada porque `montar.py` siempre parte de
`lp-base.html`, pero dejaba el archivo con un centinela de cierre y ninguno de
apertura. Ahora los centinelas cortan también.

## Lo que no se automatiza, y por qué

`convertir.py` **se niega a adivinar** el lenguaje de un bloque cuando la
heurística no da una respuesta clara: lo etiqueta `text` y deja un
`/* TODO revisar lang */`. Resaltar con la gramática equivocada despista más
que no resaltar, y un aviso obliga a mirarlo. `convertir_datos.py` usa la misma
heurística, pero sólo cuando hace falta: el módulo 2 declara el lenguaje de sus
seis bloques y el módulo 1 no declara ninguno.

Tampoco se toca el contenido. Los defectos heredados **se conservan a
propósito**, porque arreglarlos sería editar el material y no migrarlo:

- La etiqueta «End-to-End» de la gráfica de la pirámide del módulo 10 se sale
  21 px: el `margin.l` es 50 y la etiqueta mide 70. (Las gráficas de los
  módulos 1 y 2 sí llevan `automargin`, porque se generan de cero y no hay nada
  que conservar.)
- Las líneas de la ventana de logs del módulo 12 se juntan en un párrafo:
  `.log-window` no fija `white-space`. El original hace lo mismo.
- El módulo 1 trae un `U+FFFD` literal —el carácter de reemplazo— donde el
  checklist de la síntesis debería llevar su emoji. Se ve igual en el original
  publicado. El guion avisa y no lo toca.

### Las dos excepciones, y por qué lo son

Dos cosas sí cambian, y en ambos casos porque **la traducción les quita el
sentido que tenían**:

- **La felicitación de las justificaciones.** En el heredado, `feedback` sólo se
  veía al acertar —fallar daba un «❌ Incorrecto» genérico y dejaba reintentar—.
  El `Quiz` de LP-CORE la enseña a todo el mundo al enviar, así que «✅
  Correcto» le estaría diciendo a quien acaba de fallar que acertó. Se recorta
  la felicitación y se queda la explicación, que es lo que se quería guardar.
- **El emoji de cabecera de `analogy` y `warning`.** Es lo único que distingue
  un aviso de un consejo, porque la etiqueta cambia de una sección a otra
  («Error Común», «Consideración», «Seguridad», «Tip Moderno»). Así que elige
  el tipo de `Box` y se descarta **sólo cuando hay etiqueta**, que es cuando
  `Box` dibuja su propio icono; si no la hay, se conserva, porque es la única
  señal visual que le queda a la caja.

`auditar.py` conoce estas dos excepciones y no las cuenta como pérdida. Todo lo
demás que falte lo señala.

En la familia `<article id>` hay una tercera, y por el mismo motivo —la
traducción le quita el sentido que tenía—: **el cuestionario**. Ver arriba: sus
radios sólo se sostenían sobre un guion que no se lleva, y sin él la respuesta
correcta se veía en negrita antes de contestar.

Y una cuarta en el módulo 3, otra vez por lo mismo: **«el panel derecho»**. El
texto manda al estudiante tres veces a un panel lateral que en LP-CORE no
existe, porque la sección es una columna. Pasa a decir «el constructor de
abajo», que es donde está ahora. Es la frase entera lo que cambia de referente,
no el sentido de lo que enseña.

El cambio de delimitador de las fórmulas y el escape del `<` suelto no son
excepciones: son del mismo orden que `class` → `className`. El problema es del
destino, no del origen.

## Sobre `auditar.py`

**Sólo cubre la familia `courseData`**, que es la que tiene el origen ya
estructurado en `datos.json`. Para la familia `<article id>` la comprobación de
agosto de 2026 se hizo aparte, contando el texto del artículo de origen —con
los `<pre>` apartados, porque dentro hay `<` de código— contra el JSX crudo. Lo
que faltaba era, palabra por palabra, lo que la migración quita a propósito: el
«Copiar» de la barra, el «Anterior / Siguiente» del pie, las letras `A) B) C)`
que el heredado también borra al cargar, el «Ver Respuesta y Retroalimentación»
que absorbe el `Quiz`, y los `<h2>` que ahora pinta el App.

Compara el `courseData` extraído con el JSX emitido: cada palabra del origen
tiene que aparecer, con su frecuencia, en la sección o en las gráficas. Cazó
que la salida de un bloque se estaba inyectando como JSX —una del módulo 2 dice
`🐍 Original: <class 'datetime.datetime'>`, y ese `<class …>` Babel lo abre como
etiqueta—, con lo que el módulo 2 no habría compilado.

**No intenta interpretar el JSX**, y ahí está la gracia. Tres versiones
anteriores del guion daban falsos positivos por lo mismo: quitar «etiquetas»
con una expresión regular destroza el código —`if p_value < alpha:` abre una
que nunca cierra— y destroza el propio JSX, donde `<Accordion items={[…(<>`
tiene su primer `>` a cincuenta caracteres del principio. Se compara texto
crudo contra texto crudo, deshaciendo sólo los escapes que aplica el guion.

Dos trampas más que costaron su rato, por si alguien toca el guion:

- Filtrar los emojis por `unicodedata.category(c).startswith("S")` se lleva por
  delante `<` y `>`, que son `Sm`, y pega las etiquetas a las palabras. Hay que
  filtrar sólo la categoría `So`.
- La comilla invertida tiene que separar: sin ella, la primera palabra de cada
  ``code={`…`` se queda pegada al acento y no casa con la del origen.
