import asyncio
import discord
from tools.discord_bot import client, enviar_borrador
from agents.ingesta import obtener_noticias, resumir_noticia
from agents.generador import generar_copy
from agents.scheduler import programar_post
from config import DISCORD_BOT_TOKEN

async def procesar_noticia(noticia: dict) -> None:
    print(f"\n📰 Procesando: {noticia['titulo']}")
    
    # resumir la noticia
    resumen = resumir_noticia(noticia)
    print(f"✅ Resumen generado")
    
    # generar copy para cada red
    copies = generar_copy(resumen)
    print(f"✅ Copies generados")
    
    # mandar cada copy a Discord para aprobación
    for red, copy in copies.items():
        future = asyncio.get_event_loop().create_future()
        await enviar_borrador(red=red, copy=copy, future=future)
        
        decision = await future
        
        if decision["accion"] == "aprobar":
            programar_post(red=red, copy=copy)
            print(f"✅ Post de {red} programado")
            
        elif decision["accion"] == "rechazar":
            print(f"❌ Post de {red} rechazado")
            
        elif decision["accion"] == "cambios":
            print(f"✏️ Cambios solicitados para {red}: {decision['instrucciones']}")
            # regenerar con las instrucciones
            from tools.gemini import generar_texto
            nuevo_copy = generar_texto(f"{decision['instrucciones']}\n\nCopy original:\n{copy}")
            await enviar_borrador(red=red, copy=nuevo_copy, future=asyncio.get_event_loop().create_future())

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    
    # obtener noticias
    noticias = obtener_noticias(max_noticias=1)
    
    for noticia in noticias:
        await procesar_noticia(noticia)

def main():
    client.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()