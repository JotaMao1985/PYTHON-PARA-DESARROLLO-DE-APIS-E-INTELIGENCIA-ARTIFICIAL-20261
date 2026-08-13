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
const AIClassBuilder = () => {
    const [concept, setConcept] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [model, setModel] = useState(() => localStorage.getItem('gemini_model') || 'gemini-2.5-flash');
    const [showKey, setShowKey] = useState(false);
    const [generatedCode, setGeneratedCode] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const models = [
        { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash (más reciente)' },
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash (rápido)' },
        { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash (estable)' },
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro (avanzado)' }
    ];

    const saveApiKey = (key) => {
        setApiKey(key);
    };

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

        const payload = {
            contents: [{ parts: [{ text: userPrompt }] }],
            systemInstruction: { parts: [{ text: systemInstruction }] }
        };

        for (let attempt = 0; attempt < 3; attempt++) {
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
                    throw new Error(errData?.error?.message || `Error HTTP ${res.status}`);
                }

                const data = await res.json();
                let code = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
                code = code.replace(/^```python\n?/i, '').replace(/^```\n?/i, '').replace(/\n?```$/i, '').trim();
                setGeneratedCode(code);
                setLoading(false);
                return;
            } catch (e) {
                console.error(`Intento ${attempt + 1}:`, e);
                if (attempt === 2) {
                    const msg = e.message || '';
                    if (msg.toLowerCase().includes('quota')) {
                        setError(`⏳ Cuota excedida para ${model}. Espera ~30s y reintenta, o selecciona otro modelo.`);
                    } else {
                        setError(`Error al consultar Gemini: ${msg}. Verifica tu API Key.`);
                    }
                } else {
                    await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
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
                            onChange={(e) => saveApiKey(e.target.value)}
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
                        {models.map(m => (
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
