from . import control_kojima_bulb as bulb_control
import threading
import time
import os
from .command import Command
import re

# Импорт pygame для воспроизведения аудио
import pygame
import os
import random

# Инициализация микшера pygame
pygame.mixer.init()

# Путь к папке с аудиофайлами
AUDIO_RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_responses")

import random

def play_audio(file_path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"Ошибка воспроизведения аудио {file_path}: {e}")

class LightControl:
    def __init__(self, access_token, device_id):
        self.access_token = access_token
        self.device_id = device_id
        self._breathing_active = False
        self.previous_state = None
        self.color_map = {
            "красный": {"h": 0, "s": 100, "v": 100},
            "синий": {"h": 240, "s": 100, "v": 100},
            "жёлтый": {"h": 50, "s": 100, "v": 100},
            "зелёный": {"h": 120, "s": 100, "v": 100},
            "фиолетовый": {"h": 270, "s": 100, "v": 100},
            "оранжевый": {"h": 30, "s": 100, "v": 100},
            "белый": {"temperature_k": 6500},
            "бирюзовый": {"h": 180, "s": 100, "v": 100},
            "голубой": {"h": 210, "s": 100, "v": 100},
            "ярко зелёный": {"h": 145, "s": 100, "v": 100}
        }

    def is_breathing_active(self):
        return self._breathing_active

    def handle_command(self, text, assistant):
        text = text.lower()
        if "отмена" in text or "выключи режим" in text:
            if self.is_breathing_active():
                self.stop_breathing()
                print("Режим дыхания остановлен.")
                # Воспроизведение аудио для отмены
                try:
                    cancel_audio_files = [
                        os.path.join(AUDIO_RESPONSES_DIR, "cancel.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "отключаю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "завершаю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "выключаюmp3")
                    ]
                    play_audio(random.choice(cancel_audio_files), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио отмены: {e}")
                return None, 0
            elif assistant.music_mode.is_running:
                assistant.music_mode.stop_music_mode()
                print("Режим музыки остановлен.")
                try:
                    music_mode_stopped_files = [
                        os.path.join(AUDIO_RESPONSES_DIR, "music_mode_stopped.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "отключаю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "выключаю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "завершаю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3")
                    ]
                    play_audio(random.choice(music_mode_stopped_files), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио остановки музыки: {e}")
                return None, 0
            else:
                print("Нет активных режимов для отключения.")
                try:
                    no_active_modes_files = [
                        os.path.join(AUDIO_RESPONSES_DIR, "no_active_modes.mp3")
                    ]
                    play_audio(random.choice(no_active_modes_files), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио отсутствия активных режимов: {e}")
                return None, 0
        elif "включи свет" in text:
            print("Включение света...")
            self.stop_breathing()
            bulb_control.turn_on(self.access_token)
            try:
                light_on_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "light_on.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "включаю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "активирую.mp3")
                ]
                play_audio(random.choice(light_on_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио включения света: {e}")
            return None, 0
        elif "выключи свет" in text:
            print("Выключение света...")
            self.stop_breathing()
            bulb_control.turn_off(self.access_token)
            try:
                light_off_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "light_off.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "выключаю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "отключаю.mp3")
                ]
                play_audio(random.choice(light_off_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио выключения света: {e}")
            return None, 0
        elif "сделай свет теплее" in text:
            print("Установка теплого света (2700K)...")
            self.stop_breathing()
            bulb_control.set_temperature(self.access_token, 2700)
            try:
                light_warmer_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "light_warmer.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "меняю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3")
                ]
                play_audio(random.choice(light_warmer_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио теплого света: {e}")
            return None, 0
        elif "сделай свет холоднее" in text:
            print("Установка холодного света (6500K)...")
            self.stop_breathing()
            bulb_control.set_temperature(self.access_token, 6500)
            try:
                light_colder_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "light_colder.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "меняю.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3")
                ]
                play_audio(random.choice(light_colder_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио холодного света: {e}")
            return None, 0
        elif "яркость" in text and ("процентов" in text or "процента" in text):
            brightness = self._extract_brightness(text)
            if brightness is not None:
                print(f"Установка яркости: {brightness}%...")
                self.stop_breathing()
                bulb_control.set_brightness(self.access_token, brightness)
                try:
                    brightness_ready_files = [
                        os.path.join(AUDIO_RESPONSES_DIR, "brightness_ready.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "готово.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "сделано.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "меняю.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо (2).mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "хорошо.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "секунду.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "поняла вас.mp3"),
                        os.path.join(AUDIO_RESPONSES_DIR, "ага.mp3")
                    ]
                    play_audio(random.choice(brightness_ready_files), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио яркости: {e}")
                return None, 0
            else:
                print("Не удалось распознать уровень яркости.")
                try:
                    brightness_not_recognized_files = [
                        os.path.join(AUDIO_RESPONSES_DIR, "brightness_not_recognized.mp3")
                    ]
                    play_audio(random.choice(brightness_not_recognized_files), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио нераспознанной яркости: {e}")
                return None, 0
        elif any(phrase in text for phrase in ["режим дыхания", "режим дыханиe", "режим дыханья", "режим дыханье"]):
            print("Запуск режима дыхания...")
            self.breathing_effect()
            try:
                breathing_mode_started_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "breathing_mode_started.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "активирую.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "запускаю.mp3")
                ]
                play_audio(random.choice(breathing_mode_started_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио режима дыхания: {e}")
            return None, 0
        elif "цвет" in text:
            color_match = re.search(r"цвет\s+([\w\s]+)", text)
            if color_match:
                color_name = color_match.group(1).strip()
                if color_name in self.color_map:
                    color = self.color_map[color_name]
                    self.stop_breathing()
                    if "temperature_k" in color:
                        print(f"Установка цвета: {color_name} (Температура: {color['temperature_k']}K)...")
                        bulb_control.set_temperature(self.access_token, color["temperature_k"])
                    else:
                        print(f"Установка цвета: {color_name} (HSV: h={color['h']}, s={color['s']}, v={color['v']})...")
                        bulb_control.set_hsv_color(self.access_token, color)
                    try:
                        # Воспроизвести аудио с названием цвета, например "цвет синий"
                        audio_file = os.path.join(AUDIO_RESPONSES_DIR, f"color_{color_name.replace(' ', '_')}.mp3")
                        play_audio(audio_file, assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио цвета {color_name}: {e}")
                else:
                    print(f"Неизвестный цвет: {color_name}")
                    try:
                        unknown_color_files = [
                            os.path.join(AUDIO_RESPONSES_DIR, "color_not_recognized.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "color_unknown.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "что.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "что ещё раз.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "повторите.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "повторите команду.mp3"),
                            os.path.join(AUDIO_RESPONSES_DIR, "повторите ещё раз.mp3")
                        ]
                        play_audio(random.choice(unknown_color_files), assistant.voice_volume)
                    except Exception as e:
                        print(f"Ошибка воспроизведения аудио неизвестного цвета: {e}")
            else:
                print(f"Не удалось распознать цвет в команде: {text}")
                try:
                    play_audio(os.path.join(AUDIO_RESPONSES_DIR, "color_not_recognized.mp3"), assistant.voice_volume)
                except Exception as e:
                    print(f"Ошибка воспроизведения аудио нераспознанного цвета: {e}")
            return None, 0
        else:
            print(f"Команда не распознана: {text}")
            try:
                command_not_recognized_files = [
                    os.path.join(AUDIO_RESPONSES_DIR, "command_not_recognized.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "что.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "что ещё раз.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "повторите.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "повторите команду.mp3"),
                    os.path.join(AUDIO_RESPONSES_DIR, "повторите ещё раз.mp3")
                ]
                play_audio(random.choice(command_not_recognized_files), assistant.voice_volume)
            except Exception as e:
                print(f"Ошибка воспроизведения аудио нераспознанной команды: {e}")
            return None, 0

    def _extract_brightness(self, text):
        number_map = {
            "ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4,
            "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
            "десять": 10, "двадцать": 20, "тридцать": 30, "сорок": 40,
            "пятьдесят": 50, "шестьдесят": 60, "семьдесят": 70, "восемьдесят": 80,
            "девяносто": 90, "сто": 100
        }
        words = text.split()
        for i, word in enumerate(words):
            if word in number_map:
                if i + 1 < len(words) and words[i + 1] in number_map:
                    return min(number_map[words[i]] + number_map[words[i + 1]], 100)
                return number_map[word]
            elif word.isdigit():
                return int(word)
        return None

    def breathing_effect(self):
        if self._breathing_active:
            print("Режим дыхания уже запущен")
            return
        
        self.previous_state = bulb_control.get_device_state(self.access_token, self.device_id)
        if self.previous_state:
            for cap in self.previous_state:
                if cap["type"] == "devices.capabilities.on_off" and not cap["state"]["value"]:
                    print("Лампочка выключена, включаю перед запуском режима дыхания...")
                    bulb_control.turn_on(self.access_token)
                    break

        def run_breathing():
            brightness_min = 1
            brightness_max = 100
            step = 0.5
            brightness = brightness_min
            increasing = True
            sleep_time = 0.05

            print("Поток дыхания запущен")
            while self._breathing_active:
                bulb_control.set_brightness(self.access_token, int(brightness))
                if brightness == brightness_max or brightness == brightness_min:
                    for _ in range(30):
                        if not self._breathing_active:
                            break
                        time.sleep(0.1)
                else:
                    time.sleep(sleep_time)

                if increasing:
                    brightness += step
                    if brightness >= brightness_max:
                        brightness = brightness_max
                        increasing = False
                else:
                    brightness -= step
                    if brightness <= brightness_min:
                        brightness = brightness_min
                        increasing = True

            print("Поток дыхания завершен")

        self._breathing_active = True
        thread = threading.Thread(target=run_breathing, daemon=True)
        thread.start()
        self._breathing_thread = thread

    def stop_breathing(self):
        import os
        import pygame
        pygame.mixer.init()
        AUDIO_RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_responses")

        def play_audio(file_path):
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.play()
            except Exception as e:
                print(f"Ошибка воспроизведения аудио {file_path}: {e}")

        if not self._breathing_active:
            print("Режим дыхания не активен")
            return
        self._breathing_active = False
        if hasattr(self, "_breathing_thread") and self._breathing_thread.is_alive():
            print("Ожидание завершения потока дыхания...")
            self._breathing_thread.join(timeout=5)
            if self._breathing_thread.is_alive():
                print("Поток дыхания не завершился в течение 5 секунд")
            else:
                print("Поток дыхания остановлен")
        if self.previous_state:
            bulb_control.restore_device_state(self.access_token, self.device_id, self.previous_state)
            self.previous_state = None
        try:
            play_audio(os.path.join(AUDIO_RESPONSES_DIR, "cancel_mode.mp3"), self.voice_volume)
        except Exception as e:
            print(f"Ошибка воспроизведения аудио остановки режима дыхания: {e}")

class LightControlCommand(Command):
    def should_handle(self, text):
        keywords = ["свет", "яркость", "цвет", "режим", "лампочка"]
        return any(keyword in text for keyword in keywords)

    def execute(self, text, assistant):
        awaiting_confirmation, _ = assistant.light_control.handle_command(text, assistant)
        if awaiting_confirmation:
            return {'response': "Ожидание подтверждения", 'confirmation': awaiting_confirmation}
        return {'response': "Команда выполнена", 'confirmation': None}

class StopBreathingCommand(Command):
    def should_handle(self, text):
        text = text.lower()
        print(f"Checking if should handle: {text}")
        return (
            re.search(r'\bрежим\b', text, re.IGNORECASE) is not None 
            and re.search(r'\bдыхан[а-яё]*\b', text, re.IGNORECASE) is not None
        )

    def execute(self, text, assistant):
        print("Executing StopBreathingCommand")
        assistant.light_control.stop_breathing()
        return {'response': "Режим дыхания остановлен", 'confirmation': None}
