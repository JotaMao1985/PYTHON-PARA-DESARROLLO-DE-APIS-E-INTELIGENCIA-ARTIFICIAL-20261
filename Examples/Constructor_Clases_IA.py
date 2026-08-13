from google import genai
from google.genai import types
import os
import re
import time
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()  

class GeneradorClases:
    """
    Genera clases Python usando la API de Google Gemini.
    Encapsula la configuración, el prompt y la comunicación con la IA.
    """

    def __init__(self, modelo="gemini-2.5-flash"):
        # Leer la API Key de variable de entorno (seguro)
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "No se encontró GEMINI_API_KEY. "
                "Configúrala con: export GEMINI_API_KEY='tu_clave'"
            )

        # El cliente es el objeto que habla con Google. Se crea una sola vez
        # y queda guardado como atributo para reutilizarlo en cada llamada.
        self.client = genai.Client(api_key=api_key)

        # A diferencia de la librería antigua, el modelo NO se fija al
        # construir: se elige en cada petición. Lo guardamos como atributo.
        self.modelo = modelo

        # La instrucción de sistema viaja en la configuración de la petición.
        self.config = types.GenerateContentConfig(
            system_instruction=(
                "Eres un profesor de Python para estudiantes "
                "de estadística en la Universidad Santo Tomás. "
                "Genera SOLO código Python puro, sin markdown."
            )
        )
        self.intentos_max = 3

    def generar(self, concepto):
        """Genera una clase Python para el concepto dado."""
        prompt = f"""Genera una clase Python para: "{concepto}".
Incluye:
- Docstring descriptivo
- Constructor __init__ con al menos 3 atributos
- Al menos 2 métodos útiles con docstrings
- Comentarios en español
- Ejemplo de uso al final"""

        # Reintentos con backoff exponencial
        for intento in range(self.intentos_max):
            try:
                respuesta = self.client.models.generate_content(
                    model=self.modelo,
                    contents=prompt,
                    config=self.config,
                )
                codigo = respuesta.text

                # Limpiar posibles bloques markdown
                codigo = re.sub(
                    r'^\x60\x60\x60python\n?', '', codigo
                )
                codigo = re.sub(r'\n?\x60\x60\x60$', '', codigo)
                return codigo.strip()

            except Exception as e:
                print(f"Intento {intento + 1} falló: {e}")
                if intento < self.intentos_max - 1:
                    espera = 2 ** intento  # 1s, 2s, 4s
                    print(f"Reintentando en {espera}s...")
                    time.sleep(espera)
                else:
                    return f"Error después de {self.intentos_max} intentos: {e}"

# --- Uso del generador ---
if __name__ == "__main__":
    generador = GeneradorClases()

    concepto = input("¿Qué clase quieres generar? ")
    print(f"\nGenerando clase para '{concepto}'...\n")

    resultado = generador.generar(concepto)
    print(resultado)