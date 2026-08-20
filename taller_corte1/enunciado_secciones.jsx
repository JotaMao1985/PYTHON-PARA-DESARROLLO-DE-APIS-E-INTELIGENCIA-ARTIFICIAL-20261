        /* ============================================================
           CONFIG — Taller del Corte I
        ============================================================ */
        const CONFIG = {
            asignatura: 'Python para Desarrollo de APIs e Inteligencia Artificial',
            titulo: 'Taller del Corte I — «Riesgo API v0»',
            codigo: '28549',
            programa: 'Pregrado en Estadística',
            facultad: 'Universidad Santo Tomás',
            periodo: '2026-II',
            creditos: 4,
            semanas: 16,
            docente: 'Javier Mauricio Sierra',
            correoDocente: 'javiersierra@usta.edu.co',
            storageKey: 'taller-corte1-usta-2026ii',
            ra: 'Módulos 1 a 5',
            horas: 16,
            stack: 'FastAPI · Pydantic · scikit-learn · pytest',
            // Lo que el App pinta en la portada y el pie. En la plantilla venían
            // incrustados con la marca del syllabus; aquí salen de CONFIG.
            subtitulo: 'Taller del Corte I · 2026-II · Módulos 1 a 5',
            lema: 'Diagnosticar, refactorizar, medir y defender un servicio que ya funciona mal.',
            chips: ['Diagnóstico', 'Pydantic', 'POO', 'HTTP', 'sync/async', 'Auditar la IA'],
        };

        const PESO_CORTE = 60;
        const PESO_DEFINITIVA = 18;
        const AUTO = 68;
        const MANUAL = 100 - AUTO;

        const CRITERIOS = [
            ['C1', 'Entorno reproducible', 'M1', 8, 'Versiones fijadas; pip install limpio en venv nuevo; sin secretos versionados; .gitignore correcto'],
            ['C2', 'Higiene de Git y trazabilidad', 'M1', 7, 'Un autor por integrante con ≥ 2 commits sustantivos cada uno; mensajes que describen el cambio'],
            ['C3', 'Diagnóstico', 'Parte A', 15, 'Todos los defectos hallados, con causa, cita real al material y evidencia reproducible sobre el SHA que citan'],
            ['C4', 'Contratos HTTP', 'M2 · M4', 12, 'Verbos correctos; 200/404/422; el error viaja en el estado; respuesta JSON, nunca pickle'],
            ['C5', 'Modelado del dominio con POO', 'M3', 12, 'Dominio en clases con responsabilidad clara; sin estado mutable de clase; la lógica fuera de las rutas'],
            ['C6', 'Validación declarativa', 'M4', 12, 'Entradas y salidas en BaseModel; restricciones en Field; ≥ 1 validador; ValidationError → 422'],
            ['C7', 'Arquitectura del servicio', 'M5', 10, 'Modelo cargado al inicio; /health; arranque de producción sin --reload; la batería llega intacta'],
            ['C8', 'Decisión sync/async con evidencia', 'Parte C', 10, 'Los cuatro clasificados; MEDICIONES.csv completo; la interpretación explica SUS tiempos'],
            ['C9', 'Auditoría de la propuesta de IA', 'Parte D', 10, 'Los 3 defectos identificados; comprobación ejecutable; corrección que funciona'],
            ['C10', 'Bitácora de IA', 'Parte E', 4, 'Rechazos argumentados y localizables, no solo prompts aceptados'],
        ];

        const INDIVIDUAL = [
            ['I1', 'Sustentación dirigida', 50, 'sesión de la primera semana de septiembre'],
            ['I2', 'Control presencial de transferencia, sin IA', 30, 'segunda sesión de la última semana de agosto'],
            ['I3', 'Contribución trazable al repositorio', 20, 'git log del commit congelado'],
        ];

        const RUTAS = [
            ['POST', '/score', '200 con la puntuación · 422 si la entrada es inválida'],
            ['GET', '/historial', '200'],
            ['GET', '/siniestros/{id}', '200 · 404 si no existe'],
            ['GET', '/exportar', '200 en JSON'],
            ['GET', '/health', '200 · hay que crearlo'],
            ['GET', '/ping · /consulta-archivo · /servicio-externo · /calculo-pesado', '200'],
        ];

        const RESTRICCIONES = [
            ['B1', 'El entorno es reproducible: requirements.txt con versiones fijadas, sin secretos versionados, .gitignore correcto', 'M1'],
            ['B2', 'Los códigos de estado son correctos y el error viaja en el estado, no en el cuerpo con 200', 'M2'],
            ['B3', 'Nada se serializa con pickle hacia el cliente', 'M2'],
            ['B4', 'El dominio vive en clases, no en funciones sueltas con estado global', 'M3'],
            ['B5', 'Todas las entradas y salidas se declaran con BaseModel; restricciones con Field; al menos un validador; ValidationError → 422', 'M4'],
            ['B6', 'El modelo se carga al iniciar el servicio, no dentro del handler', 'M5'],
            ['B7', 'Existe un endpoint /health que responde 200', 'M5'],
            ['B8', 'El arranque documentado es de producción: uvicorn sin --reload y con --workers', 'M5'],
            ['B9', 'Ningún decorador propio oculta la identidad de la función que envuelve, ni captura excepciones para devolver None', 'M1'],
        ];

        const PERFILES = [
            ['/consulta-archivo', 'Lee un archivo del disco'],
            ['/calculo-pesado', 'Cálculo numérico intensivo en CPU'],
            ['/servicio-externo', 'Llama a otro servicio HTTP (simulado con latencia)'],
            ['/ping', 'Devuelve una constante'],
        ];

        const Tabla = ({ cols, filas, anchos = [] }) => (
            <div className="overflow-x-auto my-4">
                <table className="w-full text-sm bg-white rounded-xl overflow-hidden shadow-sm border border-gray-200">
                    <thead className="lp-gradient text-white">
                        <tr>{cols.map((c, i) => (
                            <th key={i} className={`text-left px-4 py-2.5 font-semibold ${anchos[i] || ''}`}>{c}</th>
                        ))}</tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {filas.map((f, i) => (
                            <tr key={i} className={i % 2 ? 'bg-gray-50/60' : ''}>
                                {f.map((c, j) => <td key={j} className="px-4 py-2.5 align-top break-words">{c}</td>)}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );

        const Dato = ({ valor, etiqueta, nota }) => (
            <div className="flex-1 min-w-[9rem] bg-white rounded-xl border border-gray-200 shadow-sm p-4 text-center">
                <div className="text-3xl font-extrabold text-primary leading-none">{valor}</div>
                <div className="text-xs font-semibold text-navy mt-1.5 uppercase tracking-wide">{etiqueta}</div>
                {nota && <div className="text-[11px] text-gray-500 mt-1 leading-snug">{nota}</div>}
            </div>
        );

        /* ============================================================
           SECCIÓN 1 — ENCUADRE Y REGLAS
        ============================================================ */
        const EncuadreSection = () => (
            <div>
                <Motivacion icon="fa-triangle-exclamation"
                    gancho="Les entregamos un servicio que funciona. Ese es el problema.">
                    <code>riesgo-api-v0</code> arranca, responde y hace lo que dice su README. También arrastra una
                    colección de decisiones equivocadas, todas del tipo que este curso lleva cinco semanas enseñando a
                    no tomar. Ninguna impide que corra: por eso hay que buscarlas.
                </Motivacion>

                <div className="flex flex-wrap gap-3 my-6">
                    <Dato valor={`${PESO_CORTE} %`} etiqueta="del Corte I" nota={`${PESO_DEFINITIVA} % de la definitiva`} />
                    <Dato valor="3" etiqueta="por grupo" nota="máximo" />
                    <Dato valor="2" etiqueta="semanas" nota="22 ago → 4 sep" />
                    <Dato valor="12" etiqueta="minutos" nota="de sustentación" />
                </div>

                <SectionHeader title="Lo que se evalúa, y lo que no" icon={Icons.Award} />
                <Tabla cols={['Sí se evalúa', 'No se evalúa']} filas={[
                    ['Que sepan nombrar lo que ven y por qué está mal', 'Que el código sea largo'],
                    ['Que la decisión técnica esté justificada y medida', 'Que hayan añadido funcionalidades extra'],
                    ['Que sepan comprobar si algo funciona', 'Que el servicio tenga interfaz gráfica'],
                    ['Que cada integrante responda por el repositorio', 'La elegancia del formateo'],
                ]} />
                <p className="text-gray-700 leading-relaxed mb-4">
                    Cualquier cosa que añadan más allá de lo pedido no suma puntos y sí ocupa el tiempo de la defensa.
                    La consigna es <strong>hacer lo pedido y saber por qué</strong>.
                </p>

                <SectionHeader title="La IA está permitida — y es parte de lo evaluado" icon={Icons.Cpu} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    Pueden usar cualquier asistente, sin restricción y para cualquier parte. A cambio, dos obligaciones:
                </p>
                <Pipeline steps={[
                    { num: 1, title: 'Bitácora obligatoria', desc: 'Prompts, qué aceptaron y —esto es lo que se califica— qué rechazaron y con qué argumento' },
                    { num: 2, title: 'La Parte D audita a la IA', desc: 'Se les entrega código generado por IA que parece correcto y no lo es. Encontrarlo es el ejercicio' },
                ]} />
                <Box type="danger" label="Bitácora ausente o falsificada: −15 puntos">
                    El taller está diseñado sabiendo que van a usar IA. Las partes A y B las resolverán más rápido con
                    ayuda, y está bien: ese tiempo es para las partes C, D y E, donde la IA no puede medir en su
                    máquina, no audita bien su propio código, y no se sienta en la sustentación.
                </Box>

                <SectionHeader title="Entrega" icon={Icons.GitBranch} />
                <ul className="list-disc pl-6 space-y-2 text-gray-700 leading-relaxed mb-4">
                    <li><strong>Un repositorio en GitHub por grupo</strong>, con historia real de commits. No se reciben
                        <code>.zip</code>: el criterio C2 califica <code>git log</code> por autor.</li>
                    <li>El enlace se entrega por Moodle antes del <strong>viernes 4 de septiembre, 23:59</strong>. Se
                        registra el SHA del último commit a esa hora; <strong>lo que se califica es ese commit</strong>.</li>
                    <li>El repositorio debe arrancar siguiendo <strong>su propio README</strong>, en una máquina limpia.
                        Si no arranca, la nota tiene tope de 60.</li>
                </ul>

                <SectionHeader title="Grupos y responsabilidad individual" icon={Icons.Layers} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    Máximo 3. Son 32 estudiantes: habrá diez grupos de tres y uno de dos. Esta agrupación
                    <strong> es independiente de los equipos de dos del proyecto integrador</strong> y no crea equipo de
                    proyecto. Repartan el trabajo como quieran, pero <strong>cualquier integrante puede ser preguntado
                    por cualquier línea del repositorio</strong>.
                </p>
                <Box type="warn" label="Control presencial — segunda sesión de la última semana de agosto, 10 minutos, sin IA">
                    Individual, papel y lápiz. A cada estudiante se le entrega <strong>un endpoint que no ha visto</strong>,
                    de cinco a diez líneas, y escribe: clasificación, decisión, <strong>justificación</strong> y
                    <strong> predicción</strong> de qué vería al medirlo con concurrencia 1 y 20. No se pide reproducir
                    nada de lo que entregaron: se pide llevar el criterio de la Parte C a un caso nuevo. Si hicieron la
                    Parte C ustedes, esto les sale en cinco minutos.
                </Box>
            </div>
        );

        /* ============================================================
           SECCIÓN 2 — EL ARTEFACTO Y SUS CONTRATOS
        ============================================================ */
        const ArtefactoSection = () => (
            <div>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Un microservicio de puntuación de siniestros con ocho endpoints, un modelo serializado de juguete,
                    un dataset sintético y un README. <strong>Arranca.</strong> Ninguno de los defectos impide que corra.
                </p>
                <CodeBlock lang="shell" title="Punto de partida" plegable={false} code={
`git clone <url-del-semilla> riesgo-api
cd riesgo-api
cat README.md          # léanlo: forma parte del problema`} />
                <Box type="tip" label="No se dice cuántos defectos hay">
                    Buscarlos es la Parte A. Las cuatro plantillas de entrega vienen en <code>plantillas/</code> dentro
                    del propio repositorio: cópienlas a la raíz y rellénenlas. Traen resueltos detalles de formato que
                    el calificador exige.
                </Box>

                <SectionHeader title="El contrato de rutas no se cambia" icon={Icons.Workflow} />
                <p className="text-gray-700 leading-relaxed mb-2">
                    Estas son las rutas y los verbos que el calificador va a golpear. Pueden añadir rutas si lo
                    justifican; no pueden quitar ni renombrar estas.
                </p>
                <Tabla cols={['Verbo', 'Ruta', 'Devuelve']} anchos={['w-20', 'w-64', '']}
                    filas={RUTAS.map(([v, r, d]) => [
                        <span className="font-mono font-bold text-secondary">{v}</span>,
                        <span className="font-mono">{r}</span>, d])} />

                <SectionHeader title="El contrato de dominio, tampoco" icon={Icons.Binary} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    La batería construye objetos directamente, así que dos nombres quedan fijados:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700 leading-relaxed mb-3">
                    <li><code>dominio.EvaluadorRiesgo</code> debe poder construirse <strong>solo con la póliza</strong>:
                        <code> EvaluadorRiesgo("POL-2026-0413")</code>. Cualquier colaborador —el modelo, un
                        repositorio— va como argumento <strong>opcional</strong>.</li>
                    <li>El método que registra una evaluación se sigue llamando <code>anotar(puntaje)</code>.</li>
                </ul>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Dentro de esos dos límites el modelado es suyo: dónde vive el historial, qué clases hay y qué
                    colabora con qué es justo lo que califica C5.
                </p>

                <SectionHeader title="La batería visible" icon={Icons.Bug} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    En <code>tests/test_contrato.py</code> hay once tests. Diez están <strong>en rojo</strong> sobre el
                    repositorio tal como se entrega, y <strong>todos deben pasar al terminar</strong>. Que pasen es el
                    mínimo, no la meta: hay criterios de rúbrica que los tests no ven.
                </p>
                <Box type="danger" label="No modifiquen ni borren esos tests">
                    Se comprueba el SHA-256 del archivo contra el del semilla. Sin esa comprobación, «que pasen todos
                    los tests» se cumpliría con <code>git rm tests/</code>.
                </Box>
            </div>
        );

        /* ============================================================
           SECCIÓN 3 — LAS CINCO PARTES
        ============================================================ */
        const PartesSection = () => (
            <div>
                <Accordion items={[
                    {
                        titulo: 'Parte A · Diagnóstico',
                        contenido: (
                            <div>
                                <p className="mb-3">Encuentren los defectos y documéntenlos en <code>HALLAZGOS.md</code>,
                                    una fila por defecto, con las ocho columnas de la plantilla.</p>
                                <Tabla cols={['Regla', 'Por qué']} filas={[
                                    ['La cita «Módulo · Sección» debe existir', 'Se verifica contra el menú lateral del material. Una cita inventada anula la fila'],
                                    ['«SHA donde se observa» es el commit donde el defecto todavía vive', 'Normalmente v0-semilla. La Parte B lo repara: si declaran el commit final, el comando no reproduce nada'],
                                    ['El comando de evidencia se ejecuta', 'Escríbanlo contra localhost:8000; el calificador sustituye el puerto'],
                                    ['La salida es literal, copiada de su terminal', 'Se compara con la salida real. Una salida inventada se detecta'],
                                    ['Entre 6 y 12 hallazgos', 'Una fila que no sea un defecto real resta la mitad de lo que suma una correcta'],
                                ]} />
                                <Box type="warn" label="Tuberías dentro de una celda">
                                    Si el comando lleva una tubería —y varios la llevarán, por <code>grep</code> o
                                    <code> head</code>— escríbanla escapada con barra invertida. Sin escapar, Markdown
                                    la lee como separador de columna y su fila pasa a tener nueve campos.
                                </Box>
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte B · Refactor con restricciones',
                        contenido: (
                            <div>
                                <p className="mb-3">Arreglen el servicio. Las restricciones no son sugerencias: el
                                    calificador las comprueba una por una.</p>
                                <Tabla cols={['#', 'Restricción', 'Módulo']} anchos={['w-12', '', 'w-20']}
                                    filas={RESTRICCIONES.map(([n, t, m]) => [
                                        <span className="font-mono font-bold text-secondary">{n}</span>, t,
                                        <span className="font-semibold text-navy">{m}</span>])} />
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte C · Decisión sync/async, medida',
                        contenido: (
                            <div>
                                <p className="mb-3">El servicio expone cuatro endpoints con perfiles distintos:</p>
                                <Tabla cols={['Endpoint', 'Qué hace']} anchos={['w-56', '']}
                                    filas={PERFILES.map(([e, d]) => [<span className="font-mono">{e}</span>, d])} />
                                <p className="mb-3">Para cada uno: clasifíquenlo, decidan cómo debe declararse el
                                    handler, y <strong>demuéstrenlo midiendo</strong>. Los dos vocabularios son cerrados
                                    —se parsean, escríbanlos exactamente así:</p>
                                <Tabla cols={['Columna', 'Valores admitidos']} anchos={['w-40', '']} filas={[
                                    [<code>clasificacion</code>, <span className="font-mono">IO-bound · CPU-bound · trivial</span>],
                                    [<code>decision</code>, <span className="font-mono">def · async def · async def + executor</span>],
                                ]} />
                                <p className="mb-3">Cada endpoint con <strong>dos condiciones</strong>: concurrencia 1 y
                                    concurrencia 20, 50 peticiones. El semilla trae <code>medir.py</code> funcionando:
                                    lanza las peticiones, calienta la caché, calcula los percentiles y escribe el CSV.
                                    Lo que no hace —y es lo que se califica— es rellenar <code>clasificacion</code> y
                                    <code> decision</code>, ni explicar los números.</p>
                                <Box type="danger" label="La regla falla en más de un caso, y de dos maneras distintas">
                                    En uno, seguirla da peor rendimiento. En otro, el código la incumple y
                                    <strong> la medición dice que da exactamente igual</strong>. Los dos cuentan, y el
                                    segundo solo se responde bien midiendo primero y decidiendo después.
                                </Box>
                                <p className="mb-1">Y un párrafo por endpoint en <code>HALLAZGOS.md</code> que explique
                                    <strong> los tiempos que obtuvieron ustedes</strong>. Se califica la coherencia entre
                                    la clasificación, la decisión que quedó en el código y la explicación de los
                                    números. No se califica el número.</p>
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte D · Auditoría de la propuesta de IA',
                        contenido: (
                            <div>
                                <p className="mb-3">En el repositorio hay un archivo <code>ia_propuesta.py</code>: código
                                    generado por un asistente para resolver parte de este mismo taller. Importa y
                                    ejecuta sin errores de sintaxis, está comentado, es legible y
                                    <strong> tiene tres defectos de comportamiento</strong>.</p>
                                <p className="mb-3">Entregan <code>DICTAMEN_IA.md</code> con cuatro secciones por
                                    defecto —qué está mal, por qué (citando módulo y sección), cómo lo comprobaron con
                                    su salida literal, y la corrección— más
                                    <code> ia_propuesta_corregida.py</code>.</p>
                                <Box type="tip" label="El peso está en «cómo lo comprobamos»">
                                    Afirmar que algo está mal no vale; demostrarlo, sí. Conserven los nombres y las
                                    firmas públicas: la corrección se prueba contra ese contrato.
                                    <code> ia_propuesta.py</code> no forma parte del servicio: no lo integren.
                                </Box>
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte E · Bitácora y sustentación',
                        contenido: (
                            <div>
                                <p className="mb-3"><code>BITACORA_IA.md</code> con tres secciones obligatorias:
                                    <code> ## Prompts</code>, <code>## Aceptado</code> y <code>## Rechazado</code>. En la
                                    última va lo que se califica: qué les propuso la IA que no aceptaron, y por qué. Es
                                    el único apartado con peso propio.</p>
                                <Pipeline steps={[
                                    { num: 1, title: '4 min · demo en vivo', desc: 'Levantan el servicio y le pegan con curl: un caso válido, uno inválido que debe dar 422, y /health. Sin diapositivas' },
                                    { num: 2, title: '8 min · preguntas dirigidas', desc: 'A un integrante concreto, sobre una línea concreta de SU repositorio. Todos deben poder responder por todo' },
                                ]} />
                            </div>
                        )
                    },
                ]} />
            </div>
        );

        /* ============================================================
           SECCIÓN 4 — EVALUACIÓN
        ============================================================ */
        const EvaluacionSection = () => {
            const total = CRITERIOS.reduce((a, c) => a + c[3], 0);
            const totalInd = INDIVIDUAL.reduce((a, c) => a + c[2], 0);
            return (
                <div>
                    <div className="flex flex-wrap gap-3 mb-6">
                        <Dato valor={total} etiqueta="puntos grupales" nota="10 criterios" />
                        <Dato valor={AUTO} etiqueta="los decide un script" nota="con su evidencia" />
                        <Dato valor={MANUAL} etiqueta="los lee el docente" nota="lo cualitativo" />
                        <Dato valor={totalInd} etiqueta="puntos individuales" nota="I1 · I2 · I3" />
                    </div>

                    <Box type="info" label="Cómo se combinan">
                        <p className="mb-2">La nota final de cada estudiante es:</p>
                        <div className="text-center font-mono text-base font-bold text-secondary my-3">
                            nota = min( 0,70 × grupal + 0,30 × individual , individual + 15 )
                        </div>
                        <p>Un buen repositorio no compensa no entender lo que hay dentro. Si su nota individual es 40,
                        la final no pasa de 55 por bueno que sea el trabajo del grupo. Si ambas van parejas, la cota no
                        se activa y no cambia nada.</p>
                    </Box>

                    <SectionHeader title="Rúbrica del grupo" icon={Icons.Calculator} />
                    <p className="text-gray-700 leading-relaxed mb-2">
                        Escala por criterio: <strong>4</strong> Excelente · <strong>3</strong> Competente ·
                        <strong> 2</strong> En desarrollo · <strong>1</strong> Insuficiente · <strong>0</strong> Ausente
                        o no verificable.
                    </p>
                    <Tabla cols={['#', 'Criterio', 'Cubre', 'Pts', 'Nivel 4 se ve así']}
                        anchos={['w-12', 'w-52', 'w-20', 'w-12', '']}
                        filas={CRITERIOS.map(([id, t, m, p, n4]) => [
                            <span className="font-mono font-bold text-secondary">{id}</span>,
                            <strong className="text-navy">{t}</strong>,
                            <span className="text-xs font-semibold text-gray-500">{m}</span>,
                            <span className="font-bold">{p}</span>, n4])} />

                    <SectionHeader title="Nota individual" icon={Icons.Award} />
                    <Tabla cols={['#', 'Componente', 'Pts', 'Cuándo']} anchos={['w-12', '', 'w-12', 'w-52']}
                        filas={INDIVIDUAL.map(([id, t, p, c]) => [
                            <span className="font-mono font-bold text-secondary">{id}</span>, t,
                            <span className="font-bold">{p}</span>,
                            <span className="text-gray-500">{c}</span>])} />

                    <SectionHeader title="Penalizaciones" icon={Icons.Bug} />
                    <Tabla cols={['Situación', 'Consecuencia']} filas={[
                        ['Bitácora de IA ausente o falsificada', <strong className="text-red-700">−15 puntos</strong>],
                        ['El repositorio no arranca siguiendo su propio README', <strong className="text-red-700">tope de 60</strong>],
                        ['Entrega posterior al congelado', <strong className="text-red-700">no se recibe</strong>],
                    ]} />
                </div>
            );
        };

        /* ============================================================
           SECCIÓN 5 — QUÉ SE ENTREGA Y CÓMO SE CALIFICA
        ============================================================ */
        const EntregaSection = () => (
            <div>
                <SectionHeader title="Lista de verificación" icon={Icons.Table} />
                <p className="text-gray-700 leading-relaxed mb-3">En la raíz del repositorio:</p>
                <div className="grid sm:grid-cols-2 gap-2 my-4">
                    {[
                        ['El servicio corregido', 'arranca siguiendo su propio README'],
                        ['HALLAZGOS.md', 'tabla de la Parte A + sección «Parte C»'],
                        ['MEDICIONES.csv', '4 endpoints × 2 condiciones = 8 filas'],
                        ['medir.py', 'con las modificaciones que hayan necesitado'],
                        ['DICTAMEN_IA.md', 'los tres defectos, con su comprobación'],
                        ['ia_propuesta_corregida.py', 'conservando las firmas públicas'],
                        ['BITACORA_IA.md', 'Prompts · Aceptado · Rechazado'],
                        ['requirements.txt', 'con versiones fijadas'],
                        ['README.md', 'actualizado con el arranque real'],
                    ].map(([f, d], i) => (
                        <div key={i} className="flex items-start gap-2.5 bg-white border border-gray-200 rounded-lg px-3 py-2.5 shadow-sm">
                            <i className="fas fa-square-check text-secondary mt-0.5"></i>
                            <div>
                                <div className="font-mono text-sm font-semibold text-navy">{f}</div>
                                <div className="text-xs text-gray-500 leading-snug">{d}</div>
                            </div>
                        </div>
                    ))}
                </div>

                <SectionHeader title="Cómo se califica" icon={Icons.Cpu} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    {AUTO} de los 100 puntos los resuelve un <strong>calificador automático</strong> que se corre sobre
                    su repositorio: crea un entorno limpio, instala sus dependencias, corre una batería de tests que
                    ustedes no ven, levanta su servicio y le pega, analiza la estructura de su código y ejecuta los
                    comandos de evidencia que declararon sobre el commit que citaron. Los {MANUAL} restantes los lee el
                    docente.
                </p>
                <p className="text-gray-700 leading-relaxed mb-3">
                    Reciben un reporte con <strong>la nota de cada criterio y la evidencia que la sustenta</strong>: el
                    comando ejecutado y su salida literal. Es auditable: si creen que un check está mal, se revisa
                    contra esa evidencia.
                </p>
                <Box type="warn" label="Dos consecuencias prácticas">
                    <p className="mb-2"><strong>Los formatos son rígidos porque se parsean.</strong> Una tabla torcida
                    en <code>HALLAZGOS.md</code> no se «entiende igual»: se rechaza indicando la línea. Usen las
                    plantillas que vienen en el repositorio.</p>
                    <p><strong>Que el calificador no pueda medir algo no es un aprobado.</strong> Sale marcado como no
                    verificable y pasa a revisión del docente; si tampoco así puede sustentarse, cuenta 0.</p>
                </Box>
            </div>
        );

        /* ============================================================
           CURRÍCULO
        ============================================================ */
        const curriculum = [
            { id: 'encuadre', title: 'Encuadre y reglas del juego', icon: 'BookOpen', component: EncuadreSection },
            { id: 'artefacto', title: 'El artefacto y sus contratos', icon: 'FileCode', component: ArtefactoSection },
            { id: 'partes', title: 'Las cinco partes', icon: 'Layers', component: PartesSection },
            { id: 'evaluacion', title: 'Evaluación y rúbrica', icon: 'Calculator', component: EvaluacionSection },
            { id: 'entrega', title: 'Qué se entrega y cómo se califica', icon: 'Table', component: EntregaSection },
        ];
