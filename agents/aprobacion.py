import asyncio
import discord
from tools.discord_bot import client, enviar_borrador
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

resultados = {}

async def esperar_decision(red: str, copy: str) -> dict:
    future = asyncio.get_event_loop().create_future()
    resultados[red] = future
    await enviar_borrador(red=red, copy=copy, future=future)
    decision = await future
    return decision

def iniciar_aprobacion(red: str, copy: str) -> dict:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(esperar_decision(red, copy))