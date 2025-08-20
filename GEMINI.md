# Opis Aplikacji

To jest Jarvis, Twój osobisty asystent AI! Działa trochę jak ChatGPT, ale jest Twój własny. Możesz z nim gadać, zadawać pytania, a on będzie próbował Ci pomóc. Ma też pamięć, więc pamięta Wasze rozmowy.

## Struktura Aplikacji

Projekt składa się z dwóch głównych części:

1.  **Backend (kuchnia) - `app.py` i `jarvis_core.py` (Python/Flask):**
    *   `app.py`: To serce aplikacji, które obsługuje zapytania z frontendu (np. Twoje wiadomości).
    *   `jarvis_core.py`: Tutaj dzieje się cała magia AI i przetwarzania komend. To tutaj Jarvis myśli i decyduje, jak Ci odpowiedzieć.
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