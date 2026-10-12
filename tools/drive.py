import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_FILE = "credentials_drive.json"
TOKEN_FILE = "token_drive.json"

def obtener_servicio():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"\nAbrí esta URL en el navegador:\n{auth_url}\n")
            code = input("Pegá el código de autorización acá: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    
    return build("drive", "v3", credentials=creds)

def obtener_carpeta_reciente() -> dict:
    try:
        service = obtener_servicio()
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            orderBy="modifiedTime desc",
            pageSize=1,
            fields="files(id, name, modifiedTime)"
        ).execute()
        
        carpetas = results.get("files", [])
        if not carpetas:
            print("❌ No se encontraron carpetas")
            return None
        
        carpeta = carpetas[0]
        print(f"📁 Carpeta más reciente: {carpeta['name']}")
        return carpeta
    except Exception as e:
        print(f"❌ Error al obtener carpetas: {e}")
        return None

def obtener_clips(carpeta_id: str) -> list:
    try:
        service = obtener_servicio()
        results = service.files().list(
            q=f"'{carpeta_id}' in parents and (mimeType='video/mp4' or mimeType='video/quicktime' or mimeType='video/x-msvideo')",
            fields="files(id, name, mimeType)"
        ).execute()
        
        clips = results.get("files", [])
        print(f"✅ {len(clips)} clips encontrados")
        return clips
    except Exception as e:
        print(f"❌ Error al obtener clips: {e}")
        return []

def cargar_procesados() -> list:
    if not os.path.exists("procesados.json"):
        return []
    with open("procesados.json", "r") as f:
        return json.load(f)

def guardar_procesado(clip_id: str) -> None:
    procesados = cargar_procesados()
    procesados.append(clip_id)
    with open("procesados.json", "w") as f:
        json.dump(procesados, f)