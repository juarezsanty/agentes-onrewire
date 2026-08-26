import asyncio
import discord
from tools.discord_bot import client, enviar_borrador
from agents.ingesta import obtener_noticias, resumir_noticia
from agents.generador import generar_copy
from agents.scheduler import programar_post
from tools.gemini import generar_texto
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

MAX_REINTENTOS = 3

# ─── FLUJO DE APROBACION ───────────────────────────────────────

async def aprobar_post(red: str, copy: str, contenido_completo: str = None) -> None:
    intentos = 0
    copy_actual = copy

    while intentos < MAX_REINTENTOS:
        future = asyncio.get_event_loop().create_future()
        await enviar_borrador(red=red, copy=copy_actual, future=future)
        decision = await future

        if decision["accion"] == "aprobar":
            programar_post(red=red, copy=copy_actual, contenido_completo=contenido_completo)
            print(f"✅ Post de {red} programado")
            return

        elif decision["accion"] == "rechazar":
            print(f"❌ Post de {red} rechazado")
            return

        elif decision["accion"] == "cambios":
            intentos += 1
            instrucciones = decision["instrucciones"]
            print(f"✏️ Regenerando con cambios: {instrucciones}")
            prompt = f"""
            Tenés este copy para {red}:
            {copy_actual}
            
            El community manager pidió estos cambios:
            {instrucciones}
            
            Reescribí el copy aplicando los cambios pedidos.
            """
            loop = asyncio.get_event_loop()
            copy_actual = await loop.run_in_executor(None, generar_texto, prompt)
            if not copy_actual:
                copy_actual = copy

async def procesar_contenido(contenido: str, tipo: str = "noticia", contenido_completo: str = None) -> None:
    loop = asyncio.get_event_loop()
    copies = await loop.run_in_executor(None, generar_copy, contenido, tipo)
    for red, copy in copies.items():
        if not copy:
            print(f"⚠️ Copy vacío para {red}, salteando...")
            continue
        await aprobar_post(red=red, copy=copy, contenido_completo=contenido_completo)

# ─── MODOS ────────────────────────────────────────────────────

async def modo_noticias(cantidad: int) -> None:
    print(f"\n🔍 Buscando {cantidad} noticias...")
    loop = asyncio.get_event_loop()
    noticias = await loop.run_in_executor(None, obtener_noticias, cantidad)
    
    for noticia in noticias:
        print(f"\n📰 {noticia['titulo']}")
        resultado = await loop.run_in_executor(None, resumir_noticia, noticia)
        
        if not resultado or not resultado["resumen"]:
            continue

        # aprobacion del resumen
        resumen_actual = resultado["resumen_extendido"]
        resumen_aprobado = False
        
        while not resumen_aprobado:
            from tools.discord_bot import enviar_resumen_para_aprobar
            future = asyncio.get_event_loop().create_future()
            await enviar_resumen_para_aprobar(
                titulo=resultado["titulo"],
                resumen=resumen_actual,
                link=resultado["link"],
                future=future
            )
            decision = await future

            if decision["accion"] == "aprobar":
                # publica en el canal público
                from tools.discord_bot import enviar_resumen_noticia
                await enviar_resumen_noticia(
                    titulo=resultado["titulo"],
                    resumen=resumen_actual,
                    link=resultado["link"]
                )
                resumen_aprobado = True

            elif decision["accion"] == "rechazar":
                print(f"❌ Resumen rechazado")
                resumen_aprobado = True

            elif decision["accion"] == "cambios":
                instrucciones = decision["instrucciones"]
                prompt = f"""
                Tenés este resumen:
                {resumen_actual}
                
                El editor pidió estos cambios:
                {instrucciones}
                
                Reescribí el resumen aplicando los cambios.
                """
                resumen_actual = await loop.run_in_executor(None, generar_texto, prompt)

        # procesa copies para las redes
        await procesar_contenido(resultado["resumen"], "noticia", resultado["contenido_completo"])

async def modo_clips(cantidad: int) -> None:
    print(f"\n🎬 Buscando {cantidad} clips nuevos...")
    try:
        from tools.drive import obtener_carpeta_reciente, obtener_clips, cargar_procesados, guardar_procesado
        loop = asyncio.get_event_loop()
        carpeta = await loop.run_in_executor(None, obtener_carpeta_reciente)
        if not carpeta:
            print("❌ No se encontró carpeta de clips")
            return
        clips = await loop.run_in_executor(None, obtener_clips, carpeta["id"])
        procesados = cargar_procesados()
        clips_nuevos = [c for c in clips if c["id"] not in procesados][:cantidad]
        for clip in clips_nuevos:
            contenido = f"Clip del podcast Onrewire: {clip['name'].replace('.mp4', '').replace('_', ' ')}"
            await procesar_contenido(contenido, "clip")
            guardar_procesado(clip["id"])
    except Exception as e:
        print(f"❌ Error al procesar clips: {e}")

# ─── MENU PRINCIPAL ───────────────────────────────────────────

class MenuTipoView(discord.ui.View):
    def __init__(self, future):
        super().__init__(timeout=300)
        self.future = future

    @discord.ui.button(label="📰 Noticias", style=discord.ButtonStyle.primary)
    async def noticias(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Modo noticias seleccionado")
        self.future.set_result("noticias")
        self.stop()

    @discord.ui.button(label="🎬 Clips", style=discord.ButtonStyle.primary)
    async def clips(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Modo clips seleccionado")
        self.future.set_result("clips")
        self.stop()

    @discord.ui.button(label="📰 + 🎬 Ambos", style=discord.ButtonStyle.success)
    async def ambos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Modo combinado seleccionado")
        self.future.set_result("ambos")
        self.stop()

class MenuCantidadView(discord.ui.View):
    def __init__(self, future):
        super().__init__(timeout=300)
        self.future = future

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary)
    async def uno(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 1 publicación")
        self.future.set_result(1)
        self.stop()

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary)
    async def dos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 2 publicaciones")
        self.future.set_result(2)
        self.stop()

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary)
    async def tres(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 3 publicaciones")
        self.future.set_result(3)
        self.stop()

class MenuCombinado(discord.ui.View):
    def __init__(self, future):
        super().__init__(timeout=300)
        self.future = future

    @discord.ui.button(label="1 noticia + 1 clip", style=discord.ButtonStyle.secondary)
    async def uno_uno(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 1 noticia + 1 clip")
        self.future.set_result((1, 1))
        self.stop()

    @discord.ui.button(label="2 noticias + 1 clip", style=discord.ButtonStyle.secondary)
    async def dos_uno(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 2 noticias + 1 clip")
        self.future.set_result((2, 1))
        self.stop()

    @discord.ui.button(label="1 noticia + 2 clips", style=discord.ButtonStyle.secondary)
    async def uno_dos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 1 noticia + 2 clips")
        self.future.set_result((1, 2))
        self.stop()

async def menu_principal() -> None:
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("❌ No se encontró el canal")
        return

    future_tipo = asyncio.get_event_loop().create_future()
    embed = discord.Embed(
        title="📅 ¿Qué publicamos hoy?",
        color=0x5865F2
    )
    await channel.send(embed=embed, view=MenuTipoView(future_tipo))
    tipo = await future_tipo

    if tipo == "ambos":
        future_combinado = asyncio.get_event_loop().create_future()
        await channel.send("¿Cuántos de cada uno?", view=MenuCombinado(future_combinado))
        noticias_cant, clips_cant = await future_combinado
        await modo_noticias(noticias_cant)
        await modo_clips(clips_cant)
    else:
        future_cantidad = asyncio.get_event_loop().create_future()
        await channel.send("¿Cuántas publicaciones hoy?", view=MenuCantidadView(future_cantidad))
        cantidad = await future_cantidad

        if tipo == "noticias":
            await modo_noticias(cantidad)
        elif tipo == "clips":
            await modo_clips(cantidad)

    await channel.send("✅ **Proceso completado. Todos los posts están programados.**")

# ─── ENTRADA ──────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    await menu_principal()

def main():
    client.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()