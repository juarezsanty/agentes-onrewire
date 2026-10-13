from tools.gemini import generar_texto, analizar_video

def cargar_prompt(red: str, contenido: str) -> str:
    with open(f"prompts/copy_{red}.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt.replace("{contenido}", contenido)

def generar_copy(contenido: str, tipo: str = "noticia", video_path: str = None) -> dict:
    if tipo == "noticia":
        redes = ["instagram", "tiktok"]
    else:
        redes = ["instagram", "tiktok", "youtube"]

    copies = {}
    for red in redes:
        print(f"Generando copy para {red}...")
        if video_path and tipo == "clip":
            prompt = f"""
            Analizá este clip del podcast Onrewire sobre inteligencia artificial.
            Generá un copy para {red} basándote en el contenido real del video.
            
            Seguí estas reglas del prompt base:
            {open(f"prompts/copy_{red}.txt").read()}
            """
            copy = analizar_video(video_path, prompt)
        else:
            prompt = cargar_prompt(red, contenido)
            copy = generar_texto(prompt)
        copies[red] = copy
    return copies