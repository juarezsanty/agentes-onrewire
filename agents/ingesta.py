import feedparser
import json
import os
from tools.gemini import generar_texto

FEEDS_IA = [
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://mitsloan.mit.edu/ideas-made-to-matter/rss.xml",
]

ARCHIVO_NOTICIAS = "noticias_procesadas.json"

def cargar_noticias_procesadas() -> list:
    if not os.path.exists(ARCHIVO_NOTICIAS):
        return []
    with open(ARCHIVO_NOTICIAS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_noticia_procesada(link: str) -> None:
    procesadas = cargar_noticias_procesadas()
    procesadas.append(link)
    with open(ARCHIVO_NOTICIAS, "w", encoding="utf-8") as f:
        json.dump(procesadas, f, ensure_ascii=False, indent=2)

def obtener_noticias(max_noticias: int = 5) -> list:
    procesadas = cargar_noticias_procesadas()
    noticias = []
    
    for feed_url in FEEDS_IA:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link in procesadas:
                continue
            noticias.append({
                "titulo": entry.title,
                "resumen": entry.get("summary", ""),
                "link": entry.link,
                "fuente": feed.feed.get("title", "")
            })
            if len(noticias) >= max_noticias:
                return noticias
    return noticias

def resumir_noticia(noticia: dict) -> str:
    prompt = f"""
    Resumí esta noticia sobre IA en 3 líneas en español, 
    de forma clara y directa:
    
    Título: {noticia['titulo']}
    Resumen original: {noticia['resumen']}
    """
    resultado = generar_texto(prompt)
    if resultado:
        guardar_noticia_procesada(noticia["link"])
    return resultado