import os
import openai
import requests
from dotenv import load_dotenv
import datetime
import wikipediaapi
from deep_translator import GoogleTranslator
import pyjokes
import feedparser
import json
import re
from collections import Counter
import pytz
import subprocess
import webbrowser
from googleapiclient.discovery import build
import chromadb
import tiktoken
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from googleapiclient.discovery import build as build_google_service

load_dotenv()
client = openai.OpenAI()

weather_key = os.getenv("WEATHER_API_KEY")
personality = "naturalny, pomocny, inteligentny"

# UWAGA: Ta lista została skrócona, aby naprawić błąd w pliku.
# Oryginalna lista była bardzo długa i zawierała wiele duplikatów.
# Należy ją przejrzeć i przywrócić potrzebne wpisy.
COMMON_APPLICATIONS_MAP = {
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "kalkulator": "calc.exe",
    "visual studio code": "code.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "paint": "mspaint.exe",
    "przeglądarka": "chrome.exe",
    "terminal": "cmd.exe",
}

# UWAGA: Ta lista została skrócona, aby naprawić błąd w pliku.
COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "instagram": "https://www.instagram.com",
    "wikipedia": "https://pl.wikipedia.org",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
}



# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
def init_chroma_db():
    """Inicjalizuje ChromaDB."""
    try:
        client = chromadb.Client()
        # Możesz użyć client.create_collection() lub client.get_or_create_collection()
        # w zależności od tego, czy chcesz tworzyć nową kolekcję za każdym razem,
        # czy używać istniejącej. Na potrzeby przykładu użyjemy get_or_create.
        collection = client.get_or_create_collection(name="jarvis_knowledge_base")
        print("ChromaDB zainicjalizowana pomyślnie.")
        return collection
    except Exception as e:
        print(f"Błąd podczas inicjalizacji ChromaDB: {e}")
        return None

def get_weather_forecast(city, country=None):
    """Pobiera aktualną pogodę i prognozę na 3 dni dla podanego miasta i kraju.
    Jeśli kraj nie jest podany, próbuje odgadnąć dla Polski.
    """
    print(f"Pobieranie pogody dla: {city}, kraj: {country}")
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city + (f",{country}" if country else ""),
        "appid": os.getenv("WEATHER_API_KEY"),
        "units": "metric", # Stopnie Celsjusza
        "lang": "pl" # Język polski
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Sprawdź, czy nie ma błędów HTTP
        weather_data = response.json()

        if weather_data["cod"] != "200":
            return f"Nie udało mi się znaleźć pogody dla {city}. Sprawdź pisownię lub spróbuj ponownie."

        # Aktualna pogoda
        current_temp = weather_data["list"][0]["main"]["temp"]
        current_desc = weather_data["list"][0]["weather"][0]["description"]
        current_city_name = weather_data["city"]["name"]
        
        weather_report = f"Aktualna pogoda w {current_city_name}: {current_temp}°C, {current_desc}.\n\nPrognoza na najbliższe 3 dni:\n"

        # Prognoza na 3 dni (co 8 interwałów, czyli co 24h)
        # OpenWeatherMap zwraca prognozę co 3 godziny, więc 8 * 3h = 24h
        for i in range(8, len(weather_data["list"]), 8):
            if i >= 8 * 3: # Ogranicz do 3 dni
                break
            day_data = weather_data["list"][i]
            date = datetime.datetime.fromtimestamp(day_data["dt"]).strftime('%d.%m')
            temp = day_data["main"]["temp"]
            desc = day_data["weather"][0]["description"]
            weather_report += f"- {date}: {temp}°C, {desc}.\n"

        return weather_report

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia z API pogody: {e}")
        import traceback
        traceback.print_exc()
        return "Przepraszam, nie mogę teraz sprawdzić pogody. Coś poszło nie tak z połączeniem."
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas pobierania pogody: {e}")
        import traceback
        traceback.print_exc()
        return "Ups, coś poszło nie tak podczas sprawdzania pogody. Spróbuj ponownie później."

def get_current_time(timezone_name):
    """Pobiera aktualny czas dla podanej strefy czasowej."""
    try:
        target_tz = pytz.timezone(timezone_name)
        now = datetime.datetime.now(target_tz)
        return f"Aktualny czas w {timezone_name} to {now.strftime('%H:%M:%S')}."
    except pytz.UnknownTimeZoneError:
        return f"Niestety, nie znam takiej strefy czasowej: {timezone_name}. Spróbuj inaczej, np. 'Europe/Warsaw'."
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas pobierania czasu: {e}")
        return "Ups, coś poszło nie tak podczas sprawdzania czasu."

def get_wikipedia_summary(query, lang="pl", sentences=2):
    """Pobiera krótkie podsumowanie z Wikipedii dla danego zapytania.
    Domyślnie szuka w języku polskim i zwraca 2 zdania.
    """
    try:
        wiki_wiki = wikipediaapi.Wikipedia(lang)
        page = wiki_wiki.page(query)

        if not page.exists():
            return f"Nie znalazłem nic na Wikipedii o '{query}'."
        
        return page.summary(sentences=sentences)

    except Exception as e:
        print(f"Błąd podczas pobierania z Wikipedii: {e}")
        return "Przepraszam, nie mogę teraz sprawdzić Wikipedii. Coś poszło nie tak."

def get_latest_news(rss_url="https://wiadomosci.onet.pl/.feed"): # Przykładowy RSS
    """Pobiera najnowsze nagłówki wiadomości z podanego kanału RSS.
    Domyślnie używa RSS z Onetu.
    """
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            return "Nie udało mi się pobrać żadnych wiadomości z tego źródła."
        
        news_headlines = "Najnowsze wiadomości:\n"
        for entry in feed.entries[:5]: # Pobierz 5 najnowszych
            news_headlines += f"- {entry.title}\n"
        return news_headlines

    except Exception as e:
        print(f"Błąd podczas pobierania wiadomości: {e}")
        return "Przepraszam, nie mogę teraz pobrać wiadomości. Coś poszło nie tak."

def translate_text(text, source_lang="auto", target_lang="pl"):
    """Tłumaczy tekst z jednego języka na drugi.
    Domyślnie wykrywa język źródłowy i tłumaczy na polski.
    """
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_text = translator.translate(text)
        return f"Tłumaczenie: {translated_text}"
    except Exception as e:
        print(f"Błąd podczas tłumaczenia tekstu: {e}")
        return "Przepraszam, nie mogę teraz przetłumaczyć tekstu. Coś poszło nie tak."


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Pobiera aktualną pogodę i prognozę na 3 dni dla podanego miasta i kraju.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Miasto, dla którego ma być sprawdzona pogoda, np. Warszawa",
                    },
                    "country": {
                        "type": "string",
                        "description": "Kraj, dla którego ma być sprawdzona pogoda, np. Polska",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Pobiera aktualny czas dla podanej strefy czasowej.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone_name": {
                        "type": "string",
                        "description": "Nazwa strefy czasowej, np. 'Europe/Warsaw', 'America/New_York'.",
                    },
                },
                "required": ["timezone_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_summary",
            "description": "Pobiera krótkie podsumowanie z Wikipedii dla danego zapytania.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Zapytanie do wyszukania na Wikipedii, np. 'Nikola Tesla'.",
                    },
                    "lang": {
                        "type": "string",
                        "description": "Język Wikipedii, np. 'pl' dla polskiego, 'en' dla angielskiego. Domyślnie 'pl'.",
                    },
                    "sentences": {
                        "type": "integer",
                        "description": "Liczba zdań w podsumowaniu. Domyślnie 2.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Pobiera najnowsze nagłówki wiadomości z podanego kanału RSS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rss_url": {
                        "type": "string",
                        "description": "Adres URL kanału RSS, np. 'https://www.onet.pl/rss/wiadomosci'.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Tłumaczy tekst z jednego języka na drugi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Tekst do przetłumaczenia.",
                    },
                    "source_lang": {
                        "type": "string",
                        "description": "Język źródłowy, np. 'en' dla angielskiego. Domyślnie 'auto' (automatyczne wykrywanie).",
                    },
                    "target_lang": {
                        "type": "string",
                        "description": "Język docelowy, np. 'pl' dla polskiego. Domyślnie 'pl'.",
                    },
                },
                "required": ["text"],
            },
        },
    }
]

available_functions = {
    "get_weather_forecast": get_weather_forecast,
    "get_current_time": get_current_time,
    "get_wikipedia_summary": get_wikipedia_summary,
    "get_latest_news": get_latest_news,
    "translate_text": translate_text,
}

def process_command(user_input, chat_history):
    """Przetwarza komendę użytkownika, przekazując ją do GPT."""
    print(f"Przetwarzanie komendy: '{user_input}'")
    
    # Zawsze używaj GPT, które teraz potrafi obsługiwać narzędzia
    response_text = ask_gpt(user_input, chat_history)
    
    return {"content": response_text}

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0613":
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant\n
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def ask_gpt(query, chat_history):
    """Wysyła zapytanie do modelu GPT, obsługuje narzędzia i zwraca odpowiedź."""
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    try:
        # Pierwsze wywołanie do AI, żeby sprawdzić, czy chce użyć narzędzia
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Sprawdź, czy model chce wywołać narzędzie
        if tool_calls:
            messages.append(response_message) # dodaj odpowiedź AI do historii

            # Wywołaj wszystkie narzędzia, o które prosi model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # Wywołaj funkcję z argumentami w sposób elastyczny
                function_response = function_to_call(**function_args)

                # Dodaj wynik działania funkcji do historii
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            # Drugie wywołanie do AI z wynikiem funkcji, żeby dostać końcową odpowiedź
            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            return second_response.choices[0].message.content

        # Jeśli model nie chce użyć narzędzia, zwróć jego odpowiedź bezpośrednio
        else:
            return response_message.content

    except Exception as e:
        print(f"Błąd podczas komunikacji z OpenAI: {e}")
        import traceback
        traceback.print_exc()
        return "Przepraszam, coś poszło nie tak podczas generowania odpowiedzi."
