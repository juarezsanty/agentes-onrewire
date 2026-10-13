import os
import requests
from config import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

BASE_URL = "https://open.tiktokapis.com/v2"

def obtener_auth_url() -> str:
    url = "https://www.tiktok.com/v2/auth/authorize/"
    params = {
        "client_key": TIKTOK_CLIENT_KEY,
        "scope": "user.info.basic,video.upload,video.publish",
        "response_type": "code",
        "redirect_uri": "https://github.com/juarezsanty/agentes-onrewire",
        "state": "onrewire"
    }
    req = requests.Request("GET", url, params=params).prepare()
    return req.url

def obtener_token(code: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/oauth/token/",
        data={
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://github.com/juarezsanty/agentes-onrewire"
        }
    )
    return response.json()

def publicar_video(access_token: str, video_path: str, descripcion: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # endpoint de borrador en lugar de publicación directa
    init_response = requests.post(
        f"{BASE_URL}/post/publish/inbox/video/init/",
        headers=headers,
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video_path),
                "chunk_size": os.path.getsize(video_path),
                "total_chunk_count": 1
            }
        }
    )
    
    if init_response.status_code != 200:
        print(f"❌ Error al inicializar upload: {init_response.text}")
        return None
    
    data = init_response.json().get("data", {})
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    
    if not upload_url:
        print(f"❌ No se obtuvo URL de upload: {init_response.text}")
        return None
    
    # sube el video
    with open(video_path, "rb") as f:
        video_data = f.read()
    
    upload_response = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_data)),
            "Content-Range": f"bytes 0-{len(video_data)-1}/{len(video_data)}"
        },
        data=video_data
    )
    
    if upload_response.status_code not in [200, 201]:
        print(f"❌ Error al subir video: {upload_response.text}")
        return None
    
    print(f"✅ Video subido como borrador, publish_id: {publish_id}")
    return {"publish_id": publish_id}