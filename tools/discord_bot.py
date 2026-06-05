import discord
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
views_activas = []

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    for view in views_activas:
        if hasattr(view, 'esperando_cambios') and view.esperando_cambios:
            if not view.future.done():
                view.future.set_result({
                    "accion": "cambios",
                    "instrucciones": message.content,
                    "copy": view.copy
                })
            view.stop()
            views_activas.remove(view)
            break

async def enviar_borrador(red: str, copy: str, future=None) -> None:
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if not channel:
        print("❌ No se encontró el canal")
        return

    embed = discord.Embed(
        title=f"📌 Nueva publicación — {red.upper()}",
        description=copy,
        color=0x5865F2
    )

    view = AccionesView(red=red, copy=copy, future=future)
    views_activas.append(view)
    await channel.send(embed=embed, view=view)

class AccionesView(discord.ui.View):
    def __init__(self, red: str, copy: str, future=None):
        super().__init__(timeout=None)
        self.red = red
        self.copy = copy
        self.future = future
        self.esperando_cambios = False

    @discord.ui.button(label="✅ Aprobar", style=discord.ButtonStyle.success)
    async def aprobar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ Post de {self.red} aprobado y programado.")
        if self.future and not self.future.done():
            self.future.set_result({"accion": "aprobar", "copy": self.copy})
        if self in views_activas:
            views_activas.remove(self)
        self.stop()

    @discord.ui.button(label="❌ Rechazar", style=discord.ButtonStyle.danger)
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"❌ Post de {self.red} rechazado.")
        if self.future and not self.future.done():
            self.future.set_result({"accion": "rechazar", "copy": self.copy})
        if self in views_activas:
            views_activas.remove(self)
        self.stop()

    @discord.ui.button(label="✏️ Pedir cambios", style=discord.ButtonStyle.secondary)
    async def cambios(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✏️ Escribí qué cambios querés hacer:")
        self.esperando_cambios = True

def iniciar_bot():
    client.run(DISCORD_BOT_TOKEN)