import discord
import asyncio
import aiohttp
import datetime
import json
import os
import time
import random
from discord.ext import commands
from discord.ui import View, Button, Select
from discord import SelectOption, Interaction
from random import choice


intents = discord.Intents.all()
intents.message_content = True 


bot = commands.Bot(command_prefix="!", intents=intents)

    
    

#Bot stworzony przez young mikoczan na zamówienie
#Edytuj nazwy rang aby dać uprawnienia do komend takich jak ogloszenie oraz ban mute clear kick send-panel
ALLOWED_ROLES = ["⭐◽ Admin", "🔴◽ Moderator", "👑◽ Właściciel", "💠◽ DEVELOPER"]
TICKET_CATEGORY_NAME = "💲 × PREMIUM"  # <- zmień na swoją kategorię dla ticketów

#edytuj kolory w formacie HEX #RRGGBB nie usuwaj "0x" przed wartościami możesz zmienić nazwy kolorów
COLOR_MAP = {
    "blue": 0x3498db,
    "red": 0xc85050,
    "purple": 0x9b59b6,
    "green": 0x00e056,
    "pink": 0xfc44cc,
    "ligt_blue": 0x03fce8,
    "dark_blue": 0x0d3061,
    "yellow": 0xf0cc3e
}
last_konkurs_data = {} # potrzebne do konkursów

@bot.command()
async def ogloszenie(ctx, tytul: str, opis: str, tresc: str, kolor: str, obraz: str = None, przyciski: str = None):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)

    if not has_permission:
        await ctx.reply("⛔ Nie masz uprawnień do tworzenia ogłoszeń!", delete_after=5)
        return

    kolor = kolor.lower()
    if kolor not in COLOR_MAP:
        await ctx.reply("⚠️ Niepoprawny kolor! Użyj: `blue`, `red`, `green`, `purple`, `pink`, `light_blue` oraz `dark_blue` i `yellow`.", delete_after=5)
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        await ctx.reply("⚠️ Nie mam uprawnień do usuwania wiadomości!", delete_after=5)
        return

    embed = discord.Embed(title=tytul, description=opis, color=COLOR_MAP[kolor])
    embed.add_field(name="📢 Ogłoszenie", value=tresc, inline=False)
    embed.set_footer(text=f"Ogłoszenie dodane przez: {ctx.author.name}")

    if obraz:
        embed.set_image(url=obraz)

    view = None
    if przyciski:
        view = View()
        przyciski_lista = przyciski.split('|')
        for i, btn in enumerate(przyciski_lista):
            url = btn.strip()
            if not url.startswith("http"):
                continue  # pomijamy nieprawidłowe linki
            view.add_item(Button(label=f"Link {i+1}", url=url))

    await ctx.send(embed=embed, view=view)
@bot.command()
async def ban(ctx, member: discord.Member, czas_godzin: float = None):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    await ctx.message.delete()
    await member.ban(reason=f"Banned by {ctx.author.name}")
    await ctx.send(f"🔨 Zbanowano {member.mention}!")

    if czas_godzin:
        await ctx.send(f"⏱️ Ban czasowy: {czas_godzin}h")
        await asyncio.sleep(czas_godzin * 3600)
        await ctx.guild.unban(member)
        await ctx.send(f"✅ Odbanowano {member.mention} (ban czasowy wygasł)")

@bot.command()
async def kick(ctx, member: discord.Member):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    await ctx.message.delete()
    await member.kick(reason=f"Kicked by {ctx.author.name}")
    await ctx.send(f"👢 Wyrzucono {member.mention}!")

@bot.command()
async def clear(ctx, ilosc: int = None):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=ilosc)
    await ctx.send(f"🧹 Usunięto {len(deleted)} wiadomości!", delete_after=5)

@bot.command()
async def mute(ctx, member: discord.Member, czas_godzin: float = None, *, powod: str = "Brak podanego powodu"):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)

    await member.add_roles(mute_role, reason=powod)
    await ctx.send(f"🔇 Uciszono {member.mention}!\n📄 Powód: `{powod}`")

    if czas_godzin:
        await ctx.send(f"⏱️ Mute czasowy: {czas_godzin}h")
        await asyncio.sleep(czas_godzin * 3600)
        await member.remove_roles(mute_role)
        await ctx.send(f"✅ {member.mention} został odciszony (mute czasowy wygasł)")
@bot.command()
async def konkurs(ctx, nagroda: str, czas_godzin: float = 3):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tworzenia konkursów!", delete_after=5)

    uczestnicy = set()

    class KonkursView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="🎉 Dołącz", style=discord.ButtonStyle.primary)
        async def dolacz(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id in uczestnicy:
                await interaction.response.send_message("✅ Już bierzesz udział!", ephemeral=True)
            else:
                uczestnicy.add(interaction.user.id)
                await interaction.response.send_message("🎉 Dołączyłeś do konkursu!", ephemeral=True)
                await aktualizuj_embed()

    embed = discord.Embed(
        title="📣 KONKURS 📣",
        description=(
            f"- 🎁 **Nagroda:** {nagroda}\n"
            f"- 👥 **Osoby biorące udział:** 0\n"
            f"- ⏰ **Koniec konkursu za:** {czas_godzin}h"
        ),
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2278/2278992.png")
    embed.set_footer(text=f"Konkurs dodany przez: {ctx.author.name}")

    view = KonkursView()
    konkurs_message = await ctx.send(embed=embed, view=view)

    async def aktualizuj_embed():
        embed.description = (
            f"- 🎁 **Nagroda:** {nagroda}\n"
            f"- 👥 **Osoby biorące udział:** {len(uczestnicy)}\n"
            f"- ⏰ **Koniec konkursu za:** {czas_godzin}h"
        )
        await konkurs_message.edit(embed=embed, view=view)

    await asyncio.sleep(czas_godzin * 3600)

    if not uczestnicy:
        embed.description += "\n⚠️ **Brak uczestników — konkurs anulowany.**"
        await konkurs_message.edit(embed=embed, view=None)
        return

    zwyciezca_id = choice(list(uczestnicy))
    zwyciezca = ctx.guild.get_member(zwyciezca_id)

    # Tworzenie roli, jeśli nie istnieje
    nagroda_rola = discord.utils.get(ctx.guild.roles, name="Wygrał Konkurs")
    if not nagroda_rola:
        nagroda_rola = await ctx.guild.create_role(name="Wygrał Konkurs")

    await zwyciezca.add_roles(nagroda_rola)

    embed.description += f"\n- 🏆 **Zwycięzca:** {zwyciezca.mention}!"
    await konkurs_message.edit(embed=embed, view=None)
    await ctx.send(f"🎉 Gratulacje {zwyciezca.mention}! Wygrałeś konkurs na: **{nagroda}** 🥳")

    # Zapisz dane do reroll
    last_konkurs_data[ctx.guild.id] = {
        "uczestnicy": uczestnicy,
        "nagroda": nagroda,
        "message": konkurs_message
    }

@bot.command(name="konkurs-reroll")
async def konkurs_reroll(ctx):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    data = last_konkurs_data.get(ctx.guild.id)
    if not data or not data["uczestnicy"]:
        return await ctx.reply("⚠️ Brak zapisanego konkursu do ponownego losowania.", delete_after=5)

    uczestnicy = data["uczestnicy"]
    nagroda = data["nagroda"]
    konkurs_message = data["message"]

    zwyciezca_id = choice(list(uczestnicy))
    zwyciezca = ctx.guild.get_member(zwyciezca_id)

    nagroda_rola = discord.utils.get(ctx.guild.roles, name="Wygrał Konkurs")
    if not nagroda_rola:
        nagroda_rola = await ctx.guild.create_role(name="Wygrał Konkurs")

    await zwyciezca.add_roles(nagroda_rola)

    # Aktualizacja embeda
    embed = konkurs_message.embeds[0]
    embed.description += f"\n- 🔁 **Nowy zwycięzca:** {zwyciezca.mention}!"
    await konkurs_message.edit(embed=embed)

    await ctx.send(f"🔁 Ponowne losowanie! Nowy zwycięzca: {zwyciezca.mention} 🎉")

CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
DOG_API_URL = "https://api.thedogapi.com/v1/images/search"

async def get_random_cat_image():
    async with aiohttp.ClientSession() as session:
        async with session.get(CAT_API_URL) as response:
            if response.status != 200:
                return None
            data = await response.json()
            return data[0]["url"] if data else None

async def get_random_dog_image():
    async with aiohttp.ClientSession() as session:
        async with session.get(DOG_API_URL) as response:
            if response.status != 200:
                return None
            data = await response.json()
            return data[0]["url"] if data else None

@bot.command()
async def kot(ctx):
    async with ctx.typing():
        image_url = await get_random_cat_image()
        if image_url:
            await ctx.send(f"🐱 Miau!\n{image_url}")
        else:
            await ctx.send("😿 Nie udało się pobrać obrazka kota.")

@bot.command()
async def pies(ctx):
    async with ctx.typing():
        image_url = await get_random_dog_image()
        if image_url:
            await ctx.send(f"🐶 Hau hau!\n{image_url}")
        else:
            await ctx.send("🐾 Nie udało się pobrać obrazka psa.")
class CloseTicketButton(Button):
    def __init__(self):
        super().__init__(label="Zamknij Ticket", style=discord.ButtonStyle.danger, emoji="🔒")

    async def callback(self, interaction: Interaction):
        has_permission = interaction.user == interaction.channel.topic or any(role.name in ALLOWED_ROLES for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("⛔ Nie masz uprawnień do zamknięcia tego ticketu!", ephemeral=True)
            return

        await interaction.response.send_message("✅ Ticket zostanie zamknięty za 5 sekund...", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

class TicketSelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="Pomoc Ogólna", description="Uzyskaj pomoc od administracji.", emoji="❓"),
            SelectOption(label="Zakup Rangi", description="Pomoc przy zakupie rangi.", emoji="💸"),
            SelectOption(label="Partnerstwo", description="Nawiązanie współpracy.", emoji="🤝"),
        ]
        super().__init__(placeholder="Wybierz kategorię ticketu...", options=options)

    async def callback(self, interaction: Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)

        if category is None:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        channel_name = f"ticket-{interaction.user.name}".replace(" ", "-").lower()
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        for role_name in ALLOWED_ROLES:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ticket_channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=str(interaction.user.id)  # zapisujemy ID użytkownika w topicu kanału
        )

        embed = discord.Embed(
            title=f"🎟️ Ticket - {self.values[0]}",
            description=f"Witaj {interaction.user.mention}! Opisz swój problem związany z **{self.values[0]}**.\nObsługa wkrótce odpowie!",
            color=discord.Color.blurple()
        )

        view = View()
        view.add_item(CloseTicketButton())

        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"🎟️ Twój ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.command()
async def send_panel(ctx):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        await ctx.reply("⛔ Nie masz uprawnień do wysyłania panelu ticketów!", delete_after=5)
        return

    embed = discord.Embed(
        title="🎟️ Panel Ticketów",
        description="Wybierz kategorię, aby otworzyć ticket.\nAdministracja wkrótce odpowie!",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=TicketPanel())
@bot.command()
async def unmute(ctx, member: discord.Member):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        await ctx.reply("⛔ Nie masz uprawnień do użycia tej komendy!", delete_after=5)
        return

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if mute_role is None:
        await ctx.reply("⚠️ Rola 'Muted' nie istnieje!", delete_after=5)
        return

    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.reply(f"🔈 {member.mention} został odmutowany!")
    else:
        await ctx.reply("⚠️ Ten użytkownik nie ma nadanej roli muta.", delete_after=5)
@bot.command()
async def unban(ctx, *, user: str):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)
    if not has_permission:
        return await ctx.reply("⛔ Nie masz uprawnień do tej komendy!", delete_after=5)

    # Szukanie bana
    async for ban_entry in ctx.guild.bans():
        banned_user = ban_entry.user
        if banned_user.name.lower() == user.lower() or banned_user.display_name.lower() == user.lower():
            await ctx.guild.unban(banned_user)
            await ctx.send(f"✅ Pomyślnie odbanowano {banned_user.name}!")
            return

    await ctx.reply("⚠️ Nie znaleziono użytkownika na liście banów.", delete_after=5)

@bot.command()
async def pomoc(ctx):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)

    if has_permission:
        embed = discord.Embed(
            title="📜 Lista komend dla Moderacji",
            description=(
                "**!ogloszenie <tytuł> <opis> <treść> <kolor> [obraz] [przyciski]** — Tworzy ogłoszenie\n"
                "**!ban <użytkownik> [czas w godzinach]** — Banuje użytkownika\n"
                "**!kick <użytkownik>** — Wyrzuca użytkownika\n"
                "**!clear <ilość>** — Czyści wiadomości\n"
                "**!mute <użytkownik> [czas w godzinach] [powód]** — Wycisza użytkownika\n"
                "**!unmute <użytkownik>** — Odcisza użytkownika\n"
                "**!unban <nazwa użytkownika>** — Odbanowuje użytkownika\n"
                "**!send_panel** — Wysyła panel ticketów\n"
                "**!konkurs <nagroda> [czas w godzinach]** — Tworzy konkurs\n"
                "**!konkurs-reroll** — Reroll zwycięzcy konkursu\n"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Komendy administracyjne | Sigma Bot")
    else:
        embed = discord.Embed(
            title="📜 Lista komend dla użytkowników",
            description=(
                "**!kot** — Losowy obrazek kota\n"
                "**!pies** — Losowy obrazek psa\n"
                "**!ping** — Pong\n"
                "**!info** — Informacje o bocie\n"
                "**!rangi** — Pokazuje informacje o rangach\n"
                "**!data** — Wysyła aktualną datę\n"
                "**!flip** — Rzut monetą\n"
                "**!server** — Informacje o serwerze\n"
                "**!roll { liczba }** — Losuje liczbę od 1 do { liczba }\n"
                "**!say { tekst }** — Piszę to co mu powiesz\n"
                "**!ship { @user1 } { @user2 }** — Sprawdza dopasowanie między osobami\n"
                "**!level** — Pokazuje twój level\n"
                "**!top** — Ranging Top 10 osób z najwyższym expem\n"
                "**!nagroda** — Odbierz exp co 24h\n"
                "**/hello** — Bot odpowiada Hello!\n"
                "🎟️ Otwórz ticket za pomocą przycisku z panelu ticketów!"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Komendy użytkownika | Sigma Bot")

    await ctx.send(embed=embed)
@bot.command()
async def ping(ctx):
    start_time = time.time()  # Zapisujemy czas przed wysłaniem wiadomości
    message = await ctx.reply("Pong. Opóźnienie: ...")  # Bot wysyła odpowiedź
    end_time = time.time()  # Zapisujemy czas po wysłaniu wiadomości
    latency = round((end_time - start_time) * 1000)  # Mierzymy opóźnienie w milisekundach
    await message.edit(content=f"Pong. Opóźnienie: {latency}ms")  # Edytujemy wiadomość z opóźnieniem
@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Informacje o bocie", description="Dicord Boty na zamówienie, indywidualne funkcje", color=discord.Color.red())
    embed.add_field(name="Nazwa bota", value=bot.user.name, inline=False)
    embed.add_field(name="ID bota", value=bot.user.id, inline=False)
    embed.add_field(name="Twórca", value="Young Mikoczan & DawidXT", inline=False)
    embed.add_field(name="Prefix", value="?", inline=False)
    embed.set_footer(text="Dzięki za używanie mojego bota!")
    await ctx.reply(embed=embed)
@bot.command()
async def flip(ctx):
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.reply(f"Rzut monetą: {result}")
@bot.command()
async def data(ctx):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"📅 Aktualna data i godzina: **{now}**")
# Komenda /hello (slash command)
@bot.tree.command(name="hello", description="Bot odpowiada 'Hello!'")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello Witaj! na serwerze MAGMA TEAM")


@bot.command()
async def server(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=f"🌐 Informacje o serwerze: {guild.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    embed.add_field(name="📅 Data utworzenia", value=guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    embed.add_field(name="👑 Właściciel", value="Mikoczan", inline=False)
    embed.add_field(name="👥 Ilość członków", value=guild.member_count, inline=False)
    embed.add_field(name="💬 Kanały tekstowe", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊 Kanały głosowe", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="🎭 Role", value=len(guild.roles), inline=False)
    embed.set_footer(text=f"ID serwera: {guild.id}")

    await ctx.send(embed=embed)

# Synchronizacja komend ukośnika
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="MAGMA TEAM - Autoclikcer"))
    try:
        # Synchronizacja komend ukośnika
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend/e ukośnika.")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

    print(f"Bot zalogowany jako {bot.user}")
    print(f"Bot stworzony przez young mikoczana i DawidXT")
# !say
@bot.command()
async def say(ctx, *, text: str):
    # Usuwamy potencjalne "@everyone" i "@here" oraz wzmianki
    safe_text = text.replace('@everyone', 'everyone').replace('@here', 'here')
    safe_text = discord.utils.escape_mentions(safe_text)
    await ctx.send(safe_text)

# !roll
@bot.command()
async def roll(ctx, max_number: int = 100):
    if max_number < 1:
        await ctx.send("Podaj liczbę większą niż 0!")
        return
    rolled_number = random.randint(1, max_number)
    await ctx.send(f"🎲 {ctx.author.mention} wylosował **{rolled_number}** z 1 do {max_number}!")

# !ship
@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    compatibility = random.randint(0, 100)
    ship_message = ""
    if compatibility > 80:
        ship_message = "❤️ Idealna para! ❤️"
    elif compatibility > 50:
        ship_message = "💖 Coś z tego może być!"
    elif compatibility > 30:
        ship_message = "💔 Trochę ciężko, ale kto wie?"
    else:
        ship_message = "❌ Raczej nic z tego..."
    
    await ctx.send(f"**{user1.display_name}** ❤️ **{user2.display_name}**\n"
                   f"💘 Dopasowanie: **{compatibility}%**\n{ship_message}")


# --- SYSTEM LEVELI ---
user_data = {}
try:
    if os.path.exists('user_data.json') and os.path.getsize('user_data.json') > 0:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
    else:
        user_data = {}
except json.JSONDecodeError:
    print("⚠️ Błąd przy ładowaniu user_data.json - plik uszkodzony. Tworzę nowy.")
    user_data = {}


def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

def get_exp_for_next_level(level):
    return 100 + (level - 1) * 20

# --- ANTI-SYSTEM ---

bad_words = ["kurwa", "chuj", "pizda", "jebac", "skurwysyn"]
allowed_roles_names = ALLOWED_ROLES # Rangi które mogą wysyłać invite

user_violations = {}  # user_id: count of violations

async def mute_user(guild, member, duration_hours):
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if not mute_role:
        mute_role = await guild.create_role(name="Muted", reason="Tworzenie roli do mute")
        for channel in guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)

    await member.add_roles(mute_role)
    await asyncio.sleep(duration_hours * 3600)
    await member.remove_roles(mute_role)

# --- EVENT: on_message ---

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    guild = message.guild

    # --- ANTI-INVITE ---
    if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
        allowed = False
        for role in message.author.roles:
            if role.name in allowed_roles_names:
                allowed = True
                break
        if not allowed:
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, zaproszenia są zakazane!")
            await register_violation(message.author)
            return

    # --- ANTI-SPOILER ---
    if "||" in message.content:
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, spoilery są niedozwolone!")
        await register_violation(message.author)
        return

    # --- ANTI-BADWORDS ---
    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, używasz zakazanych słów!")
        await register_violation(message.author)
        return

    # --- SYSTEM LEVELI ---
    if user_id not in user_data:
        user_data[user_id] = {'exp': 0, 'level': 1, 'last_reward': "2000-01-01"}

    exp_gain = random.randint(5, 15)
    user_data[user_id]['exp'] += exp_gain
    save_user_data()

    current_level = user_data[user_id]['level']
    exp_needed = get_exp_for_next_level(current_level)

    while user_data[user_id]['exp'] >= exp_needed:
        user_data[user_id]['exp'] -= exp_needed
        user_data[user_id]['level'] += 1
        save_user_data()

        new_level = user_data[user_id]['level']

        await message.channel.send(
            f"🎉 {message.author.mention}, gratulacje! Awansowałeś na **poziom {new_level}**! 🚀"
        )

        role_name = None
        if new_level >= 20:
            role_name = "Diamond"
        elif new_level >= 10:
            role_name = "Gold"
        elif new_level >= 5:
            role_name = "Silver"

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)

            if not role:
                color = {
                    "Silver": discord.Color.from_rgb(192, 192, 192),
                    "Gold": discord.Color.gold(),
                    "Diamond": discord.Color.teal()
                }.get(role_name, discord.Color.default())

                role = await guild.create_role(
                    name=role_name,
                    colour=color,
                    reason="Automatyczne tworzenie roli za awans"
                )

                bot_member = guild.get_member(bot.user.id)
                bot_top_role = bot_member.top_role
                await role.edit(position=bot_top_role.position - 1)

            remove_roles = []
            if role_name == "Gold":
                remove_roles.append(discord.utils.get(guild.roles, name="Silver"))
            elif role_name == "Diamond":
                remove_roles.append(discord.utils.get(guild.roles, name="Silver"))
                remove_roles.append(discord.utils.get(guild.roles, name="Gold"))

            for r in remove_roles:
                if r and r in message.author.roles:
                    await message.author.remove_roles(r)

            if role not in message.author.roles:
                await message.author.add_roles(role)
                await message.channel.send(
                    f"🏅 {message.author.mention} otrzymuje rangę **{role_name}**!"
                )

        exp_needed = get_exp_for_next_level(new_level)

    await bot.process_commands(message)

# --- FUNKCJE POMOCNICZE ---

async def register_violation(member):
    user_id = str(member.id)
    user_violations[user_id] = user_violations.get(user_id, 0) + 1

    if user_violations[user_id] >= 5:
        await member.send("🚫 Złamałeś zasady kilka razy. Otrzymujesz godzinnego mute.")
        await mute_user(member.guild, member, 1)
        user_violations[user_id] = 0

# --- KOMENDY ---

@bot.command()
async def nagroda(ctx):
    user_id = str(ctx.author.id)

    if user_id not in user_data:
        user_data[user_id] = {'exp': 0, 'level': 1, 'last_reward': "2000-01-01"}
        save_user_data()

    last_reward = datetime.datetime.strptime(user_data[user_id]['last_reward'], "%Y-%m-%d")
    now = datetime.datetime.utcnow()

    if (now - last_reward).days >= 1:
        user_data[user_id]['exp'] += 10
        user_data[user_id]['last_reward'] = now.strftime("%Y-%m-%d")
        save_user_data()
        await ctx.send(f"🎁 {ctx.author.mention} odebrałeś swoją dzienną nagrodę +10 EXP!")
    else:
        await ctx.send(f"⏳ {ctx.author.mention} musisz poczekać do jutra, aby odebrać kolejną nagrodę!")

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)

    if user_id not in user_data:
        user_data[user_id] = {'exp': 0, 'level': 1, 'last_reward': "2000-01-01"}
        save_user_data()

    level = user_data[user_id]['level']
    exp = user_data[user_id]['exp']
    exp_needed = get_exp_for_next_level(level)

    progress = int((exp / exp_needed) * 10)
    bar = '█' * progress + '░' * (10 - progress)

    embed = discord.Embed(
        title=f"📈 Poziom {member.display_name}",
        description=(
            f"Poziom: **{level}**\n"
            f"EXP: **{exp}/{exp_needed}**\n"
            f"Postęp: `{bar}` {int((exp/exp_needed)*100)}%"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    if not user_data:
        await ctx.send("Brak danych o poziomach. 😔")
        return

    sorted_users = sorted(
        user_data.items(),
        key=lambda x: (x[1]['level'], x[1]['exp']),
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 Ranking graczy",
        description="TOP 10 użytkowników z największym levelem!",
        color=discord.Color.gold()
    )

    medals = ["🥇", "🥈", "🥉"]

    user_rank = None
    for idx, (user_id, data) in enumerate(sorted_users, start=1):
        user_id_int = int(user_id)
        if user_id_int == ctx.author.id:
            user_rank = idx

        if idx <= 10:
            member = ctx.guild.get_member(user_id_int)
            name = member.display_name if member else f"User ID: {user_id}"
            medal = medals[idx-1] if idx <= len(medals) else f"#{idx}"
            embed.add_field(
                name=f"{medal} {name}",
                value=f"Poziom: **{data['level']}** | EXP: **{data['exp']}**",
                inline=False
            )

    if user_rank:
        embed.set_footer(text=f"Twoja pozycja: #{user_rank}")
    else:
        embed.set_footer(text="Nie masz jeszcze poziomu. 😔")

    await ctx.send(embed=embed)

@bot.command()
async def rangi(ctx):
    embed = discord.Embed(
        title="🏅 Dostępne Rangi",
        description="Oto rangi, które możesz zdobyć za zdobywanie poziomów!",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🥈 Silver",
        value="Zdobywasz na **poziomie 5**.\nKolor: Srebrny 🥈",
        inline=False
    )
    embed.add_field(
        name="🥇 Gold",
        value="Zdobywasz na **poziomie 10**.\nKolor: Złoty 🥇",
        inline=False
    )
    embed.add_field(
        name="💎 Diamond",
        value="Zdobywasz na **poziomie 20**.\nKolor: Turkusowy 💎",
        inline=False
    )

    embed.set_footer(text="Im wyższy poziom, tym lepsza ranga! 🚀")
    
    await ctx.send(embed=embed)
JOKES = [
    "Pisanie w C to jak używanie maszynowego – niby szybkie, ale każda literówka kończy się katastrofą.",
    "Python jest jak rower z automatyczną skrzynią biegów, a C++ jak samolot bojowy – oba dojadą do celu, ale różnica w obsłudze jest spora.",
    "Java to jedyny język, w którym 'Hello World' zajmuje pół strony kodu.",
    "Dlaczego programiści nie lubią JavaScriptu? Bo '== null' zwraca true dla dwóch różnych wartości!",
    "Kod w PHP działa… dopóki go nie dotkniesz.",
    "C++ daje ci nieograniczoną moc. C++ również daje ci nieograniczoną ilość błędów.",
    "Go jest jak Uber – szybki i bezpieczny, ale i tak każdy wraca do własnego samochodu, czyli Pythona.",
    "Assembler jest jak gotowanie na ognisku – super dla survivalowców, ale większość woli mikrofalówkę.",
    "Kiedy programista mówi, że lubi Rust, to albo jest geniuszem, albo jeszcze nie próbował pisać w nim większego projektu.",
    "Jak odróżnić początkującego programistę Javy od eksperta? Początkujący pisze jeden obiekt na 100 linii, ekspert 100 obiektów w jednej linii.",
    "Dlaczego blondynka otwiera mleko w sklepie? Bo na opakowaniu jest napisane 'Otwierać tutaj'!",
    "Dlaczego blondynka stoi pod drzewem z kartką i długopisem? Bo chce zrobić notatkę z cienia!",
    "Blondynka dzwoni na lotnisko: 'Ile trwa lot z Warszawy do Londynu?' - 'Chwileczkę' - 'Dziękuję!' *rozłącza się*",
    "Dlaczego blondynka wkłada zegarek do lodówki? Żeby mieć zimny czas!",
    "Co robi blondynka, gdy komputer wyświetla 'Naciśnij dowolny klawisz'? Szuka klawisza 'Dowolny'.",
    "Dlaczego rudy nie może być iluzjonistą? Bo nie ma w nim żadnej magii!",
    "Rudy na rozmowie o pracę: 'Czy jestem kreatywny? Mam włosy w kolorze ognia, a duszę lodowatą!'",
    "Dlaczego rudy kupił czerwoną koszulkę? Żeby wtopić się w tłum.",
    "Co mówi rudy, gdy wyjdzie na słońce? 'Spłonę szybciej niż węgiel w piecu!'",
    "Jak rozpoznać rudego na imprezie? Nie trzeba – i tak wyróżnia się w tłumie!",
    "Doktorze, mam dla pana dwie wiadomości: dobrą i złą.– Dawaj pan złą…– Operacja się udała, ale pacjent nie przeżył.– A dobra?– Możemy go oddać na organy.",
    "Tato, tato! W szkole mówią, że jestem wampirem!– No to chodź synku, zjedz obiad.– Ale ja nie lubię krwi…– A kto mówił, że to twoja krew?",
    "– Dzień dobry, chciałbym zgłosić zaginięcie żony.– Od kiedy jej pan nie widział?– Od tygodnia.– A czemu pan zgłasza dopiero teraz?– Bo zaczęły mi się kończyć czyste talerze.",
    "Mama zawsze mówiła mi, żebym patrzył pod nogi, kiedy przechodzę przez ulicę.Nie wiem po co, ale teraz widzę własne wnętrzności z bardzo ciekawej perspektywy.",
    "– Proszę księdza, czy jest szansa, że po śmierci pójdę do nieba?– Oczywiście, synu. Biorąc pod uwagę twoją jazdę samochodem, myślę, że wkrótce się przekonasz.",
     "Mama mówiła mi, że nie powinienem sikać do basenu… Ale skąd miałem wiedzieć, że widzą to wszyscy w tej windzie?",
    "– Tato, mogę iść do toalety? – Idź, synu, ale po cichu… – To nie ja decyduję, jak głośno będzie chlupać.",
    "Życie jest jak sraczka… Czasem biegniesz do celu, a czasem wszystko się sypie w najmniej oczekiwanym momencie.",
    "Sikanie pod prysznicem to jak oszczędzanie wody… Dopóki nie jesteś w publicznym basenie.",
    "Kiedyś wypadła mi do kibla moneta… Pomyślałem: *Nie warto jej wyciągać.* Potem wypadł mi telefon. *Teraz warto.*"
]
# Komenda JOKE
@bot.command()
async def joke(ctx):
    joke = random.choice(JOKES)
    await ctx.send(f"😂 {joke}")
bot.run("YOUR TOKEN")
