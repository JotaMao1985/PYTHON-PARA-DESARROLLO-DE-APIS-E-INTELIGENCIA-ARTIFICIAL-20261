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
   entra en el hueco que deja el `await`. No es un SVG: son cajas colocadas a
   mano, y por eso el panel derecho tiene altura fija —sus hijos van en
   posición absoluta y sin ella se solaparían—. */
const ComparisonDiagram = () => (
    <div className="grid md:grid-cols-2 gap-4">
        {/* WSGI */}
        <div className="bg-red-50/50 p-4 rounded-xl border border-red-100">
            <div className="text-center mb-4">
                <span className="font-bold text-red-800 text-sm uppercase tracking-wider block">Estilo WSGI</span>
                <span className="text-xs text-red-600">Bloqueante (Un camión en un carril)</span>
            </div>

            <div className="space-y-2 font-mono text-xs">
                {/* Time T1 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-400">0s</span>
                    <div className="flex-1 h-10 bg-primary text-white rounded flex items-center justify-center shadow-sm">
                        Usuario A (Procesando...)
                    </div>
                </div>

                {/* Time T2 */}
                <div className="flex items-center gap-2 opacity-50">
                    <span className="w-8 text-gray-400">5s</span>
                    <div className="flex-1 h-10 border-2 border-dashed border-red-300 bg-red-50 text-red-400 rounded flex items-center justify-center">
                        Usuario B (ESPERANDO 🛑)
                    </div>
                </div>

                {/* Time T3 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-400">10s</span>
                    <div className="flex-1 h-10 bg-gray-200 text-gray-500 rounded flex items-center justify-center">
                        Usuario A termina
                    </div>
                </div>

                {/* Time T4 */}
                <div className="flex items-center gap-2">
                    <span className="w-8 text-gray-400">11s</span>
                    <div className="flex-1 h-10 bg-secondary text-white rounded flex items-center justify-center shadow-sm">
                        Usuario B (Por fin inicia!)
                    </div>
                </div>
            </div>
        </div>

        {/* ASGI */}
        <div className="bg-green-50/50 p-4 rounded-xl border border-green-100">
            <div className="text-center mb-4">
                <span className="font-bold text-green-800 text-sm uppercase tracking-wider block">Estilo ASGI (FastAPI)</span>
                <span className="text-xs text-green-600">Asíncrono (Autopista con sobrepaso)</span>
            </div>

            <div className="relative font-mono text-xs h-[180px]">
                {/* Background grid lines */}
                <div className="absolute inset-0 flex flex-col justify-between opacity-10 pointer-events-none">
                    <div className="border-b border-black h-8"></div>
                    <div className="border-b border-black h-8"></div>
                    <div className="border-b border-black h-8"></div>
                    <div className="border-b border-black h-8"></div>
                </div>

                {/* User A Task - Start */}
                <div className="absolute top-0 left-8 w-24 h-8 bg-primary text-white rounded flex items-center justify-center text-[10px] z-10 shadow-sm">
                    A: Inicio (CPU)
                </div>

                {/* Await Period */}
                <div className="absolute top-8 left-20 bottom-8 border-l-2 border-primary border-dashed w-0 flex items-center">
                    <span className="bg-white/90 text-primary text-[10px] px-1 ml-2 whitespace-nowrap border border-primary/20 rounded">
                        ⏳ Esperando I/O (Sin uso CPU)
                    </span>
                </div>

                {/* User A Task - End */}
                <div className="absolute bottom-0 left-8 w-24 h-8 bg-primary text-white rounded flex items-center justify-center text-[10px] z-10 shadow-sm">
                    A: Fin (CPU)
                </div>

                {/* User B Task (Fits in the middle) */}
                {/* User B Task (Runs in the gap) */}
                <div className="absolute top-1/2 -translate-y-1/2 right-8 w-32 h-12 bg-secondary text-white rounded-lg shadow-md flex items-center justify-center z-20 border-2 border-white animate-pulse" title="¡Usuario B es atendido mientras A espera!">
                    <div className="text-center">
                        <div className="font-bold text-xs">Usuario B</div>
                        <div className="text-[9px]">¡Atendido en el hueco! 🚀</div>
                    </div>
                </div>

                {/* Time markers */}
                <div className="absolute left-0 top-0 text-gray-400 text-[10px]">0s</div>
                <div className="absolute left-0 bottom-0 text-gray-400 text-[10px]">10s</div>
            </div>
        </div>
    </div>
);
