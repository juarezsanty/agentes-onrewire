import msal
import requests
import os
from config import MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID

GRAPH_URL = "https://graph.microsoft.com/v1.0"

def obtener_token() -> str:
    app = msal.PublicClientApplication(
        client_id=MICROSOFT_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}"
    )
    
    # intenta obtener token desde cache
    cuentas = app.get_accounts()
    if cuentas:
        result = app.acquire_token_silent(
            scopes=["https://graph.microsoft.com/Files.Read.All"],
            account=cuentas[0]
        )
        if result and "access_token" in result:
            return result["access_token"]
    
    # si no hay cache abre el navegador para login
    result = app.acquire_token_interactive(
        scopes=["https://graph.microsoft.com/Files.Read.All"],
    )
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"❌ Error al obtener token: {result.get('error_description')}")
        return None

def obtener_carpeta_reciente() -> dict:
    token = obtener_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    
    # busca la carpeta onrewireclips
    response = requests.get(
        f"{GRAPH_URL}/me/drive/root:/onrewireclips:/children",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error al obtener carpetas: {response.status_code} - {response.text}")
        return None

    carpetas = response.json().get("value", [])
    carpetas = [c for c in carpetas if c.get("folder")]
    
    if not carpetas:
        print("❌ No se encontraron carpetas")
        return None

    # devuelve la carpeta más reciente
    carpeta_reciente = max(carpetas, key=lambda x: x["lastModifiedDateTime"])
    print(f"📁 Carpeta más reciente: {carpeta_reciente['name']}")
    return carpeta_reciente

def obtener_clips(carpeta_id: str) -> list:
    token = obtener_token()
    if not token:
        return []

    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{GRAPH_URL}/me/drive/items/{carpeta_id}/children",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error al obtener clips: {response.status_code}")
        return []

    archivos = response.json().get("value", [])
    clips = [a for a in archivos if a.get("file") and 
             a["name"].endswith((".mp4", ".mov", ".avi"))]
    
    print(f"✅ {len(clips)} clips encontrados")
    return clips

def cargar_procesados() -> list:
    if not os.path.exists("procesados.json"):
        return []
    import json
    with open("procesados.json", "r") as f:
        return json.load(f)

def guardar_procesado(clip_id: str) -> None:
    import json
    procesados = cargar_procesados()
    procesados.append(clip_id)
    with open("procesados.json", "w") as f:
        json.dump(procesados, f)