import os
import openai
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
from dotenv import load_dotenv
import datetime

# Inicjalizacja
load_dotenv()
openai.api_key = os.getenv("sk-proj-wAkmJKxW4CmNUPBmdQuNE84qf7SWdIgB0dOMtz3nNnXm0tEi5BQlPnTitnhWaDfEKtkvCHMScKT3BlbkFJ7kvrhCVZNAryeb-E_SABRbk_LTA8qHTS1q7PIihWkRAdqDNvnRSyo07kyzn6bg1sw2Eo7C4_cAY")
weather_key = os.getenv("23b3230e0bf4bcd3e2ecc1456c524e83")
engine = pyttsx3.init()
engine.setProperty('rate', 175)
chat_history = []
personality = "naturalny, pomocny, inteligentny"

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Słucham...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language="pl-PL")
        print("Ty:", query)
        return query
    except sr.UnknownValueError:
        speak("Nie zrozumiałem. Spróbuj ponownie.")
        return ""
    except sr.RequestError:
        speak("Błąd połączenia z rozpoznawaniem mowy.")
        return ""

def get_weather():
    city = "Warszawa"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&units=metric&lang=pl"
    try:
        response = requests.get(url).json()
        desc = response['weather'][0]['description']
        temp = response['main']['temp']
        return f"Aktualna pogoda w {city}: {desc}, temperatura {temp}°C."
    except:
        return "Nie mogę pobrać pogody."

def remember_fact(text):
    chat_history.append({"role": "user", "content": text})

def ask_gpt(query):
    chat_history.append({"role": "user", "content": query})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Jesteś Jarvisem – chatbotem o osobowości: {personality}."}
        ] + chat_history[-10:],
        temperature=0.8,
        max_tokens=300
    )
    message = response['choices'][0]['message']['content']
    chat_history.append({"role": "assistant", "content": message})
    return message

def play_music():
    speak("Otwieram YouTube")
    webbrowser.open("https://www.youtube.com")

def add_reminder(text):
    with open("reminders.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} – {text}\n")
    speak("Przypomnienie zapisane.")

def change_personality(cmd):
    global personality
    if "zostań zabawny" in cmd:
        personality = "zabawny, żartobliwy, luzacki"
        speak("Zmieniam styl na zabawny!")
    elif "bądź poważny" in cmd:
        personality = "poważny, rzeczowy, naukowy"
        speak("Tryb poważny włączony.")
    elif "bądź filozoficzny" in cmd:
        personality = "refleksyjny, filozoficzny, głęboki"
        speak("Okej. Czas na rozmyślania.")
    elif "bądź naturalny" in cmd:
        personality = "naturalny, pomocny, inteligentny"
        speak("Wracam do standardowego stylu.")
    else:
        speak("Nie rozumiem, jaką osobowość wybrać.")

def process_command(cmd):
    cmd = cmd.lower()

    if "pogoda" in cmd:
        speak(get_weather())

    elif "youtube" in cmd or "muzyka" in cmd:
        play_music()

    elif "zapamiętaj" in cmd:
        fact = cmd.replace("zapamiętaj", "").strip()
        remember_fact(fact)
        speak("Zapamiętane.")

    elif "przypomnij" in cmd or "kalendarz" in cmd:
        if os.path.exists("reminders.txt"):
            with open("reminders.txt", "r", encoding="utf-8") as f:
                data = f.read()
            speak("Oto twoje przypomnienia.")
            print(data)
        else:
            speak("Nie masz przypomnień.")

    elif "osobowość" in cmd or "zostań" in cmd or "bądź" in cmd:
        change_personality(cmd)

    elif "otwórz" in cmd and "google" in cmd:
        speak("Otwieram Google.")
        webbrowser.open("https://www.google.com")

    elif "koniec" in cmd or "wyjdź" in cmd:
        speak("Do zobaczenia!")
        exit()

    else:
        answer = ask_gpt(cmd)
        speak(answer)

# Główna pętla
speak("Cześć, jestem gotowy do twojwj dyspozycji.")
while True:
    command = listen()
    if command:
        process_command(command)