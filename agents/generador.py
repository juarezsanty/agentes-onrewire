from tools.gemini import generar_texto

def cargar_prompt(red: str, contenido: str) -> str:
    with open(f"prompts/copy_{red}.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt.replace("{contenido}", contenido)

def generar_copy(contenido: str, tipo: str = "noticia") -> dict:
    if tipo == "noticia":
        redes = ["instagram", "tiktok"]
    else:
        redes = ["instagram", "tiktok", "youtube"]

    copies = {}
    for red in redes:
        print(f"Generando copy para {red}...")
        prompt = cargar_prompt(red, contenido)
        copy = generar_texto(prompt)
        copies[red] = copy
    return copies