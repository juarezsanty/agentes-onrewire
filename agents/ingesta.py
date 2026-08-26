import feedparser
import json
import os
from tools.gemini import generar_texto
import time
import requests
from bs4 import BeautifulSoup
import html

FEEDS_IA = [
    # inglés - muy activos
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://syncedreview.com/feed/",
    "https://aiweekly.co/issues.rss",
    
    # español - para contenido más cercano a tu audiencia
    "https://www.xataka.com/tag/inteligencia-artificial/feed",
    "https://hipertextual.com/tag/inteligencia-artificial/feed",
    "https://www.genbeta.com/tag/inteligencia-artificial/feed",
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

def obtener_noticias(max_noticias: int = 1) -> list:
    procesadas = [n if isinstance(n, str) else n["link"] for n in cargar_noticias_procesadas()]
    hace_7_dias = time.time() - (7 * 24 * 60 * 60)
    candidatas = []

    # toma la más reciente de cada feed
    for feed_url in FEEDS_IA:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if entry.link in procesadas:
                    continue

                fecha_publicacion = entry.get("published_parsed")
                if fecha_publicacion:
                    fecha_timestamp = time.mktime(fecha_publicacion)
                    if fecha_timestamp < hace_7_dias:
                        continue

                candidatas.append({
                    "titulo": html.unescape(entry.title),
                    "resumen": html.unescape(entry.get("summary", "")),
                    "link": entry.link,
                    "fuente": feed.feed.get("title", ""),
                    "fecha": fecha_publicacion
                })
                break
        except Exception as e:
            print(f"⚠️ Error al leer feed {feed_url}: {e}")

    if not candidatas:
        return []

    # si solo hay una o menos de las pedidas, devuelve las que hay
    if len(candidatas) <= max_noticias:
        return candidatas

    # Gemini elige las más interesantes
    lista = "\n".join([f"{i+1}. {n['titulo']} ({n['fuente']})" for i, n in enumerate(candidatas)])
    prompt = f"""
    Sos el editor de un podcast argentino sobre inteligencia artificial llamado Onrewire.
    Tu audiencia es tech-savvy y habla español.
    
    De estas noticias recientes sobre IA, elegí las {max_noticias} más interesantes y relevantes 
    para tu audiencia. Respondé SOLO con los números separados por coma, sin texto extra.
    Por ejemplo: 2,5,1
    
    Noticias:
    {lista}
    """
    
    resultado = generar_texto(prompt)
    
    if not resultado:
        return candidatas[:max_noticias]
    
    try:
        indices = [int(x.strip()) - 1 for x in resultado.strip().split(",")]
        seleccionadas = [candidatas[i] for i in indices if 0 <= i < len(candidatas)]
        return seleccionadas[:max_noticias]
    except:
        return candidatas[:max_noticias]

def obtener_contenido_completo(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # si hay bloqueo de seguridad devuelve None
        if "security" in response.text.lower() or "javascript" in response.text.lower() or "checkpoint" in response.text.lower():
            print(f"⚠️ Sitio bloqueado por seguridad: {url}")
            return None
            
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        texto = soup.get_text(separator="\n", strip=True)
        return texto[:3000]
    except Exception as e:
        print(f"⚠️ No se pudo obtener contenido completo: {e}")
        return None

def resumir_noticia(noticia: dict) -> dict:
    contenido = obtener_contenido_completo(noticia["link"])
    
    base = contenido if contenido else noticia["resumen"]

    # resumen corto para el copy
    prompt_corto = f"""
    Resumí esta noticia sobre IA en 3 líneas en español para redes sociales:
    
    Título: {noticia['titulo']}
    Contenido: {base}
    """
    resumen_corto = generar_texto(prompt_corto)

    # resumen extendido para Discord
    prompt_extendido = f"""
    Hacé un resumen detallado en español de esta noticia sobre IA.
    Debe tener entre 150 y 250 palabras.
    Incluí los puntos más importantes, datos relevantes y contexto.
    No uses bullet points, escribí en párrafos.
    
    Título: {noticia['titulo']}
    Contenido: {base}
    """
    resumen_extendido = generar_texto(prompt_extendido)

    if resumen_corto:
        guardar_noticia_procesada(noticia["link"])

    return {
        "resumen": resumen_corto,
        "resumen_extendido": resumen_extendido,
        "contenido_completo": base,
        "titulo": noticia["titulo"],
        "link": noticia["link"]
    }