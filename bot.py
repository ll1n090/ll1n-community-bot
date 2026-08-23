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

# --- FORMULARZ ZAKUPU ---
class PurchaseModal(discord.ui.Modal, title="Formularz Zakupu"):
    co_kupujesz = discord.ui.TextInput(
        label="Co kupujesz?",
        placeholder="Wpisz nazwę produktu...",
        required=True,
        max_length=100
    )
    czym_placisz = discord.ui.TextInput(
        label="Czym Byś Chciał/a zapłacić?",
        placeholder="Np. Blik, PSC",
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

        channel_name = f"🎫┃ᴛɪᴄᴋᴇᴛʏ-zakup-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka3:1539590864228061284> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        close_view = CloseTicketView()

        mention_role = ticket_role.mention if ticket_role else "@tickety"

        embed = discord.Embed(
            description=(
                f"```ansi\n\u001b[1;37m🛒 | Nowe Zamówienie\u001b[0m\n```\n"
                f"> <a:Strzalka3:1539590864228061284>︲ Wzywanie zamówienia: {mention_role} {user.mention}\n"
                "> <a:Strzalka3:1539590864228061284>︲ Administracja zaraz się Tobą zajmie."
            ),
            color=discord.Color.from_rgb(43, 45, 49) 
        )
        
        embed.add_field(name="<:box:1539624615591026688> Wybrany produkt:", value=f"```\n{self.co_kupujesz.value}\n```", inline=False)
        embed.add_field(name="<a:Karta:1539623691808280696> Metoda płatności:", value=f"```\n{self.czym_placisz.value}\n```", inline=True)
        embed.add_field(name="<a:MONEY:1539624882978029628> Kwota zamówienia:", value=f"```\n{self.za_ile.value}\n```", inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"© 2026 LL1N Community • Kupujący: {user.name}")
        
        await ticket_channel.send(embed=embed, view=close_view)




# --- FORMULARZ POMOCY ---
class HelpModal(discord.ui.Modal, title="Formularz Pomocy"):
    problem = discord.ui.TextInput(
        label="Opisz krótko swój problem",
        style=discord.TextStyle.long,
        placeholder="Napisz tutaj, w czym tkwi problem i jak możemy Ci pomóc...",
        required=True,
        max_length=1000
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

        channel_name = f"🎫┃ᴛɪᴄᴋᴇᴛʏ-pomoc-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka3:1539590864228061284> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        mention_role = ticket_role.mention if ticket_role else "@tickety"

        embed = discord.Embed(
            description=f"```ansi\n\u001b[1;37m📞 ┃ Nowe Zgłoszenie Pomocy !\u001b[0m\n```\n"
                        f"> **<a:Strzalka3:1539590864228061284>︲Opis problemu:**\n{self.problem.value}\n\n"
                        f"> <a:Strzalka3:1539590864228061284>︲ Administracja zaraz się Tobą zajmie.",
            color=discord.Color.from_rgb(52, 152, 219)
        )

        embed.set_footer(text="© 2026 LL1N Community × Pomoc")
        await ticket_channel.send(content=f"{mention_role} {user.mention}", embed=embed, view=CloseTicketView())



# --- FORMULARZ PYTANIA ---
class QuestionModal(discord.ui.Modal, title="Formularz Pytania"):
    pytanie = discord.ui.TextInput(
        label="Jakie masz pytanie do administracji?",
        style=discord.TextStyle.long,
        placeholder="Zadaj tutaj swoje pytanie, na które chcesz poznać odpowiedź...",
        required=True,
        max_length=1000
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

        channel_name = f"🎫┃ᴛɪᴄᴋᴇᴛʏ-pytanie-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka3:1539590864228061284> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        mention_role = ticket_role.mention if ticket_role else "@tickety"
        await ticket_channel.send(f"{mention_role} {user.mention}")

        embed = discord.Embed(
            description=f"```ansi\n\u001b[1;37m❓ ┃ PYTANIE\u001b[0m\n```\n"
                        f"> **<a:Strzalka3:1539590864228061284>︲Treść pytania:**\n{self.pytanie.value}\n\n"
                        f"> <a:Strzalka3:1539590864228061284>︲ Administracja zaraz się Tobą zajmie.",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        embed.set_footer(text="© 2026 LL1N Community × Pytanie")
        await ticket_channel.send(embed=embed, view=CloseTicketView())

# --- FORMULARZ ODBIORU ---
class OdbiorModal(discord.ui.Modal, title="Formularz Odbioru"):
    cel = discord.ui.TextInput(
        label="Co chcesz odebrać? (np. TXT za suba, konkurs)",
        style=discord.TextStyle.short,
        placeholder="Wpisz tutaj cel otwarcia zgłoszenia...",
        required=True,
        max_length=100
    )
    szczegoly = discord.ui.TextInput(
        label="Dodatkowe informacje (np. nick z konkursu)",
        style=discord.TextStyle.long,
        placeholder="Jeśli odbierasz TXT za suba, napisz 'Sociale' i przygotuj screena na czat...",
        required=False,
        max_length=500
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

        channel_name = f"🎁┃ticket-odbior-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"<a:Strzalka3:1539590864228061284> Stworzono ticket! Idź do: {ticket_channel.mention}", ephemeral=True)

        mention_role = ticket_role.mention if ticket_role else "@tickety"
        await ticket_channel.send(f"{mention_role} {user.mention}")

        embed = discord.Embed(
            description=f"""```ansi\n\u001b[1;37m🎁  LL1N COMMUNITY × ODBIÓR NAGRÓD\u001b[0m\n```\n"""
                        f"> <a:Strzalka3:1539590864228061284> **ᴄᴇʟ ᴢɢᴌᴏsᴢᴇɴɪᴀ:** {self.cel.value}\n"
                        f"> <a:Strzalka3:1539590864228061284> **ɪɴꜰᴏʀᴍᴀᴄᴊᴇ:** {self.szczegoly.value if self.szczegoly.value else 'Brak'}\n\n"
                        f"> 📸 ┃ **Jeśli odbierasz TXT za suba/follow:**\n"
                        f"> Wyślij teraz na tym czacie screena z **widoczną** **datą** i **godziną** na ekranie.\n\n"
                        f"> <a:Strzalka3:1539590864228061284> Administracja zaraz się Tobą zajmie.",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        embed.set_footer(text="© 2026 LL1N Community × Odbiory")
        await ticket_channel.send(embed=embed, view=CloseTicketView())


# --- MENU ROZWIJANE ---
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Zakup", description="Otwórz ticket w celu zakupu naszego asortymentu.", emoji="<:wozek:1539597036884598828>", value="Zakup"),
            discord.SelectOption(label="Pomoc", description="Masz problem? Stwórz ticket byśmy mogli Ci pomóc.", emoji="<:list:1539599064155553822>", value="Pomoc"),
            discord.SelectOption(label="Mam Pytanie", description="Pytania do administracji", emoji="<:lupa:1539598440483262474>", value="Pytanie"),
            discord.SelectOption(label="Odbiór", description="ᴄʜᴄᴇsᴢ ᴏᴅᴇʙʀᴀᴄ ᴛxᴛ ᴢᴀ sᴜʙᴀ ʟᴜʙ ᴡʏɢʀᴀᴌᴇś ᴋᴏɴᴋᴜʀs? ᴛᴀ ᴋᴀᴛᴇɢᴏʀɪᴀ ᴊᴇsᴛ ᴅʟᴀ ᴄɪᴇʙɪᴇ!", emoji="<:box:1539624615591026688>", value="Odbior")
        ]
        super().__init__(placeholder="💎 Wybiɛrz kategorię swojego zgłoszenia...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        # Sprawdzanie limitu 1 ticketa (Kategoria ticketów)
        KATEGORIA_ID = 1539536958835925033 
        kategoria = interaction.guild.get_channel(KATEGORIA_ID)
        
        if kategoria:
            for kanal in kategoria.channels:
                uprawnienia = kanal.overwrites_for(interaction.user)
                if uprawnienia.read_messages is True:
                    return await interaction.response.send_message(
                        "❌ **Posiadasz już otwarty ticket!** Zamknij poprzedni, aby móc otworzyć nowy.", 
                        ephemeral=True
                    )
                wybor = self.values[0]

        if wybor == "Zakup":
            await interaction.response.send_modal(PurchaseModal(ticket_role_id=ID_ROLI_TICKETY))
        elif wybor == "Pomoc":
            await interaction.response.send_modal(HelpModal(ticket_role_id=ID_ROLI_TICKETY))
        elif wybor == "Pytanie":
            await interaction.response.send_modal(QuestionModal(ticket_role_id=ID_ROLI_TICKETY))
        elif wybor == "Odbior":
            await interaction.response.send_modal(OdbiorModal(ticket_role_id=ID_ROLI_TICKETY))
    

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn)")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("<a:Strzalka3:1539590864228061284> Zamykanie ticketa za 5 sekund...")
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
        intents.members = True

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
    embed.set_footer(text="© 2026 LL1N Community × Weryfikacja")
    
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# Komenda /regulamin (CZERWONA)
@bot.tree.command(name="regulamin", description="Wysyła regulamin serwera (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def regulamin(interaction: discord.Interaction):
    

    tekst_regulamin = (
        "```ansi\n\u001b[1;37m📌  LL1N COMMUNITY × REGULAMIN SERWERA\u001b[0m\n```\n"
        "**ᴅᴏᴌᴀᴄᴢᴀᴊᴀᴄ ᴅᴏ ɴᴀsᴢᴇɢᴏ sᴇʀᴡᴇʀᴀ, ᴀᴋᴄᴇᴘᴛᴜᴊᴇsᴢ ᴘᴏɴɪᴢsᴢᴇ ᴢᴀsᴀᴅʏ. sᴢᴀɴᴜᴊᴍʏ sɪᴇ ɴᴀᴡᴢᴀᴊᴇᴍ!**\n\n"
        "<a:Strzalka4:1540979104625594453> ︲ 1. sᴢᴀɴᴜᴊ ɪɴɴʏᴄʜ ᴄᴢᴌᴏɴᴋᴏᴡ sᴇʀᴡᴇʀᴀ. ᴡsᴢᴇʟᴋɪᴇ ᴡʏᴢᴡɪsᴋᴀ, ᴛᴏᴋsʏᴄᴢɴᴏsᴄ ɪ ᴘʀᴏᴡᴏᴋᴀᴄᴊᴇ ʙᴇᴅᴀ ᴋᴀʀᴀɴᴇ.\n"
        "<a:Strzalka4:1540979104625594453> ︲ 2. ᴢᴀᴄʜᴏᴡᴜᴊ ᴘᴏʀᴢᴀᴅᴇᴋ ɴᴀ ᴄᴢᴀᴛᴀᴄʜ. ɴɪᴇ sᴘᴀᴍᴜᴊ, ɴɪᴇ ᴡʏsʏᴌᴀᴊ ᴛʏᴄʜ sᴀᴍʏᴄʜ ᴡɪᴀᴅᴏᴍᴏsᴄɪ ɪ ɴɪᴇ ɴᴀᴅᴜᴢʏᴡᴀᴊ ᴄᴀᴘs ʟᴏᴄᴋᴀ.\n"
        "<a:Strzalka4:1540979104625594453> ︲ 3. ᴄᴀᴌᴋᴏᴡɪᴛʏ ᴢᴀκᴀᴢ ʀᴇᴋʟᴀᴍᴏᴡᴀɴɪᴀ ɪɴɴʏᴄʜ sᴇʀᴡᴇʀᴏᴡ ᴅɪsᴄᴏʀᴅ, ᴋᴀɴᴀᴌᴏᴡ ʏᴛ/ᴛᴛ ᴄᴢʏ sᴛʀᴏɴ ʙᴇᴢ ᴢɢᴏᴅʏ ᴡᴌᴀsᴄɪᴄɪᴇʟᴀ (ɴᴀ ᴘv ʀᴏᴡɴɪᴇᴢ).\n"
        "<a:Strzalka4:1540979104625594453> ︲ 4. ᴛxᴛ, ᴍᴏᴅʏ ᴋᴜᴘᴜᴊᴇsᴢ ᴛʏʟᴋᴏ ᴘʀᴢᴇᴢ ᴏꜰɪᴄᴊᴀʟɴʏ sʏsᴛᴇᴍ ᴛɪᴄᴋᴇᴛᴏᴡ. ʜᴀɴᴅᴇʟ ᴍɪᴇᴅᴢʏ ɢʀᴀᴄᴢᴀᴍɪ ᴊᴇsᴛ ᴢᴀʙʀᴏɴɪᴏɴʏ.\n"
        "<a:Strzalka4:1540979104625594453> ︲ 5. sᴢᴀɴᴜᴊ sᴛᴀʀᴀɴɪᴀ ᴀᴅᴍɪɴɪsᴛʀᴀᴄᴊɪ. ɴɪᴇ ᴏᴢɴᴀᴄᴢᴀᴊ ᴡᴌᴀsᴄɪᴄɪᴇʟᴀ ᴀɴɪ ᴘᴏᴍᴏᴄɴɪᴋᴏᴡ ʙᴇᴢ ᴡᴀᴢɴᴇɢᴏ ᴘᴏᴡᴏᴅᴜ.\n"
        "<a:Strzalka4:1540979104625594453> ︲ 6. ᴡsᴢᴇʟᴋɪᴇ ᴛʀᴇsᴄɪ +18, ɴsꜰᴡ, ɢᴏʀᴇ ʟᴜʙ ɴɪᴇʟᴇɢᴀʟɴᴇ ʟɪɴᴋɪ ʙᴇᴅᴀ sᴋᴜᴛᴋᴏᴡᴀᴄ ɴᴀᴛʏᴄʜᴍɪᴀsᴛᴏᴡʏᴍ ʙᴀɴᴇᴍ.\n\n"
        
        "<a:syrena1:1540951017569652746>︲ɴɪᴇᴢɴᴀᴊᴏᴍᴏsᴄ ʀᴇɢᴜʟᴀᴍɪɴᴜ ɴɪᴇ ᴢᴡᴀʟɴɪᴀ ᴢ ᴊᴇɢᴏ ᴘʀᴢᴇsᴛʀᴢᴇɢᴀɴɪᴀ. ʙᴀᴡ sɪᴇ ᴅᴏʙʀᴢᴇ!"
    )

    
    # Kolor zmieniony na czerwony (RGB: 231, 76, 60)
    embed = discord.Embed(description=tekst_regulamin, color=discord.Color.from_rgb(231, 76, 60))
    embed.set_footer(text="© 2026 LL1N Community × Regulamin")
    
    await interaction.response.send_message("Regulamin został wysłany na czerwono!", ephemeral=True)
    await interaction.channel.send(embed=embed)

# Komenda /ticket-setup (NIEBIESKA)
@bot.tree.command(name="ticket-setup", description="Wysyła panel ticketów z menu wyboru (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    view = TicketDropdownView()
    
    tekst_ticket = (
        "```ansi\n\u001b[1;37m🎫 LL1N COMMUNITY × STWÓRZ TICKETA\u001b[0m\n```\n"
        "> <a:Strzalka3:1539590864228061284>︲ Interesuje Cię zakup **texture packa** lub moich **modyfikacji**?\n"
        "> <a:Strzalka3:1539590864228061284>︲ A może masz jakieś **pytanie** lub **problem**?\n\n"
        "> <a:Strzalka3:1539590864228061284>︲ Rozwiń poniższą **listę** i wybierz odpowiedni powód zgłoszenia!"
    )
    
    embed = discord.Embed(description=tekst_ticket, color=discord.Color.from_rgb(52, 152, 219))
    embed.set_footer(text="© 2026 LL1N Community × Tickety")
    
    await interaction.response.send_message("Panel ticketów wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# ================= POWITALNIA =================
KANAL_POWITAN_ID = 1540972397258346606

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(KANAL_POWITAN_ID)
    if channel is None:
        return

    liczba_czlonkow = member.guild.member_count

    tekst_powitania = (
        "```ansi\n\u001b[1;37m🛬 LL1N COMMUNITY × PRZYLOTY\u001b[0m\n```\n"
        f"> <a:Strzalka3:1539590864228061284>︲**ᴡɪᴛᴀᴍʏ ɴᴀ sᴇʀᴡᴇʀᴢᴇ, {member.mention}!**\n"
        f"Cieszymy się, że do nas dołączyłeś. Jesteś naszym **{liczba_czlonkow}** użytkownikiem!\n"
        f"> <a:Strzalka3:1539590864228061284>︲**ᴋʀᴏᴋ ᴅᴏ ʀᴏᴢɢʀʏᴡᴋɪ:**\n"
        f"Aby uzyskać pełen dostęp do serwera, koniecznie przejdź na strefę weryfikacji!\n\n"
        f"> <a:Strzalka4:1540979104625594453>︲Zapoznaj się również z naszym regulaminem! Miłej zabawy!"
    )

    embed = discord.Embed(
        description=tekst_powitania,
        color=discord.Color.from_rgb(52, 152, 219)
    )
    embed.set_footer(text="© 2026 LL1N Community × Przyloty")
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    await channel.send(embed=embed)

@bot.tree.command(name="cennik", description="Wysyła estetyczny cennik modyfikacji i texture packów")
@commands.has_permissions(administrator=True)
async def cennik_komenda(interaction: discord.Interaction):
    # Soczysty pomarańczowy kolor (RGB: 230, 126, 34)
    embed = discord.Embed(
        color=discord.Color.from_rgb(230, 126, 34)
    )
    
    # Nagłówek ANSI w kolorze pomarańczowym/złotym
    embed.add_field(
        name="```ansi\n\u001b[1;33m🛒  CENNIK MODYFIKACJI & TXT × LL1N\u001b[0m\n```",
        value="> Wybierz interesującą Cię opcję uzyskania dostępu do naszych pakietów!",
        inline=False
    )
    
    embed.add_field(
        name="💳 ❜ ᴏᴘᴄᴊᴀ ᴘᴌᴀᴛɴᴀ",
        value=(
            "> <a:Strzalka3:1539509864228061284> **Cena:** 5 PLN / sztuka\n"
            "> **Metody płatności:** BLIK ❜ PSC\n"
            "> **Jak kupić?** Otwórz ticket poniżej i wybierz kategorię **Zakup**."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎁 ❜ ᴏᴘᴄᴊᴀ ᴅᴀʀᴍᴏᴡᴀ (ᴢᴀ sᴜʙᴀ)",
        value=(
            "> <a:Strzalka3:1539509864228061284> **Cena:** Całkowicie ZA DARMO!\n"
            "> **Wymagania:** Subskrypcja na naszym YT oraz obserwacja na TT.\n"
            "> **Jak odebrać?** Otwórz ticket poniżej, wybierz kategorię **Odbiór** i przygotuj screena z widoczną godziną!"
        ),
        inline=False
    )
    
    embed.set_footer(text="© 2026 LL1N Community × Handlowe")
    
    await interaction.response.send_message("Cennik został pomyślnie wysłany!", ephemeral=True)
    await interaction.channel.send(embed=embed)

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
