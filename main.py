import discord
from discord.ext import commands
from google import genai
from google.genai import types
from config import COLORS, AI_API_KEY, AI_MAX_HISTORY, AI_MODEL, BOT_TOKEN

# Inicjalizacja bota
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Zmienne globalne
chat_history = {}
ai_client = None

def split_message(text, max_length=2000):
    """Dzieli długą wiadomość na części mniejsze niż max_length znaków"""
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    # Dziel po liniach, żeby zachować formatowanie
    lines = text.split('\n')

    for line in lines:
        # Jeśli linia jest dłuższa niż limit, podziel ją na słowa
        if len(line) > max_length:
            words = line.split(' ')
            current_line = ""

            for word in words:
                if len(current_line + word + " ") > max_length:
                    if current_line:
                        if len(current_chunk + current_line + "\n") > max_length:
                            chunks.append(current_chunk.rstrip())
                            current_chunk = current_line + "\n"
                        else:
                            current_chunk += current_line + "\n"
                        current_line = word + " "
                    else:
                        # Słowo jest dłuższe niż limit - przytnij je
                        chunks.append(word[:max_length-3] + "...")
                        current_line = ""
                else:
                    current_line += word + " "

            if current_line:
                if len(current_chunk + current_line + "\n") > max_length:
                    chunks.append(current_chunk.rstrip())
                    current_chunk = current_line + "\n"
                else:
                    current_chunk += current_line + "\n"
        else:
            # Sprawdź czy dodanie linii nie przekroczy limitu
            if len(current_chunk + line + "\n") > max_length:
                chunks.append(current_chunk.rstrip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk.rstrip())

    return chunks

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='ask', aliases=['ai', 'chat'])
async def ask_ai(ctx, *, prompt: str):
    """Zadaj pytanie AI asystentowi Pimpkowi"""
    global ai_client, chat_history

    # Inicjalizacja klienta AI w funkcji ask
    if not ai_client:
        if not AI_API_KEY:
            embed = discord.Embed(
                title="❌ AI niedostępne",
                description="Klucz API nie jest skonfigurowany. Skontaktuj się z administratorem.",
                color=COLORS['ERROR']
            )
            await ctx.send(embed=embed)
            return

        try:
            ai_client = genai.Client(api_key=AI_API_KEY)
            # print("✅ Klient AI zainicjalizowany pomyślnie")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Błąd inicjalizacji AI",
                description=f"Nie udało się zainicjalizować AI: {str(e)[:100]}...",
                color=COLORS['ERROR']
            )
            await ctx.send(embed=embed)
            print(f"❌ Błąd inicjalizacji AI: {e}")
            return

    # Sprawdź długość promptu
    if len(prompt) > 2000:
        embed = discord.Embed(
            title="❌ Zbyt długie pytanie",
            description="Twoje pytanie jest zbyt długie. Maksymalna długość to 2000 znaków.",
            color=COLORS['ERROR']
        )
        await ctx.send(embed=embed)
        return

    user_id = ctx.author.id

    # Inicjalizuj historię dla użytkownika jeśli nie istnieje
    if user_id not in chat_history:
        chat_history[user_id] = []

    # Sprawdzamy, czy użytkownik na coś odpowiada
    if (ctx.message.reference and
            ctx.message.reference.resolved and
            isinstance(ctx.message.reference.resolved, discord.Message)):

        replied_to_message = ctx.message.reference.resolved
        replied_to_author_id = replied_to_message.author.id
        replied_to_content = replied_to_message.content

        # Dodajemy informację o odpowiadanej wiadomości do historii
        chat_history[user_id].append(
            f"{replied_to_author_id}: (Odpowiedź na wiadomość) {replied_to_content}"
        )
        chat_history[user_id].append(f"{user_id}: {prompt}")
    else:
        # Jeśli nie odpowiada, dodajemy tylko jego prompt
        chat_history[user_id].append(f"{user_id}: {prompt}")

    # Zachowaj tylko ostatnie 14 wiadomości dla kontekstu
    context = "\n".join(chat_history[user_id][-14:])

    # Instrukcja systemowa dla AI
    system_instruction = f"""Jesteś AI asystentem, który pomaga użytkownikom. Nazywasz się Pimpek. Lubisz żartować. Odpowiadaj w wesoły sposób.
    Aby oznaczyć użytkownika na Discordzie, użyj jego ID w formacie <@ID_użytkownika>.
    Na przykład, aby oznaczyć użytkownika o ID 1234567890, napisz <@1234567890>.
    Id użytkownika masz w historii rozmów (zwróć uwagę na '(ID: ...)'):\n
    {context}; nie musisz mówić 'Pimpek: ' na samym początku. Witaj się tylko wtedy gdy użytkownik się z tobą przywita"""

    # Użyj typing zamiast emoji reakcji
    async with ctx.typing():
        try:
            # Generuj odpowiedź AI
            response = ai_client.models.generate_content(
                model=AI_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                ),
                contents=[prompt]
            )

            response_text = response.text

            # Podziel długie odpowiedzi na części z bezpiecznym limitem
            chunks = split_message(response_text, max_length=1900)  # 1900 zamiast 2000 dla bezpieczeństwa
            num_chunks = len(chunks)

            # Wyślij odpowiedź
            for i, chunk in enumerate(chunks):
                if num_chunks > 1:
                    content = f"{chunk}\n\n*Część ({i + 1}/{num_chunks})*"
                    # Sprawdź czy dodanie numeru części nie przekracza limitu
                    if len(content) > 2000:
                        content = chunk  # Wyślij bez numeru części
                else:
                    content = chunk

                if i == 0:
                    await ctx.reply(content, mention_author=True)
                else:
                    await ctx.send(content)

            # Dodaj odpowiedź do historii
            chat_history[user_id].append(f"Pimpek: {response_text}")

            # Ogranicz historię do 20 ostatnich wiadomości
            if len(chat_history[user_id]) > AI_MAX_HISTORY:
                chat_history[user_id] = chat_history[user_id][-20:]

        except Exception as e:
            embed = discord.Embed(
                title="❌ Błąd AI",
                description=f"Wystąpił błąd podczas generowania odpowiedzi: {str(e)[:100]}...",
                color=COLORS['ERROR']
            )
            await ctx.send(embed=embed)
            print(f"Błąd AI dla użytkownika {ctx.author}: {e}")

@bot.command(name='clear_history', aliases=['clear_chat', 'reset_ai'])
async def clear_user_history(ctx):
    """Wyczyść swoją historię czatu z AI"""
    global chat_history
    user_id = ctx.author.id

    if user_id in chat_history:
        del chat_history[user_id]
        embed = discord.Embed(
            title="🗑️ Historia wyczyszczona",
            description=f"{ctx.author.mention} Twoja historia czatu z AI została wyczyszczona!",
            color=COLORS['SUCCESS']
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Brak historii",
            description=f"{ctx.author.mention} Nie masz historii czatu do wyczyszczenia.",
            color=COLORS['INFO']
        )

    await ctx.send(embed=embed)

@bot.command(name='clear_all_history')
@commands.has_permissions(administrator=True)
async def clear_all_history(ctx):
    """Wyczyść historię czatu wszystkich użytkowników (tylko admin)"""
    global chat_history
    chat_history.clear()

    embed = discord.Embed(
        title="🗑️ Wszystkie historie wyczyszczone",
        description="Historia czatu dla wszystkich użytkowników została wyczyszczona!",
        color=COLORS['SUCCESS']
    )
    await ctx.send(embed=embed)

@clear_all_history.error
async def clear_all_history_error(ctx, error):
    """Obsługa błędów dla clear_all_history"""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Brak uprawnień",
            description="Tylko administratorzy mogą wyczyścić historię wszystkich użytkowników.",
            color=COLORS['ERROR']
        )
        await ctx.send(embed=embed)

# Uruchomienie bota
if __name__ == "__main__":
    bot.run(BOT_TOKEN)