# Migración del material a LP-CORE

Convierte un módulo heredado —HTML estático con vocabulario propio— en un
capítulo de LP-CORE, la librería de componentes que este curso comparte con
Lógica de Programación Financiera.

**El HTML migrado no se versiona.** Es salida derivada: se regenera con estos
cuatro guiones a partir del módulo original y de su receta, que sí están en el
repositorio. `.gitignore` cubre `_migrado_*.html` y `build/`.

## Cómo se migra un módulo

```bash
N=11; F=$(ls ${N}_Python*.html)

python3 scripts/migracion/graficas.py  "$F" --salida build/migracion/m$N
python3 scripts/migracion/convertir.py "$F" --todas \
        --salida build/migracion/m$N/jsx --graficas build/migracion/m$N/graficas.json
python3 scripts/migracion/estilos.py   "$F" --piezas build/migracion/m$N
python3 scripts/migracion/montar.py    scripts/migracion/recetas/modulo_$N.json
```

El orden importa: `estilos.py` mira el JSX ya convertido para saber qué clases
siguen vivas, y `montar.py` necesita las tres piezas.

| Guion | Qué hace |
|---|---|
| `graficas.py` | `Plotly.newPlot` de `plotly.io.to_html` → `usePlotly` + `ChartFrame`. Descarta el `template` por defecto y la altura, que la fija la clase del marco. |
| `convertir.py` | Una `<section>` → un componente de sección. `div.box` → `Box`, `<pre>` con resaltado a mano → `CodeBlock`, `box solution` → `Accordion`. |
| `estilos.py` | Rescata del `<style>` original sólo las reglas de los diagramas propios que LP-CORE no cubre, con las variables resueltas. |
| `montar.py` | Arma el archivo sobre `lp-base.html`: `<head>`, `CONFIG`, CSS, gráficas, secciones y `curriculum`. Poda lo que quede de la demo de LPF. |

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

Los iconos salen del objeto `Icons` de LP-CORE; uno que no exista se dibuja como
un hueco en blanco y sin error de consola.

## Lo que no se automatiza, y por qué

`convertir.py` **se niega a adivinar** el lenguaje de un bloque cuando la
heurística no da una respuesta clara: lo etiqueta `text` y deja un
`/* TODO revisar lang */`. Resaltar con la gramática equivocada despista más
que no resaltar, y un aviso obliga a mirarlo.

Tampoco se toca el contenido. Los módulos 10 y 11 traen dos defectos
heredados que **se conservan a propósito**, porque arreglarlos sería editar el
material y no migrarlo:

- La etiqueta «End-to-End» de la gráfica de la pirámide se sale 21 px: el
  `margin.l` es 50 y la etiqueta mide 70. Se arregla con `automargin: true`.
- Las líneas de la ventana de logs del módulo 12 se juntan en un párrafo:
  `.log-window` no fija `white-space`. El original hace lo mismo.

## Familias de módulos

Sólo los módulos 10, 11 y 12 llevan `<section id="…">`, que es de lo que parte
`convertir.py`. Los demás necesitan trabajo de herramienta que aún no está:

| Familia | Módulos | Falta |
|---|---|---|
| Sección directa | 10, 11, 12 | nada — es lo que hay aquí |
| React con navegación propia | 3, 4, 6, 13 | no es conversión, es re-alojar sus componentes |
| HTML plano, pequeños | 1, 2 | trocear por `<h2>` |
| HTML plano con SVG | 5, 7, 8, 9 | trocear por `<h2>` + pasar a camelCase 1 919 atributos con guion (`stroke-width`, `text-anchor`…) repartidos en 231 diagramas |
