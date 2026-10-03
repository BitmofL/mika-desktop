import requests
from commands.command import Command
import pygame
import os

# Инициализация микшера pygame
pygame.mixer.init()

AUDIO_RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_responses")

def play_audio(file_path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"Ошибка воспроизведения аудио {file_path}: {e}")

class WeatherCommand(Command):
    def should_handle(self, text: str) -> bool:
        """Проверяет, содержит ли текст ключевые слова, связанные с погодой."""
        text = text.lower().strip()
        weather_keywords = ["погода","погоду", "температура", "осадки"]
        return any(keyword in text for keyword in weather_keywords)

    def execute(self, text: str, assistant: object) -> dict:
        """Выполняет запрос погоды для автоматически определенного города с помощью WeatherAPI."""
        # Шаг 1: Определение города по IP
        try:
            ip_info = requests.get("https://ipinfo.io/json").json()
            city = ip_info.get("city", "Unknown")
        except Exception as e:
            return {'response': f"Ошибка при определении города: {str(e)}", 'confirmation': None}

        if city == "Unknown":
            return {'response': "Не удалось определить ваш город. Укажите город в настройках.", 'confirmation': None}

        # Шаг 2: Проверка API-ключа
        api_key = '4845bb8ed49544e3b49163915250106'
        if not api_key:
            return {'response': "API-ключ для WeatherAPI не указан в настройках.", 'confirmation': None}

        # Шаг 3: Запрос погоды через WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=ru"
        try:
            response = requests.get(url)
            data = response.json()
            if "error" in data:
                return {'response': f"Не удалось получить погоду для {city}: {data['error']['message']}", 'confirmation': None}

            temp = data["current"]["temp_c"]
            weather_desc = data["current"]["condition"]["text"]
            response_text = f"В городе {city} сейчас {temp:.1f}°C, {weather_desc}."
            import random
            try:
                weather_report_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "weather_report.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3")
                ]
                play_audio(random.choice(weather_report_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио WeatherCommand: {e}")

            
            weather_condition = weather_desc.lower()
            image_path = None
            if "ясно" in weather_condition or "солнечно" in weather_condition:
                image_path = "images/sunny.png"
            elif "облачно" in weather_condition or "пасмурно" in weather_condition:
                image_path = "images/cloudy.png"
            elif "дождь" in weather_condition or "ливень" in weather_condition:
                image_path = "images/rain.png"
            elif "снег" in weather_condition or "метель" in weather_condition:
                image_path = "images/snow.png"

            return {'response': response_text, 'confirmation': None, 'popup': {'text': response_text, 'image': image_path}}
        except Exception as e:
            return {'response': f"Ошибка при получении погоды: {str(e)}", 'confirmation': None}
