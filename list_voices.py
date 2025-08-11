
import pyttsx3
import sys

# Przekierowanie standardowego wyjścia do pliku, aby uniknąć problemów z kodowaniem w konsoli
sys.stdout = open('voices.txt', 'w', encoding='utf-8')

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print(f"Znaleziono {len(voices)} głosów:")
    print("-" * 30)

    for i, voice in enumerate(voices):
        print(f"Głos #{i}")
        print(f"  ID: {voice.id}")
        print(f"  Nazwa: {voice.name}")
        print(f"  Wiek: {voice.age}")
        print(f"  Płeć: {voice.gender}")
        print(f"  Język: {voice.languages}")
        print("-" * 30)

except Exception as e:
    print(f"Wystąpił błąd: {e}")

finally:
    # Zamknięcie pliku jest ważne
    sys.stdout.close()

# Wydrukowanie komunikatu do konsoli, że skrypt zakończył działanie
# To zostanie wyświetlone w terminalu, bo przekierowaliśmy tylko stdout dla printów powyżej
# (Chociaż w tym przypadku, po zamknięciu sys.stdout, to może nie zadziałać, ale warto spróbować)
print("Skończyłem. Sprawdź plik voices.txt")
