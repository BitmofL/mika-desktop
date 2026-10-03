from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import time
import numpy as np
import commands.control_kojima_bulb as bulb_control
import commands.computer_control
import commands.music_mode
import commands.light_control
import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from command_handler import CommandHandler

class AudioProcessor(QThread):
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._running = True

    def run(self):
        self.assistant._process_audio()

    def stop(self):
        self._running = False
        self.quit()
        self.wait()

class VoiceAssistant(QObject):
    stopped = pyqtSignal()
    state_changed = pyqtSignal(bool)
    command_result = pyqtSignal(dict)  # New signal to emit command results including popup
    CONFIG_FILE = "settings.json"

    def __init__(self, model_path="vosk-model-small-ru-0.22"):
        super().__init__()
        if model_path == "vosk-model-small-ru-0.22":
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), model_path))
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
        except Exception as e:
            print(f"Ошибка при загрузке модели Vosk: {e}")
            exit(1)
        
        self.activation_phrases = ["мика", "мико", "мику", "мике"]
        self.is_activated = False
        self.audio_queue = queue.Queue()
        self.last_activity_time = 0
        self.command_timeout = 5
        self.silence_threshold = 170  # Значение по умолчанию
        self.api_key = ""  # API ключ
        self.music_sensitivity_threshold = 0.0001  # Чувствительность музыкального режима по умолчанию
        self.voice_volume = 1.0  # Громкость голоса по умолчанию
        self.expecting_command = False

        self.p = pyaudio.PyAudio()
        self.selected_mic = 0
        self.selected_speaker = 0
        self.device_id = ""
        self.access_token = ""
        self._load_settings()  # Загружаем настройки из файла

        self.music_mode = commands.music_mode.MusicMode(self.access_token, self.device_id)
        self.music_mode.set_sensitivity_threshold(self.music_sensitivity_threshold)
        self.light_control = commands.light_control.LightControl(self.access_token, self.device_id)
        self.shutdown_handler = commands.computer_control.ShutdownHandler(self.light_control)
        self.command_handler = CommandHandler(self)
        self.stream = self._init_audio_stream()

        self.audio_thread = AudioProcessor(self)
        self.awaiting_confirmation = None
        self.confirmation_handler = None
        self.confirmation_start_time = 0
        self.confirmation_timeout = 10


    def _load_settings(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.selected_mic = data.get("mic_index", 0)
                    self.selected_speaker = data.get("speaker_index", 0)
                    self.device_id = data.get("device_id", "")
                    self.access_token = data.get("access_token", "")
                    self.client_id = data.get("client_id", "")
                    self.client_secret = data.get("client_secret", "")
                    self.silence_threshold = data.get("silence_threshold", 170)
                    self.api_key = data.get("api_key", "")
                    self.music_sensitivity_threshold = data.get("music_sensitivity_threshold", 0.0001)
                    self.voice_volume = data.get("voice_volume", 1.0)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {str(e)}")

    def update_settings(self, mic_index, speaker_index, device_id, access_token, silence_threshold, api_key, music_sensitivity_threshold, voice_volume=1.0):
        self.selected_mic = mic_index
        self.selected_speaker = speaker_index
        self.device_id = device_id
        self.access_token = access_token
        self.client_id = getattr(self, 'client_id', '')
        self.client_secret = getattr(self, 'client_secret', '')
        self.silence_threshold = silence_threshold
        self.api_key = api_key
        self.music_sensitivity_threshold = music_sensitivity_threshold
        self.voice_volume = voice_volume
        if hasattr(self, 'music_mode'):
            self.music_mode.set_sensitivity_threshold(music_sensitivity_threshold)
        self._save_settings()
        self._restart_stream()

    def _save_settings(self):
        data = {
            "mic_index": self.selected_mic,
            "speaker_index": self.selected_speaker,
            "device_id": self.device_id,
            "access_token": self.access_token,
            "client_id": getattr(self, 'client_id', ''),
            "client_secret": getattr(self, 'client_secret', ''),
            "silence_threshold": self.silence_threshold,
            "api_key": self.api_key,
            "music_sensitivity_threshold": self.music_sensitivity_threshold,
            "voice_volume": self.voice_volume
        }
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")

    def _init_audio_stream(self):
        return self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=2048,
            input_device_index=self.selected_mic,
            stream_callback=self._audio_callback,
            start=True
        )

    def _restart_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = self._init_audio_stream()

    def _find_device_index_by_name(self, device_name, input=True):
        device_count = self.p.get_device_count()
        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            if input and device_info.get('maxInputChannels', 0) > 0:
                if device_name.lower() in device_info.get('name', '').lower():
                    return i
            elif not input and device_info.get('maxOutputChannels', 0) > 0:
                if device_name.lower() in device_info.get('name', '').lower():
                    return i
        return 0

    def _audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put((in_data, time.time()))
        return (in_data, pyaudio.paContinue)

    def _check_silence(self, audio_data):
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(audio_np.astype(np.float32))))
        return rms < self.silence_threshold

    def request_confirmation(self, handler):
        self.awaiting_confirmation = True
        self.confirmation_handler = handler
        self.confirmation_start_time = time.time()

    def _process_audio(self):
        while self.audio_thread._running:
            try:
                data, timestamp = self.audio_queue.get(timeout=0.5)
                if not self._check_silence(data):
                    self.last_activity_time = time.time()
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    recognized_text = result.get('text', '').lower()
                    #print(f"Распознанный текст: {recognized_text}")
                    if recognized_text:
                        if not self.is_activated and not self.awaiting_confirmation:
                            if any(phrase in recognized_text for phrase in self.activation_phrases):
                                self.is_activated = True
                                self.state_changed.emit(True)
                               # print("\nАктивирован! Говорите команду...")
                        elif self.is_activated:
                            if not any(phrase in recognized_text for phrase in self.activation_phrases):
                                self._handle_command(recognized_text)
                        elif self.awaiting_confirmation:
                            new_state = self.confirmation_handler.handle_confirmation(recognized_text, self)
                            if new_state is None:
                                self.awaiting_confirmation = False
                                self.confirmation_handler = None
                            else:
                                self.awaiting_confirmation = True
                
                if self.is_activated and (time.time() - self.last_activity_time > self.command_timeout):
                   # print("\nТаймаут из-за тишины. Ожидание активационной фразы...")
                    self.is_activated = False
                    self.state_changed.emit(False)
                
                if self.awaiting_confirmation and (time.time() - self.confirmation_start_time > self.confirmation_timeout):
                   # print("\nТаймаут подтверждения. Ожидание активационной фразы...")
                    self.awaiting_confirmation = False
                    self.confirmation_handler = None
                    self.is_activated = False
                    self.state_changed.emit(False)
            except queue.Empty:
                continue

    def _handle_command(self, text):
        text_lower = text.lower()
       # print(f"Обработка команды: {text_lower}")
        result = self.command_handler.handle(text_lower, self)
        response = result['response']
        confirmation = result.get('confirmation')
        print(response)
        if confirmation:
            self.request_confirmation(confirmation)
        # Emit the command result including popup data if any
        self.command_result.emit(result)

    def start(self):
       # print("Ожидание активационной фразы...")
        import pygame
        import os
        import random

        AUDIO_RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "audio_responses")
        pygame.mixer.init()

        def play_audio(file_path, volume=1.0):
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(volume)
                sound.play()
            except Exception as e:
                print(f"Ошибка воспроизведения аудио {file_path}: {e}")

        greeting_files = [
            os.path.join(AUDIO_RESPONSES_DIR, "здравствуйте.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "привет.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "к вашим услугам.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "я здесь, чем помочь.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "я здесь.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "жду указаний.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "слушаю вас.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "слушаю внимательно.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "слушаю.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "я тут, чем помочь.mp3"),
            os.path.join(AUDIO_RESPONSES_DIR, "я тут.mp3")
        ]

        play_audio(random.choice(greeting_files), self.voice_volume)

        self.audio_thread._running = True
        self.audio_thread.start()

    def stop(self):
        self.audio_thread._running = False
        self.audio_thread.quit()
        self.audio_thread.wait()
        self._save_settings()
        self.is_activated = False
        self.state_changed.emit(False)
        self.stopped.emit()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
       # print("Работа ассистента остановлена")
