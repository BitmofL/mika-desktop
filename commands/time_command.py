from commands.command import Command
import datetime
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

class TimeCommand(Command):
    def should_handle(self, text: str) -> bool:
        text = text.lower().strip()
        weather_keywords = ['время','времени']
        return any(keyword in text for keyword in weather_keywords)
    def execute(self, text: str, assistant: object) -> dict:
        # Получает текущее время в формате ЧЧ:ММ
        current_time = datetime.datetime.now().strftime("%H:%M")
        # Формирует ответ с текущим временем
        response = f"Текущее время: {current_time}"
        import random
        try:
            current_time_files = [
                os.path.join(AUDIO_RESPONSES_DIR, "current_time.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3")
            ]
            play_audio(random.choice(current_time_files), assistant.voice_volume)
        except Exception as e:
            print(f"Ошибка воспроизведения аудио TimeCommand: {e}")
        # Возвращает словарь с ответом и без необходимости подтверждения
        return {'response': response, 'confirmation': None, 'popup': {'text': response, 'image': None}}
