import discord
from discord.ext import commands
import time
import random
import asyncio
from datetime import datetime

# Zdefiniowanie intents
intents = discord.Intents.all()
intents.message_content = True 

# Tworzenie instancji bota
bot = commands.Bot(command_prefix="?", intents=intents)

# ✅ LISTA ŻARTÓW
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


# ✅ Komenda ping
@bot.command()
async def ping(ctx):
    start_time = time.time()  # Zapisujemy czas przed wysłaniem wiadomości
    message = await ctx.reply("Pong. Opóźnienie: ...")  # Bot wysyła odpowiedź
    end_time = time.time()  # Zapisujemy czas po wysłaniu wiadomości
    latency = round((end_time - start_time) * 1000)  # Mierzymy opóźnienie w milisekundach
    await message.edit(content=f"Pong. Opóźnienie: {latency}ms")  # Edytujemy wiadomość z opóźnieniem

# Komenda bot-info
@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Informacje o bocie", description="Dicord Boty na zamówienie, indywidualne funkcje", color=discord.Color.blue())
    embed.add_field(name="Nazwa bota", value=bot.user.name, inline=False)
    embed.add_field(name="ID bota", value=bot.user.id, inline=False)
    embed.add_field(name="Twórca", value="Young Mikoczan", inline=False)
    embed.add_field(name="Prefix", value="?", inline=False)
    embed.set_footer(text="Dzięki za używanie mojego bota!")
    await ctx.reply(embed=embed)

# Komenda flip - rzut monetą
@bot.command()
async def flip(ctx):
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.reply(f"Rzut monetą: {result}")

# Lista ról, które mogą wykonywać komendę
ALLOWED_ROLES = ["⭐◽ Admin", "🔴◽ Moderator", "👑◽ Właściciel", "💠◽ DEVELOPER"]

# Mapowanie nazw kolorów na wartości HEX
COLOR_MAP = {
    "blue": 0x3498db,
    "red": 0xe74c3c,
    "purple": 0x9b59b6
}

@bot.command()
async def ogloszenie(ctx, tytul: str, opis: str, tresc: str, kolor: str):
    has_permission = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)

    if not has_permission:
        await ctx.reply("⛔ Nie masz uprawnień do tworzenia ogłoszeń!", delete_after=5)
        return

    kolor = kolor.lower()
    if kolor not in COLOR_MAP:
        await ctx.reply("⚠️ Niepoprawny kolor! Użyj: `blue`, `red` lub `purple`.", delete_after=5)
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        await ctx.reply("⚠️ Nie mam uprawnień do usuwania wiadomości!", delete_after=5)
        return

    embed = discord.Embed(title=tytul, description=opis, color=COLOR_MAP[kolor])
    embed.add_field(name="📢 Ogłoszenie", value=tresc, inline=False)
    embed.set_footer(text=f"Ogłoszenie dodane przez: {ctx.author.name}")

    await ctx.send(embed=embed)

# Komenda TEMP MUTE
@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time: int):
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 {member.mention} został wyciszony na {time} minut.")

    await asyncio.sleep(time * 60)
    await member.remove_roles(role)
    await ctx.send(f"🔊 {member.mention} został odciszony.")

# Komenda CLEAR
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Usunięto {amount} wiadomości.", delete_after=3)

# Komenda DATA
@bot.command()
async def data(ctx):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"📅 Aktualna data i godzina: **{now}**")

# Komenda JOKE
@bot.command()
async def joke(ctx):
    joke = random.choice(JOKES)
    await ctx.send(f"😂 {joke}")

# Komenda /hello (slash command)
@bot.tree.command(name="hello", description="Bot odpowiada 'Hello!'")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")

# Synchronizacja komend ukośnika
@bot.event
async def on_ready():
    try:
        # Synchronizacja komend ukośnika
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend ukośnika.")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

    print(f"Bot zalogowany jako {bot.user}")

bot.run("MTM1NTI1ODI1NTM5NTUyNDgyOA.Gzxurw.mGpMnhwQnQWiWDQL9Eq0QW-2F1usvnimY6sw4w")
