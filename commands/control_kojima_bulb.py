import requests

# Конфигурация
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "https://oauth.yandex.ru/verification_code"
DEVICE_ID = "YOUR_DEVICE_ID"
import json
import os

TOKEN_STORE_PATH = os.path.join(os.path.dirname(__file__), "token_store.json")

def get_access_token():
    """Чтение актуального ACCESS_TOKEN из файла token_store.json"""
    try:
        with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        return tokens.get("ACCESS_TOKEN")
    except Exception as e:
        print(f"Ошибка при чтении ACCESS_TOKEN из файла: {e}")
        return None

def get_refresh_token():
    """Чтение актуального REFRESH_TOKEN из файла token_store.json"""
    try:
        with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        return tokens.get("REFRESH_TOKEN")
    except Exception as e:
        print(f"Ошибка при чтении REFRESH_TOKEN из файла: {e}")
        return None
AUTH_URL = "https://oauth.yandex.ru/token"
API_URL = "https://api.iot.yandex.net/v1.0"

def get_new_tokens():
    """Получение нового access_token через refresh_token"""
    try:
        auth_data = {
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(AUTH_URL, data=auth_data)
        response.raise_for_status()
        tokens = response.json()
        return tokens.get("access_token"), tokens.get("refresh_token")
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code}")
        print("Ответ сервера:", e.response.text)
        return None, None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None, None

def send_action(access_token: str, action_type: str, instance: str, value):
    """Отправка действия на устройство"""
    import commands.token_manager as token_manager
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    url = f"{API_URL}/devices/{DEVICE_ID}/actions"
    payload = {
        "actions": [{
            "type": action_type,
            "state": {"instance": instance, "value": value}
        }]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Команда выполнена: {action_type} - {instance}: {value}")
        print(f"Ответ API: {response.json()}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Ошибка 401 Unauthorized. Попытка обновить токены...")
            new_access_token, new_refresh_token = token_manager.refresh_tokens()
            if new_access_token:
                headers["Authorization"] = f"Bearer {get_access_token()}"
                try:
                    retry_response = requests.post(url, json=payload, headers=headers)
                    retry_response.raise_for_status()
                    print(f"Команда выполнена после обновления токена: {action_type} - {instance}: {value}")
                    print(f"Ответ API: {retry_response.json()}")
                    return retry_response.json()
                except Exception as retry_e:
                    print(f"Ошибка после повторной попытки: {retry_e}")
                    return None
            else:
                print("Не удалось обновить токены")
                return None
        else:
            print(f"Ошибка HTTP: {e.response.status_code}")
            print("Ответ сервера:", e.response.text)
            return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def get_device_state(access_token: str, device_id: str):
    """Получить текущее состояние устройства"""
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    url = f"{API_URL}/devices/{DEVICE_ID}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        device_info = response.json()
        return device_info.get("capabilities", [])
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code}")
        print("Ответ сервера:", e.response.text)
        return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def restore_device_state(access_token: str, device_id: str, capabilities):
    """Восстановить состояние устройства"""
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    url = f"{API_URL}/devices/{DEVICE_ID}/actions"
    payload = {
        "actions": capabilities
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Состояние устройства восстановлено")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code}")
        print("Ответ сервера:", e.response.text)
        return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def turn_on(access_token: str):
    """Включить лампочку"""
    return send_action(access_token, "devices.capabilities.on_off", "on", True)

def turn_off(access_token: str):
    """Выключить лампочку"""
    return send_action(access_token, "devices.capabilities.on_off", "on", False)

def set_brightness(access_token: str, brightness: int):
    """Установить яркость (1-100)"""
    if 1 <= brightness <= 100:
        return send_action(access_token, "devices.capabilities.range", "brightness", brightness)
    else:
        print("Яркость должна быть от 1 до 100")
        return None

def set_temperature(access_token: str, temperature_k: int):
    """Установить температуру цвета (2700-6500 K)"""
    if 2700 <= temperature_k <= 6500:
        return send_action(access_token, "devices.capabilities.color_setting", "temperature_k", temperature_k)
    else:
        print("Температура цвета должна быть от 2700 до 6500 K")
        return None

def set_color_scene(access_token: str, scene_id: str):
    """Установить цветовую сцену"""
    available_scenes = [
        "alice", "candle", "fantasy", "garland", "jungle", "neon", "night",
        "ocean", "party", "reading", "rest", "romance", "new_year", "halloween", "breathing"
    ]
    if scene_id in available_scenes:
        return send_action(access_token, "devices.capabilities.color_setting", "scene", scene_id)
    else:
        print(f"Недоступная сцена: {scene_id}. Доступные сцены: {', '.join(available_scenes)}")
        return None

def set_color(access_token: str, rgb: tuple):
    """Установить цвет в формате RGB"""
    try:
        r, g, b = rgb
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            print("Значения RGB должны быть от 0 до 255")
            return None
        color_value = (r << 16) + (g << 8) + b
        print(f"Установка RGB цвета: ({r}, {g}, {b}) -> {color_value}")
        return send_action(access_token, "devices.capabilities.color_setting", "rgb", color_value)
    except ValueError:
        print("RGB должен быть кортежем из трех чисел (r, g, b)")
        return None

def set_hsv_color(access_token: str, hsv: dict):
    """Установить цвет в формате HSV"""
    try:
        h, s, v = hsv["h"], hsv["s"], hsv["v"]
        if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= v <= 100):
            print("HSV значения должны быть: h (0-360), s (0-100), v (0-100)")
            return None
        hsv_value = {"h": h, "s": s, "v": v}
        print(f"Установка HSV цвета: h={h}, s={s}, v={v}")
        return send_action(access_token, "devices.capabilities.color_setting", "hsv", hsv_value)
    except (KeyError, ValueError):
        print("HSV должен быть словарем с ключами 'h', 's', 'v'")
        return None

if __name__ == "__main__":
    access_token = ACCESS_TOKEN
    turn_on(access_token)
    set_brightness(access_token, 50)
    set_hsv_color(access_token, {"h": 0, "s": 100, "v": 100})