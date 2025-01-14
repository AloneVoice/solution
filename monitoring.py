import requests
import pandas as pd
from io import StringIO
import time
from collections import Counter
from datetime import datetime

# Funkcja do pobierania logów z URL
def fetch_logs():
    response = requests.get("https://kingbank.pl/get-system-logs")
    response.raise_for_status()
    return pd.read_csv(StringIO(response.content.decode('utf-8')), names=[
        "date", "time", "ip", "method", "url", "http_version", "status", "referrer", "user_agent", "params"
    ])

# Funkcja do wykrywania wielokrotnych nieudanych prób logowania
def detect_failed_logins(logs):
    anomalies = []
    failed_login_attempts = logs[(logs["status"] == 400)]

    # Zliczanie nieudanych prób logowania z podziałem na IP
    ip_counts = Counter(failed_login_attempts["ip"])

    # Próg dla podejrzanej aktywności (np. 2 nieudane próby z jednego IP)
    for ip, count in ip_counts.items():
        if count > 1:
            # Pobieramy datę, czas i login z pierwszego zdarzenia
            first_occurrence = failed_login_attempts[failed_login_attempts["ip"] == ip].iloc[0]
            login_match = None
            if "login=" in first_occurrence["params"]:
                # Wyciągamy login z parametru
                params = first_occurrence["params"]
                login_match = params.split("login=")[1].split("&")[0]  # Pobiera login między `login=` a `&`

            anomalies.append(f"""
===================================
Wykryto wielokrotne nieudane próby logowania:
Data i czas pierwszego zdarzenia: {first_occurrence['date']} {first_occurrence['time']}
IP: {ip}
Login: {login_match if login_match else "Nie znaleziono"}
Opis: {count} nieudanych prób logowania z jednego IP.
===================================
            """)
    return anomalies

# Funkcja do zapisywania anomalii do pliku .log
def save_anomalies_to_log(anomalies, file_name="anomalies.log"):
    with open(file_name, "a", encoding="utf-8") as log_file:
        for anomaly in anomalies:
            log_file.write(anomaly + "\n")

# Funkcja główna do monitorowania logów
def main():
    przetworzone_wiersze = 0
    print("Monitoring logów w czasie rzeczywistym...")

    while True:
        try:
            # Pobierz logi
            logs = fetch_logs()

            # Przetwórz tylko nowe logi
            nowe_wiersze = logs.iloc[przetworzone_wiersze:]
            if not nowe_wiersze.empty:
                # Wykryj nieudane próby logowania
                anomalies = detect_failed_logins(nowe_wiersze)
                if anomalies:
                    for anomaly in anomalies:
                        print(anomaly)
                    save_anomalies_to_log(anomalies)

                # Zaktualizuj liczbę przetworzonych wierszy
                przetworzone_wiersze += len(nowe_wiersze)

            # Odczekaj chwilę przed ponownym sprawdzeniem
            time.sleep(5)
        except Exception as e:
            print(f"Błąd: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
