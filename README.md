# Onrewire Agent 🤖

Sistema agéntico para automatizar la gestión de redes sociales del podcast Onrewire.

## ¿Qué hace?

- Detecta clips nuevos en Google Drive y los procesa automáticamente
- Busca noticias sobre inteligencia artificial
- Genera copy adaptado para Instagram, TikTok y YouTube
- Genera imágenes de portada
- Notifica al community manager por Discord para aprobar, rechazar o pedir cambios
- Programa y publica automáticamente el contenido aprobado

## Stack

- Python 3.x
- LangGraph — orquestación de agentes
- Gemini 1.5 Flash — generación de texto
- Discord.py — notificaciones y aprobaciones
- Google Drive API — ingesta de clips

## Instalación

1. Cloná el repositorio
2. Creá el entorno virtual
```bash
    python -m venv venv
    source venv/Scripts/activate  # Windows
    source venv/bin/activate      # Mac/Linux
```
3. Instalá las dependencias
```bash
    pip install -r requirements.txt
```
4. Copiá el archivo de ejemplo y completá las claves
```bash
    cp .env.example .env
```

## Configuración

Completá el archivo `.env` con tus claves:

| Variable | Descripción |
|---|---|
| `GEMINI_API_KEY` | API key de Google AI Studio |
| `DISCORD_BOT_TOKEN` | Token del bot de Discord |
| `DISCORD_CHANNEL_ID` | ID del canal de aprobaciones |
| `GOOGLE_DRIVE_FOLDER_ID` | ID de la carpeta de clips en Drive |

## Estructura del proyecto