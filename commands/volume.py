from commands.command import Command
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import re
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

import random

class VolumeCommand(Command):
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        
    def should_handle(self, text: str) -> bool:
        text = self._normalize(text)
        sound_keywords = ["звук", "громкость", "тише", "громче", "уровень", "процент", "половина", "полная", "максимум", "средняя", "минимальная", "0%", "минимум"]
        if any(keyword in text for keyword in sound_keywords):
            return True
        if ("включи" in text or "выключи" in text) and "звук" in text:
            return True
        return False

    def execute(self, text: str, assistant: object) -> dict:
        text = self._normalize(text)
        current_volume = self.volume.GetMasterVolumeLevelScalar()
        
        # Извлечение числового значения для установки любого процента
        percent = self._extract_percent(text)
        
        # Установка произвольного процента звука (например, "сделай громкость 25" или "громкость тридцать")
        if percent is not None:
            volume_level = percent / 100.0
            self.volume.SetMasterVolumeLevelScalar(volume_level, None)
            try:
                play_audio(os.path.join(AUDIO_RESPONSES_DIR, f"volume_{percent}.mp3"), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': f"Громкость {percent}%", 'confirmation': None}
        
        # Обработка различных формулировок
        if self._match(text, ["выключи звук", "отключи звук", "без звука"]):
            self.volume.SetMute(1, None)
            return {'response': "Звук выключен", 'confirmation': None}
            
        elif self._match(text, ["включи звук", "верни звук"]):
            self.volume.SetMute(0, None)
            try:
                sound_on_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "sound_on.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "включаю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3")
                ]
                play_audio(random.choice(sound_on_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': "Звук включен", 'confirmation': None}
            
        elif self._match(text, ["полная", "максимум", "на всю", "максимальная"]):
            self.volume.SetMasterVolumeLevelScalar(1.0, None)
            try:
                volume_100_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "volume_100.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3")
                ]
                play_audio(random.choice(volume_100_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': "Громкость 100%", 'confirmation': None}
            
        elif self._match(text, ["половина", "среднюю", "средняя", "50%", "половину"]):
            self.volume.SetMasterVolumeLevelScalar(0.5, None)
            try:
                volume_50_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "volume_50.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3")
                ]
                play_audio(random.choice(volume_50_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': "Громкость 50%", 'confirmation': None}
        
        elif self._match(text, ["минимальная", "0%", "минимум"]):
            self.volume.SetMasterVolumeLevelScalar(0.0, None)
            return {'response': "Громкость 0%", 'confirmation': None}

        elif self._match(text, ["громче", "прибавь", "+"]):
            new_vol = min(1.0, current_volume + 0.05)
            self.volume.SetMasterVolumeLevelScalar(new_vol, None)
            try:
                volume_up_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, f"volume_{math.ceil(new_vol*100)}.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3")
                ]
                play_audio(random.choice(volume_up_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': f"Громкость {math.ceil(new_vol*100)}%", 'confirmation': None}
            
        elif self._match(text, ["тише", "убавь", "-"]):
            new_vol = max(0.0, current_volume - 0.05)
            self.volume.SetMasterVolumeLevelScalar(new_vol, None)
            try:
                volume_down_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, f"volume_{math.ceil(new_vol*100)}.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3")
                ]
                play_audio(random.choice(volume_down_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио VolumeCommand: {e}")
            return {'response': f"Громкость {math.ceil(new_vol*100)}%", 'confirmation': None}
            
        return {'response': "Не поняла команду управления звуком", 'confirmation': None}

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
        return text

    def _match(self, text: str, keywords: list) -> bool:
        return any(keyword in text for keyword in keywords)

    def _extract_percent(self, text: str):
        # Словарь для преобразования словесных чисел в цифровые
        word_to_number = {
            'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4,
            'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
            'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14,
            'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19,
            'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
            'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
            'сто': 100
        }

        # Поиск чисел в текстовом формате
        words = text.split()
        current_num = 0
        for word in words:
            if word in word_to_number:
                current_num += word_to_number[word]
                if current_num > 100:  # Ограничиваем до 100
                    current_num = 100
            elif word in ["процентов", "проц", "%", "proc"]:
                if 0 <= current_num <= 100:
                    return current_num
                break

        # Поиск чисел в цифровом формате
        match = re.search(r'(?:\b|\s)(\d{1,2}|\d{1,2}\d?)\s?(?:процентов|проц|%|proc)?\b', text)
        if match:
            value = int(match.group(1))
            return max(0, min(100, value))

        return None