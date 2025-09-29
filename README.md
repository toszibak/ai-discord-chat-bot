# Dokumentacja Discord Bot z AI

Bot Discord integrujący AI asystenta Google Gemini, który umożliwia prowadzenie naturalnych rozmów z użytkownikami na serwerze Discord.

## Instalacja wymaganych bibliotek

### Wymagania systemowe
- **Python 3.8 lub wyższy**
- Aktywne połączenie internetowe
- Konto Discord Developer Portal
- Klucz API Google Gemini

### Instalacja bibliotek

**Podstawowe biblioteki:**
```bash
pip install discord.py
pip install google-genai
```

**Dla systemów Linux/macOS:**
```bash
python3 -m pip install -U discord.py
python3 -m pip install -U google-genai
```

**Dla Windows:**
```bash
py -3 -m pip install -U discord.py
py -3 -m pip install -U google-genai
```

### Środowisko wirtualne (zalecane)

Zaleca się używanie środowiska wirtualnego, aby uniknąć konfliktów między bibliotekami :

```bash
# Tworzenie środowiska wirtualnego
python -m venv bot-env

# Aktywacja (Linux/macOS)
source bot-env/bin/activate

# Aktywacja (Windows)
bot-env\Scripts\activate.bat

# Instalacja bibliotek w środowisku wirtualnym
pip install discord.py google-genai
```

### Opis bibliotek

#### discord.py
- **Wersja:** 2.6.3 (najnowsza)
- **Funkcja:** Wrapper API Discord umożliwiający łatwą integrację z platformą
- **Funkcjonalności:** obsługa komend, eventów, embedów, zarządzanie serwerem
- **Licencja:** MIT

#### google-genai
- **Funkcja:** Oficjalna biblioteka Google do integracji z Gemini API
- **Funkcjonalności:** generowanie tekstu, obsługa różnych modeli Gemini, streaming odpowiedzi
- **Obsługuje:** wszystkie modele Gemini 2.5 Flash, Pro, i inne warianty

## Przegląd plików

### config.py
Zawiera wszystkie ustawienia bota, które można łatwo modyfikować bez ingerencji w główny kod.

### main.py
Główny plik zawierający logikę bota Discord i integrację z API Google Gemini.

## Szczegółowy opis funkcjonalności

### Konfiguracja (config.py)

```python
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
```

**Modyfikowalne parametry:**
- `BOT_TOKEN` - token bota Discord
- `AI_API_KEY` - klucz API Google Gemini
- `AI_MODEL` - model AI (dostępne modele opisane poniżej)
- `AI_MAX_HISTORY` - maksymalna liczba wiadomości w historii (domyślnie 20)
- `COLORS` - kolory komunikatów embed

## Dostępne modele Google Gemini w darmowym planie

### Najważniejsze modele dostępne za darmo

#### Gemini 2.5 Flash
**Model zalecanany do botów Discord**
- **Kod modelu:** `gemini-2.5-flash`
- **Limity darmowe:** 15 zapytań/minutę, 1500 zapytań/dzień
- **Okno kontekstowe:** 1,048,576 tokenów
- **Obsługuje:** tekst, obrazy, wideo, audio
- **Najlepszy dla:** szybkich odpowiedzi, wysokiej wydajności, zadań wymagających myślenia

#### Gemini 2.5 Flash-Lite
**Najszybszy model z serii Flash**
- **Kod modelu:** `gemini-2.5-flash-lite`
- **Limity darmowe:** wyższe niż Flash (optymalizowany pod wydajność)
- **Okno kontekstowe:** 1,048,576 tokenów
- **Obsługuje:** tekst, obrazy, wideo, audio, PDF
- **Najlepszy dla:** wysokiej przepustowości, zadań wymagających szybkości

#### Gemini 2.5 Pro
**Najbardziej zaawansowany model**
- **Kod modelu:** `gemini-2.5-pro`
- **Limity darmowe:** 5 zapytań/minutę, 25 zapytań/dzień
- **Okno kontekstowe:** 1,048,576 tokenów
- **Obsługuje:** audio, obrazy, wideo, tekst, PDF
- **Najlepszy dla:** złożonych zadań programistycznych, matematycznych, analizy dokumentów

### Modele specjalistyczne (dostępne za darmo z ograniczeniami)

#### Gemini 2.5 Flash Image
- **Kod modelu:** `gemini-2.5-flash-image-preview`
- **Funkcja:** generowanie i edycja obrazów
- **Okno kontekstowe:** 32,768 tokenów

#### Gemini 2.0 Flash
- **Kod modelu:** `gemini-2.0-flash`
- **Starszy model z natywną obsługą narzędzi
- **Okno kontekstowe:** 1,048,576 tokenów

### Limity darmowego planu (2025)

**Ogólne ograniczenia:**
- **Gemini 2.5 Flash:** 15 zapytań/minutę, 1500 zapytań/dzień
- **Gemini 2.5 Pro:** 5 zapytań/minutę, 25 zapytań/dzień
- **Token limit:** 250,000 tokenów/minutę
- **Użycie komercyjne:** dozwolone w ramach darmowego planu

### Rekomendacje modeli dla botów Discord

**Dla większości zastosowań:**
```python
AI_MODEL = "gemini-2.5-flash"
```

**Dla botów z wysokim ruchem:**
```python
AI_MODEL = "gemini-2.5-flash-lite"
```

**Dla zaawansowanych zadań (niski ruch):**
```python
AI_MODEL = "gemini-2.5-pro"
```

Modele automatycznie przełączają się między wariantami w zależności od obciążenia i typu zapytań, co optymalizuje wydajność.

### Inicjalizacja bota

```python
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
```

Bot wykorzystuje prefix `!` dla komend i wymaga uprawnień do odczytu treści wiadomości.

### Funkcja dzielenia wiadomości

```python
def split_message(text, max_length=2000):
```

**Odpowiada za:**
- Dzielenie długich odpowiedzi AI na fragmenty mniejsze niż 2000 znaków
- Zachowanie formatowania tekstu przy podziale
- Obsługę słów dłuższych niż limit

**Modyfikacje:**
- Zmiana `max_length` dla różnych limitów długości wiadomości

### Główna komenda AI

```python
@bot.command(name='ask', aliases=['ai', 'chat'])
async def ask_ai(ctx, *, prompt: str):
```

**Funkcjonalność:**
- Obsługuje komendy: `!ask`, `!ai`, `!chat`
- Inicjalizuje klienta AI przy pierwszym użyciu
- Sprawdza długość promptu (limit 2000 znaków)
- Zarządza historią rozmowy dla każdego użytkownika
- Obsługuje odpowiedzi na inne wiadomości
- Dzieli długie odpowiedzi na części

**Instrukcja systemowa dla AI:**
```python
system_instruction = f"""Jesteś AI asystentem, który pomaga użytkownikom. Nazywasz się Pimpek. Lubisz żartować. Odpowiadaj w wesoły sposób.
Aby oznaczyć użytkownika na Discordzie, użyj jego ID w formacie <@ID_użytkownika>."""
```

**Modyfikacje:**
- Zmiana nazwy i osobowości AI w `system_instruction`
- Dostosowanie limitów długości promptu
- Modyfikacja sposobu obsługi historii rozmowy

### Komendy zarządzania historią

#### Czyszczenie historii użytkownika
```python
@bot.command(name='clear_history', aliases=['clear_chat', 'reset_ai'])
async def clear_user_history(ctx):
```

**Funkcje:**
- `!clear_history`, `!clear_chat`, `!reset_ai`
- Usuwa historię rozmowy konkretnego użytkownika

#### Czyszczenie wszystkich historii (admin)
```python
@bot.command(name='clear_all_history')
@commands.has_permissions(administrator=True)
async def clear_all_history(ctx):
```

**Funkcje:**
- `!clear_all_history`
- Wymaga uprawnień administratora
- Usuwa historie wszystkich użytkowników
- Zawiera obsługę błędów dla brakujących uprawnień

## Zarządzanie danymi

### Historia rozmowy
```python
chat_history = {}
```

Bot przechowuje historię rozmowy w słowniku, gdzie:
- Klucz: ID użytkownika Discord
- Wartość: lista wiadomości w formacie `"ID: treść"`

Historia jest automatycznie ograniczana do ostatnich 20 wiadomości (konfigurowane przez `AI_MAX_HISTORY`).

### Klient AI
```python
ai_client = None
```

Klient Google Gemini jest inicjalizowany przy pierwszym użyciu komendy `!ask` i pozostaje aktywny przez cały czas działania bota.

## Możliwe modyfikacje

### Personalizacja AI
- Zmiana instrukcji systemowej w funkcji `ask_ai()`
- Dostosowanie parametrów generowania odpowiedzi
- Modyfikacja modelu AI w pliku config.py
- Wybór odpowiedniego modelu Gemini w zależności od potrzeb

### Rozszerzenie funkcjonalności
- Dodanie nowych komend Discord
- Implementacja różnych trybów AI
- Zapisywanie historii do pliku/bazy danych
- Dodanie komend moderacyjnych

### Optymalizacja wydajności
- Zmiana limitu historii (`AI_MAX_HISTORY`)
- Modyfikacja sposobu dzielenia wiadomości
- Implementacja cache'owania odpowiedzi
- Wybór szybszego modelu (`gemini-2.5-flash-lite`) dla wysokiego ruchu

### Zabezpieczenia
- Dodanie filtru treści
- Implementacja rate limitingu
- Rozszerzenie systemu uprawnień
- Monitorowanie limitów API w czasie rzeczywistym

Bot wymaga aktywnych tokenów Discord i Google Gemini API do poprawnego funkcjonowania. W przypadku przekroczenia limitów darmowego planu, API zwróci błąd 429 z informacją o czasie oczekiwania.
