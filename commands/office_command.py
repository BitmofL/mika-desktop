import os
import random
from commands.command import Command
import pygame

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

class OfficeApplicationCommand(Command):
    def should_handle(self, text: str) -> bool:
        text = self._normalize_text(text)
        folder_keywords = ["загрузки", "документы", "фото", "проводник"]
        if any(keyword in text for keyword in folder_keywords):
            return False
        return any(keyword in text for keyword in [
            "ворд", "открой", "эксель" , "включи", "пауэрпоинт"
        ])

    APPLICATIONS = {
        "word": {
            "keywords": ["ворд", "word", "microsoft word"],
            "executable": "WINWORD.EXE",
            "audio": "open_word.mp3"
        },
        "excel": {
            "keywords": ["эксель", "excel", "microsoft excel"],
            "executable": "EXCEL.EXE",
            "audio": "open_excel.mp3"
        },
        "powerpoint": {
            "keywords": ["презентации", "powerpoint", "microsoft powerpoint"],
            "executable": "POWERPNT.EXE",
            "audio": "open_powerpoint.mp3"
        }
    }

    def should_handle(self, text: str) -> bool:
        text = text.lower().strip()
        for app in self.APPLICATIONS.values():
            if any(keyword in text for keyword in app["keywords"]):
                return True
        return False

    def execute(self, text: str, assistant: object) -> dict:
        text = text.lower().strip()
        for app_name, app_info in self.APPLICATIONS.items():
            if any(keyword in text for keyword in app_info["keywords"]):
                executable = app_info["executable"]
                audio_file = app_info["audio"]
                try:
                    # Попытка найти исполняемый файл в типичных местах
                    possible_paths = [
                        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft Office", "root", "Office16", executable),
                        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft Office", "root", "Office16", executable),
                        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft Office", "Office16", executable),
                        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft Office", "Office16", executable),
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            os.startfile(path)
                            try:
                                audio_variants = [
                                    os.path.join(AUDIO_RESPONSES_DIR, audio_file),
                                    os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3")
                                ]
                                play_audio(random.choice(audio_variants), assistant.voice_volume)
                            except Exception as e:
                                print(f"Ошибка воспроизведения аудио OfficeApplicationCommand: {e}")
                            return {'response': f"Открываю {app_name.capitalize()}", 'confirmation': None}
                    return {'response': f"Не удалось найти исполняемый файл для {app_name.capitalize()}", 'confirmation': None}
                except Exception as e:
                    return {'response': f"Ошибка при открытии {app_name.capitalize()}: {str(e)}", 'confirmation': None}
        return {'response': "Не понял команду для открытия приложения", 'confirmation': None}
