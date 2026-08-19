import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

# === KONFIGURACJA NAZWY RANGI ===
ID_ROLI_WIDZ = 1539527929359241316

# ==========================================
# 1. SERWER WWW DO WYBUDZANIA BOTA (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot status: ONLINE"

def run_web_server():
    # Port 10000 jest wymagany przez Render dla każdego Web Service
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# ==========================================
# 2. LOGIKA WERYFIKACJI DISCORDA
# ==========================================
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_user_btn", emoji="🍏")
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_user_btn", emoji="🍏")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(ID_ROLI_WIDZ) # TUTAJ popraw wcięcie na 8 spacji
        
        if role:
            if role in user.roles:
                await interaction.response.send_message("<a:Strzalka1:1539554457174548480> Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await user.add_roles(role)
                await interaction.response.send_message("<a:Strzalka1:1539554457174548480> Pomyślnie przeszedłeś weryfikację! Witaj na serwerze! 🎉", ephemeral=True)
        else:
            await interaction.response.send_message("Błąd: Nie znaleziono roli Widza na serwerze. Powiadom admina!", ephemeral=True)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
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

@bot.tree.command(name="weryfikacja-setup", description="Wysyła panel do weryfikacji konta")
@app_commands.checks.has_permissions(administrator=True)
async def setup_verif(interaction: discord.Interaction):
    view = VerificationView()
    embed = discord.Embed(
        description="```ansi\n\u001b[1;37m✅ LL1N COMMUNITY × WERYFIKACJA\u001b[0m\n```\n> <a:Strzalka1:1539554457174548480>︲ Aby uzyskać pełny dostęp do wszystkich kanałów serwera **LL1N COMMUNITY**,> <a:Strzalka1:1539554457174548480>︲ kliknij poniższy zielony przycisk.\n\n> <a:Strzalka1:1539554457174548480>︲Pamiętaj o przestrzeganiu regulaminu. Życzymy miłego pobytu!",
        color=discord.Color.from_rgb(119, 178, 85)
    )
    embed.set_footer(text="© 2026 LL1N Community × weryfikacja")
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# ==========================================
# 3. URUCHOMIENIE SERWERA I BOTA
# ==========================================
if __name__ == "__main__":
    keep_alive() # Odpala serwer Flask, żeby Render widział otwarty port
    
    # Pobiera bezpiecznie token, który wkleiłeś w panelu Rendera
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
