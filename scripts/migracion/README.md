# Migración del material a LP-CORE

Convierte un módulo heredado en un capítulo de LP-CORE, la librería de
componentes que este curso comparte con Lógica de Programación Financiera.

**El HTML migrado no se versiona.** Es salida derivada: se regenera con estos
guiones a partir del módulo original y de su receta, que sí están en el
repositorio. `.gitignore` cubre `_migrado_*.html` y `build/`.

Hay **dos bocas de entrada**, porque el material heredado no es homogéneo, y
una sola cadena de salida. Lo que cambia es de dónde se saca el contenido; el
contrato de piezas —`jsx/<id>.jsx` y `graficas.jsx`— y el montaje son los
mismos.

## Familias de módulos

| Familia | Módulos | Cómo se migra |
|---|---|---|
| `<section id>` + Plotly | 10, 11, 12 | `graficas.py` + `convertir.py` |
| **`courseData` + Chart.js** | **1, 2** | **`convertir_datos.py`** |
| ReactDOM con navegación propia | 3, 4, 6, 13 | pendiente: no es conversión, es re-alojar sus componentes |
| HTML plano, sin secciones ni gráficas | 5, 7, 8, 9 | pendiente: trocear por `<h2>` y pasar a camelCase 1 919 atributos con guion (`stroke-width`, `text-anchor`…) repartidos en 231 diagramas |

> Hasta agosto de 2026 esta tabla decía que los módulos 1 y 2 eran «HTML plano,
> pequeños» a los que sólo les faltaba trocear por `<h2>`. Era falso, y la
> herramienta que describía no habría servido: son aplicaciones de una sola
> página con todo el contenido en un objeto `courseData`, y sus gráficas son de
> Chart.js, no de Plotly. Los que necesitan el troceo por `<h2>` son el 5, el 7,
> el 8 y el 9.

## Cómo se migra un módulo

**Familia `<section id>`** (10, 11, 12):

```bash
N=11; F=$(ls ${N}_Python*.html)

python3 scripts/migracion/graficas.py  "$F" --salida build/migracion/m$N
python3 scripts/migracion/convertir.py "$F" --todas \
        --salida build/migracion/m$N/jsx --graficas build/migracion/m$N/graficas.json
python3 scripts/migracion/estilos.py   "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py    scripts/migracion/recetas/modulo_$N.json
```

**Familia `courseData`** (1 y 2). Un guion menos: las gráficas salen del mismo
objeto que el texto, así que no hay paso aparte.

```bash
N=1; F=$(ls ${N}_Python*.html)

python3 scripts/migracion/convertir_datos.py "$F" --salida build/migracion/m$N
python3 scripts/migracion/estilos.py         "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py          scripts/migracion/recetas/modulo_$N.json
python3 scripts/migracion/auditar.py $N
```

El orden importa: `estilos.py` mira el JSX ya convertido para saber qué clases
siguen vivas, y `montar.py` necesita las piezas.

| Guion | Qué hace |
|---|---|
| `graficas.py` | `Plotly.newPlot` de `plotly.io.to_html` → `usePlotly` + `ChartFrame`. Descarta el `template` por defecto y la altura, que la fija la clase del marco. |
| `convertir.py` | Una `<section>` → un componente de sección. `div.box` → `Box`, `<pre>` con resaltado a mano → `CodeBlock`, `box solution` → `Accordion`. |
| `convertir_datos.py` | El objeto `courseData` → secciones y gráficas. Ver abajo. |
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

## La receta

Un JSON por módulo en `recetas/`. Rutas relativas a la raíz del repositorio,
para que el resultado no dependa de desde dónde se invoque:

```jsonc
{
  "base":    "../../Usta 2026II/…/lp-base.html",  // la plantilla vive en el otro curso
  "piezas":  "build/migracion/m11",
  "salida":  "_migrado_11_lpcore.html",
  "config":  { /* lo que el App lee: titulo, ra, horas, asignatura, lema… */ },
  "secciones": [ { "id": "vms", "componente": "VmsSection",
                   "titulo": "3. Contenedores vs máquinas virtuales",
                   "icono": "Layers" } ]
}
```

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

## Sobre `auditar.py`

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
