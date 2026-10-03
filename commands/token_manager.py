import commands.control_kojima_bulb as bulb_control
import json
import os

TOKEN_STORE_PATH = os.path.join(os.path.dirname(__file__), "token_store.json")

def refresh_tokens():
    """Обновление access_token и refresh_token через get_new_tokens"""
    new_access_token, new_refresh_token = bulb_control.get_new_tokens()
    if new_access_token and new_refresh_token:
        update_refresh_token_in_file(new_refresh_token)
        update_access_token_in_file(new_access_token)
        print("Токены успешно обновлены")
        return new_access_token, new_refresh_token
    else:
        print("Не удалось обновить токены")
        return None, None

def update_refresh_token_in_file(new_refresh_token):
    """Обновить REFRESH_TOKEN в файле token_store.json"""
    try:
        with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        tokens["REFRESH_TOKEN"] = new_refresh_token
        with open(TOKEN_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
        print("REFRESH_TOKEN обновлен в файле token_store.json")
    except Exception as e:
        print(f"Ошибка при обновлении REFRESH_TOKEN в файле: {e}")

def update_access_token_in_file(new_access_token):
    """Обновить ACCESS_TOKEN в файле token_store.json"""
    try:
        with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        tokens["ACCESS_TOKEN"] = new_access_token
        with open(TOKEN_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
        print("ACCESS_TOKEN обновлен в файле token_store.json")
    except Exception as e:
        print(f"Ошибка при обновлении ACCESS_TOKEN в файле: {e}")
