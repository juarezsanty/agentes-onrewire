from tools.gemini import generar_texto

def cargar_prompt(red: str, contenido: str) -> str:
    with open(f"prompts/copy_{red}.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt.replace("{contenido}", contenido)

def generar_copy(contenido: str) -> dict:
    copies = {}
    for red in ["instagram", "tiktok", "youtube"]:
        print(f"Generando copy para {red}...")
        prompt = cargar_prompt(red, contenido)
        copy = generar_texto(prompt)
        copies[red] = copy
    return copies