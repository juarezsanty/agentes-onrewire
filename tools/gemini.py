import asyncio
import time
from google import genai
from config import GEMINI_API_KEY
import time
import pathlib

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


def analizar_video(video_path: str, prompt: str) -> str:
    try:
        print(f"🎬 Subiendo video a Gemini...")
        video_file = client.files.upload(file=video_path)
        
        # espera a que el archivo esté activo
        print(f"⏳ Esperando que Gemini procese el video...")
        while video_file.state.name == "PROCESSING":
            time.sleep(3)
            video_file = client.files.get(name=video_file.name)
        
        if video_file.state.name != "ACTIVE":
            print(f"❌ El archivo no está activo: {video_file.state.name}")
            return None
        
        print(f"✅ Video listo, generando copy...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt]
        )
        
        # elimina el archivo de Gemini después de usarlo
        client.files.delete(name=video_file.name)
        
        return response.text
    except Exception as e:
        print(f"Error al analizar video: {e}")
        return None