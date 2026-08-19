import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import asyncio

# === KONFIGURACJA ID RANG ===
ID_ROLI_WIDZ = 1539527929359241316
ID_ROLI_TICKETY = 1539525896501862481  # Twoja rola administracji z dostępem do ticketów

# ==========================================
# 1. SERWER WWW DO WYBUDZANIA BOTA (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot status: ONLINE"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# ==========================================
# 2. LOGIKA WERYFIKACJI DISCORDA (ZIELONA)
# ==========================================
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_user_btn", emoji="🍏")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(ID_ROLI_WIDZ)
        
        if role:
            if role in user.roles:
                await interaction.response.send_message("<a:Strzalka2:1539571409599070218> Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await user.add_roles(role)
                await interaction.response.send_message("<a:Strzalka2:1539571409599070218> Pomyślnie przeszedłeś weryfikację! Witaj na serwerze! 🎉", ephemeral=True)
        else:
            await interaction.response.send_message("Błąd: Nie znaleziono roli Widza na serwerze. Powiadom admina!", ephemeral=True)

# ==========================================
# 3. LOGIKA TICKETÓW (NIEBIESKA - ROZWIJANA)
# ==========================================
class PurchaseModal(discord.ui.Modal, title="Formularz Zakupu"):
    co_kupujesz = discord.ui.TextInput(
        label="Co kupujesz?",
        placeholder="Wpisz nazwę produktu...",
        required=True,
        max_length=100
    )
    czym_placisz = discord.ui.TextInput(
        label="Czym Byś Chciał/a zapłacić?",
        placeholder="Np. Blik,PSC",
        required=True,
        max_length=10
    )
    za_ile = discord.ui.TextInput(
        label="Za ile pieniędzy kupujesz?",
        placeholder="Np. 20zł",
        required=True,
        max_length=20
    )

    def __init__(self, ticket_role_id):
        super().__init__()
        self.ticket_role_id = ticket_role_id

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = interaction.channel.category
        ticket_role = guild.get_role(self.ticket_role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if ticket_role:
            overwrites[ticket_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"🛒┃zakup-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka:1536867225359613962> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        close_view = CloseTicketView()

        mention_role = ticket_role.mention if ticket_role else "@tickety"
        await ticket_channel.send(f"<:wozek:1539597036884598828> **Nowe Zamówienie !** {mention_role} {user.mention}")

        embed = discord.Embed(
            description=f"```ansi\n\u001b[1;34m📩 ┃ ZGŁOSZENIE: ZAKUP\u001b[0m\n```\n"
                        f"> **Produkt:** {self.co_kupujesz.value}\n"
                        f"> **Ilość:** {self.ile_sztuk.value}\n"
                        f"> **Cena:** {self.za_ile.value}\n\n"
                        f"> <a:Strzalka:1536867225359613962>︲ Administracja zaraz się Tobą zajmie.",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        embed.set_footer(text=f"© 2026 LL1N Community × Zakup")
        await ticket_channel.send(embed=embed, view=close_view)


class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Zakup", description="Otwórz ticket w celu zakupu naszego asortymentu.", emoji="<:wozek:1539597036884598828>", value="Zakup"),
            discord.SelectOption(label="Pomoc", description="Masz problem? Stwórz ticket byśmy mogli Ci pomóc.", emoji="<:list:1539599064155553822>", value="Pomoc"),
            discord.SelectOption(label="Mam Pytanie", description="Pytania do administracji", emoji="<:lupa:1539598440483262474>", value="Pytanie")
        ]
        super().__init__(placeholder="💎 Wybiɛrz katɛgorię swojego zgłoszenia...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        wybor = self.values[0]  # Bezpieczne pobranie wybranego tekstu z listy

        if wybor == "Zakup":
            await interaction.response.send_modal(PurchaseModal(ticket_role_id=ID_ROLI_TICKETY))
            return

        guild = interaction.guild
        user = interaction.user
        category = interaction.channel.category
        ticket_role = guild.get_role(ID_ROLI_TICKETY)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if ticket_role:
            overwrites[ticket_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"📩┃{wybor.lower()}-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka:1536867225359613962> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        close_view = CloseTicketView()
        
        nazwa_opcji = "Zgłoszenie"
        for o in self.options:
            if o.value == wybor:
                nazwa_opcji = o.label
                break
        
        embed = discord.Embed(
            description=f"```ansi\n\u001b[1;34m📩 ┃ ZGŁOSZENIE: {nazwa_opcji.upper()}\u001b[0m\n```\n> <a:Strzalka:1536867225359613962>︲ Witaj {user.mention}!\n> <a:Strzalka:1536867225359613962>︲ Napisz tutaj, w czym możemy Ci pomóc.\n\n> <a:Strzalka:1536867225359613962>︲ Administracja zaraz się Tobą zajmie.",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        embed.set_footer(text=f"© 2026 LL1N Community × {wybor}")
        await ticket_channel.send(embed=embed, view=close_view)


class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("<a:Strzalka:1536867225359613962> Zamykanie ticketa za 5 sekund...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except discord.NotFound:
            pass

# ==========================================
# 4. GŁÓWNA KONFIGURACJA BOTA
# ==========================================
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(VerificationView())
        self.add_view(TicketDropdownView())
        self.add_view(CloseTicketView())

bot = Bot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name} - weryfikacja i tickety gotowe.")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(f"Błąd synchronizacji komend: {e}")

# Komenda /weryfikacja-setup (Zielona)
@bot.tree.command(name="weryfikacja-setup", description="Wysyła panel do weryfikacji konta")
@app_commands.checks.has_permissions(administrator=True)
async def setup_verif(interaction: discord.Interaction):
    view = VerificationView()
    
    tekst_verif = (
        "```ansi\n\u001b[1;37m✅ LL1N COMMUNITY × WERYFIKACJA\u001b[0m\n```\n"
        "> <a:Strzalka2:1539571409599070218>︲ Dostęp do wszystkich kanałów serwera **LL1N COMMUNITY**,\n"
        "> <a:Strzalka2:1539571409599070218>︲ uzyskasz po kliknięciu zielonego przycisku poniżej.\n\n"
        "> <a:Strzalka2:1539571409599070218>︲Pamiętaj o przestrzeganiu regulaminu. Życzymy miłego pobytu!"
    )
    
    embed = discord.Embed(description=tekst_verif, color=discord.Color.from_rgb(119, 178, 85))
    embed.set_footer(text="© 2026 LL1N Community × weryfikacja")
    
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# Komenda /ticket-setup (NIEBIESKA)
@bot.tree.command(name="ticket-setup", description="Wysyła panel ticketów z menu wyboru (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    view = TicketDropdownView()
    
    tekst_ticket = (
        "```ansi\n\u001b[1;37m🎫 LL1N COMMUNITY × STWÓRZ TICKETA\u001b[0m\n```\n"
        "> <a:Strzalka3:1539590864228061284>︲ Interesuje Cię zakup texture packa lub moich modyfikacji?\n"
        "> <a:Strzalka3:1539590864228061284>︲ A może masz jakieś **pytanie** lub **problem**?\n\n"
        "> <a:Strzalka3:1539590864228061284>︲ Rozwiń listę poniżej i wybierz powód! Odpowiemy najszybciej jak to możliwe!"
    )
    
    embed = discord.Embed(description=tekst_ticket, color=discord.Color.from_rgb(52, 152, 219))
    embed.set_footer(text="© 2026 LL1N Community × tickety")
    
    await interaction.response.send_message("Panel ticketów wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# ==========================================
# 5. URUCHOMIENIE BOTA
# ==========================================
if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    
    if token:
        bot.run(token)
    else:
        print("❌ BŁĄD: Nie znaleziono zmiennej środowiskowej DISCORD_TOKEN!")

