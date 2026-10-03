import random
import random
from .command import Command
import os
from pathlib import Path
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

class SystemFoldersCommand(Command):
    def should_handle(self, text: str) -> bool:
        text = text.lower().strip()
        return any(
            keyword in text 
            for keyword in ["загрузки", "документы", "фото", "проводник", "видео"]
        ) and any(
            action in text 
            for action in ["открой", "запусти", "включи", "покажи"]
        )

    def execute(self, text: str, assistant: object) -> dict:  
        folders = {
            "загрузки": Path.home() / "Downloads",
            "документы": Path.home() / "Documents",
            "фото": Path.home() / "Pictures",
            "видео": Path.home() / "Videos"
        }

        if "проводник" in text:
            self._open_explorer()
            try:
                import random
                explorer_opened_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "explorer_opened.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3")
                ]
                play_audio(random.choice(explorer_opened_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио SystemFoldersCommand: {e}")
            return {'response': "Проводник запущен", 'confirmation': None}

        for folder_name, path in folders.items():
            if folder_name in text:
                if path.exists():
                    os.startfile(path)
                    try:
                        import random
                        open_folder_files = [
                            #os.path.join(AUDIO_RESPONSES_DIR, f"open_{folder_name}.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3")
                        ]
                        play_audio(random.choice(open_folder_files), assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио SystemFoldersCommand: {e}")
                    return {'response': f"Открываю {folder_name}", 'confirmation': None}
                try:
                    play_audio(os.path.join(AUDIO_RESPONSES_DIR, "folder_not_found.mp3"), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио SystemFoldersCommand: {e}")
                return {'response': f"Папка {folder_name} не найдена", 'confirmation': None}
        
        return {'response': "", 'confirmation': None}

    def _open_explorer(self):
        if os.name == 'nt':
            os.system('explorer')
        else:
            os.system('nautilus')
