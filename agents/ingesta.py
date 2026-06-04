import feedparser
from tools.gemini import generar_texto

FEEDS_IA = [
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://mitsloan.mit.edu/ideas-made-to-matter/rss.xml",
]

def obtener_noticias(max_noticias: int = 5) -> list:
    noticias = []
    for feed_url in FEEDS_IA:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:2]:
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
    return generar_texto(prompt)