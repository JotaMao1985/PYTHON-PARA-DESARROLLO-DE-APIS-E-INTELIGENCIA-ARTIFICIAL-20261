/* ============================================================
   COMPONENTES PROPIOS DEL MÓDULO 4

   Dos figuras. No salen de ningún conversor porque en el heredado no hay nada
   que convertir: el módulo 4 llegó **sin una sola imagen**. Ni diagrama, ni
   gráfica, ni esquema; lo único visual eran los iconos de sección y unas
   tarjetas de colores.

   Viven aquí, y no en `build/migracion/m4/graficas.jsx`, porque `build/` no se
   versiona: lo rehace `graficas.py` a partir del Plotly del heredado, y el
   heredado del 4 no tiene ninguno. Lo que se escribe a mano va en
   `componentes/`, que sí se versiona, y lo nombra la receta.

   Las dos se enganchan por `interactiveType` en el heredado —`flujo_422` en la
   sección 7 y `sesgo_cero` en la 5—, que `ACOMPANANTES` traduce a la etiqueta
   correspondiente. El mecanismo las coloca **antes del bloque de código**
   —`seccion_jsx` añade el acompañante y después el `CodeBlock`—, y en las dos
   es donde deben ir: la figura resume lo que el texto acaba de explicar y el
   código lo demuestra a continuación.
============================================================ */

/* La sección 7 explica con palabras el camino que recorre un dato malo desde
   que entra hasta que el cliente lee el error. Esto es ese camino. Los cuatro
   rótulos son los mismos términos que usa el texto, en el mismo orden, para
   que el dibujo y la prosa no se contradigan. */
const FlujoValidacion422 = () => (
    <Pipeline steps={[
        {
            num: 1,
            title: 'Llega el JSON',
            desc: 'El cuerpo de la petición entra tal cual. Si estuviera roto, ni habría llegado aquí: eso sería un 400.'
        },
        {
            num: 2,
            title: 'El modelo comprueba',
            desc: 'Pydantic contrasta cada campo contra el contrato: tipos, rangos, patrones y tus validadores.'
        },
        {
            num: 3,
            title: 'ValidationError',
            desc: 'Si algo no cuadra, .errors() reúne TODOS los fallos, no se para en el primero.'
        },
        {
            num: 4,
            title: 'Respuesta 422',
            desc: 'FastAPI vuelca esa lista en {"detail": [...]} y es lo que lee quien consume tu API.'
        },
    ]} />
);

/* El lema del capítulo —«Poner 0 donde faltaba el dato no rellena el hueco:
   mueve la media»— no se demostraba en ninguna parte. Aquí se demuestra, y con
   el mismo ejemplo que ya usa la justificación 3 del cuestionario: los
   cigarrillos que dice fumar un encuestado.

   El ejemplo se eligió porque tiene la trampa dentro: dos de los que SÍ
   contestaron respondieron 0, y ese 0 es un dato —no fuman—. Confundirlo con
   el hueco de los que no contestaron es exactamente el error que la sección
   enseña a evitar. */
const SesgoPorCero = () => {
    const observados = [20, 0, 15, 0, 30, 10, 25, 5];   // los que contestaron
    const sinRespuesta = 4;                              // los que no

    const suma = observados.reduce((a, b) => a + b, 0);
    const mediaReal = suma / observados.length;
    const mediaConCeros = suma / (observados.length + sinRespuesta);
    const caida = Math.round((1 - mediaConCeros / mediaReal) * 100);

    usePlotly('chart-m4-sesgo',
        () => [
            {
                type: "bar",
                x: ["Solo los que contestaron", "Rellenando con 0 los que no"],
                y: [mediaReal, mediaConCeros],
                text: [mediaReal.toFixed(2), mediaConCeros.toFixed(2)],
                textposition: "outside",
                cliponaxis: false,
                marker: {
                    color: ["#3D008D", "#ED1E79"],
                    line: { color: "#3D008D", width: 1 }
                },
                hovertemplate: "<b>%{x}</b><br>media = %{y:.2f} cigarrillos/día<extra></extra>"
            }
        ],
        () => ({
            xaxis: {
                automargin: true
            },
            yaxis: {
                title: { text: "Cigarrillos al día (media)" },
                rangemode: "tozero",
                automargin: true
            },
            showlegend: false,
            font: {
                family: "Montserrat, Helvetica Neue, Arial, sans-serif",
                size: 12,
                color: "#1E293B"
            },
            margin: { l: 60, r: 40, t: 30, b: 50 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)"
        }), []);

    return (
        <ChartFrame
            id="chart-m4-sesgo"
            height="chart-h-320"
            caption={`Doce encuestados, ocho contestaron. Rellenar con 0 los cuatro huecos baja la media de ${mediaReal.toFixed(2)} a ${mediaConCeros.toFixed(2)} cigarrillos al día: un ${caida} % menos, y sin que falte un solo dato en la tabla.`} />
    );
};
