import os
from plyer import notification
from .command import Command
import sys
import random
import pygame


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает как в разработке, так и в PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def shutdown_computer():
    """Инициировать выключение компьютера через 5 секунд."""
    os.system("shutdown /s /t 5")

def show_shutdown_confirmation():
    """Показать уведомление Windows для подтверждения выключения."""
    notification.notify(
        title="Подтверждение выключения",
        message="Вы уверены, что хотите выключить компьютер? Скажите 'да' или 'нет'.",
        app_name="Mika Assistant",
        timeout=10
    )

class ShutdownHandler:
    def __init__(self, light_control):
        self.light_control = light_control

def initiate_shutdown(self, assistant):
    print("Вы уверены? Скажите 'да' или 'нет'...")
    self.light_control.stop_breathing()
    try:
        confirmation_audio_files = [
            os.path.join(AUDIO_RESPONSES_DIR, "подтвердите да или нет.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "are_you_sure.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "точно да или нет.mp3")
        ]
        play_audio(random.choice(confirmation_audio_files), assistant.voice_volume)
    except Exception as e:
        print(f"Ошибка воспроизведения аудио подтверждения выключения: {e}")
    show_shutdown_confirmation()

    def handle_confirmation(self, text, assistant):
        text_lower = text.lower()
        if any(word in text_lower for word in ["да", "ага", "конечно", "давай", "ок", "окей"]):
            print("Выключение компьютера...")
            shutdown_computer()
            assistant.stop()
            return None
        else:
            cancel_words = ["нет", "не", "отмена", "стоп", "не надо", "не нужно"]
            if any(word in text_lower.split() for word in cancel_words):
                print("Отмена выключения.")
                return None
            else:
                print("Скажите 'да' или 'нет'.")
                return "shutdown"



# Инициализация микшера pygame
pygame.mixer.init()

AUDIO_RESPONSES_DIR = resource_path("audio_responses")

def play_audio(file_path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"Ошибка воспроизведения аудио {file_path}: {e}")


class ShutdownCommand(Command):
    def should_handle(self, text):
        return "выключись" in text.lower()

    def execute(self, text, assistant):
        print("Выключаюсь...")
        assistant.light_control.stop_breathing()
        assistant.music_mode.stop_music_mode(play_cancel_sound=False)
        assistant.stop()
        try:
            shutdown_audio_files = [
                os.path.join(AUDIO_RESPONSES_DIR, "assistant_shutdown.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "выключаю.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "завершаю.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "до встречи.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "засыпаю.mp3"),
                os.path.join(AUDIO_RESPONSES_DIR, "пока пока.mp3")
            ]
            play_audio(random.choice(shutdown_audio_files), assistant.voice_volume)
        except Exception as e:
            print(f"Ошибка воспроизведения аудио ShutdownCommand: {e}")
        return {'response': "Ассистент выключен", 'confirmation': None}

class ComputerShutdownCommand(Command):
    def should_handle(self, text):
        return any(x in text.lower() for x in ["выключи компьютер", "выключи пк", "выключи комп"])

    def execute(self, text, assistant):
        assistant.shutdown_handler.initiate_shutdown()
        return {'response': "Подтвердите выключение", 'confirmation': assistant.shutdown_handler}
