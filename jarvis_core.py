

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
openai.api_key = os.getenv("OPENAI_API_KEY")
weather_key = os.getenv("WEATHER_API_KEY")
personality = "naturalny, pomocny, inteligentny"

COMMON_APPLICATIONS_MAP = {
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---

    # "notatnik": "notepad.exe",
    # "chrome": "chrome.exe",
    # "firefox": "firefox.exe",
    # "word": "winword.exe",
    # "excel": "excel.exe",
    # "powerpoint": "powerpnt.exe",
    # "kalkulator": "calc.exe",
    # "paint": "mspaint.exe",
    # "cmd": "cmd.exe",
    # "powershell": "powershell.exe",
    # "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    # "edge": "msedge.exe",
    # "vlc": "vlc.exe",
    # "spotify": "spotify.exe",
    # "discord": "discord.exe",
    # "steam": "steam.exe",
    # "visual studio code": "code.exe",
    # "vs code": "code.exe",
    # "terminal": "wt.exe", # Windows Terminal
    # "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    # "eksplorator plików": "explorer.exe",
    # "menedżer zadań": "taskmgr.exe",
    # "panel sterowania": "control.exe",
    # "sklep microsoft": "ms-windows-store://",
    # "zdjęcia": "ms-photos://",
    # "kamera": "microsoft.windows.camera:",
    # "poczta": "outlookmail:",
    # "kalendarz": "outlookcal:",
    # "mapy": "bingmaps:",
    # "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    # "muzyka": "ms-music:",
    # "alarmy i zegar": "ms-clock:",
    # "kalkulator windows": "calculator:",
    # "pogoda windows": "msnweather:",
    # "xbox": "xboxapp:",
    # "one drive": "onedrive:",
    # "teams": "msteams:",
    # "zoom": "zoommtg:",
    # "skype": "skype:",
    # "whatsapp": "whatsapp:",
    # "telegram": "tg:",
    # "messenger": "fb-messenger:",
    # "twitter": "twitter:",
    # "facebook": "facebook:",
    # "instagram": "instagram:",
    # "linkedin": "linkedin:",
    # "youtube": "youtube:",
    # "netflix": "netflix:",
    # "hulu": "hulu:",
    # "amazon prime video": "primevideo:",
    # "disney plus": "disneyplus:",
    # "steam": "steam:",
    # "epic games": "com.epicgames.launcher:",
    # "origin": "origin:",
    # "uplay": "uplay:",
    # "gog galaxy": "goggalaxy:",
    # "blizzard battle.net": "battlenet:",
    # "riot games": "riotgames:",
    # "minecraft": "minecraft:",
    # "roblox": "roblox:",
    # "fortnite": "fortnite:",
    # "league of legends": "leagueoflegends:",
    # "valorant": "valorant:",
    # "csgo": "steam://rungameid/730",
    # "dota 2": "steam://rungameid/570",
    # "apex legends": "steam://rungameid/1172470",
    # "rocket league": "steam://rungameid/252950",
    # "among us": "steam://rungameid/945360",
    # "cyberpunk 2077": "steam://rungameid/1091500",
    # "wiedźmin 3": "steam://rungameid/292030",
    # "grand theft auto v": "steam://rungameid/271590",
    # "red dead redemption 2": "steam://rungameid/1174180",
    # "forza horizon 4": "microsoft-forza-horizon-4:",
    # "forza horizon 5": "microsoft-forza-horizon-5:",
    # "microsoft flight simulator": "flightsimulator:",
    # "age of empires ii": "aoe2de:",
    # "age of empires iv": "aoe4:",
    # "halo infinite": "haloinfinite:",
    # "sea of thieves": "seaofthieves:",
    # "state of decay 2": "stateofdecay2:",
    # "gears 5": "gears5:",
    # "doom eternal": "doometernal:",
    # "fallout 4": "fallout4:",
    # "skyrim": "skyrim:",
    # "gta v": "steam://rungameid/271590",
    # "rdr2": "steam://rungameid/1174180",
    # "lol": "leagueoflegends:",
    # "cs": "steam://rungameid/730",
    # "dota": "steam://rungameid/570",
    # "apex": "steam://rungameid/1172470",
    # "rl": "steam://rungameid/252950",
    # "among": "steam://rungameid/945360",
    # "cp2077": "steam://rungameid/1091500",
    # "wiedzmin": "steam://rungameid/292030",
    # "gta": "steam://rungameid/271590",
    # "rdr": "steam://rungameid/1174180",
    # "fh4": "microsoft-forza-horizon-4:",
    # "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears 5": "gears5:",
    "aplikacja doom eternal": "doometernal:",
    "aplikacja fallout 4": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears 5": "gears5:",
    "aplikacja doom eternal": "doometernal:",
    "aplikacja fallout 4": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:
COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears 5": "gears5:",
    "aplikacja doom eternal": "doometernal:",
    "aplikacja fallout 4": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

COMMON_WEBSITES_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "onet": "https://www.onet.pl",
    "wp": "https://www.wp.pl",
    "interia": "https://www.interia.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "allegro": "https://www.allegro.pl",
    "olx": "https://www.olx.pl",
    "zalando": "https://www.zalando.pl",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discordapp": "https://discord.com",
    "spotifyweb": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "outlook": "https://outlook.live.com",
    "onedriveweb": "https://onedrive.live.com",
    "teamsweb": "https://teams.microsoft.com",
    "zoomweb": "https://zoom.us/join",
    "skypeweb": "https://web.skype.com/",
    "whatsappweb": "https://web.whatsapp.com/",
    "telegramweb": "https://web.telegram.org/",
    "messengerweb": "https://www.messenger.com/",
    "twitterweb": "https://twitter.com/home",
    "facebookweb": "https://www.facebook.com/",
    "instagramweb": "https://www.instagram.com/",
    "linkedinweb": "https://www.linkedin.com/feed/",
    "netflixweb": "https://www.netflix.com/",
    "huluweb": "https://www.hulu.com/",
    "amazonprimeweb": "https://www.primevideo.com/",
    "disneyplusweb": "https://www.disneyplus.com/",
    "steamweb": "https://store.steampowered.com/",
    "epicgamesweb": "https://www.epicgames.com/store/",
    "originweb": "https://www.origin.com/pol/pl-pl/store",
    "uplayweb": "https://ubisoftconnect.com/pl-PL/",
    "goggalaxyweb": "https://www.gog.com/galaxy",
    "blizzardweb": "https://eu.battle.net/shop/pl/",
    "riotgamesweb": "https://www.riotgames.com/pl",
    "minecraftweb": "https://www.minecraft.net/pl-pl/",
    "robloxweb": "https://www.roblox.com/",
    "fortniteweb": "https://www.epicgames.com/fortnite/pl/home",
    "leagueoflegendsweb": "https://www.leagueoflegends.com/pl-pl/",
    "valorantweb": "https://playvalorant.com/pl-pl/",
    "csgoweb": "https://blog.counter-strike.net/",
    "dota2web": "https://www.dota2.com/home",
    "apexlegendsweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rocketleagueweb": "https://www.rocketleague.com/",
    "amongusweb": "https://innersloth.com/games/among-us/",
    "cyberpunk2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzmin3web": "https://www.thewitcher.com/pl/witcher3/",
    "grandtheftautovweb": "https://www.rockstargames.com/gta-v",
    "reddeadredemption2web": "https://www.rockstargames.com/reddeadredemption2",
    "forzahorizon4web": "https://forzamotorsport.net/en-us/games/fh4",
    "forzahorizon5web": "https://forzamotorsport.net/en-us/games/fh5",
    "microsoftflightsimulatorweb": "https://www.flightsimulator.com/",
    "ageofempiresiiweb": "https://www.ageofempires.com/games/aoeii/",
    "ageofempiresivweb": "https://www.ageofempires.com/games/aoeiv/",
    "haloinfiniteweb": "https://www.halowaypoint.com/halo-infinite",
    "seaofthievesweb": "https://www.seaofthieves.com/",
    "stateofdecay2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gears5web": "https://www.gears5.com/",
    "doometernalweb": "https://bethesda.net/en/game/doom-eternal",
    "fallout4web": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
    "gtaweb": "https://www.rockstargames.com/gta-v",
    "rdrweb": "https://www.rockstargames.com/reddeadredemption2",
    "lolweb": "https://www.leagueoflegends.com/pl-pl/",
    "csweb": "https://blog.counter-strike.net/",
    "dotaweb": "https://www.dota2.com/home",
    "apexweb": "https://www.ea.com/pl-pl/games/apex-legends",
    "rlweb": "https://www.rocketleague.com/",
    "amongweb": "https://innersloth.com/games/among-us/",
    "cp2077web": "https://www.cyberpunk.net/pl/pl/",
    "wiedzminweb": "https://www.thewitcher.com/pl/witcher3/",
    "fh4web": "https://forzamotorsport.net/en-us/games/fh4",
    "fh5web": "https://forzamotorsport.net/en-us/games/fh5",
    "msfsweb": "https://www.flightsimulator.com/",
    "aoe2web": "https://www.ageofempires.com/games/aoeii/",
    "aoe4web": "https://www.ageofempires.com/games/aoeiv/",
    "haloweb": "https://www.halowaypoint.com/halo-infinite",
    "sotweb": "https://www.seaofthieves.com/",
    "sod2web": "https://www.stateofdecay.com/state-of-decay-2/",
    "gearsweb": "https://www.gears5.com/",
    "doomweb": "https://bethesda.net/en/game/doom-eternal",
    "falloutweb": "https://fallout.bethesda.net/en/games/fallout-4",
    "skyrimweb": "https://elderscrolls.bethesda.net/en/skyrim",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
    "notatnik": "notepad.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "kalkulator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "przeglądarka": "iexplore.exe", # Domyślna przeglądarka na Windows
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
    "visual studio code": "code.exe",
    "vs code": "code.exe",
    "terminal": "wt.exe", # Windows Terminal
    "ustawienia": "ms-settings:", # Otwiera ustawienia Windows
    "eksplorator plików": "explorer.exe",
    "menedżer zadań": "taskmgr.exe",
    "panel sterowania": "control.exe",
    "sklep microsoft": "ms-windows-store://",
    "zdjęcia": "ms-photos://",
    "kamera": "microsoft.windows.camera:",
    "poczta": "outlookmail:",
    "kalendarz": "outlookcal:",
    "mapy": "bingmaps:",
    "filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "muzyka": "ms-music:",
    "alarmy i zegar": "ms-clock:",
    "kalkulator windows": "calculator:",
    "pogoda windows": "msnweather:",
    "xbox": "xboxapp:",
    "one drive": "onedrive:",
    "teams": "msteams:",
    "zoom": "zoommtg:",
    "skype": "skype:",
    "whatsapp": "whatsapp:",
    "telegram": "tg:",
    "messenger": "fb-messenger:",
    "twitter": "twitter:",
    "facebook": "facebook:",
    "instagram": "instagram:",
    "linkedin": "linkedin:",
    "youtube": "youtube:",
    "netflix": "netflix:",
    "hulu": "hulu:",
    "amazon prime video": "primevideo:",
    "disney plus": "disneyplus:",
    "steam": "steam:",
    "epic games": "com.epicgames.launcher:",
    "origin": "origin:",
    "uplay": "uplay:",
    "gog galaxy": "goggalaxy:",
    "blizzard battle.net": "battlenet:",
    "riot games": "riotgames:",
    "minecraft": "minecraft:",
    "roblox": "roblox:",
    "fortnite": "fortnite:",
    "league of legends": "leagueoflegends:",
    "valorant": "valorant:",
    "csgo": "steam://rungameid/730",
    "dota 2": "steam://rungameid/570",
    "apex legends": "steam://rungameid/1172470",
    "rocket league": "steam://rungameid/252950",
    "among us": "steam://rungameid/945360",
    "cyberpunk 2077": "steam://rungameid/1091500",
    "wiedźmin 3": "steam://rungameid/292030",
    "grand theft auto v": "steam://rungameid/271590",
    "red dead redemption 2": "steam://rungameid/1174180",
    "forza horizon 4": "microsoft-forza-horizon-4:",
    "forza horizon 5": "microsoft-forza-horizon-5:",
    "microsoft flight simulator": "flightsimulator:",
    "age of empires ii": "aoe2de:",
    "age of empires iv": "aoe4:",
    "halo infinite": "haloinfinite:",
    "sea of thieves": "seaofthieves:",
    "state of decay 2": "stateofdecay2:",
    "gears 5": "gears5:",
    "doom eternal": "doometernal:",
    "fallout 4": "fallout4:",
    "skyrim": "skyrim:",
    "gta v": "steam://rungameid/271590",
    "rdr2": "steam://rungameid/1174180",
    "lol": "leagueoflegends:",
    "cs": "steam://rungameid/730",
    "dota": "steam://rungameid/570",
    "apex": "steam://rungameid/1172470",
    "rl": "steam://rungameid/252950",
    "among": "steam://rungameid/945360",
    "cp2077": "steam://rungameid/1091500",
    "wiedzmin": "steam://rungameid/292030",
    "gta": "steam://rungameid/271590",
    "rdr": "steam://rungameid/1174180",
    "fh4": "microsoft-forza-horizon-4:",
    "fh5": "microsoft-forza-horizon-5:",
    "msfs": "flightsimulator:",
    "aoe2": "aoe2de:",
    "aoe4": "aoe4:",
    "halo": "haloinfinite:",
    "sot": "seaofthieves:",
    "sod2": "stateofdecay2:",
    "gears": "gears5:",
    "doom": "doometernal:",
    "fallout": "fallout4:",
    "skyrim": "skyrim:",
    "google chrome": "chrome.exe",
    "mozilla firefox": "firefox.exe",
    "microsoft edge": "msedge.exe",
    "internet explorer": "iexplore.exe",
    "spotify app": "spotify.exe",
    "discord app": "discord.exe",
    "steam app": "steam.exe",
    "vlc media player": "vlc.exe",
    "visual studio code app": "code.exe",
    "windows terminal": "wt.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft paint": "mspaint.exe",
    "kalkulator windows": "calc.exe",
    "menedżer zadań windows": "taskmgr.exe",
    "panel sterowania windows": "control.exe",
    "eksplorator plików windows": "explorer.exe",
    "sklep microsoft store": "ms-windows-store://",
    "aplikacja zdjęcia": "ms-photos://",
    "aplikacja kamera": "microsoft.windows.camera:",
    "aplikacja poczta": "outlookmail:",
    "aplikacja kalendarz": "outlookcal:",
    "aplikacja mapy": "bingmaps:",
    "aplikacja filmy i tv": "ms-windows-store://pdp/?ProductId=9wzdncrfj3p2",
    "aplikacja muzyka": "ms-music:",
    "aplikacja alarmy i zegar": "ms-clock:",
    "aplikacja kalkulator": "calculator:",
    "aplikacja pogoda": "msnweather:",
    "aplikacja xbox": "xboxapp:",
    "aplikacja one drive": "onedrive:",
    "aplikacja teams": "msteams:",
    "aplikacja zoom": "zoommtg:",
    "aplikacja skype": "skype:",
    "aplikacja whatsapp": "whatsapp:",
    "aplikacja telegram": "tg:",
    "aplikacja messenger": "fb-messenger:",
    "aplikacja twitter": "twitter:",
    "aplikacja facebook": "facebook:",
    "aplikacja instagram": "instagram:",
    "aplikacja linkedin": "linkedin:",
    "aplikacja youtube": "youtube:",
    "aplikacja netflix": "netflix:",
    "aplikacja hulu": "hulu:",
    "aplikacja amazon prime video": "primevideo:",
    "aplikacja disney plus": "disneyplus:",
    "aplikacja steam": "steam:",
    "aplikacja epic games": "com.epicgames.launcher:",
    "aplikacja origin": "origin:",
    "aplikacja uplay": "uplay:",
    "aplikacja gog galaxy": "goggalaxy:",
    "aplikacja blizzard battle.net": "battlenet:",
    "aplikacja riot games": "riotgames:",
    "aplikacja minecraft": "minecraft:",
    "aplikacja roblox": "roblox:",
    "aplikacja fortnite": "fortnite:",
    "aplikacja league of legends": "leagueoflegends:",
    "aplikacja valorant": "valorant:",
    "aplikacja csgo": "steam://rungameid/730",
    "aplikacja dota 2": "steam://rungameid/570",
    "aplikacja apex legends": "steam://rungameid/1172470",
    "aplikacja rocket league": "steam://rungameid/252950",
    "aplikacja among us": "steam://rungameid/945360",
    "aplikacja cyberpunk 2077": "steam://rungameid/1091500",
    "aplikacja wiedźmin 3": "steam://rungameid/292030",
    "aplikacja grand theft auto v": "steam://rungameid/271590",
    "aplikacja red dead redemption 2": "steam://rungameid/1174180",
    "aplikacja forza horizon 4": "microsoft-forza-horizon-4:",
    "aplikacja forza horizon 5": "microsoft-forza-horizon-5:",
    "aplikacja microsoft flight simulator": "flightsimulator:",
    "aplikacja age of empires ii": "aoe2de:",
    "aplikacja age of empires iv": "aoe4:",
    "aplikacja halo infinite": "haloinfinite:",
    "aplikacja sea of thieves": "seaofthieves:",
    "aplikacja state of decay 2": "stateofdecay2:",
    "aplikacja gears 5": "gears5:",
    "aplikacja doom eternal": "doometernal:",
    "aplikacja fallout 4": "fallout4:",
    "aplikacja skyrim": "skyrim:",
    "aplikacja gta v": "steam://rungameid/271590",
    "aplikacja rdr2": "steam://rungameid/1174180",
    "aplikacja lol": "leagueoflegends:",
    "aplikacja cs": "steam://rungameid/730",
    "aplikacja dota": "steam://rungameid/570",
    "aplikacja apex": "steam://rungameid/1172470",
    "aplikacja rl": "steam://rungameid/252950",
    "aplikacja among": "steam://rungameid/945360",
    "aplikacja cp2077": "steam://rungameid/1091500",
    "aplikacja wiedzmin": "steam://rungameid/292030",
    "aplikacja gta": "steam://rungameid/271590",
    "aplikacja rdr": "steam://rungameid/1174180",
    "aplikacja fh4": "microsoft-forza-horizon-4:",
    "aplikacja fh5": "microsoft-forza-horizon-5:",
    "aplikacja msfs": "flightsimulator:",
    "aplikacja aoe2": "aoe2de:",
    "aplikacja aoe4": "aoe4:",
    "aplikacja halo": "haloinfinite:",
    "aplikacja sot": "seaofthieves:",
    "aplikacja sod2": "stateofdecay2:",
    "aplikacja gears": "gears5:",
    "aplikacja doom": "doometernal:",
    "aplikacja fallout": "fallout4:",
    "aplikacja skyrim": "skyrim:",
}

# --- Inicjalizacja Bazy Wiedzy (ChromaDB) ---
# Użyjemy prostej, nietrwałej bazy danych w pamięci.
# Aby baza była trwała, odkomentuj poniższą linię.
chroma_client = chromadb.Client()
# chroma_client = chromadb.PersistentClient(path="jarvis_knowledge.db") 
knowledge_collection = chroma_client.get_or_create_collection(name="jarvis_knowledge")

# --- Moduł 1: Integracja z Systemem Operacyjnym ---

def list_directory_contents(path="."):
    """Wyświetla zawartość podanego katalogu."""
    try:
        if not os.path.isdir(path):
            return f"Błąd: Ścieżka '{path}' nie jest katalogiem."
        items = os.listdir(path)
        if not items:
            return f"Katalog '{path}' jest pusty."
        
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
        
        response = f"""Zawartość katalogu '{path}':
"""
        if dirs:
            response += "\nFoldery:\n" + "\n".join(f"- {d}" for d in dirs)
        if files:
            response += "\nPliki:\n" + "\n".join(f"- {f}" for f in files)
            
        return response
    except Exception as e:
        return f"Nie udało się odczytać katalogu '{path}': {e}"

def create_directory(path):
    """Tworzy nowy katalog w podanej ścieżce."""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Utworzono katalog: '{path}'"
    except Exception as e:
        return f"Nie udało się utworzyć katalogu '{path}': {e}"

def read_file_content(path):
    """Odczytuje i zwraca zawartość pliku."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"""Zawartość pliku '{path}':

{content}"""
    except FileNotFoundError:
        return f"Błąd: Plik '{path}' nie został znaleziony."
    except Exception as e:
        return f"Nie udało się odczytać pliku '{path}': {e}"

def write_to_file(path, content):
    """Zapisuje podaną treść do pliku, nadpisując go, jeśli istnieje."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Zapisano treść w pliku '{path}'."
    except Exception as e:
        return f"Nie udało się zapisać do pliku '{path}': {e}"

def execute_shell_command(command):
    """Wykonuje polecenie systemowe i zwraca jego wynik."""
    # UWAGA: Ta funkcja jest potężna, ale i ryzykowna.
    # Należy ją stosować z dużą ostrożnością.
    try:
        # Dodatkowe zabezpieczenie: proste sprawdzenie, czy polecenie nie jest zbyt ryzykowne
        # W przyszłości można tu dodać bardziej zaawansowaną logikę walidacji
        blacklist = ["rm -rf", "sudo", "mv /", "mkfs"]
        if any(item in command for item in blacklist):
            return "Ze względów bezpieczeństwa to polecenie jest zablokowane."

        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
        if not output:
            output = "(brak danych wyjściowych)"
        return f"""Wynik polecenia '{command}':
{output}"""
    except subprocess.CalledProcessError as e:
        return f"""Błąd wykonania polecenia '{command}':
{e.stderr}"""
    except Exception as e:
        return f"Wystąpił krytyczny błąd podczas wykonywania polecenia: {e}"

def open_application(app_name):
    """Otwiera aplikację lub plik za pomocą domyślnego programu."""
    app_name_lower = app_name.lower()
    target_app = COMMON_APPLICATIONS_MAP.get(app_name_lower, app_name)

    try:
        os.startfile(target_app)
        return f"Otwieram: {app_name}"
    except FileNotFoundError:
        return f"Nie mogę znaleźć aplikacji/pliku: {app_name}. Spróbuj podać pełną nazwę lub ścieżkę."
    except Exception as e:
        return f"Wystąpił błąd podczas otwierania {app_name}: {e}"

def open_web_page(url):
    """Otwiera podany URL w domyślnej przeglądarce internetowej, uwzględniając popularne strony."""
    url_lower = url.lower()
    target_url = COMMON_WEBSITES_MAP.get(url_lower, url)

    try:
        # Dodajemy http:// jeśli brakuje, aby webbrowser działał poprawnie
        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url
        webbrowser.open(target_url)
        return f"Otwieram stronę: {url}"
    except Exception as e:
        return f"Nie udało się otworzyć strony {url}: {e}"

# --- Moduł 2: Rozszerzenie Bazy Wiedzy ---

def search_web(query):
    """Przeszukuje internet za pomocą Google Custom Search API."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            return "Brak klucza API Google lub ID wyszukiwarki (CSE ID) w konfiguracji."

        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=3).execute()

        if 'items' in res:
            results = []
            for item in res['items']:
                title = item.get('title', 'Brak tytułu')
                link = item.get('link', 'Brak linku')
                snippet = item.get('snippet', 'Brak opisu')
                results.append(f"- {title}\n  {snippet}\n  {link}")
            return "Oto co znalazłem w internecie:\n" + "\n\n".join(results)
        else:
            return f"Nie znalazłem żadnych wyników dla zapytania: '{query}'"

    except Exception as e:
        return f"Wystąpił błąd podczas wyszukiwania w internecie: {e}"

def get_text_chunks(text, max_tokens=500):
    """Dzieli tekst na mniejsze części (chunks) na podstawie tokenów."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk_tokens))
    return chunks

def add_document_to_knowledge_base(path):
    """Odczytuje plik, dzieli go na części i dodaje do bazy wiedzy."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = get_text_chunks(content)
        
        # Użyjemy ścieżki pliku jako ID dla dokumentów, aby uniknąć duplikatów
        # i umożliwić łatwe usuwanie/aktualizację w przyszłości.
        ids = [f"{path}-{i}" for i in range(len(chunks))]
        
        knowledge_collection.add(
            documents=chunks,
            ids=ids
        )
        return f"Nauczyłem się zawartości pliku: {path}"
    except FileNotFoundError:
        return f"Błąd: Plik '{path}' nie został znaleziony."
    except Exception as e:
        return f"Nie udało się dodać dokumentu do bazy wiedzy: {e}"

def query_knowledge_base(query, n_results=3):
    """Wyszukuje w bazie wiedzy najbardziej relewantne informacje."""
    try:
        results = knowledge_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        print(f"Błąd podczas przeszukiwania bazy wiedzy: {e}")
        return []

# --- Moduł 3: Zarządzanie Produktownością ---

SCOPES = ["https://www.googleapis.com/auth/calendar"]

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_calendar_service():
    """Tworzy obiekt usługi do interakcji z Google Calendar API."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # Uruchomienie lokalnego serwera do autoryzacji
            # To wymaga interakcji użytkownika w przeglądarce przy pierwszym uruchomieniu
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build_google_service("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_gmail_service():
    """Tworzy obiekt usługi do interakcji z Gmail API."""
    creds = None
    # Używamy tego samego token.json, ale z innym zakresem
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build_google_service("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def list_upcoming_events(max_results=10):
    """Wyświetla nadchodzące wydarzenia z kalendarza Google."""
    service = get_calendar_service()
    if not service:
        return "Nie udało się połączyć z Kalendarzem Google. Sprawdź konfigurację."
    
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' oznacza UTC
    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "Brak nadchodzących wydarzeń w kalendarzu."

        response = f"""Oto Twoje nadchodzące wydarzenia:\n"""
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            # Proste formatowanie daty i godziny
            start_formatted = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
            response += f"""- {event['summary']} (o {start_formatted})\n"""
        return response

    except HttpError as error:
        return f"Wystąpił błąd podczas pobierania wydarzeń: {error}"
    except Exception as e:
        return f"Wystąpił nieoczekiwany błąd: {e}"

def create_calendar_event(summary, description, start_time, end_time):
    """Tworzy nowe wydarzenie w kalendarza Google."""
    service = get_calendar_service()
    if not service:
        return "Nie udało się połączyć z Kalendarzem Google. Sprawdź konfigurację."

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Warsaw', # Można to sparametryzować
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Warsaw',
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Utworzono wydarzenie: {created_event.get('htmlLink')}"
    except HttpError as error:
        return f"Wystąpił błąd podczas tworzenia wydarzenia: {error}"
    except Exception as e:
        return f"Wystąpił nieoczekiwany błąd: {e}"

def list_unread_emails(max_results=5):
    """Wyświetla listę nieprzeczytanych wiadomości e-mail z Gmaila."""
    service = get_gmail_service()
    if not service:
        return "Nie udało się połączyć z Gmailem. Sprawdź konfigurację."

    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            return "Brak nieprzeczytanych wiadomości."

        response = "Oto Twoje nieprzeczytane wiadomości:\n"
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            headers = msg['payload']['headers']
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            response += f"- Od: {sender}, Temat: {subject}\n"
        return response

    except HttpError as error:
        return f"Wystąpił błąd podczas pobierania wiadomości: {error}"
    except Exception as e:
        return f"Wystąpił nieoczekiwany błąd: {e}"

def send_email(to, subject, body):
    """Wysyła wiadomość e-mail za pośrednictwem Gmaila."""
    service = get_gmail_service()
    if not service:
        return "Nie udało się połączyć z Gmailem. Sprawdź konfigurację."

    try:
        message = create_message('me', to, subject, body)
        send_message(service, 'me', message)
        return f"Wiadomość do {to} została wysłana."
    except Exception as e:
        return f"Nie udało się wysłać wiadomości: {e}"

def create_message(sender, to, subject, message_text):
    """Tworzy wiadomość e-mail w formacie MIME."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, user_id, message):
    """Wysyła wiadomość e-mail."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise

# --- Nowe funkcje ---

def get_wikipedia_summary(topic):
    """Wyszukuje hasło w Wikipedii i zwraca podsumowanie."""
    try:
        wiki_wiki = wikipediaapi.Wikipedia('pl')
        page_py = wiki_wiki.page(topic)
        if page_py.exists():
            return f"""Oto co znalazłem na temat {topic} w Wikipedii: {page_py.summary[0:500]}..."""
        else:
            return f"Niestety, nie znalazłem artykułu o '{topic}' w Wikipedii."
    except Exception as e:
        print(f"Błąd Wikipedii: {e}")
        return "Wystąpił błąd podczas wyszukiwania w Wikipedii."

def translate_text(text, target_lang='en'):
    """Tłumaczy tekst na podany język."""
    try:
        # Usuwamy słowo kluczowe "przetłumacz", aby uzyskać czysty tekst do tłumaczenia
        text_to_translate = re.sub(r'przetłumacz', '', text, flags=re.IGNORECASE).strip()
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text_to_translate)
        return f'Tłumaczenie: "{translated}"'
    except Exception as e:
        print(f"Błąd tłumaczenia: {e}")
        return "Nie udało mi się przetłumaczyć tekstu."

def get_joke():
    """Zwraca losowy żart."""
    return pyjokes.get_joke(language='pl', category='all')

def get_news():
    """Pobiera najnowsze wiadomości z kanału RSS."""
    try:
        # Użyjemy kanału RSS z TVN24 dla przykładu
        feed = feedparser.parse("https://www.tvn24.pl/najnowsze.xml")
        news_items = []
        for entry in feed.entries[:5]: # Pobieramy 5 najnowszych wiadomości
            news_items.append(f"- {entry.title}")
        return f"""Oto 5 najnowszych nagłówków z TVN24:\n" + "\n".join(news_items)"""
    except Exception as e:
        print(f"Błąd wiadomości: {e}")
        return "Nie mogę w tej chwili pobrać najnowszych wiadomości."

def calculate(expression):
    """Bezpiecznie oblicza wyrażenie matematyczne."""
    try:
        # Usuwamy słowo kluczowe "oblicz"
        expression = re.sub(r'oblicz', '', expression, flags=re.IGNORECASE).strip()
        # Dozwolone znaki i funkcje
        allowed_chars = "0123456789.+-*/() "
        if not all(char in allowed_chars for char in expression):
            return "Używasz niedozwolonych znaków. Mogę wykonywać tylko proste operacje."
        # Bezpieczne wykonanie obliczenia
        result = eval(expression)
        return f"Wynik to: {result}"
    except Exception as e:
        print(f"Błąd kalkulatora: {e}")
        return "Nie potrafię tego obliczyć. Sprawdź, czy wyrażenie jest poprawne."

def get_timezone_from_coordinates(lat, lon):
    """Pobiera nazwę strefy czasowej na podstawie współrzędnych."""
    try:
        # Użyjemy API timezonedb, aby uzyskać strefę czasową
        # To API wymaga klucza, ale jest darmowe. Załóżmy, że jest w .env
        timezone_db_key = os.getenv("TIMEZONEDB_API_KEY")
        if not timezone_db_key:
            # Fallback do innej metody, jeśli klucz nie jest dostępny
            url = f"http://api.geonames.org/timezoneJSON?lat={lat}&lng={lon}&username=demo"
            response = requests.get(url).json()
            if "timezoneId" in response:
                return response["timezoneId"]
            return None

        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_db_key}&format=json&by=position&lat={lat}&lng={lon}"
        response = requests.get(url).json()
        if response['status'] == 'OK':
            return response['zoneName']
        else:
            return None
    except Exception as e:
        print(f"Błąd pobierania strefy czasowej: {e}")
        return None

def get_current_time(city_name=None):
    """Zwraca aktualną datę i godzinę, opcjonalnie dla danego miasta."""
    if city_name:
        coords = get_coordinates_from_city_name(city_name)
        if coords:
            timezone_name = get_timezone_from_coordinates(coords['lat'], coords['lon'])
            if timezone_name:
                try:
                    tz = pytz.timezone(timezone_name)
                    now_utc = datetime.datetime.now(pytz.utc)
                    local_time = now_utc.astimezone(tz)
                    return f"W {city_name.capitalize()} jest teraz {local_time.strftime('%Y-%m-%d %H:%M:%S')}."
                except pytz.UnknownTimeZoneError:
                    return f"Nieznana strefa czasowa: {timezone_name}"
            else:
                return f"Nie udało mi się ustalić strefy czasowej dla {city_name.capitalize()}."
        else:
            return f"Nie mogę znaleźć miasta {city_name.capitalize()}."
    else:
        # Domyślnie zwraca czas lokalny serwera
        now = datetime.datetime.now()
        return f"Aktualna data i godzina to: {now.strftime('%Y-%m-%d %H:%M:%S')}."

def get_coordinates_from_city_name(city_name):
    """Pobiera współrzędne geograficzne dla podanej nazwy miasta za pomocą Nominatim (OpenStreetMap)."""
    try:
        # Nominatim preferuje nazwy bez polskich znaków, ale spróbujmy z nimi najpierw
        # Transliteracja polskich znaków dla API (Nominatim też może mieć z tym problem)
        city_transliterated = city_name.replace('Ł', 'L').replace('ł', 'l').replace('ą', 'a').replace('ę', 'e').replace('ć', 'c').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        
        # Nominatim wymaga nagłówka User-Agent
        headers = {'User-Agent': 'JarvisWeatherApp/1.0 (your_email@example.com)'} # Zmień na swój email
        
        # Spróbuj z nazwą miasta i kodem kraju
        url = f"https://nominatim.openstreetmap.org/search?q={city_transliterated},PL&format=json&limit=1"
        response = requests.get(url, headers=headers).json()

        if response and len(response) > 0:
            # Nominatim zwraca 'lat' i 'lon' jako stringi, trzeba je przekonwertować
            lat = float(response[0]['lat'])
            lon = float(response[0]['lon'])
            # Nominatim zwraca 'display_name' jako pełną nazwę, możemy spróbować wyciągnąć samą nazwę miasta
            found_name = response[0]['name'] if 'name' in response[0] else response[0]['display_name'].split(',')[0]
            
            # Spróbujmy znaleźć polską nazwę, jeśli dostępna w 'localname' lub 'name' z 'address' dict
            display_name_pl = found_name
            if 'address' in response[0]:
                if 'city' in response[0]['address']:
                    display_name_pl = response[0]['address']['city']
                elif 'town' in response[0]['address']:
                    display_name_pl = response[0]['address']['town']
                elif 'village' in response[0]['address']:
                    display_name_pl = response[0]['address']['village']

            return {"name": display_name_pl, "lat": lat, "lon": lon, "local_names": {'pl': display_name_pl}}
        else:
            return None
    except Exception as e:
        print(f"Błąd geokodowania (Nominatim): {e}")
        return None

def get_weather_forecast(lat, lon, days_in_future=1, city_name_display="Warszawa"):
    """Pobiera prognozę pogody na określoną liczbę dni w przyszłości na podstawie współrzędnych."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_key}&units=metric&lang=pl"
        print(f"Forecast API URL: {url}") # Debug print
        response = requests.get(url).json()
        print(f"Forecast API Response: {response}") # Debug print

        if response.get("cod") != "200":
            return f"Nie mogę pobrać prognozy pogody dla {city_name_display}. (Kod błędu: {response.get("cod")}, Wiadomość: {response.get("message")})"

        forecast_by_day = {}
        today = datetime.date.today()

        for item in response['list']:
            dt_object = datetime.datetime.fromtimestamp(item['dt'])
            forecast_date = dt_object.date()

            # Tylko prognozy na przyszłe dni, do days_in_future dni w przód
            if today <= forecast_date <= today + datetime.timedelta(days=days_in_future - 1):
                if forecast_date not in forecast_by_day:
                    forecast_by_day[forecast_date] = {'temps': [], 'descriptions': []}
                forecast_by_day[forecast_date]['temps'].append(item['main']['temp'])
                forecast_by_day[forecast_date]['descriptions'].append(item['weather'][0]['description'])

        if not forecast_by_day:
            return f"Nie mam prognozy na najbliższe {days_in_future} dni dla {city.capitalize()}."

        result_messages = [f"Prognoza pogody dla {city.capitalize()} na najbliższe {days_in_future} dni:"]
        sorted_dates = sorted(forecast_by_day.keys())

        for date in sorted_dates:
            avg_temp = sum(forecast_by_day[date]['temps']) / len(forecast_by_day[date]['temps'])
            most_common_desc = Counter(forecast_by_day[date]['descriptions']).most_common(1)[0][0]
            day_name = date.strftime("%A")
            result_messages.append(f"- {day_name} ({date.strftime('%d.%m.%Y')}): {most_common_desc}, średnia temperatura około {avg_temp:.1f}°C.")
        
        return "\n".join(result_messages)

    except Exception as e:
        print(f"Błąd prognozy pogody: {e}")
        return "Nie mogę pobrać prognozy pogody."

# --- Istniejące funkcje (bez zmian) ---


def get_weather(lat, lon, city_name_display="Warszawa"):
    """Pobiera pogodę dla danego miasta na podstawie współrzędnych."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_key}&units=metric&lang=pl"
    try:
        print(f"Weather API URL: {url}") # Debug print
        response = requests.get(url).json()
        print(f"Weather API Response: {response}") # Debug print
        if response.get("cod") != 200:
            return f"Nie mogę pobrać pogody dla {city_name_display}. (Kod błędu: {response.get("cod")}, Wiadomość: {response.get("message")})"
        
        desc = response['weather'][0]['description']
        temp = response['main']['temp']
        timezone_name = get_timezone_from_coordinates(lat, lon)
        if timezone_name:
            tz = pytz.timezone(timezone_name)
            now_utc = datetime.datetime.now(pytz.utc)
            local_time = now_utc.astimezone(tz)
            time_str = local_time.strftime('%H:%M')
            return f"W {city_name_display} jest teraz {time_str}. Pogoda: {desc}, temperatura {temp}°C."
        else:
            return f"Aktualna pogoda w {city_name_display}: {desc}, temperatura {temp}°C."

    except Exception as e:
        print(f"Błąd pogody: {e}")
        return "Nie mogę pobrać pogody."

def ask_gpt(query, chat_history):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 1. Wyszukaj w bazie wiedzy
    knowledge = query_knowledge_base(query)
    
    # 2. Przygotuj kontekst dla GPT
    system_prompt = f"Jesteś Jarvisem – chatbotem o osobowości: {personality}."
    if knowledge:
        knowledge_context = "\n".join(knowledge)
        system_prompt += f"""
Oto informacje z Twojej bazy wiedzy, które mogą być pomocne:
---
{knowledge_context}
---"""

    current_chat_history = chat_history + [{"role": "user", "content": query}]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + current_chat_history[-10:],
            temperature=0.8,
            max_tokens=400 # Zwiększamy, aby zmieścić potencjalnie dłuższe odpowiedzi z kontekstem
        )
        message = response.choices[0].message.content
        return message
    except Exception as e:
        print(f"Błąd OpenAI: {e}")
        return "Przepraszam, mam problem z połączeniem z moim mózgiem."


def add_reminder(text):
    with open("reminders.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} – {text}\n")
    return "Przypomnienie zapisane."

def change_personality(cmd):
    global personality
    if "zostań zabawny" in cmd:
        personality = "zabawny, żartobliwy, luzacki"
        return "Zmieniam styl na zabawny!"
    elif "bądź poważny" in cmd:
        personality = "poważny, rzeczowy, naukowy"
        return "Tryb poważny włączony."
    elif "bądź filozoficzny" in cmd:
        personality = "refleksyjny, filozoficzny, głęboki"
        return "Okej. Czas na rozmyślania."
    elif "bądź naturalny" in cmd:
        personality = "naturalny, pomocny, inteligentny"
        return "Wracam do standardowego stylu."
    else:
        return "Nie rozumiem, jaką osobowość wybrać."

# --- Zaktualizowany process_command ---

def process_command(cmd, chat_history):
    cmd_lower = cmd.lower()
    response = {"type": "text", "content": ""}

    print(f"User command: {cmd_lower}") # Debug print

    # --- Moduł 1: Integracja z Systemem Operacyjnym ---
    list_match = re.search(r"(pokaż|wyświetl|listuj) (pliki|zawartość)(?: w (.*))?", cmd_lower)
    create_dir_match = re.search(r"(stwórz|utwórz) (katalog|folder) (.*)", cmd_lower)
    read_file_match = re.search(r"(odczytaj|pokaż|przeczytaj) plik (.*)", cmd_lower)
    write_file_match = re.search(r"(zapisz|napisz)(?: do pliku)? (.*?): (.*)", cmd_lower)
    execute_match = re.search(r"(wykonaj|uruchom) polecenie (.*)", cmd_lower)
    search_match = re.search(r"(wyszukaj|znajdź) w (internecie|google) (.*)", cmd_lower)
    learn_match = re.search(r"(naucz się|zapamiętaj|przeczytaj i zapamiętaj) plik (.*)", cmd_lower)
    calendar_match = re.search(r"(pokaż|co mam w) kalendarz(u)?", cmd_lower)
    create_event_match = re.search(r"(dodaj|stwórz) wydarzenie (.*) od (.*) do (.*)", cmd_lower)
    open_app_match = re.search(r"(otwórz|uruchom) (.+)", cmd_lower)
    open_web_match = re.search(r"(otwórz|przejdź do) (?:stronę|strony)?\s*(https?://[^\s]+|www\.[^\s]+|[^\s]+\.[a-z]{2,}|google|youtube|facebook|twitter|wikipedia|amazon|netflix)", cmd_lower)

    # Najpierw sprawdzamy polecenia otwierania stron, bo są bardziej specyficzne
    if open_web_match:
        url = open_web_match.group(2).strip()
        response["content"] = open_web_page(url)
        return response
    elif open_app_match:
        app_name = open_app_match.group(2).strip()
        response["content"] = open_application(app_name)
        return response
    elif list_match:
        path = list_match.group(3).strip() if list_match.group(3) else "."
        response["content"] = list_directory_contents(path)
        return response

    # --- Obsługa Czasu ---
    time_match = re.search(r"(która godzina|jaki jest czas)(?: w (.+))?", cmd_lower)
    if time_match:
        city_name = time_match.group(2).strip() if time_match.group(2) else None
        response["content"] = get_current_time(city_name)

    # --- Obsługa Pogody ---
    # Prognoza pogody na konkretną liczbę dni (np. "prognoza pogody w warszawie na 3 dni")
    forecast_multi_day_match = re.search(r"(prognoza|pogoda)(?: dla| w)? (.+?) na (\d+) dni", cmd_lower)
    # Prognoza pogody na jutro/pojutrze (np. "pogoda w krakowie jutro")
    forecast_single_day_match = re.search(r"(prognoza|pogoda)(?: dla| w)? (.+?) (jutro|pojutrze)", cmd_lower)
    # Aktualna pogoda (np. "pogoda w warszawie")
    current_weather_match = re.search(r"pogoda w (.+)", cmd_lower)

    city_name = None
    days_to_forecast = 0

    if forecast_multi_day_match:
        city_name = forecast_multi_day_match.group(2).strip()
        days_to_forecast = int(forecast_multi_day_match.group(3))
    elif forecast_single_day_match:
        city_name = forecast_single_day_match.group(2).strip()
        when = forecast_single_day_match.group(3).strip()
        if when == "jutro":
            days_to_forecast = 1
        elif when == "pojutrze":
            days_to_forecast = 2
    elif current_weather_match:
        city_name = current_weather_match.group(1).strip()
    elif "pogoda" in cmd_lower:
        city_name = "Warszawa" # Domyślne miasto

    if city_name:
        coords = get_coordinates_from_city_name(city_name)
        if coords:
            display_city_name = coords['name']
            if 'local_names' in coords and 'pl' in coords['local_names']:
                display_city_name = coords['local_names']['pl'] # Użyj polskiej nazwy, jeśli dostępna
            if days_to_forecast > 0:
                if 0 < days_to_forecast <= 5:
                    response["content"] = get_weather_forecast(coords['lat'], coords['lon'], days_to_forecast, display_city_name)
                else:
                    response["content"] = "Mogę podać prognozę tylko do 5 dni w przód."
            else:
                response["content"] = get_weather(coords['lat'], coords['lon'], display_city_name)
        else:
            response["content"] = f"Nie mogę znaleźć współrzędnych dla miasta '{city_name}'. Sprawdź, czy nazwa jest poprawna."

    elif "godzina" in cmd_lower or "czas" in cmd_lower:
        print("Detected time query.") # Debug print
        response["content"] = get_current_time()
    elif "przetłumacz" in cmd_lower:
        response["content"] = translate_text(cmd)
    elif "znajdź w wikipedii" in cmd_lower:
        topic = cmd_lower.replace("znajdź w wikipedii", "").strip()
        response["content"] = get_wikipedia_summary(topic)
    elif "oblicz" in cmd_lower:
        response["content"] = calculate(cmd)
    elif "żart" in cmd_lower or "dowcip" in cmd_lower:
        response["content"] = get_joke()
    elif "wiadomości" in cmd_lower or "news" in cmd_lower:
        response["content"] = get_news()
    elif "zapamiętaj" in cmd_lower:
        response["content"] = "Zapamiętane w kontekście tej rozmowy."
    elif "przypomnij" in cmd_lower or "kalendarz" in cmd_lower:
        if os.path.exists("reminders.txt"):
            with open("reminders.txt", "r", encoding="utf-8") as f:
                data = f.read()
            response["content"] = "Oto twoje przypomnienia:\n" + data
        else:
            response["content"] = "Nie masz żadnych przypomnień."
    elif "osobowość" in cmd_lower or "zostań" in cmd_lower or "bądź" in cmd_lower:
        response["content"] = change_personality(cmd_lower)
    else:
        response["content"] = ask_gpt(cmd, chat_history)
    return response

