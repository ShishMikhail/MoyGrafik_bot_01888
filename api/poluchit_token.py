import requests

def get_new_access_token():
    url = "https://api.moygrafik.ru/oauth/v2/token"
    data = {
        'client_id': '5_40i8muscyag4cg08cgkk8skc0ck4coc04c4wccwocc8ocoksww',
        'client_secret': 'zl2jjjh35z40ks8os48ssss4ggk80gsck8ck44k40k8okk08w',
        'grant_type': 'password',
        'username': 'moygrafik@boobl-goom.ru',
        'password': '!qaz2wsX'
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        # Записываем access token в файл
        with open('access_token.txt', 'w') as f:
            f.write(access_token)
        print("Access token успешно сохранён.")
    else:
        print(f"Failed to obtain access token: {response.status_code}, {response.text}")

def use_access_token():
    # Читаем токен из файла
    try:
        with open('access_token.txt', 'r') as f:
            access_token = f.read().strip()
            print(f"Используем токен: {access_token}")

    except FileNotFoundError:
        print("Токен не найден. Получите новый токен.")

# Получение нового токена
get_new_access_token()

# Использование сохраненного токена
use_access_token()