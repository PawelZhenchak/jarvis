import os
import openai
import requests
from dotenv import load_dotenv
import datetime
import wikipediaapi
from deep_translator import GoogleTranslator
import pyjokes
import feedparser
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

def process_command(user_input, chat_history):
    """Przetwarza komendę użytkownika i zwraca odpowiedź."""
    print(f"Przetwarzanie komendy: '{user_input}'")
    command = user_input.lower()
    print(f"Znormalizowana komenda (lowercase): '{command}'")
    print(f"'godzina' in command: {'godzina' in command}")
    print(f"'pogoda' in command: {'pogoda' in command}")

    # Sprawdź, czy użytkownik pyta o godzinę
    if "godzina" in command or "czas" in command or "która jest" in command:
        print("Wykryto pytanie o godzinę.")
        now = datetime.datetime.now()
        response_text = f"Jest godzina {now.strftime('%H:%M')}."
    # Sprawdź, czy użytkownik pyta o pogodę
    elif "pogoda" in command:
        print("Wykryto pytanie o pogodę.")
        city = None
        country = None

        # Nowe, bardziej elastyczne podejście do ekstrakcji miasta i kraju
        # Najpierw szukamy frazy "pogoda w" lub "pogoda dla" i bierzemy resztę zdania
        match = re.search(r"pogoda\s*(?:w|dla)?\s*(.*)", command, re.IGNORECASE)
        if match:
            location_string = match.group(1).strip()
            print(f"Wyodrębniony ciąg lokalizacji: '{location_string}'")

            # Teraz próbujemy podzielić ciąg na miasto i kraj
            parts = [p.strip() for p in location_string.split(',') if p.strip()]
            if len(parts) >= 1:
                city = parts[0]
                if len(parts) >= 2:
                    country = parts[1]
            
            print(f"Wyodrębnione miasto: '{city}', kraj: '{country}'")
        else:
            print("Nie znaleziono ciągu lokalizacji po 'pogoda'.")
        
        if city:
            response_text = get_weather_forecast(city, country)
        else:
            response_text = "Dla jakiego miasta mam sprawdzić pogodę? Możesz też podać kraj."
    else:
        # Jeśli komenda nie jest rozpoznana, użyj GPT
        print("Komenda nie rozpoznana, przekazuję do GPT.")
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
    """Wysyła zapytanie do modelu GPT i zwraca odpowiedź."""
    messages = []
    # Dodaj historię czatu
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Dodaj aktualne zapytanie użytkownika
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150, # Ogranicz długość odpowiedzi
            temperature=0.7, # Kreatywność odpowiedzi
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd podczas komunikacji z OpenAI: {e}")
        return "Przepraszam, coś poszło nie tak podczas generowania odpowiedzi."
