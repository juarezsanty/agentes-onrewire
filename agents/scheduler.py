import json
import os
from datetime import datetime
from config import HORARIOS_PUBLICACION

ARCHIVO_PROGRAMADOS = "programados.json"

def cargar_programados() -> list:
    if not os.path.exists(ARCHIVO_PROGRAMADOS):
        return []
    with open(ARCHIVO_PROGRAMADOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_programados(posts: list) -> None:
    with open(ARCHIVO_PROGRAMADOS, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def programar_post(red: str, copy: str, contenido_completo: str = None) -> dict:
    posts = cargar_programados()
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    horarios_usados = [p["horario"] for p in posts if p["fecha"] == hoy and p["red"] == red]
    
    horario_elegido = None
    for horario in HORARIOS_PUBLICACION:
        if horario not in horarios_usados:
            horario_elegido = horario
            break
    
    if not horario_elegido:
        horario_elegido = HORARIOS_PUBLICACION[0]

    post = {
        "red": red,
        "copy": copy,
        "fecha": hoy,
        "horario": horario_elegido,
        "estado": "programado",
        "contenido_completo": contenido_completo
    }

    posts.append(post)
    guardar_programados(posts)
    
    print(f"📅 Post programado para {red} el {hoy} a las {horario_elegido}")
    return post

def ver_programados() -> None:
    posts = cargar_programados()
    if not posts:
        print("No hay posts programados")
        return
    for post in posts:
        print(f"\n📌 {post['red'].upper()} — {post['fecha']} {post['horario']}")
        print(f"   Estado: {post['estado']}")
        print(f"   Copy: {post['copy'][:80]}...")