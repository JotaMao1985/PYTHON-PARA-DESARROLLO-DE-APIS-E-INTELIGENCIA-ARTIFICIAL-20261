from google import genai
from google.genai import errors
import os
import re
import sys
import time

from dotenv import load_dotenv
load_dotenv()

INSTRUCCION = (
    "Eres un profesor de Python para estudiantes "
    "de estadística en la Universidad Santo Tomás. "
    "Genera SOLO código Python puro, sin markdown."
)

class ErrorDeGeneracion(RuntimeError):
    """La generación falló.

    Se LANZA en vez de devolver el texto del error como si fuera código: quien
    llama no puede confundir un fallo con una clase generada.
    """

class GeneradorClases:
    """
    Genera clases Python usando la API de Google Gemini.
    Encapsula la configuración, el prompt y la comunicación con la IA.
    """

    # Sólo se reintenta lo que puede salir distinto la segunda vez: la cuota
    # (429) y una caída del servidor (5xx). Una clave inválida o un modelo que
    # no existe van a fallar igual las tres veces, y reintentarlos sólo hace
    # esperar al estudiante siete segundos antes de leer el error.
    REINTENTABLES = (429, 500, 502, 503, 504)

    def __init__(self, modelo="gemini-3.6-flash", intentos_max=3):
        # Leer la API Key de variable de entorno (seguro)
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "No se encontró GEMINI_API_KEY. "
                "Configúrala con: export GEMINI_API_KEY='tu_clave'"
            )

        # El cliente es el objeto que habla con Google. Se crea UNA sola vez y
        # queda como atributo para reutilizarlo en cada llamada.
        self.cliente = genai.Client(api_key=api_key)

        # A diferencia de la librería antigua, el modelo NO se fija al construir:
        # se elige en cada petición. Por eso se guarda como atributo y no como
        # parte del cliente —cambiar de modelo no obliga a rehacer la conexión—.
        self.modelo = modelo
        self.intentos_max = intentos_max

    def generar(self, concepto):
        """Genera una clase Python para el concepto dado."""
        prompt = f"""Genera una clase Python para: "{concepto}".
Incluye:
- Docstring descriptivo
- Constructor __init__ con al menos 3 atributos
- Al menos 2 métodos útiles con docstrings
- Comentarios en español
- Ejemplo de uso al final"""

        # Reintentos con backoff exponencial, sólo para lo reintentable
        for intento in range(self.intentos_max):
            try:
                interaccion = self.cliente.interactions.create(
                    model=self.modelo,
                    system_instruction=INSTRUCCION,
                    input=prompt,
                    # El modelo razona antes de responder. Para una clase de
                    # veinte líneas "low" sobra, y ahorra segundos y tokens.
                    generation_config={"thinking_level": "low"},
                )
            except errors.APIError as e:
                codigo_http = getattr(e, "code", None)
                if codigo_http in self.REINTENTABLES and intento < self.intentos_max - 1:
                    espera = 2 ** intento  # 1s, 2s, 4s
                    print(f"Gemini devolvió {codigo_http}; reintento en {espera}s...")
                    time.sleep(espera)
                    continue
                raise ErrorDeGeneracion(self._explicar(codigo_http, e)) from e

            # Un 200 no garantiza texto. Si el filtro de contenido bloqueó la
            # petición, la respuesta llega sin salida; eso NO es un éxito, y
            # devolverlo como cadena vacía deja al estudiante sin saber qué pasó.
            codigo = (interaccion.output_text or "").strip()
            if not codigo:
                raise ErrorDeGeneracion(
                    f"Gemini respondió sin código (estado: {interaccion.status}). "
                    "Suele ser el filtro de contenido: prueba con otro concepto."
                )
            return self._sin_vallas(codigo)

        raise ErrorDeGeneracion(
            f"Sin respuesta de Gemini tras {self.intentos_max} intentos."
        )

    @staticmethod
    def _sin_vallas(texto):
        """Quita las vallas markdown si el modelo las puso igual.

        Se le pidió código puro, pero a veces lo envuelve. Se busca el primer
        bloque cercado en cualquier posición, no sólo al principio del texto.
        """
        cercado = re.search(r'\x60{3}[a-zA-Z]*\n(.*?)\x60{3}', texto, re.S)
        return cercado.group(1).strip() if cercado else texto

    @staticmethod
    def _explicar(codigo_http, error):
        """Traduce el error de la API a algo que el estudiante pueda accionar.

        El mensaje que manda Google está en inglés y habla de `projects` y
        `credentials`; lo único que sirve es qué hacer a continuación.
        """
        if codigo_http == 400:
            return ("La API Key no es válida. Revisa que la copiaste completa "
                    "desde aistudio.google.com/apikey.")
        if codigo_http == 403:
            return "La API Key no tiene permiso para usar la API de Gemini."
        if codigo_http == 404:
            return ("Ese modelo ya no está disponible. Los modelos se retiran: "
                    "consulta ai.google.dev/gemini-api/docs/models.")
        if codigo_http == 429:
            return "Cuota excedida. Espera ~30 s y reintenta."
        return f"Error de la API de Gemini: {error}"

# --- Uso del generador ---
if __name__ == "__main__":
    concepto = input("¿Qué clase quieres generar? ")

    # El aviso de progreso va por stderr, no por stdout. Por stdout sale SÓLO
    # la clase generada, y así se puede encadenar sin que el archivo resultante
    # se llene de mensajes:
    #     python Constructor_Clases_IA.py > Cuenta.py
    print(f"\nGenerando clase para '{concepto}'...\n", file=sys.stderr)

    try:
        print(GeneradorClases().generar(concepto))
    except (ValueError, ErrorDeGeneracion) as e:
        # El fallo también sale por stderr, y con código de salida 1. Así el
        # estudiante —y cualquier script que llame a éste— distingue un error
        # de una clase.
        sys.exit(f"ERROR: {e}")
