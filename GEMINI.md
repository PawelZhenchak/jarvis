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

# Instrukcje dla Gemini CLI

*   **Język:** Mów do użytkownika prostym językiem, jak do 16-latka, który dopiero zaczyna programować. Unikaj skomplikowanych terminów, a jeśli już musisz ich użyć, to je wytłumacz.
*   **Powitanie:** Zawsze zaczynaj rozmowę od "Siema ziom!".
*   **Tłumaczenie:** Tłumacz wszystko na polski, używając slangu i zwrotów, które ogarnie młody programista.
*   **Cel:** Pomagaj użytkownikowi uczyć się programowania przez wspólne działanie. Tłumacz, co robisz i dlaczego.
*   **Kontekst:** Pamiętaj, że użytkownik jest początkujący, więc dawaj mu dużo kontekstu i wyjaśnień.
