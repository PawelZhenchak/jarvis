# Opis Aplikacji

To jest Jarvis, Twój osobisty asystent AI! Działa trochę jak ChatGPT, ale jest Twój własny. Możesz z nim gadać, zadawać pytania, a on będzie próbował Ci pomóc. Ma też pamięć, więc pamięta Wasze rozmowy.

## Struktura Aplikacji

Projekt składa się z dwóch głównych części:

1.  **Backend (kuchnia) - `app.py` i `jarvis_core.py` (Python/Flask):**
    *   `app.py`: To serce aplikacji, które obsługuje zapytania z frontendu (np. Twoje wiadomości).
    *   `jarvis_core.py`: Tutaj dzieje się cała magia AI i przetwarzania komend. To tutaj Jarvis myśli i i decyduje, jak Ci odpowiedzieć.
    *   **Baza danych (`jarvis_chats.db`):** Jarvis przechowuje tutaj historię Waszych rozmów, żeby pamiętać, o czym gadaliście.

2.  **Frontend (kelnerzy) - folder `frontend/` (Next.js/React):**
    *   To jest to, co widzisz w przeglądarce. Interfejs użytkownika, przez który rozmawiasz z Jarvisem.
    *   Używa Next.js i Reacta do budowania dynamicznych stron.
    *   Komunikuje się z backendem, wysyłając Twoje wiadomości i odbierając odpowiedzi Jarvisa.

## Jak to działa?

Kiedy wysyłasz wiadomość:
1.  Frontend (kelner) wysyła Twoją wiadomość do backendu (kuchni).
2.  Backend przekazuje wiadomość do `jarvis_core.py` (mózgu Jarvisa).
3.  `jarvis_core.py` przetwarza wiadomość, sprawdza historię rozmowy i generuje odpowiedź.
4.  Odpowiedź wraca do backendu, a stamtąd do frontendu.
5.  Frontend wyświetla odpowiedź Jarvisa na ekranie.

# Integracja z MCP Toolkit

## Gemini Added Memories
- Wrócono do commita `b3ccbba` (wczorajsza działająca wersja Jarvisa).

*   **Język:** Mów do użytkownika prostym językiem, jak do 16-latka, który dopiero zaczyna programować. Unikaj skomplikowanych terminów, a jeśli już musisz ich użyć, to je wytłumacz.
*   **Powitanie:** Zawsze zaczynaj rozmowę od "Siema ziom!".
*   **Tłumaczenie:** Tłumacz wszystko na polski, używając slangu i zwrotów, które ogarnie młody programista.
*   **Cel:** Pomagaj użytkownikowi uczyć się programowania przez wspólne działanie. Tłumacz, co robisz i dlaczego.
*   **Kontekst:** Pamiętaj, że użytkownik jest początkujący, więc dawaj mu dużo kontekstu i wyjaśnień.

# Log Zdarzeń - Naprawa Jarvisa (20.08.2025)

Tak, ziom, jak najbardziej! To nie zadziałało "samo z siebie". Zrobiliśmy kilka ważnych rzeczy, żeby to naprawić:

   1. Naprawiliśmy frontend: Najpierw okazało się, że w folderze frontend brakowało potrzebnych paczek (takich klocków, z których zbudowana jest strona). Uruchomiłem npm install, co pobrało i zainstalowało te wszystkie "klocki". Bez tego strona w ogóle by nie wstała.

   2. Wyczyszczenie bałaganu: Kiedy pojawił się błąd połączenia, próbowałem go naprawić, zmieniając kod. Okazało się, że to nie to. Dlatego cofnęliśmy cały projekt do "czystej", wczorajszej wersji za pomocą Gita. To dało nam pewność, że nie ma tam żadnych przypadkowych zmian, które mogłyby psuć aplikację.

   3. Zmiana sposobu uruchamiania: Najważniejsza zmiana na końcu. Zamiast odpalać backend w tle, gdzie nie widzieliśmy co się dzieje, uruchomiłeś go ręcznie w osobnym oknie. To dało mu odpowiednie środowisko do pracy i rozwiązało ostateczny problem z połączeniem.

  Więc tak, zdecydowanie to naprawiliśmy! Dobra robota.

# Log Zdarzeń - Implementacja Aplikacji Desktopowej i STT (21.08.2025)

Dziś zrobiliśmy ogromny krok naprzód! Jarvis zyskał aplikację desktopową i nowy, niezawodny system rozpoznawania mowy.

- **Aplikacja Desktopowa Electron**: Stworzyliśmy i uruchomiliśmy Jarvisa jako samodzielną aplikację na komputer.
- **Migracja Rozpoznawania Mowy (STT)**: Przeniesiliśmy całą logikę zamiany mowy na tekst do backendu Pythona, używając usługi AssemblyAI. To rozwiązało problemy z mikrofonem w aplikacji Electron.
- **Naprawa Błędów**:
    - Rozwiązaliśmy problem z uruchamianiem aplikacji Electron, który powodował jej natychmiastowe zamykanie.
    - Naprawiliśmy błąd rysowania w komponencie `stardust.tsx` (ujemny promień).
    - Poprawiliśmy literówkę w kodzie frontendu (`JSON_stringify`).
- **Usprawnienia**: Aplikacja teraz lepiej informuje o problemach z mikrofonem i siecią, wyświetlając przyjazne komunikaty.

# Log Zdarzeń - Nowe Funkcje i Burzliwa Migracja AI (24.08.2025)

Dzisiejsza sesja była prawdziwym maratonem, w trakcie którego znacząco rozbudowaliśmy możliwości Jarvisa, a także przeprowadziliśmy skomplikowaną operację na jego "mózgu", która przypominała scenariusz z dobrego filmu akcji.

### Nowe Funkcje i Usprawnienia:

1.  **Przycisk "STOP"**: Dodaliśmy w interfejsie przycisk, który pozwala natychmiast przerwać wypowiedź Jarvisa, dając użytkownikowi pełną kontrolę.
2.  **Dostęp do Internetu (Google Search)**: Zintegrowaliśmy Jarvis z Google Search API. Potrafi on teraz wyszukiwać aktualne informacje w internecie, aby odpowiadać na pytania wykraczające poza jego bazową wiedzę.
3.  **Rozpoznawanie Obrazków (Multimodalność)**: Zaimplementowaliśmy funkcjonalność multimodalną. Użytkownik może teraz wysłać obrazek, a Jarvis (dzięki modelowi `gpt-4o`) jest w stanie go przeanalizować i odpowiedzieć na pytania na jego temat.
4.  **Tryb Płynnej Rozmowy**: Po wielu próbach i poprawkach, wdrożyliśmy w pełni działający tryb ciągłej konwersacji. Po odpowiedzi Jarvisa, mikrofon automatycznie włącza się ponownie, a dzięki detekcji ciszy, aplikacja nie wymaga klikania po każdej wypowiedzi.

### Prace "pod maską" i Naprawione Błędy:

-   **Burzliwa Migracja AI**: Podjęliśmy ambitną próbę migracji rdzenia AI z **OpenAI** na **Google Gemini**. Po napotkaniu problemów z limitami darmowych zapytań na obu platformach, ostatecznie, na Twoją decyzję, wróciliśmy do stabilnej i w pełni skonfigurowanej implementacji opartej na **OpenAI**. To była cenna lekcja.
-   **Naprawa Logiki Narzędzi**: Poprawiliśmy błąd w narzędziu do podawania ciekawostek, które teraz poprawnie zwraca ich zadaną liczbę.
-   **Naprawa Interfejsu**: Rozwiązaliśmy kluczowy problem znikających wiadomości użytkownika w oknie czatu oraz irytujący błąd zapętlającego się stanu "myślenia" w trybie płynnej rozmowy.
-   **Konfiguracja i Debugowanie**: Zdiagnozowaliśmy i rozwiązaliśmy szereg problemów konfiguracyjnych, w tym brakujące lub niepoprawne klucze API oraz błędy związane z wirtualnym środowiskiem Pythona (`venv`).

Po tej sesji Jarvis jest nie tylko bardziej interaktywny i potężniejszy, ale też znacznie stabilniejszy. Kawał dobrej, inżynierskiej roboty!

# Log Zdarzeń - Debugowanie i Naprawa Wysyłania Audio (25.08.2025)

Dzisiaj skupiliśmy się na naprawie krytycznego błędu, który uniemożliwiał Jarvisowi rozumienie poleceń głosowych. To była klasyczna detektywistyczna robota!

- **Problem**: Po nagraniu polecenia głosowego, backend (Python) zgłaszał błąd `Error: No audio data in request`, mimo że frontend (przeglądarka) wydawał się wysyłać dane.

- **Dochodzenie i Ślepe Zaułki**:
    1.  Początkowo podejrzewaliśmy, że problemem jest format audio. Zmieniliśmy w kodzie format z `audio/webm` na `audio/wav`, licząc, że to rozwiąże problem.
    2.  Niestety, to nie pomogło. Błąd nadal występował, co oznaczało, że problem leży głębiej.

- **Przełom i Rozwiązanie**:
    1.  Zajrzeliśmy do kodu backendu (`app.py`) i odkryliśmy kluczową informację: serwer oczekiwał *surowych danych audio* (`request.data`), a nie danych zapakowanych w formularz (`request.files`).
    2.  Nasz frontend wysyłał audio opakowane w `FormData` - czyli w takim "pudełku". Backend oczekiwał samego pliku, bez pudełka. To było źródło całego nieporozumienia.
    3.  Naprawiliśmy kod we frontendzie (`chat-interface.tsx`), usuwając pakowanie w `FormData`. Teraz frontend wysyła surowe dane audio bezpośrednio w ciele zapytania.
    4.  Dodatkowo ustawiliśmy poprawny nagłówek `Content-Type: audio/webm` i wróciliśmy do tego formatu, który jest bardziej standardowy dla przeglądarek.

- **Rezultat**: Po tych zmianach komunikacja wróciła do normy. Backend w końcu "usłyszał", co wysyła frontend, i funkcja zamiany mowy na tekst znów działa poprawnie. Dobra robota!