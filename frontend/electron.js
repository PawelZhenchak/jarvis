const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

console.log("Plik electron.js wystartował.");

function createWindow() {
  console.log("Tworzę okno aplikacji...");
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
  });
  console.log("Okno stworzone. Ładuję URL: http://localhost:3000");
  mainWindow.loadURL('http://localhost:3000');

  mainWindow.webContents.on('did-finish-load', () => {
    console.log("URL pomyślnie załadowany.");
  });
}

function checkServerReady(callback) {
    const url = 'http://localhost:3000';
    const maxRetries = 15; // Zwiększono liczbę prób
    let retries = 0;

    const tryConnect = () => {
        console.log(`Sprawdzam czy serwer frontend jest gotowy... próba ${retries + 1}`);
        const req = http.get(url, (res) => {
            if (res.statusCode === 200) {
                console.log("Serwer frontendu jest gotowy!");
                callback();
            } else {
                console.log(`Serwer odpowiedział kodem ${res.statusCode}. Ponawiam próbę...`);
                retry();
            }
        });

        req.on('error', (err) => {
            console.log(`Błąd połączenia: ${err.message}. Ponawiam próbę...`);
            retry();
        });
    };

    const retry = () => {
        retries++;
        if (retries < maxRetries) {
            setTimeout(tryConnect, 2000); // Czekaj 2 sekundy przed kolejną próbą
        } else {
            console.error("Nie udało się połączyć z serwerem frontendu po wielu próbach. Zamykam aplikację.");
            app.quit();
        }
    };

    tryConnect();
}

app.on('ready', () => {
    console.log("Aplikacja Electron gotowa. Uruchamiam procesy w tle...");

    const rootDir = path.join(__dirname, '..');
    console.log(`Uruchamianie start_jarvis.bat z folderu: ${rootDir}`);

    const bat = spawn('cmd.exe', ['/c', 'start_jarvis.bat'], {
      cwd: rootDir,
      detached: true,
      stdio: 'ignore'
    });

    bat.unref();

    console.log("Oczekiwanie na start serwera deweloperskiego Next.js...");
    checkServerReady(() => {
        console.log("Serwer gotowy, tworzę okno aplikacji.");
        createWindow();
    });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    console.log("Wszystkie okna zamknięte. Zamykam aplikację.");
    app.quit();
  }
});

app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) {
        console.log("Aplikacja aktywowana. Tworzę nowe okno.");
        checkServerReady(() => {
            createWindow();
        });
    }
});