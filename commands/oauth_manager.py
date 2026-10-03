import webbrowser
import requests

AUTH_URL = "https://oauth.yandex.ru/authorize"
TOKEN_URL = "https://oauth.yandex.ru/token"
REDIRECT_URI = "https://oauth.yandex.ru/verification_code"

def get_authorization_url(client_id: str, scope: str = "") -> str:
    """
    Формирует URL для авторизации OAuth Яндекса.
    """
    url = f"{AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={REDIRECT_URI}"
    if scope:
        url += f"&scope={scope}"
    return url

def exchange_code_for_tokens(client_id: str, client_secret: str, code: str):
    """
    Обменивает authorization_code на access_token и refresh_token.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI
    }
    try:
        response = requests.post(TOKEN_URL, data=data)
        response.raise_for_status()
        tokens = response.json()
        return tokens.get("access_token"), tokens.get("refresh_token")
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP при обмене кода: {e.response.status_code}")
        print("Ответ сервера:", e.response.text)
        return None, None
    except Exception as e:
        print(f"Ошибка при обмене кода: {e}")
        return None, None
