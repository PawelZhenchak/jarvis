@echo off
ECHO Uruchamianie Jarvisa...

ECHO Startuje backend (serwer Python)...
start "Jarvis Backend" /D "%CD%" python app.py

ECHO Startuje frontend (serwer Next.js)...
start "Jarvis Frontend" /D "%CD%\frontend" npm run dev

ECHO Wszystko gotowe! Miłej zabawy z Jarvisem!
pause