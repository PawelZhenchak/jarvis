import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import uuid
import sqlite3
from dotenv import load_dotenv
from jarvis_core import process_command

# --- Inicjalizacja Aplikacji ---
load_dotenv()
app = Flask(__name__, static_folder='frontend/build')

# --- Konfiguracja Bazy Danych ---
DB_FILE = "jarvis_chats.db"

def get_db_connection():
    """Tworzy połączenie z bazą danych."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicjalizuje bazę danych i tworzy tabelę, jeśli nie istnieje."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON messages (chat_id, timestamp);')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                title TEXT
            )
        ''')
        conn.commit()


# --- Główne Trasy Aplikacji ---
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/chat/<chat_id>')
def chat_page(chat_id):
    return app.send_static_file('index.html')

@app.route('/chat_data')
def chat_data():
    chat_id = request.args.get('chat_id')
    chat_history = []
    all_chats = []

    with get_db_connection() as conn:
        if chat_id:
            history_rows = conn.execute(
                'SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC',
                (chat_id,)
            ).fetchall()
            chat_history = [dict(row) for row in history_rows]

        chat_ids_rows = conn.execute(
            'SELECT c.chat_id, c.title FROM chats c ORDER BY c.chat_id DESC'
        ).fetchall()
        all_chats = [dict(row) for row in chat_ids_rows]

    return jsonify({'chat_history': chat_history, 'all_chats': all_chats})

@app.route('/ask', methods=['POST'])
def ask():
    print("--- Otrzymano POST na /ask ---")
    data = request.json
    print(f"Dane z frontendu: {data}")

    user_input = data.get('message')
    chat_id = data.get('chat_id')
    print(f"Wiadomość od usera: '{user_input}', ID czatu: '{chat_id}'")

    if not user_input or not chat_id:
        print("Błąd: Brak wiadomości lub ID czatu")
        return jsonify({"error": "Brak wiadomości lub ID czatu"}), 400

    with get_db_connection() as conn:
        # Pobierz historię do przekazania do AI
        history_rows = conn.execute(
            'SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC',
            (chat_id,)
        ).fetchall()
        chat_history = [dict(row) for row in history_rows]
        print(f"Historia czatu dla AI: {chat_history}")

        # Przetwórz komendę
        print("Przetwarzanie komendy przez jarvis_core...")
        response_data = process_command(user_input, chat_history)
        print(f"Odpowiedź z process_command: {response_data}")
        assistant_response = response_data['content']

        # Zapisz obie wiadomości do bazy danych
        print("Zapisywanie wiadomości do bazy danych...")
        conn.execute(
            'INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
            (chat_id, 'user', user_input)
        )
        conn.execute(
            'INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
            (chat_id, 'assistant', assistant_response)
        )
        conn.commit()
        print("Zapisano pomyślnie.")

    print(f"--- Wysyłanie odpowiedzi do frontendu: {response_data} ---")
    return jsonify(response_data)

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    chat_id = request.json.get('chat_id')
    if not chat_id:
        return jsonify({"error": "Brak ID czatu do usunięcia"}), 400

    with get_db_connection() as conn:
        conn.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
        conn.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
        conn.commit()
    return jsonify({"success": True, "message": f"Czat {chat_id} usunięty."})

@app.route('/summarize_chat', methods=['POST'])
def summarize_chat():
    chat_id = request.json.get('chat_id')
    if not chat_id:
        return jsonify({"error": "Brak ID czatu do podsumowania"}), 400

    with get_db_connection() as conn:
        history_rows = conn.execute(
            'SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC',
            (chat_id,)
        ).fetchall()
        chat_history = [dict(row) for row in history_rows]

        if not chat_history:
            return jsonify({"error": "Brak historii czatu do podsumowania"}), 400

        # Przygotuj historię dla GPT
        gpt_history = []
        for msg in chat_history:
            gpt_history.append({"role": msg['role'], "content": msg['content']})
        
        # Dodaj instrukcję dla GPT, aby podsumował czat
        gpt_history.append({"role": "user", "content": "Podsumuj tę rozmowę w jednym, krótkim zdaniu (maksymalnie 10 słów) i podaj tytuł. Nie dodawaj żadnych dodatkowych komentarzy, tylko sam tytuł."})

        try:
            from jarvis_core import ask_gpt
            summary_title = ask_gpt("", gpt_history) # Pusty query, bo historia jest w gpt_history
            
            # Upewnij się, że tytuł nie jest zbyt długi
            if len(summary_title.split()) > 10:
                summary_title = "Podsumowanie czatu"

            conn.execute('INSERT OR REPLACE INTO chats (chat_id, title) VALUES (?, ?)', (chat_id, summary_title))
            conn.commit()
            return jsonify({"success": True, "title": summary_title})
        except Exception as e:
            print(f"Błąd podczas podsumowywania czatu: {e}")
            return jsonify({"error": "Błąd podczas podsumowywania czatu"}), 500

if __name__ == '__main__':
    init_db()  # Upewnij się, że baza danych jest gotowa
    app.run(debug=True)
