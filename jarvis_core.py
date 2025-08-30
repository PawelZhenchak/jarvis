import os
import openai
import threading
import requests
from dotenv import load_dotenv
import datetime
import wikipediaapi
from deep_translator import GoogleTranslator
import pyjokes
import feedparser
import json
import speech_recognition as sr
import pyttsx3
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

# --- LangChain Imports ---
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()
print(f"load_dotenv() result: {load_dotenv()}")
print(f"os.environ['YOUTUBE_API_KEY'] after load_dotenv: {os.environ.get('YOUTUBE_API_KEY')}")
client = openai.OpenAI()

# Inicjalizacja silnika TTS (pyttsx3)
try:
    engine = pyttsx3.init()
    # Ustawienie głosu na polski (Paulina)
    # ID głosu można znaleźć uruchamiając list_voices.py
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PL-PL_PAULINA_11.0"
    engine.setProperty('voice', voice_id)
except Exception as e:
    print(f"Błąd podczas inicjalizacji silnika TTS: {e}")
    engine = None

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
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "ustawienia": "ms-settings:",
    "sklep microsoft": "ms-windows-store:",
    "wordpad": "wordpad.exe",
    "mspaint": "mspaint.exe",
    "snippingtool": "snippingtool.exe",
    "notepad++": "notepad++.exe", # Jeśli zainstalowany i w PATH
    "vlc": "vlc.exe", # Jeśli zainstalowany i w PATH
    "spotify": "spotify.exe", # Jeśli zainstalowany i w PATH
    "discord": "discord.exe", # Jeśli zainstalowany i w PATH
    "steam": "steam.exe", # Jeśli zainstalowany i w PATH
    "firefox": "firefox.exe", # Jeśli zainstalowany i w PATH
    "edge": "msedge.exe", # Jeśli zainstalowany i w PATH
    "telegram": "telegram.exe", # Jeśli zainstalowany i w PATH
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
    "allegro": "https://allegro.pl",
    "olx": "https://www.olx.pl",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "discord": "https://discord.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "twitch": "https://www.twitch.tv",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "interia": "https://www.interia.pl",
    "gazeta": "https://www.gazeta.pl",
    "sport.pl": "https://www.sport.pl",
    "money.pl": "https://www.money.pl",
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

def get_joke():
    """Opowiada losowy dowcip.
    """
    try:
        return pyjokes.get_joke(language='en', category='neutral') # Domyślnie angielskie, neutralne dowcipy
    except Exception as e:
        print(f"Błąd podczas pobierania dowcipu: {e}")
        return "Przepraszam, nie mogę teraz opowiedzieć dowcipu. Coś poszło nie tak."

def get_random_fact(count=1):
    """Podaje losową, ciekawą informację lub zadaną liczbę informacji."""
    facts = [
        "Miód nigdy się nie psuje.",
        "Serce krewetki znajduje się w jej głowie.",
        "Ośmiornice mają trzy serca.",
        "Mrówki potrafią podnieść ciężar 50 razy większy od własnego ciała.",
        "Pszczoły potrafią rozpoznawać ludzkie twarze.",
        "W kosmosie nie można płakać, bo łzy nie spływają.",
        "Krokodyle nie potrafią wystawić języka.",
        "Słońce jest tak duże, że zmieściłoby się w nim milion Ziem.",
        "Najdłuższa wojna w historii trwała 335 lat.",
        "Ludzkie DNA ma około 2 metry długości."
    ]
    import random
    
    if count >= len(facts):
        selected_facts = facts
    else:
        selected_facts = random.sample(facts, count)

    if count == 1:
        return selected_facts[0]
    else:
        return "\n".join(f"{i+1}. {fact}" for i, fact in enumerate(selected_facts))

def speak_in_background(text_to_speak):
    """Helper function to run TTS in a separate thread."""
    if engine:
        try:
            # This is a blocking call, but it's running in a separate thread
            engine.say(text_to_speak)
            engine.runAndWait()
        except Exception as e:
            print(f"Błąd podczas odtwarzania mowy w tle: {e}")

def speak(text):
    """Zamienia tekst na mowę i odtwarza go w tle, aby nie blokować głównego wątku."""
    if engine:
        # Uruchom mówienie w osobnym wątku
        thread = threading.Thread(target=speak_in_background, args=(text,))
        thread.daemon = True  # Wątek umrze, gdy główny program się zakończy
        thread.start()
    else:
        print("Silnik TTS nie jest dostępny. Mowa nie może być odtworzona.")

def listen_to_user():
    """Słucha użytkownika przez mikrofon i zamienia mowę na tekst.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Mów teraz...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="pl-PL") # Rozpoznawanie mowy po polsku
        print(f"Powiedziałeś: {text}")
        return text
    except sr.UnknownValueError:
        print("Nie zrozumiałem, co powiedziałeś.")
        return ""
    except sr.RequestError as e:
        print(f"Błąd połączenia z usługą rozpoznawania mowy; {e}")
        return ""


import requests
import re
import json # Needed for parsing initial data from YouTube page

youtube_api_key = os.getenv("YOUTUBE_API_KEY")
print(f"YouTube API Key loaded: {youtube_api_key is not None}")

def search_youtube(query):
    """Wyszukuje filmiki na YouTube na podstawie zapytania i otwiera pierwszy znaleziony filmik za pomocą YouTube Data API."""
    if not youtube_api_key:
        return "Przepraszam, klucz API YouTube nie jest skonfigurowany. Nie mogę wyszukać filmików."

    try:
        youtube = build("youtube", "v3", developerKey=youtube_api_key)

        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=1  # Get only the first result
        )
        response = request.execute()

        if response and response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(video_url)
            return f"Otwieram filmik na YouTube: {video_url} dla zapytania: {query}."
        else:
            return f"Nie znalazłem żadnych filmików na YouTube dla zapytania: {query}."

    except Exception as e:
        print(f"Błąd podczas wyszukiwania YouTube przez API: {e}")
        return f"Przepraszam, nie mogę wyszukać filmiku na YouTube dla zapytania {query}. Coś poszło nie tak z API."

def open_application(app_name):
    """Otwiera podaną aplikację na komputerze użytkownika.
    Najpierw sprawdza w zdefiniowanej mapie, a następnie próbuje uruchomić nazwę aplikacji bezpośrednio.
    """
    app_path = COMMON_APPLICATIONS_MAP.get(app_name.lower())
    if app_path:
        try:
            subprocess.Popen(app_path)
            return f"Otwieram {app_name}."
        except FileNotFoundError:
            return f"Nie mogę znaleźć aplikacji {app_name} pod zdefiniowaną ścieżką. Spróbuję uruchomić ją bezpośrednio."
        except Exception as e:
            print(f"Błąd podczas otwierania aplikacji {app_name} z mapy: {e}")
            return f"Przepraszam, nie mogę otworzyć {app_name}. Coś poszło nie tak."
    
    # Jeśli nie znaleziono w mapie, spróbuj uruchomić bezpośrednio
    try:
        subprocess.Popen(app_name)
        return f"Otwieram {app_name}."
    except FileNotFoundError:
        return f"Nie mogę znaleźć aplikacji o nazwie {app_name}. Upewnij się, że jest zainstalowana i dostępna w ścieżce systemowej, lub dodaj ją do listy COMMON_APPLICATIONS_MAP."
    except Exception as e:
        print(f"Błąd podczas otwierania aplikacji {app_name} bezpośrednio: {e}")
        return f"Przepraszam, nie mogę otworzyć {app_name}. Coś poszło nie tak."

def open_website(url_or_name):
    """Otwiera podaną stronę internetową w przeglądarce użytkownika.
    Może otworzyć stronę z predefiniowanej listy lub dowolny URL.
    """
    # Try to find in predefined map first
    site_url = COMMON_WEBSITES_MAP.get(url_or_name.lower())
    
    if site_url:
        target_url = site_url
    else:
        # Assume it's a direct URL
        if not url_or_name.startswith(("http://", "https://")):
            target_url = "https://" + url_or_name
        else:
            target_url = url_or_name

    try:
        webbrowser.open(target_url)
        return f"Otwieram {url_or_name}."
    except Exception as e:
        print(f"Błąd podczas otwierania strony {url_or_name}: {e}")
        return f"Przepraszam, nie mogę otworzyć {url_or_name}. Coś poszło nie tak."

TODO_FILE = "todos.txt"

def add_todo(item):
    """Dodaje nowe zadanie do listy zadań.
    """
    try:
        with open(TODO_FILE, "a", encoding="utf-8") as f:
            f.write(item + "\n")
        return f"Dodano zadanie: {item}"
    except Exception as e:
        print(f"Błąd podczas dodawania zadania: {e}")
        return "Przepraszam, nie mogę teraz dodać zadania."

def list_todos():
    """Wyświetla wszystkie zadania z listy zadań.
    """
    try:
        if not os.path.exists(TODO_FILE):
            return "Lista zadań jest pusta."
        
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            todos = f.readlines()
        
        if not todos:
            return "Lista zadań jest pusta."
        
        response = "Twoje zadania:\n"
        for i, todo in enumerate(todos):
            response += f"{i+1}. {todo.strip()}\n"
        return response
    except Exception as e:
        print(f"Błąd podczas listowania zadań: {e}")
        return "Przepraszam, nie mogę teraz wyświetlić zadań."

def remove_todo(item_index):
    """Usuwa zadanie z listy zadań na podstawie jego numeru.
    """
    try:
        if not os.path.exists(TODO_FILE):
            return "Lista zadań jest pusta. Nic do usunięcia."
        
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            todos = f.readlines()
        
        if not todos:
            return "Lista zadań jest pusta. Nic do usunięcia."
        
        if item_index < 1 or item_index > len(todos):
            return f"Nieprawidłowy numer zadania. Podaj numer od 1 do {len(todos)}."
        
        removed_item = todos.pop(item_index - 1).strip()
        
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.writelines(todos)
        
        return f"Usunięto zadanie: {removed_item}"
    except Exception as e:
        print(f"Błąd podczas usuwania zadania: {e}")
        return "Przepraszam, nie mogę teraz usunąć zadania."


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
    },
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "Opowiada losowy dowcip.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_fact",
            "description": "Podaje losową, ciekawą informację lub zadaną liczbę informacji.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Liczba losowych ciekawostek do zwrócenia. Domyślnie 1."
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Użyj tego narzędzia, gdy użytkownik chce coś włączyć, znaleźć, obejrzeć lub posłuchać na YouTube. Narzędzie wyszukuje na YouTube wideo na podstawie zapytania (np. 'najnowsze wiadomości', 'piosenka sanah') i automatycznie otwiera w przeglądarce pierwszy znaleziony filmik.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Zapytanie do wyszukania na YouTube, np. 'śmieszne koty', 'najnowsze wiadomości'.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Otwiera podaną aplikację na komputerze użytkownika.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Nazwa aplikacji do otwarcia, np. 'notatnik', 'chrome'.",
                    },
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Otwiera podaną stronę internetową w przeglądarce użytkownika. Może otworzyć stronę z predefiniowanej listy (np. 'google', 'youtube') lub dowolny URL (np. 'https://www.example.com').",
            "parameters": {
                "type": "object",
                "properties": {
                    "url_or_name": {
                        "type": "string",
                        "description": "Nazwa strony internetowej (np. 'google') lub pełny URL (np. 'https://www.example.com') do otwarcia.",
                    },
                },
                "required": ["url_or_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "Dodaje nowe zadanie do listy zadań.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "Treść zadania do dodania.",
                    },
                },
                "required": ["item"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "Wyświetla wszystkie zadania z listy zadań.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_todo",
            "description": "Usuwa zadanie z listy zadań na podstawie jego numeru.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_index": {
                        "type": "integer",
                        "description": "Numer zadania do usunięcia (licząc od 1).",
                    },
                },
                "required": ["item_index"],
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
    "get_joke": get_joke,
    "get_random_fact": get_random_fact,
    "search_youtube": search_youtube, # Added this line
    "open_application": open_application,
    "open_website": open_website,
    "add_todo": add_todo,
    "list_todos": list_todos,
    "remove_todo": remove_todo,
}

def process_command(user_input, chat_history, file_path=None):
    """Przetwarza komendę użytkownika, decydując czy użyć standardowej logiki GPT, czy logiki RAG z dokumentem."""
    print(f"Przetwarzanie komendy: '{user_input}'")

    # --- Easter Egg ---
    normalized_input = user_input.lower()
    if "najpiękniejsza" in normalized_input and ("dziewczyna" in normalized_input or "kobieta" in normalized_input):
        return {"content": "Ola Reczulska!!!!"}
    # --- Koniec Easter Egg ---

    if file_path:
        print(f"Używanie kontekstu z pliku: {file_path}")
        response_text = ask_gpt_with_document(user_input, chat_history, file_path)
    else:
        # Standardowa logika, jeśli nie ma pliku
        print("Brak pliku, używanie standardowej logiki GPT.")
        response_text = ask_gpt(user_input, chat_history)
    
    return {"content": response_text}


def ask_gpt_with_document(query, chat_history, file_path):
    """
    Obsługuje zapytania do AI w kontekście załadowanego dokumentu, używając LangChain RAG.
    """
    from langchain_core.messages import HumanMessage, AIMessage

    print("--- Rozpoczynam procesowanie z dokumentem (RAG) ---")
    try:
        # 1. Załaduj dokument
        print(f"1. Ładowanie dokumentu: {file_path}")
        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith(".txt") or file_path.lower().endswith(".md"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            return "Niestety, obsługuję tylko pliki .pdf, .txt i .md."
        
        docs = loader.load()

        # 2. Podziel dokument na kawałki (chunking)
        print("2. Dzielenie dokumentu na fragmenty.")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # 3. Stwórz wektorową bazę danych (vector store)
        print("3. Tworzenie wektorowej bazy danych (FAISS).")
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()

        # 4. Stwórz prompt do uwzględniania historii konwersacji
        contextualize_q_system_prompt = (
            "Biorąc pod uwagę historię rozmowy i ostatnie pytanie użytkownika, "
            "które może odnosić się do kontekstu w historii czatu, "
            "sformułuj samodzielne pytanie, które może być zrozumiane bez historii czatu. "
            "NIE odpowiadaj na pytanie, po prostu przeformułuj je, jeśli to konieczne, w przeciwnym razie zwróć je w oryginalnej formie."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            client, retriever, contextualize_q_prompt
        )

        # 5. Stwórz główny prompt do odpowiedzi na pytanie
        qa_system_prompt = (
            "Jesteś asystentem do odpowiadania na pytania. "
            "Użyj poniższych fragmentów odzyskanego kontekstu, aby odpowiedzieć na pytanie. "
            "Jeśli nie znasz odpowiedzi, po prostu powiedz, że nie wiesz. "
            "Odpowiadaj zwięźle i po polsku.\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # 6. Stwórz łańcuch (chain) do tworzenia odpowiedzi
        question_answer_chain = create_stuff_documents_chain(client, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # 7. Wywołaj łańcuch i uzyskaj odpowiedź
        print("4. Wywoływanie łańcucha RAG w celu uzyskania odpowiedzi.")
        langchain_history = []
        for msg in chat_history:
            if msg['role'] == 'user':
                langchain_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                langchain_history.append(AIMessage(content=msg['content']))

        result = rag_chain.invoke({"input": query, "chat_history": langchain_history})
        
        print("--- Procesowanie RAG zakończone ---")
        return result["answer"]

    except Exception as e:
        print(f"Błąd podczas przetwarzania dokumentu z LangChain: {e}")
        import traceback
        traceback.print_exc()
        return "Przepraszam, wystąpił błąd podczas analizy dokumentu. Spróbuj ponownie."



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
        raise NotImplementedError(f"num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.")

def ask_gpt(query, chat_history):
    """Wysyła zapytanie do modelu GPT, obsługuje narzędzia i zwraca odpowiedź."""
    # Ustaw strefę czasową
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    current_time = datetime.datetime.now(warsaw_tz)
    # Dodano nazwę dnia tygodnia i miesiąca do formatu, żeby AI miało pełen kontekst
    formatted_time = current_time.strftime("%A, %d %B %Y, %H:%M:%S")

    # Stwórz systemowy prompt
    current_working_directory = os.getcwd()
    system_prompt = (
        f"Jesteś Jarvis, osobisty asystent AI. Twoja osobowość jest {personality}. "
        f"Zawsze odpowiadaj po polsku. "
        f"Dzisiaj jest {formatted_time} (czasu warszawskiego). Bądź świadomy tej daty i godziny, odpowiadając na pytania. "
        f"Aktualny katalog roboczy to: {current_working_directory}."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        # Pomijaj stare wiadomości systemowe, jeśli istnieją w historii
        if msg.get("role") == "system":
            continue
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