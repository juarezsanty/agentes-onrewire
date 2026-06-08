import asyncio
import time
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generar_texto(prompt: str, reintentos: int = 5) -> str:
    for intento in range(reintentos):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                espera = (intento + 1) * 15
                print(f"⏳ Gemini saturado, esperando {espera} segundos...")
                time.sleep(espera)
            else:
                print(f"Error al generar texto: {e}")
                return None
    print("❌ Gemini no respondió después de varios intentos")
    return None

async def generar_texto_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generar_texto, prompt)