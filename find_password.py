import hashlib

# Dane wejściowe
target_hash = "ecd3f38a04e0f41e171adbfa836b7adf786c06c4"  # Podany hash
salt = "28e5ebf4b19836289f8e893b37827375"  # Podany salt
password_file = "rockyou.txt"  # Ścieżka do pliku z hasłami

# Funkcja do generowania hash'y
def generate_hash(salt, password):
    combinations = [
        salt + password,
        password + salt,
        hashlib.sha1((salt + password).encode()).hexdigest(),
    ]
    for combo in combinations:
        hash_attempt = hashlib.sha1(combo.encode()).hexdigest()
        if hash_attempt == target_hash:
            return hash_attempt
    return None

# Otwieranie pliku z hasłami i testowanie każdego hasła
try:
    with open(password_file, "r", encoding="latin-1") as file:  # Plik rockyou.txt używa kodowania latin-1
        for line in file:
            password = line.strip()  # Usunięcie białych znaków (np. \n)
            hash_attempt = generate_hash(salt, password)

            # Sprawdzenie, czy hash się zgadza
            if hash_attempt == target_hash:
                print(f"Znaleziono hasło: {password}")
                break
        else:
            print("Nie znaleziono hasła w pliku.")
except FileNotFoundError:
    print(f"Plik {password_file} nie został znaleziony. Upewnij się, że jest w poprawnej lokalizacji.")
