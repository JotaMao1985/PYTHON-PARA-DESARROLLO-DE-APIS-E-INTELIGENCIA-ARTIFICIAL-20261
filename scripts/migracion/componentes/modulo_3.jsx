/* ============================================================
   CONSTRUCTOR IA DE CLASES — componente propio del módulo 3

   Se copia del heredado casi literal. Lo que cambia, y por qué:

   · **El marco.** En el heredado vivía en un panel lateral fijo de 384 px
     (`flex flex-col h-full` dentro de un `w-96`), y en LP-CORE la sección es
     una columna: `h-full` lo dejaría de altura cero y `flex-1 overflow-y-auto`
     le pondría un scroll dentro del scroll. Pasa a ser una tarjeta con su
     borde, que es lo que es cuando no hay panel donde meterla.
   · **`Icons.Sparkles`.** El objeto `Icons` de LP-CORE no lo trae —son
     diecisiete y ninguno es ése—, y `renderIcon` devuelve `null` en silencio
     para un nombre que no conoce. Se usa el icono de Font Awesome, que la
     plantilla ya carga y que este mismo componente usa para todo lo demás.
   · **`lang="python"`.** El `CodeBlock` del heredado sólo aceptaba `title` y
     `code`; el de LP-CORE resalta según `lang`, y sin declararlo cae en
     `pseudo`, que es la gramática de Lógica de Programación.
   · **`not-prose`.** `.prose-lp` estiliza `label`, `input` y `select` para
     texto corrido; aquí son controles de formulario.

   Lo que NO cambia: la clave viaja en la cabecera `x-goog-api-key` y no en la
   URL, que es la regla que este mismo módulo enseña más abajo. Y no se guarda
   en `localStorage`: sólo el modelo elegido.
============================================================ */

/* Los modelos caducan. `gemini-2.0-flash` se apagó el 1 de junio de 2026 y los
   `gemini-1.5-*` ya no existen para una clave nueva: pedirlos devuelve 404, así
   que tres de las cuatro opciones que ofrecía esta lista estaban muertas.
   Se revisa contra ai.google.dev/gemini-api/docs/deprecations cada semestre.

   `pensamiento` es lo que hay que mandar en `generationConfig.thinkingConfig`
   para que el modelo no gaste medio minuto razonando antes de escribir una
   clase de veinte líneas. La forma NO es la misma en las dos familias —los 3.x
   usan `thinkingLevel`, los 2.5 el `thinkingBudget` en tokens— y mandarle a un
   modelo la llave de la otra familia es un 400. Por eso viaja junto al `id`,
   y no como una constante suelta: es una propiedad del modelo, no de la app.
   `gemini-2.5-pro` no puede apagar el pensamiento; se queda sin la clave. */
const MODELOS_GEMINI = [
    { id: 'gemini-3.6-flash', name: 'Gemini 3.6 Flash (recomendado)', pensamiento: { thinkingLevel: 'low' } },
    { id: 'gemini-3.5-flash-lite', name: 'Gemini 3.5 Flash-Lite (el más rápido)', pensamiento: { thinkingLevel: 'low' } },
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash (estable)', pensamiento: { thinkingBudget: 0 } },
    { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro (avanzado)' }
];
const MODELO_POR_DEFECTO = MODELOS_GEMINI[0].id;

/* Un error de la API dice mucho en su código de estado, y el mensaje que Google
   manda está en inglés y habla de `projects` y `credentials`. Se traduce a lo
   que el estudiante puede hacer al respecto, que es el único dato que le sirve.
   El texto original se conserva al final: sin él no hay forma de depurar. */
const mensajeDeError = (status, detalle, modelo) => {
    if (status === 400 && /api.?key/i.test(detalle)) {
        return `La API Key no es válida. Revisa que la copiaste completa desde aistudio.google.com/apikey, sin espacios al principio ni al final.`;
    }
    if (status === 403) {
        return `La API Key existe pero no tiene permiso para usar la API de Gemini. Genera una nueva en aistudio.google.com/apikey. (${detalle})`;
    }
    if (status === 404) {
        return `El modelo «${modelo}» ya no está disponible. Elige otro en la lista de arriba. (${detalle})`;
    }
    if (status === 429) {
        return `⏳ Cuota excedida para ${modelo}. Espera ~30 s y reintenta, o selecciona otro modelo.`;
    }
    if (status >= 500) {
        return `El servidor de Gemini falló (HTTP ${status}). No es culpa tuya: reintenta en un minuto.`;
    }
    return `Error al consultar Gemini (HTTP ${status}): ${detalle}`;
};

/* Un 200 sin texto no es un éxito. Las tres causas, en orden de frecuencia:
   el filtro de seguridad bloqueó la petición antes de generar nada
   (`promptFeedback.blockReason`), la bloqueó después de generarla
   (`finishReason: SAFETY`), o el modelo se quedó sin tokens (`MAX_TOKENS`). */
const mensajeDeRespuestaVacia = (data, candidato) => {
    const bloqueoPrevio = data?.promptFeedback?.blockReason;
    if (bloqueoPrevio) {
        return `Gemini rechazó el concepto por su filtro de contenido (${bloqueoPrevio}). Prueba con otro concepto.`;
    }
    const razon = candidato?.finishReason;
    if (razon === 'SAFETY' || razon === 'PROHIBITED_CONTENT') {
        return `Gemini bloqueó la respuesta por su filtro de contenido (${razon}). Prueba con otro concepto.`;
    }
    if (razon === 'MAX_TOKENS') {
        return `La respuesta se cortó por longitud antes de escribir el código. Reintenta, o elige un concepto más concreto.`;
    }
    return `Gemini respondió sin código${razon ? ` (${razon})` : ''}. Reintenta en unos segundos.`;
};

const AIClassBuilder = () => {
    const [concept, setConcept] = useState('');
    const [apiKey, setApiKey] = useState('');
    // El modelo elegido se recuerda, y por eso hay que validarlo al leerlo:
    // quien probara «Gemini 2.0 Flash» el semestre pasado se quedó con ese id
    // grabado, y desde que Google lo apagó el constructor le contestaba 404 en
    // cada intento —para siempre, porque el valor muerto seguía en el disco—.
    const [model, setModel] = useState(() => {
        const guardado = localStorage.getItem('gemini_model');
        return MODELOS_GEMINI.some(m => m.id === guardado) ? guardado : MODELO_POR_DEFECTO;
    });
    const [showKey, setShowKey] = useState(false);
    const [generatedCode, setGeneratedCode] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const saveModel = (m) => {
        setModel(m);
        localStorage.setItem('gemini_model', m);
    };

    const generateClass = async () => {
        if (!apiKey.trim()) { setError('Por favor ingresa tu API Key de Gemini.'); return; }
        if (!concept.trim()) { setError('Por favor escribe un concepto.'); return; }
        setLoading(true); setError(null); setGeneratedCode(null);

        const systemInstruction = "Eres un profesor de Python para estudiantes universitarios de estadística en la Universidad Santo Tomás (Colombia). Genera SOLO código Python puro. No uses bloques markdown (no uses ```). No agregues explicaciones fuera del código.";

        const userPrompt = `Genera una clase Python para el concepto: "${concept.trim()}".\nLa clase debe incluir:\n- Un docstring descriptivo\n- Un constructor __init__ con atributos relevantes (al menos 3)\n- Al menos 2 métodos útiles con docstrings\n- Comentarios explicativos en español\n- Un ejemplo de uso al final (como código, no como comentario)`;

        // La clave NO va en la URL. Una URL se escribe en el historial del
        // navegador, en los logs de cualquier proxy y en la cabecera Referer;
        // una cabecera de petición, no. Es la misma regla que este módulo
        // enseña más abajo («nunca escribas tu API Key en el código») y que
        // el módulo 2 explica una semana antes. La API de Gemini admite las
        // dos formas: se usa la buena.
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

        const elegido = MODELOS_GEMINI.find(m => m.id === model);
        const payload = {
            contents: [{ parts: [{ text: userPrompt }] }],
            systemInstruction: { parts: [{ text: systemInstruction }] },
            generationConfig: elegido?.pensamiento ? { thinkingConfig: elegido.pensamiento } : {}
        };

        // Sólo se reintenta lo que puede salir distinto la segunda vez: la
        // cuota (429) y una caída del servidor (5xx). Una clave inválida o un
        // modelo que no existe van a fallar igual tres veces; reintentarlos
        // sólo hacía que el estudiante mirara girar la ruedita tres segundos
        // antes de leer el error.
        const esReintentable = (status) => status === 429 || status >= 500;

        for (let intento = 0; intento < 3; intento++) {
            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-goog-api-key': apiKey.trim()
                    },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    const detalle = errData?.error?.message || `Error HTTP ${res.status}`;
                    if (esReintentable(res.status) && intento < 2) {
                        await new Promise(r => setTimeout(r, 1000 * Math.pow(2, intento)));
                        continue;
                    }
                    setError(mensajeDeError(res.status, detalle, model));
                    setLoading(false);
                    return;
                }

                const data = await res.json();
                const candidato = data?.candidates?.[0];

                // `parts[0].text` no basta. La respuesta puede traer varias
                // partes, y con los modelos que piensan la primera puede ser el
                // resumen del razonamiento (`thought: true`) y no el código.
                const partes = candidato?.content?.parts || [];
                let code = partes.filter(p => p.text && !p.thought).map(p => p.text).join('');

                // Y puede no traer texto ninguno: si el filtro de seguridad
                // bloqueó la petición, la respuesta es un 200 con `parts`
                // vacío. El código anterior lo guardaba como cadena vacía, que
                // es falsa, así que la tarjeta volvía al estado inicial —el
                // botón parecía no hacer nada—. Ahora se dice qué pasó.
                if (!code.trim()) {
                    setError(mensajeDeRespuestaVacia(data, candidato));
                    setLoading(false);
                    return;
                }

                // Se pidió código puro, pero el modelo a veces lo envuelve en
                // un bloque markdown igual. Si hay valla, se toma lo de dentro;
                // el regex anterior sólo servía si empezaba exactamente por
                // ```python en el primer carácter.
                const cercado = code.match(/```[a-zA-Z]*\s*\n([\s\S]*?)```/);
                if (cercado) code = cercado[1];

                setGeneratedCode(code.trim());
                setLoading(false);
                return;
            } catch (e) {
                // Aquí sólo caen los fallos de red: sin conexión, DNS, CORS.
                console.error(`Intento ${intento + 1}:`, e);
                if (intento === 2) {
                    setError(`No se pudo conectar con la API de Gemini (${e.message}). Revisa tu conexión a internet.`);
                } else {
                    await new Promise(r => setTimeout(r, 1000 * Math.pow(2, intento)));
                }
            }
        }
        setLoading(false);
    };

    return (
        <div className="my-6 rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden not-prose">
            <div className="p-6 border-b border-gray-200 space-y-4">
                <h3 className="font-bold text-gray-800 flex items-center gap-2" style={{ margin: 0 }}>
                    <i className="fas fa-wand-magic-sparkles text-secondary"></i> Constructor IA de Clases
                </h3>

                {/* API Key */}
                <div>
                    <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">API Key de Gemini</label>
                    <div className="flex gap-2">
                        <input
                            type={showKey ? 'text' : 'password'}
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="flex-1 font-mono text-xs p-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                            placeholder="Ingresa tu API Key de Gemini..."
                        />
                        <button
                            onClick={() => setShowKey(prev => !prev)}
                            className="px-3 rounded-lg border border-gray-300 text-gray-500 hover:bg-gray-50 text-xs transition-colors"
                        >
                            <i className={`fas ${showKey ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                        </button>
                    </div>
                    <p className="text-[10px] text-gray-400 mt-1" style={{ margin: '0.25rem 0 0 0' }}>No se guarda. Ingresa tu clave en cada sesión.</p>
                </div>

                {/* Modelo */}
                <div>
                    <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Modelo</label>
                    <select
                        value={model}
                        onChange={(e) => saveModel(e.target.value)}
                        className="w-full text-sm p-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-secondary focus:border-secondary outline-none bg-white transition-all"
                    >
                        {MODELOS_GEMINI.map(m => (
                            <option key={m.id} value={m.id}>{m.name}</option>
                        ))}
                    </select>
                </div>

                {/* Concepto */}
                <div>
                    <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Concepto</label>
                    <input
                        type="text"
                        value={concept}
                        onChange={(e) => setConcept(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && generateClass()}
                        className="w-full text-sm p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-secondary focus:border-secondary outline-none transition-all"
                        placeholder="Ej: Banco, Vehículo, Hospital, Estudiante..."
                    />
                </div>

                {/* Botón */}
                <button
                    onClick={generateClass}
                    disabled={loading}
                    className="w-full py-3 rounded-xl text-white font-semibold text-sm transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 lp-gradient"
                >
                    {loading ? (
                        <><i className="fas fa-spinner fa-spin"></i> Generando...</>
                    ) : (
                        <><i className="fas fa-wand-magic-sparkles"></i> Generar Clase Python</>
                    )}
                </button>
            </div>

            {/* Resultados */}
            <div className="p-6 space-y-4">
                {error && (
                    <div className="p-4 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                        <i className="fas fa-exclamation-circle mr-2"></i>{error}
                    </div>
                )}

                {generatedCode && (
                    <div className="animate-fade-in">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-xs font-bold text-primary uppercase">Clase Generada</span>
                        </div>
                        <CodeBlock lang="python" code={generatedCode} />
                    </div>
                )}

                {!generatedCode && !error && !loading && (
                    <div className="text-center py-10 text-gray-400">
                        <i className="fas fa-wand-magic-sparkles text-4xl opacity-30"></i>
                        <p className="text-sm mt-4">Escribe un concepto y presiona<br /><strong>«Generar Clase Python»</strong></p>
                    </div>
                )}
            </div>
        </div>
    );
};
