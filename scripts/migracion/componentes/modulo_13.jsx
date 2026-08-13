/* ============================================================
   COMPONENTES PROPIOS DEL MÓDULO 13

   Uno solo, y es lo que queda después de deduplicar: el heredado traía su
   propio `Box`, su `Pipeline`, su `usePlotly` y su `ChartFrame` —los mismos
   que la plantilla, props incluidas— y un `CodeBlock` con un resaltador
   escrito a mano que Prism sustituye. Todo eso se va. El `QA` se queda porque
   LP-CORE no tiene nada equivalente.

   Se copia **literal**, como los del módulo 6: ya se dibujaba dentro de la
   columna de contenido. `navy` y `bg` son los mismos colores en las dos
   configuraciones de Tailwind, y además el heredado los repite en un `style`
   en línea, así que la tarjeta se ve igual aunque la clase faltara.

   El `Filename` del heredado **no se porta**: se declara —«versión ligera
   para algún caso suelto», dice su comentario— y no lo invoca nadie. Migrarlo
   sería publicar algo que nunca se publicó, igual que el laboratorio del
   módulo 3.
============================================================ */

/* Pregunta y respuesta de la autoevaluación, quince veces. La respuesta está
   a la vista: no es un cuestionario que califique —para eso está `Quiz`—,
   sino un solucionario que el texto pide leer DESPUÉS de intentarlo. Por eso
   no se convierte en `Accordion`: plegarla cambiaría el trato, y el material
   ya dice en voz alta cuándo conviene mirarla. */
const QA = ({ q, a }) => (
    <div className="border border-gray-200 rounded-xl bg-white px-5 py-4 mb-4 shadow-sm">
        <div className="font-semibold text-navy mb-2" style={{ color: '#001A4D' }}>{q}</div>
        <div className="bg-bg px-4 py-3 rounded-md border-l-4 text-[0.95rem]"
             style={{ background: '#F8FAFC', borderColor: '#FDB913' }}>
            {a}
        </div>
    </div>
);
