from commands.command import Command
import webbrowser
import re
import pygame
import os

# Инициализация микшера pygame
pygame.mixer.init()

AUDIO_RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_responses")

import random

def play_audio(file_path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"Ошибка воспроизведения аудио {file_path}: {e}")

class BrowserCommand(Command):
    def _normalize_text(self, text):
        return text.lower().strip()

    def should_handle(self, text: str) -> bool:
        text = self._normalize_text(text)
        folder_keywords = ["загрузки", "документы", "фото", "проводник"]
        office_keywords = ["ворд", "word", "microsoft word", "эксель", "excel", "microsoft excel", "презентации", "powerpoint", "microsoft powerpoint"]
        if any(keyword in text for keyword in folder_keywords + office_keywords):
            return False
        return any(keyword in text for keyword in [
            "браузер", "открой", "поиск", "ютуб", "почту", "вконтакте", "вк", "включи", "хочу посмотреть"
        ])

    def execute(self, text: str, assistant: object) -> dict:
        text = self._normalize_text(text)

        if "браузер" in text and any(keyword in text for keyword in ["открой", "включи", "хочу посмотреть"]):
            if not any(site in text for site in ["поиск", "ютуб", "почту", "вконтакте", "вк", "видео"]):
                try:
                    # Используем os.startfile для открытия браузера по умолчанию
                    os.startfile("http://")
                    try:
                        browser_opened_files = [
                            os.path.join(AUDIO_RESPONSES_DIR, "browser_opened.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3")
                        ]
                        play_audio(random.choice(browser_opened_files), assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио BrowserCommand: {e}")
                    return {'response': "Браузер открыт", 'confirmation': None}
                except Exception as e:
                    return {'response': f"Ошибка при открытии браузера: {str(e)}", 'confirmation': None}

        sites = {
            "ютуб": "https://www.youtube.com",
            "видео": "https://www.youtube.com",
            "почту": "https://mail.google.com",
            "вконтакте": "https://vk.com"
        }

        for site_name, url in sites.items():
            if site_name in text:
                try:
                    webbrowser.open(url)
                    try:
                        open_site_files = [
                            os.path.join(AUDIO_RESPONSES_DIR, f"open_{site_name}.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3")
                        ]
                        play_audio(random.choice(open_site_files), assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио BrowserCommand: {e}")
                    return {'response': f"Открываю {site_name}", 'confirmation': None}
                except webbrowser.Error as e:
                    return {'response': f"Ошибка при открытии {site_name}: {str(e)}", 'confirmation': None}

        if "поиск" in text:
            match = re.search(r"поиск\s+(.+)", text)
            if match:
                query = match.group(1).replace(" ", "+")
                search_url = f"https://yandex.ru/search/?text={query}"
                try:
                    webbrowser.open(search_url)
                    try:
                        searching_files = [
                            os.path.join(AUDIO_RESPONSES_DIR, "searching.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "открываю.mp3")
                        ]
                        play_audio(random.choice(searching_files), assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио BrowserCommand: {e}")
                    return {'response': f"Выполняю поиск: {match.group(1)}", 'confirmation': None}
                except webbrowser.Error as e:
                    return {'response': f"Ошибка при выполнении поиска: {str(e)}", 'confirmation': None}

        return {'response': "Не понял команду для браузера", 'confirmation': None}
