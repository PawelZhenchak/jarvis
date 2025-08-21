const { app, BrowserWindow } = require('electron');
const path = require('path');
console.log("Plik electron.js wystartował. [KROK 1]");

function createWindow() {
  console.log("Funkcja createWindow() została wywołana. [KROK 2]");
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      webSecurity: false // TYLKO DO TESTÓW! Nie używać w produkcji.
    }
  });
  console.log("Okno przeglądarki (BrowserWindow) zostało stworzone. [KROK 3]");

  console.log("Próbuję załadować URL: http://localhost:3000 [KROK 4]");
  mainWindow.loadURL('http://localhost:3000');

  mainWindow.webContents.on('did-finish-load', () => {
    console.log("URL został pomyślnie załadowany. [KROK 5]");
  });

  mainWindow.on('closed', () => {
    console.log("Okno zostało zamknięte. [KROK 6]");
  });
}

app.on('ready', () => {
    console.log("Aplikacja Electron jest gotowa ('ready' event). [KROK 7]");
    createWindow();
});

app.on('window-all-closed', function () {
  console.log("Wszystkie okna zostały zamknięte ('window-all-closed' event). [KROK 8]");
  if (process.platform !== 'darwin') {
    console.log("System to nie macOS, zamykam aplikację. [KROK 9]");
    app.quit();
  }
});

app.on('activate', function () {
    console.log("Aplikacja została aktywowana ('activate' event). [KROK 10]");
    if (BrowserWindow.getAllWindows().length === 0) {
        console.log("Brak otwartych okien, tworzę nowe. [KROK 11]");
        createWindow();
    }
});

console.log("Zakończono konfigurację eventów Electrona. [KROK 12]");