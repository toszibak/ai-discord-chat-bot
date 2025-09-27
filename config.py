import discord
from discord.ext import commands

# Discord Bot Token
BOT_TOKEN = "YOUR_TOKEN"

# Google Gemini API Key  
AI_API_KEY = "YOUR_TOKEN"

# Model AI do użycia
AI_MODEL = "gemini-2.5-flash"

# Maksymalna długość historii (liczba wiadomości)
AI_MAX_HISTORY = 20

# Kolory dla embed wiadomości
COLORS = {
    'SUCCESS': discord.Color.green(),
    'ERROR': discord.Color.red(),
    'WARNING': discord.Color.orange(),
    'INFO': discord.Color.blue(),
}
