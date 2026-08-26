from dotenv import load_dotenv
import os

load_dotenv()

# LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Discord
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Publicación
POSTS_POR_DIA = 3
HORARIOS_PUBLICACION = ["09:00", "14:00", "19:00"]

# Redes activas
REDES = ["instagram", "tiktok", "youtube"]

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")

DISCORD_NOTICIAS_CHANNEL_ID = int(os.getenv("DISCORD_NOTICIAS_CHANNEL_ID", "0"))