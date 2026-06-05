import os
import base64
from datetime import datetime
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

CARPETA_IMAGENES = "imagenes"

def crear_carpeta():
    if not os.path.exists(CARPETA_IMAGENES):
        os.makedirs(CARPETA_IMAGENES)

def generar_imagen(descripcion: str, nombre: str = None) -> str:
    crear_carpeta()

    prompt = f"futuristic AI technology digital art, {descripcion}, dark background, neon blue and purple colors, high quality, professional podcast cover"

    if not nombre:
        nombre = datetime.now().strftime("%Y%m%d_%H%M%S")

    ruta = f"{CARPETA_IMAGENES}/{nombre}.png"

    try:
        print(f"🎨 Generando imagen...")
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_images(
            model="imagen-4.0-fast-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        imagen = response.generated_images[0]
        with open(ruta, "wb") as f:
            f.write(imagen.image.image_bytes)
        print(f"✅ Imagen guardada en {ruta}")
        return ruta
    except Exception as e:
        print(f"❌ Error: {e}")
        return None