/* Lección 4 — «La aplicación: qué es y cómo se levanta».
 *
 * No sale de `heredado/5_…html` ni de ningún conversor: es una lección nueva,
 * escrita entera a mano, y por eso vive aquí. La receta la declara en
 * `secciones` con `"propia": true`, y `montar.py` sólo le pone su fila del
 * `curriculum` — el componente lo estampa desde este archivo.
 *
 * Los dos ejercicios —`OrdenaPasos` y `DetectaError`— son de LP-CORE, los
 * trae `lp-base.html`, y no hay que traerlos aquí.
 */

const ArrancarSection = () => (
    <div className="prose-lp">
        <section className="usta-card p-6 md:p-8 mb-8">
            <h3 className="text-xl md:text-2xl font-semibold mb-4 text-secondary mt-2">2.1 La aplicación: el objeto que el servidor busca</h3>

            <p className="text-gray-700 leading-relaxed mb-5">Hace un momento, en la sección 1.2, escribimos la aplicación WSGI más simple del mundo: una función llamada <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">app</code> que recibía la petición y devolvía bytes. Y dijimos que nadie escribe eso a mano. Lo que no dijimos es <strong>qué ocupa su lugar</strong>, y la respuesta son las tres líneas con las que empieza cualquier servicio de este curso:</p>

            <CodeBlock title="main.py" lang="python" code={`from fastapi import FastAPI

app = FastAPI()`} />

            <p className="text-gray-700 leading-relaxed mb-5">Ese <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">app</code> es <strong>la misma pieza</strong> que la función de la sección 1.2, y por eso se llama igual. No es un archivo, no es un proceso y no es el servidor: es un objeto de Python que vive dentro de tu módulo y que cumple el papel de <em>aplicación</em>. La diferencia es que ya no lo escribes tú —lo construye el framework— y que habla ASGI en vez de WSGI.</p>

            <Box type="tip" label="Tres cosas que conviene fijar ahora">
                <ol className="list-decimal ml-5 space-y-2 mb-0">
                    <li><strong>Es un objeto, y se crea una sola vez.</strong> Al importar el módulo se ejecuta <code className="font-mono text-xs">FastAPI()</code> y nace la aplicación. Todo lo demás le va añadiendo cosas encima.</li>
                    <li><strong>El decorador no ejecuta nada.</strong> Cuando escribes <code className="font-mono text-xs">@app.get("/health")</code> no estás atendiendo una petición: estás <em>registrando</em> esa función en la tabla de rutas del objeto. Con tres decoradores no has respondido a nadie; has rellenado un directorio.</li>
                    <li><strong>Es lo que el servidor importa.</strong> Uvicorn no ejecuta tu archivo como un guion: lo importa como módulo y busca dentro esa variable. Si no la encuentra, no arranca.</li>
                </ol>
            </Box>

            <p className="text-gray-700 leading-relaxed mb-5">La tercera tiene una consecuencia que sorprende a todo el mundo el primer día, y conviene verla antes de tropezar con ella:</p>

            <Box type="warn" label="El tropiezo del primer día">
                <p className="mb-0">Ejecutar <code className="font-mono text-xs">python main.py</code> es el reflejo que traes de los cuatro módulos anteriores, y aquí <strong>no levanta ningún servidor</strong>. Python importa el archivo, crea el objeto, registra las rutas… y termina. No hay error y no hay salida: la terminal devuelve el <em>prompt</em> y parece que no ha pasado nada. Ha pasado casi todo; falta lo único que hace de esto un servicio, que es alguien escuchando en un puerto. Ese alguien es <strong>uvicorn</strong>, y es el asunto de la sección siguiente.</p>
            </Box>

            <Pipeline steps={[
                { num: 1, title: 'main.py', desc: 'El archivo que escribes' },
                { num: 2, title: 'app', desc: 'El objeto FastAPI, con sus rutas ya registradas' },
                { num: 3, title: 'uvicorn', desc: 'Lo importa y se queda escuchando' },
                { num: 4, title: ':8000', desc: 'Cualquier cliente puede ya pedirle algo' },
            ]} />

            <h3 className="text-xl md:text-2xl font-semibold mb-4 text-secondary mt-8">2.2 De archivo a servicio: el comando</h3>

            <p className="text-gray-700 leading-relaxed mb-5">Vamos a levantarlo de verdad. Guarda esto en un archivo llamado <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">main.py</code>, en una carpeta cualquiera, con el entorno virtual de los prerrequisitos activado:</p>

            <CodeBlock title="main.py" lang="python" code={`from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def raiz():
    return {"servicio": "estadisticas", "estado": "vivo"}


@app.get("/health")
def health_check():
    return {"status": "ok"}`} plegable={false} />

            <p className="text-gray-700 leading-relaxed mb-5">Eso es todo: dos rutas. La segunda, <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">/health</code>, no es decorativa: es la que usan los sistemas de monitoreo para preguntar «¿sigues vivo?», y volverá a aparecer en las buenas prácticas de este módulo y en el despliegue de la semana 12. Y sí, pone <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">def</code> y no <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">async def</code>: estas dos funciones no esperan a nada, así que no hay nada que asincronizar. Por qué eso importa es justamente la sección 5.</p>

            <p className="text-gray-700 leading-relaxed mb-5">Ahora, desde la terminal y <strong>en esa misma carpeta</strong>:</p>

            <CodeBlock title="Terminal" lang="shell" code={`uvicorn main:app --reload`} />

            <p className="text-gray-700 leading-relaxed mb-5">Cinco fragmentos, y cada uno responde a una pregunta distinta. Vale la pena leerlos de uno en uno, porque los tres errores más frecuentes del primer arranque son errores de esta línea:</p>

            <table className="min-w-full divide-y divide-gray-200 my-8 shadow-sm border border-gray-200 rounded-lg overflow-hidden block md:table overflow-x-auto">
                <thead className="bg-gray-100">
                    <tr>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Fragmento</th>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Qué es</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>uvicorn</code></td><td className="px-6 py-4 text-sm text-gray-800">El servidor ASGI. Es un programa aparte, no una función de tu código: lo instalaste con <code>pip</code> y ahora lo invocas por su nombre.</td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>main</code></td><td className="px-6 py-4 text-sm text-gray-800">El <strong>módulo</strong> donde vive la aplicación: el archivo <code>main.py</code>, escrito sin la extensión, tal como lo escribirías en un <code>import</code>.</td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>:</code></td><td className="px-6 py-4 text-sm text-gray-800">Separa <em>dónde</em> vive el objeto de <em>cómo se llama</em>. A la izquierda, el módulo; a la derecha, la variable.</td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>app</code></td><td className="px-6 py-4 text-sm text-gray-800">El nombre exacto de la variable dentro de ese módulo. Si en tu archivo pusiste <code>api = FastAPI()</code>, aquí va <code>api</code>. Coincide letra por letra o no arranca.</td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>--reload</code></td><td className="px-6 py-4 text-sm text-gray-800">Vigila los archivos y reinicia solo al guardar. Comodísimo mientras escribes, prohibido en producción, por lo que vimos en 1.3.</td></tr>
                </tbody>
            </table>

            <p className="text-gray-700 leading-relaxed mb-5">Fíjate en que el comando <strong>no nombra un archivo, nombra un módulo</strong>. Es una distinción que parece pedante hasta que el código deja de ser un archivo suelto y pasa a vivir dentro de un paquete, que es exactamente lo que ocurre en el proyecto integrador:</p>

            <CodeBlock title="Terminal" lang="shell" code={`# Un archivo suelto: main.py en la carpeta actual.
# Es lo que usa la semilla del taller del corte I.
uvicorn main:app --reload

# El MISMO objeto, cuando el codigo vive en un paquete: app/main.py
# Es lo que usa el proyecto integrador, y lo que ira en el
# Dockerfile de la semana 11.
uvicorn app.main:app --reload`} />

            <p className="text-gray-700 leading-relaxed mb-5">El punto separa la carpeta del archivo, igual que en cualquier <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">import</code>. Que el paquete se llame <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">app</code> y la variable también es una coincidencia desafortunada, universal en este ecosistema, y la causa de que <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">app.main:app</code> parezca un trabalenguas. No lo es: a la izquierda de los dos puntos está <strong>dónde</strong>; a la derecha, <strong>cómo se llama</strong>.</p>

            <h3 className="text-xl md:text-2xl font-semibold mb-4 text-secondary mt-8">2.3 Qué pasa al pulsar Enter</h3>

            <p className="text-gray-700 leading-relaxed mb-5">La terminal <strong>no</strong> te devuelve el <em>prompt</em>. Se queda ocupada, escupiendo esto y esperando:</p>

            <CodeBlock title="Salida de uvicorn" lang="text" code={`INFO:     Will watch for changes in these directories: ['/Users/tu/proyecto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [41283] using StatReload
INFO:     Started server process [41285]
INFO:     Waiting for application startup.
INFO:     Application startup complete.`} />

            <p className="text-gray-700 leading-relaxed mb-5">Que la terminal quede ocupada <strong>es la señal de que funciona</strong>. Alguna línea puede cambiar según la versión —el vigilante de archivos se anuncia como <code className="font-mono text-xs">StatReload</code> o como <code className="font-mono text-xs">WatchFiles</code> según lo que tengas instalado—, pero la que importa es siempre la segunda: <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">127.0.0.1</code> es tu propia máquina —nadie más de la red puede entrar todavía— y <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">8000</code> es el puerto donde escucha. Con eso ya tienes tres direcciones que abrir en el navegador:</p>

            <table className="min-w-full divide-y divide-gray-200 my-8 shadow-sm border border-gray-200 rounded-lg overflow-hidden block md:table overflow-x-auto">
                <thead className="bg-gray-100">
                    <tr>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Dirección</th>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Qué verás</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>http://127.0.0.1:8000/</code></td><td className="px-6 py-4 text-sm text-gray-800"><code>&#123;"servicio":"estadisticas","estado":"vivo"&#125;</code> — el diccionario que devuelve <code>raiz()</code>, convertido a JSON sin que tú hicieras nada.</td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>http://127.0.0.1:8000/health</code></td><td className="px-6 py-4 text-sm text-gray-800"><code>&#123;"status":"ok"&#125;</code></td></tr>
                    <tr><td className="px-6 py-4 text-sm text-gray-800"><code>http://127.0.0.1:8000/docs</code></td><td className="px-6 py-4 text-sm text-gray-800">Una página de documentación interactiva que <strong>tú no escribiste</strong>.</td></tr>
                </tbody>
            </table>

            <p className="text-gray-700 leading-relaxed mb-5">Y lo mismo desde la terminal, con el <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">curl</code> de la semana 2 —porque una API no se prueba sólo con el navegador—. Ojo: la primera terminal está ocupada por el servidor, así que esto va en una <strong>segunda</strong>:</p>

            <CodeBlock title="Terminal" lang="shell" code={`curl http://127.0.0.1:8000/health
# {"status":"ok"}`} />

            <p className="text-gray-700 leading-relaxed mb-5">La tercera dirección merece que te detengas. En <code className="bg-gray-100 text-pink-600 px-2 py-0.5 rounded font-mono text-sm border border-gray-200">/docs</code>, FastAPI ha montado una página con tus dos endpoints, sus respuestas y un botón «Try it out» que los ejecuta desde el navegador. No la generó adivinando: la leyó de tu código, y por eso está siempre al día. En cuanto los endpoints empiecen a recibir modelos de Pydantic —los de la semana 4—, esa misma página dirá qué campos exige cada uno, de qué tipo y con qué restricciones. Es el pago de haber escrito los tipos.</p>

            <Box type="info" label="Mientras el servidor corre">
                <p className="mb-0">Con <code className="font-mono text-xs">--reload</code> no hace falta parar y volver a arrancar: guardas el archivo, uvicorn lo detecta, reinicia solo y en la terminal aparece una línea nueva. Para detenerlo del todo, <strong>Ctrl + C</strong> en la terminal donde está corriendo.</p>
            </Box>

            <OrdenaPasos
                titulo="Ordene el primer arranque"
                enunciado={<>Ya tiene escrito el <code className="font-mono text-xs">main.py</code> de la sección 2.2, solo, en una carpeta vacía. Ordene lo que hay que hacer <strong>desde la terminal</strong> para verlo respondiendo y dejarlo parado al terminar.</>}
                lang="shell"
                pasos={[
                    'python3 -m venv venv',
                    'source venv/bin/activate',
                    'pip install fastapi uvicorn',
                    'uvicorn main:app --reload',
                    'curl http://127.0.0.1:8000/health',
                    'Ctrl + C para detener el servidor',
                ]}
                pista="Dos dependencias mandan sobre todo lo demás: nada se instala donde debe hasta que el entorno está activado, y nadie responde en el puerto 8000 hasta que hay alguien escuchando."
            />

            <h3 className="text-xl md:text-2xl font-semibold mb-4 text-secondary mt-8">2.4 Cuando no arranca</h3>

            <p className="text-gray-700 leading-relaxed mb-5">Cuatro mensajes cubren casi todo lo que falla el primer día. Los cuatro dicen exactamente lo que pasó; el problema es que lo dicen en un vocabulario que todavía no es el tuyo. Conviene reconocerlos de vista:</p>

            <table className="min-w-full divide-y divide-gray-200 my-8 shadow-sm border border-gray-200 rounded-lg overflow-hidden block md:table overflow-x-auto">
                <thead className="bg-gray-100">
                    <tr>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Lo que dice la terminal</th>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Qué pasó</th>
                        <th className="px-6 py-4 text-left text-xs font-extrabold text-gray-700 uppercase tracking-wider">Qué hacer</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                        <td className="px-6 py-4 text-sm text-gray-800"><code>Error loading ASGI app. Could not import module "main".</code></td>
                        <td className="px-6 py-4 text-sm text-gray-800">Uvicorn no encontró ningún módulo llamado <code>main</code>. Casi siempre la terminal está en otra carpeta.</td>
                        <td className="px-6 py-4 text-sm text-gray-800">Lista la carpeta con <code>ls</code> (o <code>dir</code> en Windows): tiene que aparecer <code>main.py</code>. Si no aparece, <code>cd</code> hasta donde esté.</td>
                    </tr>
                    <tr>
                        <td className="px-6 py-4 text-sm text-gray-800"><code>Error loading ASGI app. Attribute "app" not found in module "main".</code></td>
                        <td className="px-6 py-4 text-sm text-gray-800">El archivo se importó bien, pero dentro no hay ninguna variable que se llame <code>app</code>. Suele llamarse <code>api</code>, o el archivo está a medias.</td>
                        <td className="px-6 py-4 text-sm text-gray-800">Haz que coincidan las dos: o renombras la variable, o cambias lo que va a la derecha de los dos puntos.</td>
                    </tr>
                    <tr>
                        <td className="px-6 py-4 text-sm text-gray-800"><code>[Errno 48] Address already in use</code></td>
                        <td className="px-6 py-4 text-sm text-gray-800">El puerto 8000 ya está ocupado, casi siempre por otro uvicorn que quedó vivo en otra pestaña. El número del error cambia con el sistema: 48 en macOS, 98 en Linux, 10048 en Windows.</td>
                        <td className="px-6 py-4 text-sm text-gray-800">Busca la terminal anterior y para el servidor con <strong>Ctrl + C</strong>, o arranca en otro puerto: <code>uvicorn main:app --reload --port 8001</code>.</td>
                    </tr>
                    <tr>
                        <td className="px-6 py-4 text-sm text-gray-800"><code>ModuleNotFoundError: No module named 'fastapi'</code></td>
                        <td className="px-6 py-4 text-sm text-gray-800">Python arrancó, pero en un entorno donde FastAPI no está instalado. Casi siempre es el entorno virtual sin activar.</td>
                        <td className="px-6 py-4 text-sm text-gray-800">Actívalo y repite el <code>pip install</code> de los prerrequisitos. El <em>prompt</em> te lo dice: si no ves el nombre del entorno delante, no está activo.</td>
                    </tr>
                </tbody>
            </table>

            <Box type="danger" label="Y un quinto que no da ningún mensaje">
                <p className="mb-0">Ejecutar <code className="font-mono text-xs">python main.py</code>. No sale ningún error, no sale ninguna advertencia, y no hay servidor: es lo que vimos en 2.1. De ahí una regla que te va a servir todo el semestre —<strong>si la terminal te devuelve el <em>prompt</em>, no hay servidor; si se queda ocupada, sí lo hay</strong>.</p>
            </Box>

            <DetectaError
                titulo="Diagnostique por qué no arranca"
                enunciado={<>Este archivo se llama <code className="font-mono text-xs">main.py</code> y es Python perfectamente válido: no le falta ni un paréntesis. Aun así, al ejecutar el comando de la primera línea, uvicorn se niega a arrancar y responde <code className="font-mono text-xs">Error loading ASGI app. Attribute "app" not found in module "main"</code>. El comando <strong>no se puede cambiar</strong> —es el que exige el enunciado del taller—, así que la corrección va en el archivo. <strong>¿Qué línea hay que tocar?</strong></>}
                lang="python"
                lineas={[
                    '# Se levanta con:  uvicorn main:app --reload',
                    '',
                    'from fastapi import FastAPI',
                    '',
                    'api = FastAPI()',
                    '',
                    '',
                    '@api.get("/health")',
                    'def health_check():',
                    '    return {"status": "ok"}',
                ]}
                lineaCorrecta={5}
                tipos={[
                    'Error de sintaxis: al archivo le falta un delimitador o una palabra clave.',
                    'Error de nombre: el objeto de la aplicación no se llama como el comando espera.',
                    'Error de importación: FastAPI no está instalado en el entorno que está activo.',
                    'Error de ruta: el decorador registra un camino que nadie va a pedir.',
                ]}
                tipoCorrecto={1}
                explicacion={<>La línea 5 bautiza la aplicación como <code className="font-mono text-xs">api</code>, y lo que va a la derecha de los dos puntos en <code className="font-mono text-xs">main:app</code> no es una convención: es el nombre exacto de la variable que uvicorn va a buscar dentro del módulo. Fíjese en <em>cuál</em> de los dos mensajes salió, porque los dos de la tabla anterior dicen cosas distintas: <code className="font-mono text-xs">Could not import module "main"</code> significa que ni siquiera encontró el archivo; <code className="font-mono text-xs">Attribute "app" not found</code> significa que el archivo se importó bien —Python lo leyó entero, sin quejarse— y que lo que falta está dentro. La línea 8 es cómplice, pero no es la culpable: si renombra la variable, ese decorador hay que ajustarlo también.</>}
                impacto={<>Es el segundo tropiezo más común del primer día, y tiene <strong>dos arreglos igual de válidos</strong>: renombrar la variable a <code className="font-mono text-xs">app</code>, o escribir <code className="font-mono text-xs">uvicorn main:api --reload</code>. En este curso se arregla siempre por el lado de la variable, y no por gusto: la semilla del taller y el <code className="font-mono text-xs">Dockerfile</code> de la semana 11 dan por hecho que se llama <code className="font-mono text-xs">app</code>. Cuando el comando lo escribe otro —un Dockerfile, un servicio de despliegue, un compañero—, el que se adapta es su archivo.</>}
            />

        </section>
    </div>
);
