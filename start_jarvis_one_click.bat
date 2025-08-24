@echo off
echo Uruchamiam Jarvisa...

echo Startuje backend (serwer Python)...
start cmd /k "python app.py"

echo Czekam na uruchomienie backendu... (daj mu chwilę)
timeout /t 5 /nobreak >nul

echo Startuje frontend (aplikacja Electron)...
start cmd /k "cd frontend && npm run electron:dev"

echo Jarvis powinien być gotowy!
echo Mozesz zamknac to okno.
exit