        /* ============================================================
           CONFIG — Taller del Corte II
        ============================================================ */
        const CONFIG = {
            asignatura: 'Python para Desarrollo de APIs e Inteligencia Artificial',
            titulo: 'Taller del Corte II — «Pólizas API v0»',
            codigo: '28549',
            programa: 'Pregrado en Estadística',
            facultad: 'Universidad Santo Tomás',
            periodo: '2026-II',
            creditos: 4,
            semanas: 16,
            docente: 'Javier Mauricio Sierra',
            correoDocente: 'javiersierra@usta.edu.co',
            storageKey: 'taller-corte2-usta-2026ii',
            ra: 'Módulos 6 a 11',
            horas: 32,
            stack: 'FastAPI · SQLAlchemy · Alembic · pytest · Docker',
            subtitulo: 'Taller del Corte II · 2026-II · Módulos 6 a 11',
            lema: 'Diagnosticar, refactorizar, contar y defender un servicio que persiste mal.',
            chips: ['Diagnóstico', 'Pydantic v2', 'Depends', 'SQLAlchemy', 'N+1', 'pytest', 'Docker', 'Auditar la IA'],
        };

        const PESO_CORTE = 60;
        const PESO_DEFINITIVA = 18;
        const AUTO = 72;
        const MANUAL = 100 - AUTO;

        const CRITERIOS = [
            ['C1', 'Entorno y configuración', 'M1 · M8', 8, 'Versiones fijadas; instalación limpia; sin secretos; .gitignore correcto; Settings con caché y .env.example'],
            ['C2', 'Higiene de Git y trazabilidad', 'M1', 7, 'Una persona por integrante con ≥ 2 commits sustantivos cada una; mensajes que describen el cambio'],
            ['C3', 'Diagnóstico', 'Parte A', 15, 'Todos los defectos hallados, con causa, cita real al material y evidencia reproducible sobre el SHA que citan'],
            ['C4', 'Contratos HTTP y validación', 'M6 · M7', 12, 'response_model en todo; 201/404/409/422; PUT parcial; validadores que devuelven; submodelos tipados; coherencia de fechas'],
            ['C5', 'Persistencia e inyección', 'M8 · M9', 15, 'Sesión por petición; claves foráneas activas; Alembic aplica en limpio; from_attributes; modelado con responsabilidades claras'],
            ['C6', 'Tests', 'M10', 10, 'Batería visible verde e intacta; tests propios aislados con dependency_overrides; dos corridas iguales; la base de la app no cambia'],
            ['C7', 'Decisión medida sobre la carga de relaciones', 'Parte C', 10, 'Las 4 estrategias defendibles; conteos reproducibles; la interpretación explica SUS números'],
            ['C8', 'Auditoría de los tests de la IA', 'Parte D', 10, 'Los 3 defectos, cada uno con una mutación demostrada; tests corregidos que detectan las mutaciones del calificador'],
            ['C9', 'Contenedor', 'M11', 9, 'Construye; responde desde el host; imagen sin .env ni base de datos; no root; HEALTHCHECK; multietapa con base fijada'],
            ['C10', 'Bitácora de IA', 'Parte E', 4, 'Rechazos argumentados y localizables, no solo prompts aceptados'],
        ];

        const INDIVIDUAL = [
            ['I1', 'Sustentación dirigida', 50, 'sesiones de la tercera y cuarta semana de octubre'],
            ['I2', 'Control presencial de transferencia, sin IA', 30, 'sesión de la segunda semana de octubre'],
            ['I3', 'Contribución trazable al repositorio', 20, 'git log del commit congelado, con las identidades de EQUIPO.md'],
        ];

        const RUTAS = [
            ['POST', '/polizas', '201 con la póliza creada · 422 si la entrada es inválida · 409 si el número ya existe'],
            ['GET', '/polizas', '200, cada póliza con sus siniestros'],
            ['GET', '/polizas/{id}', '200 · 404 si no existe'],
            ['PUT', '/polizas/{id}', '200 con la póliza actualizada · 404 · 422; parcial'],
            ['POST', '/polizas/{id}/siniestros', '201 · 404 si la póliza no existe · 422'],
            ['GET', '/siniestros', '200, cada siniestro con su póliza'],
            ['GET', '/resumen', '200, número de siniestros y monto total por póliza'],
            ['POST', '/score', '200 con la puntuación · 404 si la póliza no existe · 422; registra la predicción'],
            ['GET', '/predicciones', '200, cada predicción con el numero de su póliza y su puntaje'],
            ['GET', '/health', '200 · hay que crearlo'],
        ];

        const RESTRICCIONES = [
            ['B1', 'Entorno reproducible: requirements.txt con versiones fijadas; .env.example con valores con los que el servicio arranca (el calificador lo copia a .env si no hay .env); sin secretos versionados; .gitignore que cubre .env, *.db y el entorno virtual, y nada de eso sigue en el índice', 'M1 · M8'],
            ['B2', 'La configuración se lee con BaseSettings desde .env; la función que la entrega lleva lru_cache y se inyecta con Depends; la app honra la variable DATABASE_URL', 'M8'],
            ['B3', 'Sesión por petición: database.get_db es un generador con yield que cierra la sesión; ninguna sesión a nivel de módulo; toda ruta que toca la base recibe la sesión con Depends(get_db)', 'M8 · M9'],
            ['B4', 'Modelos con SQLAlchemy 2.0 (DeclarativeBase, Mapped, mapped_column, relationship); PRAGMA foreign_keys activo en SQLite; esquemas de salida con from_attributes=True', 'M9'],
            ['B5', 'Existe alembic/ con al menos una revisión; alembic/env.py toma la URL de DATABASE_URL; alembic upgrade head sobre una base vacía crea el esquema; create_all desaparece del arranque', 'M9'],
            ['B6', 'response_model en todas las rutas; 201 al crear, 404 si no existe, 409 si el número de póliza está repetido, 422 si la entrada es inválida; el PUT es parcial y no destruye lo que no se envió', 'M6'],
            ['B7', 'Los validadores de campo devuelven el valor; el campo anidado de siniestros se tipa con un BaseModel; hay un model_validator que exige fecha_fin posterior a fecha_inicio; las restricciones van en Field', 'M7'],
            ['B8', 'tests/test_contrato.py llega intacto y pasa; los tests propios sustituyen la sesión con app.dependency_overrides sobre una base temporal; pytest pasa dos veces seguidas; la base de la aplicación no cambia al correrlos', 'M10'],
            ['B9', 'Dockerfile multietapa sobre python:3.11.9-slim-bookworm, .dockerignore, usuario no root, HEALTHCHECK, CMD sin --reload y con --host 0.0.0.0; docker run -p 8000:8000 responde en /health desde el host', 'M11'],
            ['B10', 'Existe GET /health que responde 200 e indica si la base de datos responde', 'M6 · M9'],
        ];

        const PERFILES = [
            ['/polizas', 'Todas las pólizas, cada una con la lista de sus siniestros'],
            ['/polizas/{id}', 'Una póliza con sus siniestros'],
            ['/siniestros', 'Todos los siniestros, cada uno con el número de su póliza'],
            ['/resumen', 'Por póliza: cuántos siniestros tiene y cuánto suman'],
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
                    gancho="Les entregamos un servicio que funciona, persiste y hasta trae tests. Ese es el problema.">
                    <code>polizas-api-v0</code> arranca, responde, guarda en SQLite y tiene un <code>Dockerfile</code>.
                    También arrastra una colección de decisiones equivocadas, todas del tipo que los módulos 6 a 11
                    enseñan a no tomar. Ninguna impide que corra: por eso hay que buscarlas.
                </Motivacion>

                <div className="flex flex-wrap gap-3 my-6">
                    <Dato valor={`${PESO_CORTE} %`} etiqueta="del Corte II" nota={`${PESO_DEFINITIVA} % de la definitiva`} />
                    <Dato valor="1 a 3" etiqueta="por grupo" nota="a su elección" />
                    <Dato valor="4" etiqueta="semanas" nota="21 sep → 16 oct" />
                    <Dato valor="12" etiqueta="minutos" nota="de sustentación" />
                </div>

                <SectionHeader title="Lo que se evalúa, y lo que no" icon={Icons.Award} />
                <Tabla cols={['Sí se evalúa', 'No se evalúa']} filas={[
                    ['Que sepan nombrar lo que ven y por qué está mal', 'Que el código sea largo'],
                    ['Que la decisión técnica esté justificada y medida', 'Que hayan añadido funcionalidades extra'],
                    ['Que sepan demostrar que algo funciona, y que un test lo demuestre', 'Que el servicio tenga interfaz gráfica'],
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
                    { num: 2, title: 'La Parte D audita a la IA', desc: 'Se les entrega una batería de tests generada por IA que está en verde y no demuestra nada. Encontrar por qué es el ejercicio' },
                ]} />
                <Box type="danger" label="Bitácora ausente o falsificada: −15 puntos">
                    El taller está diseñado sabiendo que van a usar IA. Las partes A y B las resolverán más rápido con
                    ayuda, y está bien: ese tiempo es para las partes C, D y E, donde la IA no puede contar consultas
                    en su máquina, no audita bien sus propios tests, y no se sienta en la sustentación.
                </Box>

                <SectionHeader title="Entrega" icon={Icons.GitBranch} />
                <ul className="list-disc pl-6 space-y-2 text-gray-700 leading-relaxed mb-4">
                    <li><strong>Un repositorio en GitHub por grupo, clonado del semilla</strong>, con historia real de
                        commits. No se reciben <code>.zip</code>: el criterio C2 califica <code>git log</code> por persona.</li>
                    <li><strong>Clonen el semilla; no descarguen carpetas del sitio del curso.</strong> El calificador
                        comprueba que el commit del semilla está en la historia de su repositorio.</li>
                    <li>El enlace se entrega por Moodle antes del <strong>viernes 16 de octubre, 23:59</strong>. A esa
                        hora se lee el remoto de cada grupo y se registra el SHA; <strong>lo que se califica es ese commit</strong>.</li>
                    <li>El repositorio debe arrancar siguiendo <strong>su propio README</strong>, con <code>uvicorn</code> y con
                        <code> docker run</code>. Si no arranca de ninguna de las dos maneras, la nota tiene tope de 60.</li>
                    <li><strong>Antes de congelar, corran <code>python verificar_entrega.py</code></strong>: hace las mismas
                        comprobaciones de entrada que el calificador y les dice qué falta.</li>
                </ul>

                <SectionHeader title="Grupos y responsabilidad individual" icon={Icons.Layers} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    De 1 a 3 personas, a su elección; un grupo de una persona hace el mismo taller. Esta agrupación
                    <strong> es independiente de los equipos del proyecto integrador</strong>. Declaren el equipo en
                    <code> EQUIPO.md</code> con <strong>todas</strong> las identidades con las que hacen commits: el
                    calificador agrupa los commits por persona con esa tabla. Repartan el trabajo como quieran, pero
                    <strong> cualquier integrante puede ser preguntado por cualquier línea del repositorio</strong>.
                </p>
                <Box type="warn" label="Control presencial — sesión de la segunda semana de octubre, 10 minutos, sin IA">
                    Individual, papel y lápiz. A cada estudiante se le entrega <strong>un endpoint con relaciones que
                    no ha visto</strong>, de cinco a diez líneas, y escribe: la estrategia de carga, cuántas consultas
                    SQL esperaría con 10 registros y con 10 000, y <strong>por qué</strong>. No se pide reproducir nada
                    de lo que entregaron: se pide llevar el criterio de la Parte C a un caso nuevo. Si hicieron la
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
                    Un servicio de gestión de pólizas con nueve endpoints —pólizas, siniestros, resumen, puntuación e
                    histórico de predicciones—, un modelo serializado de juguete, una base SQLite con datos, tests, un
                    <code> Dockerfile</code> y un README. <strong>Arranca.</strong> Ninguno de los defectos impide que corra.
                </p>
                <CodeBlock lang="shell" title="Punto de partida" plegable={false} code={
`git clone https://github.com/JotaMao1985/polizas-api-v0 polizas-api
cd polizas-api
cat README.md          # léanlo: forma parte del problema`} />
                <Box type="tip" label="No se dice cuántos defectos hay">
                    Buscarlos es la Parte A. Las cinco plantillas de entrega vienen en <code>plantillas/</code> dentro
                    del propio repositorio: cópienlas a la raíz y rellénenlas. Traen resueltos detalles de formato que
                    el calificador exige, y <code>verificar_entrega.py</code> les dice si algo quedó en el sitio equivocado.
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

                <SectionHeader title="El contrato de datos, tampoco" icon={Icons.Binary} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    La batería oculta arranca su servicio sobre una base de datos vacía y espera cuatro cosas:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700 leading-relaxed mb-3">
                    <li>La aplicación lee la ruta de la base de <code>DATABASE_URL</code>, y <code>alembic upgrade head</code>
                        crea el esquema en esa base: <code>alembic/env.py</code> toma la URL de la misma configuración.</li>
                    <li>Los modelos se siguen llamando <code>modelos.Poliza</code>, <code>modelos.Siniestro</code> y
                        <code> modelos.Prediccion</code>; la aplicación sigue siendo <code>main:app</code>; la dependencia que
                        entrega la sesión se llama <code>database.get_db</code>.</li>
                    <li>Las respuestas conservan los nombres de campo de la entrada más el <code>id</code>;
                        <code> /score</code> devuelve <code>numero</code>, <code>puntaje</code> en [0, 1] y <code>alto_riesgo</code>.</li>
                </ul>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Dentro de esos límites el modelado es suyo: qué columnas, qué cascadas, dónde vive la lógica del
                    puntaje y del resumen es justo lo que califica C5.
                </p>

                <SectionHeader title="La batería visible" icon={Icons.Bug} />
                <p className="text-gray-700 leading-relaxed mb-3">
                    En <code>tests/test_contrato.py</code> hay doce tests. La mayoría están <strong>en rojo</strong> sobre el
                    repositorio tal como se entrega, y <strong>todos deben pasar al terminar</strong>. Que pasen es el
                    mínimo, no la meta: hay criterios de rúbrica que los tests no ven.
                </p>
                <Box type="danger" label="No modifiquen ni borren esos tests">
                    Se comprueba que el archivo llega intacto. Sin esa comprobación, «que pasen todos los tests» se
                    cumpliría con <code>git rm tests/</code>.
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
                                    ['La cita «Módulo · Sección» debe existir en los módulos 6 a 11', 'Se verifica contra el menú lateral del material. Una cita inventada anula la fila'],
                                    ['«SHA donde se observa» es el commit donde el defecto todavía vive', 'Normalmente v0-semilla. La Parte B lo repara: si declaran el commit final, el comando no reproduce nada'],
                                    ['El comando de evidencia se ejecuta', 'Contra localhost:8000; el calificador sustituye el puerto. Un comando docker también vale'],
                                    ['La salida es literal, copiada de su terminal', 'Se compara con la salida real. Una salida inventada se detecta'],
                                    ['Entre 8 y 14 hallazgos', 'Una fila que no sea un defecto real resta la mitad de lo que suma una correcta'],
                                ]} />
                                <Box type="warn" label="Tuberías dentro de una celda">
                                    Si el comando lleva una tubería —y varios la llevarán, por <code>grep</code> o
                                    <code> jq</code>— escríbanla escapada con barra invertida. Sin escapar, Markdown la
                                    lee como separador de columna y su fila pasa a tener nueve campos.
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
                                <Tabla cols={['#', 'Restricción', 'Módulo']} anchos={['w-12', '', 'w-24']}
                                    filas={RESTRICCIONES.map(([n, t, m]) => [
                                        <span className="font-mono font-bold text-secondary">{n}</span>, t,
                                        <span className="font-semibold text-navy">{m}</span>])} />
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte C · Decisión medida: cómo se cargan las relaciones',
                        contenido: (
                            <div>
                                <p className="mb-3">Cuatro endpoints devuelven datos que viven en más de una tabla:</p>
                                <Tabla cols={['Endpoint', 'Qué devuelve']} anchos={['w-56', '']}
                                    filas={PERFILES.map(([e, d]) => [<span className="font-mono">{e}</span>, d])} />
                                <p className="mb-3">Para cada uno: decidan <strong>cómo debe cargarse la relación</strong>,
                                    déjenlo en el código, y <strong>demuéstrenlo contando las consultas SQL</strong> que el
                                    servicio emite. El vocabulario es cerrado —se parsea, escríbanlo exactamente así:</p>
                                <Tabla cols={['Columna', 'Valores admitidos']} anchos={['w-40', '']} filas={[
                                    [<code>estrategia</code>, <span className="font-mono">lazy · selectinload · joinedload · agregada</span>],
                                ]} />
                                <p className="mb-3">Cada endpoint con <strong>dos tamaños</strong>: 10 y 2000 pólizas, con tres
                                    siniestros cada una. El semilla trae <code>contar_consultas.py</code> funcionando: siembra
                                    por la API, levanta la aplicación en proceso, cuenta cada sentencia SQL y escribe
                                    <code> CONSULTAS.csv</code>. Lo que no hace —y es lo que se califica— es rellenar
                                    <code> estrategia</code>, ni explicar los números. <strong>Se califica el número de consultas,
                                    no el tiempo</strong>: el conteo es determinista y el calificador lo reproduce.</p>
                                <Box type="danger" label="La regla falla en más de un caso, y de dos maneras distintas">
                                    «Cargar todo de una vez es más eficiente». En un caso, seguirla da peor rendimiento. En
                                    otro, el código la incumple y <strong>la medición dice que da exactamente igual</strong>.
                                    Los dos cuentan, y el segundo solo se responde bien contando primero y decidiendo después.
                                </Box>
                                <p className="mb-1">Y un párrafo por endpoint en <code>HALLAZGOS.md</code> que explique
                                    <strong> las consultas que obtuvieron ustedes</strong>: por qué ese número, por qué cambia
                                    o no entre 10 y 2000. Se califica la coherencia entre la estrategia, la que quedó en el
                                    código y la explicación de los números.</p>
                            </div>
                        )
                    },
                    {
                        titulo: 'Parte D · Auditoría de los tests propuestos por la IA',
                        contenido: (
                            <div>
                                <p className="mb-3">En el repositorio hay un archivo <code>ia_tests_propuesta.py</code>: una
                                    batería de tests generada por un asistente para este mismo servicio. Se ejecuta con
                                    <code> pytest ia_tests_propuesta.py</code> y <strong>está en verde</strong>. Tiene tres
                                    defectos: tests que no pueden fallar, tests que no prueban lo que dicen probar y tests
                                    que unas veces pasan y otras no.</p>
                                <p className="mb-3">Entregan <code>DICTAMEN_IA.md</code> con cuatro secciones por defecto —qué
                                    está mal, por qué (citando módulo y sección), cómo lo comprobaron, y la corrección— más
                                    <code> tests/test_ia_corregido.py</code>, que debe pasar sobre su servicio.</p>
                                <Box type="tip" label="La comprobación tiene una forma concreta: una mutación">
                                    Introduzcan a propósito un defecto en el servicio —un 404 que deja de devolverse, un
                                    <code> commit</code> que se quita, un validador que acepta lo que no debe—, muestren que el
                                    test original sigue en verde y que el corregido se pone en rojo, y vuelvan a dejar el
                                    servicio como estaba. El calificador hace lo mismo con tres mutaciones que ustedes no ven:
                                    sus tests corregidos deben pasar sobre el código sano y fallar con cada mutación.
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
                                    última va lo que se califica: qué les propuso la IA que no aceptaron, y por qué.</p>
                                <p className="mb-3">Sustentación de <strong>12 minutos</strong> (grupos de una persona: 9),
                                    repartida por sorteo entre dos sesiones; el repositorio se congela para todos el mismo día.</p>
                                <Pipeline steps={[
                                    { num: 1, title: '4 min · demo en vivo, en Docker', desc: 'docker build, docker run -p, curl /health, un POST /polizas que devuelve 201; después GET /polizas dos veces: tras docker restart y tras borrar el contenedor y levantar otro desde la misma imagen. Lo que pase con los datos en cada caso, tienen que poder explicarlo. Sin diapositivas' },
                                    { num: 2, title: '8 min · preguntas dirigidas', desc: 'A un integrante concreto, sobre una línea concreta de SU repositorio, al menos una por integrante. Todos deben poder responder por todo' },
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
                        ['El repositorio no arranca siguiendo su propio README, ni con uvicorn ni con docker run', <strong className="text-red-700">tope de 60</strong>],
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
                        ['El servicio corregido', 'arranca siguiendo su propio README, con uvicorn y con docker run'],
                        ['EQUIPO.md', 'integrantes e identidades git'],
                        ['HALLAZGOS.md', 'tabla de la Parte A + sección «Parte C»'],
                        ['CONSULTAS.csv', '4 endpoints × 2 tamaños = 8 filas'],
                        ['contar_consultas.py', 'con las modificaciones que hayan necesitado'],
                        ['DICTAMEN_IA.md', 'los tres defectos, cada uno con su mutación'],
                        ['tests/test_ia_corregido.py', 'la batería corregida, en verde sobre su servicio'],
                        ['BITACORA_IA.md', 'Prompts · Aceptado · Rechazado'],
                        ['alembic/ · Dockerfile · .dockerignore · .env.example', 'la infraestructura de las partes B5 y B9'],
                        ['requirements.txt', 'con versiones fijadas'],
                        ['README.md', 'actualizado con el arranque real, local y en contenedor'],
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
                    su repositorio: lo clona en el SHA congelado, crea un entorno limpio, instala sus dependencias,
                    aplica sus migraciones sobre una base vacía, corre una batería de tests que ustedes no ven, levanta
                    su servicio y le pega, construye y arranca su imagen de Docker, cuenta las consultas de la Parte C,
                    muta su servicio para ver si sus tests lo notan, analiza la estructura de su código y ejecuta los
                    comandos de evidencia que declararon sobre el commit que citaron. Los {MANUAL} restantes los lee el
                    docente.
                </p>
                <p className="text-gray-700 leading-relaxed mb-3">
                    Reciben un reporte con <strong>la nota de cada criterio y la evidencia que la sustenta</strong>: el
                    comando ejecutado y su salida literal. Es auditable: si creen que un check está mal, se revisa
                    contra esa evidencia.
                </p>
                <Box type="warn" label="Tres consecuencias prácticas">
                    <p className="mb-2"><strong>Los formatos son rígidos porque se parsean.</strong> Una tabla torcida
                    en <code>HALLAZGOS.md</code> no se «entiende igual»: se rechaza indicando la línea. Usen las plantillas.</p>
                    <p className="mb-2"><strong>La estructura también se comprueba.</strong> El servicio y los entregables
                    van en la raíz, y la historia desciende del semilla. <code>verificar_entrega.py</code> se lo dice antes
                    que el calificador.</p>
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
