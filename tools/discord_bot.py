import discord
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

async def enviar_borrador(red: str, copy: str) -> None:
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

    view = AccionesView(red=red, copy=copy)
    await channel.send(embed=embed, view=view)

class AccionesView(discord.ui.View):
    def __init__(self, red: str, copy: str):
        super().__init__(timeout=None)
        self.red = red
        self.copy = copy

    @discord.ui.button(label="✅ Aprobar", style=discord.ButtonStyle.success)
    async def aprobar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ Post de {self.red} aprobado.")
        self.stop()

    @discord.ui.button(label="❌ Rechazar", style=discord.ButtonStyle.danger)
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"❌ Post de {self.red} rechazado.")
        self.stop()

    @discord.ui.button(label="✏️ Pedir cambios", style=discord.ButtonStyle.secondary)
    async def cambios(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✏️ Escribí qué cambios querés hacer:")
        self.stop()

def iniciar_bot():
    client.run(DISCORD_BOT_TOKEN)