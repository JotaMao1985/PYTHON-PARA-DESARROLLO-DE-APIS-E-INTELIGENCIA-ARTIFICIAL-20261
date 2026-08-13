#!/usr/bin/env python3
"""Deduplica un módulo heredado que ya viene escrito en componentes.

El módulo 13 es el único de su familia y **no hay nada que convertir**: su
contenido no vive en datos —ni en un `courseData`, ni en un `curriculum` con
el JSX dentro— sino en siete componentes de sección, `IntroSection`,
`CicloVidaSection`… , que el `curriculum` sólo nombra:

    { id: 'ciclo', title: '2. Ciclo de vida del modelo', icon: 'Activity',
      component: CicloVidaSection }

Lo que hay que hacer con él es **quitarle lo que LP-CORE ya pone**. El
heredado trae su propio `Box`, su `Pipeline`, su `usePlotly` y su
`ChartFrame`, y son los mismos —mismas props, mismos tipos, mismo marcado—,
así que las secciones siguen funcionando con los de la plantilla sin tocar ni
una línea. También trae su propio `CodeBlock`, con un resaltador escrito a
mano de cien líneas que se cambia por el de LP-CORE, que usa Prism y conoce
las cinco gramáticas que este módulo necesita.

Tres cosas sí se mueven de sitio, y ninguna es cosmética:

- **Los `usePlotly` salen de la sección.** `montar.py` emite cada sección como
  una flecha de cuerpo-expresión —`const X = () => (<div …>…</div>)`—, y ahí
  no cabe un hook. Cada `usePlotly` se va con su `<ChartFrame>` a un
  componente de gráfica en `graficas.jsx`, que es donde los módulos 10, 11 y
  12 ya los tienen, y la sección se queda con `<GraficaXxx caption="…" />`.
- **Las constantes de código se pegan en su `CodeBlock`.** El heredado las
  declara al lado de la sección que las usa —veintisiete, cada una en un solo
  sitio— y fuera del componente no hay dónde ponerlas. Se copian literales
  dentro de `code={` … `}`, que es como las emiten las otras tres bocas.
- **`chart-h-340` y `chart-h-380` no existen en LP-CORE.** No se traducen: son
  reglas del `<style>` heredado y las rescata `estilos.py`, igual que
  `.usta-card`. Traducirlas a la altura más cercana cambiaría el dibujo.

Lo que **no** se mueve es el `QA` de la autoevaluación —quince preguntas con
su respuesta a la vista—, que LP-CORE no tiene: se porta a mano, como todo
componente propio. El `Filename` del heredado no se porta porque no se usa: se
declara y no lo invoca nadie.

Uso:
    python3 scripts/migracion/deduplicar.py <archivo.html> --salida dir/
"""

import argparse
import json
import re
import sys
from pathlib import Path

# El nombre del componente de gráfica sale del `id` del `<ChartFrame>`, que es
# el mismo que el del `usePlotly`: `chart-docker-comp` → `GraficaDockerComp`.
# Así el nombre no se inventa y las dos piezas se siguen la pista.
PREFIJO_GRAFICA = "Grafica"


def literales(cuerpo):
    """Las constantes de código de primer nivel: `const nombre = \\`…\\`;`.

    Se busca el cierre saltando las comillas invertidas escapadas, que es lo
    mismo que hace `convertir_react.py` con el `pythonCode`: contar comillas
    sin mirar el escape corta el literal por la mitad en cuanto uno de estos
    bloques enseña una plantilla de JavaScript, y aquí hay dos que lo hacen.
    """
    salida = {}
    for m in re.finditer(r"^        const (\w+) = `", cuerpo, re.M):
        j = m.end()
        while j < len(cuerpo):
            j = cuerpo.find("`", j)
            if j == -1 or cuerpo[j - 1] != "\\":
                break
            j += 1
        if j != -1:
            salida[m.group(1)] = cuerpo[m.end():j]
    return salida


def entradas(cuerpo, avisos):
    """El `curriculum`: id, título, icono y nombre del componente de sección."""
    m = re.search(r"const curriculum = \[(.*?)\n        \];", cuerpo, re.S)
    if not m:
        return []
    lista = []
    for fila in re.finditer(r"\{\s*id:\s*'([^']+)'\s*,\s*title:\s*'((?:[^'\\]|\\.)*)'\s*,"
                            r"\s*icon:\s*'(\w+)'\s*,\s*component:\s*(\w+)\s*,?\s*\}",
                            m.group(1)):
        lista.append({"id": fila.group(1), "titulo": fila.group(2).replace("\\'", "'"),
                      "icono": fila.group(3), "componente": fila.group(4)})
    if not lista:
        avisos.append("el `curriculum` no dio ninguna entrada legible")
    return lista


def fuente_componente(cuerpo, nombre, avisos):
    """El código del componente `nombre`, de su `const` a su línea de cierre.

    Se corta por la indentación, no contando llaves: el cuerpo lleva dentro
    fragmentos de Python, de Dockerfile y de HTML en plantillas literales, y
    ahí las llaves y los paréntesis no son del programa que se está leyendo.
    Un componente de primer nivel cierra con `);` o `};` a ocho espacios.
    """
    m = re.search(r"^        const " + nombre + r" = \(\) => (\(|\{)$", cuerpo, re.M)
    if not m:
        avisos.append(f"el `curriculum` nombra «{nombre}» y no hay ningún "
                      f"`const {nombre} = () =>` que empiece una línea")
        return None, None
    cierre = r"^        \);$" if m.group(1) == "(" else r"^        \};$"
    f = re.compile(cierre, re.M).search(cuerpo, m.end())
    if not f:
        avisos.append(f"«{nombre}» no cierra donde se esperaba")
        return None, None
    return cuerpo[m.start():f.start()], m.group(1)


def partir(fuente, abre):
    """(jsx, hooks) de un componente de sección.

    Los dos cuerpos que usa el heredado: la flecha que devuelve el JSX
    directamente y la que abre bloque para llamar antes a `usePlotly`.
    """
    if abre == "(":
        return fuente.split("\n", 1)[1].rstrip(), ""
    cabeza, sep, resto = fuente.partition("\n            return (\n")
    if not sep:
        return fuente.split("\n", 1)[1].rstrip(), ""
    return resto.rstrip(), cabeza.split("\n", 1)[1].strip("\n")


def pegar_literales(jsx, textos, avisos):
    """`code={trainPyCode}` → `code={`…`}`, con el literal copiado tal cual.

    Vale para el `{projectTreeContent}` suelto del árbol de directorios, que
    no va en un `CodeBlock` sino dentro de un `<div>` con `whitespace-pre`:
    la forma que se sustituye es la llave, no el atributo.
    """
    def una(m):
        nombre = m.group(1)
        if nombre not in textos:
            return m.group(0)
        return "{`" + textos[nombre] + "`}"
    jsx, n = re.subn(r"\{(\w+)\}", una, jsx)
    pendientes = [c for c in re.findall(r"\{(\w+)\}", jsx) if c in textos]
    if pendientes:
        avisos.append(f"quedaron constantes sin pegar: {', '.join(pendientes)}")
    return jsx, n


def nombre_grafica(chart_id):
    """`chart-docker-comp` → `GraficaDockerComp`."""
    partes = [p for p in re.split(r"[-_]", chart_id) if p and p != "chart"]
    return PREFIJO_GRAFICA + "".join(p.capitalize() for p in partes)


def sacar_graficas(jsx, hooks, avisos):
    """Cada `usePlotly` con su `<ChartFrame>` → un componente de gráfica.

    El hook y el marco tienen que viajar juntos: el hook pinta sobre el `id`
    que el marco crea en el DOM, y si el marco se queda en la sección y el
    hook se va, Plotly pinta sobre un elemento que aún no existe.
    """
    componentes = []
    arranques = [m.start() for m in re.finditer(r"\busePlotly\(", hooks)]
    for i, ini in enumerate(arranques):
        fin = arranques[i + 1] if i + 1 < len(arranques) else len(hooks)
        llamada = hooks[ini:fin].rstrip()
        chart_id = re.match(r"usePlotly\(\s*'([\w-]+)'", llamada)
        if not chart_id:
            avisos.append("un `usePlotly` no declara el id de su gráfica como "
                          "cadena literal; se queda en la sección y no pintará")
            continue
        chart_id = chart_id.group(1)

        marco = re.search(r"<ChartFrame\s[^>]*?\bid=\"" + re.escape(chart_id)
                          + r"\"[^>]*?/>", jsx, re.S)
        if not marco:
            avisos.append(f"«{chart_id}» tiene `usePlotly` y ningún `<ChartFrame>` "
                          f"que lo pinte")
            continue
        atributos = marco.group(0)
        alto = re.search(r'height="([^"]+)"', atributos)
        pie = re.search(r'caption="((?:[^"\\]|\\.)*)"', atributos, re.S)

        nombre = nombre_grafica(chart_id)
        componentes.append(
            f"const {nombre} = ({{ caption }}) => {{\n"
            + re.sub(r"^", "    ", llamada, flags=re.M) + "\n"
            + f'    return <ChartFrame id="{chart_id}"'
            + (f' height="{alto.group(1)}"' if alto else "")
            + " caption={caption} />;\n};")
        jsx = (jsx[:marco.start()] + f"<{nombre}"
               + (f' caption="{pie.group(1)}"' if pie else "")
               + " />" + jsx[marco.end():])
    return jsx, componentes


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path)
    p.add_argument("--salida", type=Path, help="carpeta donde escribir las piezas")
    args = p.parse_args()

    if not args.archivo.exists():
        print(f"ERROR: no existe {args.archivo}", file=sys.stderr)
        return 1

    texto = args.archivo.read_text(encoding="utf-8")
    m = re.search(r'<script type="text/babel">(.*?)</script>', texto, re.S)
    if not m or "component:" not in m.group(1):
        print("ERROR: el archivo no tiene un `curriculum` con `component:` dentro de\n"
              "       un <script type=\"text/babel\">. Este guion es para el módulo 13,\n"
              "       que ya viene en componentes. Para los que guardan el JSX en el\n"
              "       propio `curriculum` use convertir_react.py.", file=sys.stderr)
        return 1

    cuerpo = m.group(1)
    globales = []
    lista = entradas(cuerpo, globales)
    textos = literales(cuerpo)
    if args.salida:
        (args.salida / "jsx").mkdir(parents=True, exist_ok=True)

    titulos, graficas, total = {}, [], 0
    for e in lista:
        avisos = []
        fuente, abre = fuente_componente(cuerpo, e["componente"], avisos)
        if fuente is None:
            globales.extend(avisos)
            continue
        jsx, hooks = partir(fuente, abre)
        jsx, pegados = pegar_literales(jsx, textos, avisos)
        jsx, propias = sacar_graficas(jsx, hooks, avisos)
        graficas.extend(propias)
        titulos[e["id"]] = e["titulo"]

        if args.salida:
            (args.salida / "jsx" / f"{e['id']}.jsx").write_text(jsx + "\n", encoding="utf-8")
        else:
            print(jsx)
        print(f"{'OK  ' if not avisos else 'AVISO'} {e['id']:12s} "
              f"{len(jsx.splitlines()):4d} líneas · {jsx.count('<CodeBlock'):2d} CodeBlock · "
              f"{jsx.count('<Box'):2d} Box · {len(propias)} gráficas · "
              f"{pegados} constantes pegadas", file=sys.stderr)
        for a in avisos:
            print(f"        · {a}", file=sys.stderr)
        total += len(avisos)

    if args.salida:
        (args.salida / "titulos.json").write_text(
            json.dumps(titulos, ensure_ascii=False, indent=1), encoding="utf-8")
        (args.salida / "graficas.jsx").write_text("\n\n".join(graficas) + "\n",
                                                  encoding="utf-8")

    # Lo que las secciones invocan y este guion no declara. En esta familia es
    # LA comprobación: todo lo que no ponga LP-CORE hay que portarlo a mano, y
    # un componente que no existe deja la página en blanco sin decir por qué.
    usados = sorted({c for f in (args.salida / "jsx").glob("*.jsx")
                     for c in re.findall(r"<([A-Z]\w+)", f.read_text(encoding="utf-8"))}
                    ) if args.salida else []
    if usados:
        print(f"\nCOMPRUEBE que la plantilla o la receta declaran: {', '.join(usados)}",
              file=sys.stderr)

    for a in globales:
        print(f"        · {a}", file=sys.stderr)
    print(f"\n{len(lista)} secciones · {len(graficas)} gráficas · "
          f"{total + len(globales)} avisos por revisar", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
