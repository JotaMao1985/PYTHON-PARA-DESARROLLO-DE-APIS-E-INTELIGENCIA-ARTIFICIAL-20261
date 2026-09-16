/* ============================================================
   COMPONENTES PROPIOS DEL MÓDULO 6

   Dos, y los dos se copian del heredado **tal cual**. Es la excepción entre
   los componentes propios de esta familia, y por un motivo que conviene decir:
   el del módulo 3 vivía en un panel lateral de 384 px y hubo que rehacerle el
   marco; éstos dos ya se dibujaban dentro de la columna de contenido, que es
   exactamente donde LP-CORE los pone. No hay nada que adaptar.

   Lo que sí se comprobó antes de copiarlos:

   · `useState` está declarado en la plantilla (`const { useState, useEffect,
     useRef } = React;`), así que el `Tooltip` funciona sin traerse nada.
   · `.animate-fade-in` la define `lp-base.html`, con la misma animación.
   · `primary`, `secondary`, `navy` y `gold` son los mismos colores en las dos
     configuraciones de Tailwind, así que `bg-primary` y `text-secondary`
     siguen significando lo mismo.
   · `.prose-lp` sólo estiliza `p`, `h3`, `h4`, `ul`, `ol`, `li`, `strong` y
     las tablas. Aquí no hay ninguno de ésos, así que no hace falta `not-prose`.

   El tercer componente propio del heredado —`InteractiveQuiz`— **no está
   aquí**, y tampoco se perdió: sus ocho preguntas van al `Quiz` de LP-CORE,
   que hace lo mismo. Portarlo sería publicar un segundo cuestionario al lado
   del que la plantilla ya trae. Lo hace `convertir_react.py`; ver su función
   `cuestionario`.
============================================================ */

/* El cuadro emergente de los términos técnicos. El módulo lo usa cuatro veces,
   siempre para WSGI y ASGI, y siempre dentro de un título: el borde punteado
   es lo que avisa de que ahí hay algo que leer. Se abre también al enfocar con
   el teclado, no sólo al pasar el ratón. */
const Tooltip = ({ children, title, text, color = '#3D008D' }) => {
    const [show, setShow] = useState(false);
    return (
        <span className="relative inline-block"
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)}
            onFocus={() => setShow(true)}
            onBlur={() => setShow(false)}
            tabIndex="0"
        >
            <span className="cursor-help border-b-2 border-dashed font-bold" style={{ borderColor: color, color }}>{children}</span>
            {show && (
                <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-4 rounded-xl shadow-2xl border text-left animate-fade-in"
                    style={{ background: 'white', borderColor: color }}
                >
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }}></div>
                        <span className="font-bold text-sm" style={{ color }}>{title}</span>
                    </div>
                    <p className="text-xs text-gray-600 leading-relaxed">{text}</p>
                    <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0"
                        style={{ borderLeft: '8px solid transparent', borderRight: '8px solid transparent', borderTop: `8px solid ${color}` }}
                    ></div>
                </div>
            )}
        </span>
    );
};

/* Las dos líneas de tiempo de la sección de arquitectura: a la izquierda WSGI,
   donde el usuario B espera a que termine el A, y a la derecha ASGI, donde
   entra en el hueco que deja el `await`. No es un SVG: son cajas en flujo normal.

   Los dos paneles se rotulan «un worker, un hilo» y llevan un pie que lo dice,
   porque sin ese supuesto el izquierdo enseña «WSGI atiende de uno en uno», que
   es falso. Hasta 1fb1473 el panel derecho tenía altura fija con hijos en
   posición absoluta y la etiqueta de la espera se solapaba con la tarjeta de
   Usuario B —32 px ya a 1440 px de ventana—; siete de sus ocho etiquetas
   incumplían el contraste AA, la peor en 1,59. Ahora reflujan y pasan todas. */
const ComparisonDiagram = () => (
    <div className="grid md:grid-cols-2 gap-4">
        {/* WSGI */}
        <div className="bg-red-50/50 p-4 rounded-xl border border-red-100 min-w-0" role="img"
            aria-label="Línea de tiempo con un worker WSGI de un solo hilo: en el segundo 0 el usuario A ocupa el hilo; en el segundo 5 llega el usuario B y espera, porque el hilo sigue ocupado durante la espera de entrada y salida de A; en el segundo 10 A termina y libera el hilo; hasta el segundo 11 no empieza a atenderse a B.">
            <div className="text-center mb-4">
                <span className="font-bold text-red-800 text-sm uppercase tracking-wider block">Estilo WSGI — un worker, un hilo</span>
                <span className="text-xs text-red-800">El hilo queda ocupado durante toda la espera</span>
            </div>

            <div className="space-y-2 font-mono text-xs">
                {/* Time T1 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600">0s</span>
                    <div className="flex-1 min-w-0 h-10 bg-primary text-white rounded flex items-center justify-center shadow-sm">
                        Usuario A (Procesando...)
                    </div>
                </div>

                {/* Time T2 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600">5s</span>
                    <div className="flex-1 min-w-0 h-10 border-2 border-dashed border-red-400 bg-red-50 text-red-800 rounded flex items-center justify-center">
                        Usuario B (ESPERANDO 🛑)
                    </div>
                </div>

                {/* Time T3 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600">10s</span>
                    <div className="flex-1 min-w-0 h-10 bg-gray-200 text-gray-700 rounded flex items-center justify-center">
                        Usuario A termina
                    </div>
                </div>

                {/* Time T4 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600">11s</span>
                    <div className="flex-1 min-w-0 h-10 bg-[#C41461] text-white rounded flex items-center justify-center shadow-sm">
                        Usuario B (Por fin inicia!)
                    </div>
                </div>
            </div>
        </div>

        {/* ASGI */}
        <div className="bg-green-50/50 p-4 rounded-xl border border-green-100 min-w-0" role="img"
            aria-label="Línea de tiempo con un worker ASGI de un solo hilo: en el segundo 0 la petición de A ocupa la CPU; durante su espera de entrada y salida la CPU queda libre, y el servidor atiende al usuario B en ese hueco; en el segundo 10 A retoma la CPU y termina.">
            <div className="text-center mb-4">
                <span className="font-bold text-green-800 text-sm uppercase tracking-wider block">Estilo ASGI (FastAPI) — un worker, un hilo</span>
                <span className="text-xs text-green-800">El hilo se libera durante la espera de I/O</span>
            </div>

            {/* Tres filas en flujo normal, no cajas absolutas sobre una altura fija.
                La versión anterior clavaba los hijos con `absolute` dentro de un
                `h-[180px]`, y la etiqueta de la espera llevaba `whitespace-nowrap`:
                en cuanto el panel bajaba de ~420 px de ancho, la tarjeta de Usuario B
                le caía encima. Se solapaban 32 px ya a 1440 px de ventana. Así reflujan. */}
            <div className="font-mono text-xs space-y-2">
                {/* Usuario A ocupa la CPU */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600 flex-shrink-0">0s</span>
                    <div className="flex-1 min-w-0 h-8 bg-primary text-white rounded flex items-center justify-center text-[10px] shadow-sm">
                        A: Inicio (CPU)
                    </div>
                </div>

                {/* La espera de I/O: aquí es donde entra Usuario B */}
                <div className="flex items-start gap-2">
                    <span className="w-8 flex-shrink-0" aria-hidden="true"></span>
                    <div className="flex-1 min-w-0 border-l-2 border-dashed border-primary pl-3 py-2 flex flex-wrap items-center gap-2">
                        <span className="bg-white text-primary text-[10px] px-1.5 py-0.5 border border-primary/30 rounded">
                            ⏳ Esperando I/O (sin uso de CPU)
                        </span>
                        <span className="bg-[#C41461] text-white rounded-lg shadow-md px-3 py-1.5 text-center leading-tight border-2 border-white">
                            <span className="font-bold text-xs block">Usuario B</span>
                            <span className="text-[10px] block">¡Atendido en el hueco! 🚀</span>
                        </span>
                    </div>
                </div>

                {/* Usuario A retoma la CPU y termina */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-600 flex-shrink-0">10s</span>
                    <div className="flex-1 min-w-0 h-8 bg-primary text-white rounded flex items-center justify-center text-[10px] shadow-sm">
                        A: Fin (CPU)
                    </div>
                </div>
            </div>
        </div>

        {/* El supuesto tiene que ir escrito: sin él, el panel de la izquierda se lee
            como «WSGI atiende de uno en uno», que es falso y es el error que el
            cuestionario repetía en su justificación. */}
        <p className="md:col-span-2 text-xs text-gray-600 italic mt-1 mb-0">
            Los dos paneles suponen <strong>un worker con un solo hilo</strong>, para que la comparación
            sea justa. Con cuatro workers, WSGI atiende cuatro peticiones a la vez; lo que sigue sin hacer
            es aprovechar la espera de I/O de cada una, que es exactamente lo que ASGI sí hace.
        </p>
    </div>
);
