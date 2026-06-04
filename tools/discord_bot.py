import discord
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

async def enviar_notificacion(mensaje: str):
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(mensaje)
    else:
        print("No se encontró el canal")

def iniciar_bot():
    client.run(DISCORD_BOT_TOKEN)