import discord
from discord.ext import commands
from discord import app_commands

# === KONFIGURACJA NAZWY RANGI ===
# Upewnij się, że nazwa roli poniżej jest IDENTYCZNA jak na Twoim Discordzie!
NAZWA_ROLI_WIDZ = "🎮 ┃ ᴡɪᴅᴢ"

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Przycisk działa zawsze, nawet po restarcie bota

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_user_btn", emoji="🍏")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Szukanie roli Widza na serwerze
        role = discord.utils.get(guild.roles, name=NAZWA_ROLI_WIDZ)
        
        if role:
            if role in user.roles:
                # Komunikat ukryty (widoczny tylko dla gracza)
                await interaction.response.send_message("» Jesteś już zweryfikowany!", ephemeral=True)
            else:
                # Nadawanie rangi i wysłanie potwierdzenia
                await user.add_roles(role)
                await interaction.response.send_message("» Pomyślnie przeszedłeś weryfikację! Witaj na serwerze! 🎉", ephemeral=True)
        else:
            await interaction.response.send_message("Błąd: Nie znaleziono roli Widza na serwerze. Powiadom admina!", ephemeral=True)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoku, żeby przycisk działał non-stop
        self.add_view(VerificationView())

bot = Bot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name} - weryfikacja gotowa.")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)

# === ZMIENIONA KOMENDA SLASH ===
# Wpisujesz /weryfikacja-setup na kanale #✅┃ᴡᴇʀʏꜰɪᴋᴀᴄᴊᴀ
@bot.tree.command(name="weryfikacja-setup", description="Wysyła panel do weryfikacji konta")
@app_commands.checks.has_permissions(administrator=True)
async def setup_verif(interaction: discord.Interaction):
    view = VerificationView()
    embed = discord.Embed(
        title="🔒 ┃ Weryfikacja konta",
        description="Aby uzyskać pełny dostęp do wszystkich kanałów serwera **LL1N COMMUNITY**, kliknij poniższy zielony przycisk.\n\nPamiętaj o przestrzeganiu regulaminu. Życzymy miłego pobytu!",
        color=discord.Color.from_rgb(119, 178, 85) # Zielony kolor pod Twoje logo
    )
    embed.set_footer(text="© 2026 LL1N Community × weryfikacja")
    
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)


bot.run("MTUzOTU0MjI2ODU4OTkwMzkyMg.G3rGyG.r6k5SGXEeANsmIBuEF082h7v3zhcugw9xLw5cw")
