from PyQt6.QtGui import QTransform, QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QTimer, QEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QComboBox, QLineEdit, QSlider,
    QScrollArea, QDialog, QFormLayout, QDialogButtonBox, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QCursor, QIcon
import sys
import sounddevice as sd
from Mika_main import VoiceAssistant
import locale
import random
import json
import os
import math
locale.setlocale(locale.LC_ALL, 'Russian')
from PyQt6.QtCore import QLocale
QLocale.setDefault(QLocale("ru_RU"))
import sys
import os

def resource_path(relative_path):
    """Функция для получения абсолютного пути к ресурсу, работает как в режиме разработки, так и в PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class AnimatedOutlineButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hovered = False
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_angle)
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Type.Enter:
                self._hovered = True
                self._timer.start(30)  
                self.update()
            elif event.type() == QEvent.Type.Leave:
                self._hovered = False
                self._timer.stop()
                self._angle = 0
                self.update()
        return super().eventFilter(obj, event)

    def update_angle(self):
        self._angle = (self._angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._hovered:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            base_color = QColor("#9d96ba")
            pen_width = 3
            painter.setPen(Qt.PenStyle.NoPen)

            rect = self.rect().adjusted(3, 3, -3, -3)
            radius = 8  

           
            is_circular = abs(rect.width() - rect.height()) < 5 and abs(radius - rect.width() / 2) < 5

            if is_circular:
                
                center = rect.center()
                radius_circle = rect.width() / 2
                circumference = 2 * 3.141592653589793 * radius_circle

                def point_at_distance_circle(d):
                    angle = (d / circumference) * 2 * 3.141592653589793
                    x = center.x() + radius_circle * math.cos(angle)
                    y = center.y() + radius_circle * math.sin(angle)
                    return (x, y)

                trail_length = 60
                segments = 15
                for i in range(segments):
                    alpha = int(255 * (1 - i / segments))
                    color = QColor(base_color)
                    color.setAlpha(alpha)
                    pen = QPen(color)
                    pen.setWidth(pen_width)
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)

                    start_pos = point_at_distance_circle((self._angle - i * (trail_length / segments)) % circumference)
                    end_pos = point_at_distance_circle((self._angle - i * (trail_length / segments) + (trail_length / segments)) % circumference)
                    painter.drawLine(int(start_pos[0]), int(start_pos[1]), int(end_pos[0]), int(end_pos[1]))

                pen = QPen(base_color)
                pen.setWidth(pen_width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                start_pos = point_at_distance_circle(self._angle % circumference)
                end_pos = point_at_distance_circle((self._angle + (trail_length / segments)) % circumference)
                painter.drawLine(int(start_pos[0]), int(start_pos[1]), int(end_pos[0]), int(end_pos[1]))
            else:
                # Анимация вокруг периметра с закругленными углами
                perimeter = 2 * (rect.width() + rect.height())

                def point_at_distance(d):
                    if d < rect.width():
                        return rect.left() + d, rect.top()
                    d -= rect.width()
                    if d < rect.height():
                        return rect.right(), rect.top() + d
                    d -= rect.height()
                    if d < rect.width():
                        return rect.right() - d, rect.bottom()
                    d -= rect.width()
                    return rect.left(), rect.bottom() - d

                trail_length = 60
                segments = 15
                for i in range(segments):
                    alpha = int(255 * (1 - i / segments))
                    color = QColor(base_color)
                    color.setAlpha(alpha)
                    pen = QPen(color)
                    pen.setWidth(pen_width)
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)

                    start_pos = point_at_distance((self._angle - i * (trail_length / segments)) % perimeter)
                    end_pos = point_at_distance((self._angle - i * (trail_length / segments) + (trail_length / segments)) % perimeter)
                    painter.drawLine(int(start_pos[0]), int(start_pos[1]), int(end_pos[0]), int(end_pos[1]))

                pen = QPen(base_color)
                pen.setWidth(pen_width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                start_pos = point_at_distance(self._angle % perimeter)
                end_pos = point_at_distance((self._angle + (trail_length / segments)) % perimeter)
                painter.drawLine(int(start_pos[0]), int(start_pos[1]), int(end_pos[0]), int(end_pos[1]))

class PopupWindow(QDialog):
    def __init__(self, text, image_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Информация")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #1A1A1A; color: white;")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)

        self.label_text = QLabel(text)
        self.label_text.setWordWrap(True)
        self.label_text.setStyleSheet("font-size: 32px; font-family: Arial;")
        layout.addWidget(self.label_text)

        if image_path:
            pixmap = QPixmap(resource_path(image_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.label_image = QLabel()
                self.label_image.setPixmap(scaled_pixmap)
                self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(self.label_image)

        self.btn_close = AnimatedOutlineButton("Закрыть")
        self.btn_close.setFixedSize(100, 40)
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add timer to auto-close the popup after 10 seconds
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.close)
        self.auto_close_timer.start(10000)


class FaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 500)
        self.eye_state = "closed"

        self.face_closed = QPixmap(resource_path("images/Mika_close.png")).scaled(
            500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.face_open = QPixmap(resource_path("images/Mika_open.png")).scaled(
            500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink)

        self.blink_duration_timer = QTimer(self)
        self.blink_duration_timer.setSingleShot(True)
        self.blink_duration_timer.timeout.connect(self.end_blink)

    def start_animation(self):
        self.eye_state = "open"
        self.start_blink_timer()
        self.update()

    def stop_animation(self):
        self.eye_state = "closed"
        self.blink_timer.stop()
        self.update()

    def start_blink_timer(self):
        interval = random.randint(2000, 4000)
        self.blink_timer.setInterval(interval)
        self.blink_timer.start()

    def blink(self):
        self.eye_state = "blinking"
        self.update()
        self.blink_duration_timer.start(200)
        interval = random.randint(2000, 4000)
        self.blink_timer.setInterval(interval)

    def end_blink(self):
        if self.eye_state == "blinking":
            self.eye_state = "open"
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_pixmap = self.face_closed if self.eye_state in ["closed", "blinking"] else self.face_open
        painter.drawPixmap(0, 0, current_pixmap)

class DeviceTile(QWidget):
    def __init__(self, device_name, image_path, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(140, 160)
        self.setStyleSheet("""
            background-color: #2E2E2E;
            border-radius: 15px;
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        self.icon_label = QLabel()
        pixmap = QPixmap(resource_path(image_path)).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel(device_name)
        self.text_label.setStyleSheet("color: white; font-size: 12px;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)

        self.trash_button = QPushButton()
        trash_pixmap = QPixmap(resource_path("fotos/trash.PNG")).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.trash_button.setIcon(QIcon(trash_pixmap))
        self.trash_button.setIconSize(trash_pixmap.size())
        self.trash_button.setFixedSize(24, 24)
        self.trash_button.setStyleSheet("border: none; background: transparent;")
        self.trash_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.trash_button.clicked.connect(self.confirm_delete)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.trash_button)
        self.layout.addLayout(top_layout)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)

    def confirm_delete(self):
        reply = QMessageBox.question(self, "Удалить плитку", f"Вы уверены, что хотите удалить плитку '{self.text_label.text()}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_tile()

    def delete_tile(self):
        self.setParent(None)
        self.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Выбрано устройство: {self.text_label.text()}")

class AssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        font = QApplication.font()
        font.setFamily("Arial")
        QApplication.setFont(font)
        self.assistant = VoiceAssistant()
        self.assistant.stopped.connect(self.on_assistant_stopped)
        self.assistant.state_changed.connect(self.on_assistant_state_changed)
        self.assistant.command_result.connect(self.on_command_result)  # Connect signal for popup
        self.init_ui()
        self.start_assistant()

    def start_assistant(self):
        self.thread = QThread()
        self.assistant.moveToThread(self.thread)
        self.thread.started.connect(self.assistant.start)
        self.thread.start()
        self.btn_start_assistant.hide()
       
    def on_assistant_stopped(self):
        self.btn_start_assistant.show()

    def on_assistant_state_changed(self, is_active):
        if is_active:
            self.face_widget.start_animation()
        else:
            self.face_widget.stop_animation()

    def init_ui(self):
        self.setWindowTitle("Mika Assistant")
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("QMainWindow { background-color: #1A1A1A; color: white; }")

        self.stacked_widget = QStackedWidget()
        self.main_page = self.create_main_page()
        self.settings_page = QWidget()
        self.settings_stacked = QStackedWidget()
        self.settings_page_layout = QVBoxLayout(self.settings_page)
        self.settings_page_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_page_layout.addWidget(self.settings_stacked)

        self.settings_tab = self.create_settings_page()
        self.devices_tab = self.create_devices_page()
        self.bulb_settings_tab = self.create_bulb_settings_page()

        self.settings_stacked.addWidget(self.settings_tab)
        self.settings_stacked.addWidget(self.devices_tab)
        self.settings_stacked.addWidget(self.bulb_settings_tab)

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        self.setCentralWidget(self.stacked_widget)
        self.load_settings_to_ui()

    def on_command_result(self, result):
        popup = result.get('popup')
        if popup:
            text = popup.get('text', '')
            image_path = popup.get('image')
            # Показать всплывающее окно, даже если главное окно сведено к минимуму
            if self.isMinimized():
                self.showNormal()
            popup_window = PopupWindow(text, image_path, self)
            popup_window.show()
            popup_window.raise_()
            popup_window.activateWindow()
        
    def create_devices_page(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #1A1A1A;")
        main_layout = QVBoxLayout(widget)

        search_layout = QHBoxLayout()
        self.device_search_input = QLineEdit()
        self.device_search_input.setPlaceholderText("Поиск по имени устройства...")
        self.device_search_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; }")
        self.device_search_input.textChanged.connect(self.filter_devices)
        search_layout.addWidget(self.device_search_input)

        self.btn_add_tile = AnimatedOutlineButton("+")
        self.btn_add_tile.setFixedSize(30, 30)
        self.btn_add_tile.setStyleSheet("""
            QPushButton {
                background-color: #2E2E2E;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
            }
        """)
        self.btn_add_tile.clicked.connect(self.open_add_tile_dialog)
        search_layout.addWidget(self.btn_add_tile)

        main_layout.addLayout(search_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: #1A1A1A; border: none; }")
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.bulb_tile = DeviceTile("Лампочка KOJIMA e27", resource_path("fotos/kojima_lamb.PNG"), self)
        original_mousePressEvent = self.bulb_tile.mousePressEvent
        def new_mousePressEvent(event):
            self.open_bulb_settings(event)
            original_mousePressEvent(event)
        self.bulb_tile.mousePressEvent = new_mousePressEvent
        self.scroll_layout.addWidget(self.bulb_tile)

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        self.mobile_tile = DeviceTile("Мой телефон", resource_path("fotos/mobile.PNG"), self)
        self.scroll_layout.addWidget(self.mobile_tile)

        nav_button_style = """
            QPushButton { background-color: #1A1A1A; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #2E2E2E; }
        """
        btn_back = AnimatedOutlineButton("Назад")
        btn_back.setStyleSheet(nav_button_style)
        btn_back.clicked.connect(lambda: [self.stacked_widget.setCurrentIndex(0), self.save_settings()])
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget

    def open_add_tile_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новую плитку")
        dialog.setFixedSize(300, 150)
        dialog.setStyleSheet("background-color: black; color: white;")

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        layout.addRow("Название:", name_input)

        photo_input = QLineEdit()
        layout.addRow("Путь к фото:", photo_input)

        def browse_photo():
            file_path, _ = QFileDialog.getOpenFileName(dialog, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                photo_input.setText(file_path)

        browse_button = QPushButton("Обзор")
        browse_button.clicked.connect(browse_photo)
        layout.addRow("", browse_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self.add_new_tile(name_input.text(), photo_input.text(), dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec()

    def add_new_tile(self, name, photo_path, dialog):
        if not name or not photo_path:
            return
        new_tile = DeviceTile(name, photo_path, self)
        self.scroll_layout.addWidget(new_tile)
        dialog.accept()

    def open_bulb_settings(self, event):
        self.settings_stacked.setCurrentWidget(self.bulb_settings_tab)

    def filter_devices(self, text):
        text = text.lower()
        for tile in self.findChildren(DeviceTile):
            if text in tile.text_label.text().lower():
                tile.show()
            else:
                tile.hide()

    def create_bulb_settings_page(self):
        from commands.oauth_manager import get_authorization_url
        widget = QWidget()
        layout = QVBoxLayout(widget)

        nav_button_style = """
            QPushButton { background-color: #1A1A1A; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #2E2E2E; }
        """

        btn_back = QPushButton("Назад")
        btn_back.setStyleSheet(nav_button_style)
        btn_back.clicked.connect(lambda: [self.settings_stacked.setCurrentWidget(self.devices_tab), self.save_settings()])

        device_id_layout = QHBoxLayout()
        device_id_label = QLabel("Лампочка DEVICE_ID:")
        device_id_label.setStyleSheet("color: white; font-size: 14px;")
        self.bulb_device_id_input = QLineEdit(getattr(self.assistant, 'device_id', ''))
        self.bulb_device_id_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        device_id_layout.addWidget(device_id_label)

        info_button_device_id = QPushButton("i")
        info_button_device_id.setFixedSize(20, 20)
        info_button_device_id.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        def show_device_id_info():
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import Qt
            msg = QMessageBox()
            msg.setWindowTitle("Информация")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText('DEVICE_ID можно узнать в мобильном приложении вашей лампочки, в личном кабинете Яндекс IoT или в настройках вашего устройства в приложении Яндекс.')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            msg.exec()
        info_button_device_id.clicked.connect(show_device_id_info)
        device_id_layout.addWidget(info_button_device_id)

        device_id_layout.addWidget(self.bulb_device_id_input)

        client_id_layout = QHBoxLayout()
        client_id_label = QLabel("CLIENT_ID:")
        client_id_label.setStyleSheet("color: white; font-size: 14px;")
        self.client_id_input = QLineEdit(getattr(self.assistant, 'client_id', ''))
        self.client_id_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        client_id_layout.addWidget(client_id_label)

        info_button_client_id = QPushButton("i")
        info_button_client_id.setFixedSize(20, 20)
        info_button_client_id.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        def show_client_id_info():
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import Qt
            msg = QMessageBox()
            msg.setWindowTitle("Информация")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText('Чтобы получить CLIENT_ID, создайте приложение на <a href="https://oauth.yandex.ru/client/new/id">https://oauth.yandex.ru/client/new/id</a> и получите client_id.')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            msg.exec()
        info_button_client_id.clicked.connect(show_client_id_info)
        client_id_layout.addWidget(info_button_client_id)

        client_id_layout.addWidget(self.client_id_input)

        client_secret_layout = QHBoxLayout()
        client_secret_label = QLabel("CLIENT_SECRET:")
        client_secret_label.setStyleSheet("color: white; font-size: 14px;")
        self.client_secret_input = QLineEdit(getattr(self.assistant, 'client_secret', ''))
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        client_secret_layout.addWidget(client_secret_label)

        info_button_client_secret = QPushButton("i")
        info_button_client_secret.setFixedSize(20, 20)
        info_button_client_secret.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        def show_client_secret_info():
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import Qt
            msg = QMessageBox()
            msg.setWindowTitle("Информация")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText('Чтобы получить CLIENT_SECRET, создайте приложение на <a href="https://oauth.yandex.ru/client/new/id">https://oauth.yandex.ru/client/new/id</a> и получите client_secret.')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            msg.exec()
        info_button_client_secret.clicked.connect(show_client_secret_info)
        client_secret_layout.addWidget(info_button_client_secret)

        client_secret_layout.addWidget(self.client_secret_input)

        auth_code_layout = QVBoxLayout()
        auth_code_label = QLabel("Authorization Code:")
        auth_code_label.setStyleSheet("color: white; font-size: 14px;")
        self.auth_code_input = QLineEdit()
        self.auth_code_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        auth_code_layout.addWidget(auth_code_label)
        auth_code_layout.addWidget(self.auth_code_input)

        def open_auth_url():
            client_id = self.client_id_input.text()
            if not client_id:
                QMessageBox.warning(self, "Ошибка", "Введите CLIENT_ID перед авторизацией")
                return
            url = get_authorization_url(client_id)
            import webbrowser
            webbrowser.open(url)

        auth_button = QPushButton("Получить код авторизации")
        auth_button.setStyleSheet(nav_button_style)
        auth_button.clicked.connect(open_auth_url)

        layout.addLayout(device_id_layout)
        layout.addLayout(client_id_layout)
        layout.addLayout(client_secret_layout)
        layout.addLayout(auth_code_layout)
        layout.addWidget(auth_button)
        layout.addStretch()
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignBottom)

        return widget

    def create_main_page(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        nav_layout.setContentsMargins(0, 0, 10, 0)
        
        nav_button_style = """
            QPushButton { background-color: #1A1A1A; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #2E2E2E; }
        """
        
        self.btn_settings = AnimatedOutlineButton("Настройки")
        self.btn_settings.setStyleSheet(nav_button_style)
        self.btn_settings.clicked.connect(lambda: [self.stacked_widget.setCurrentIndex(1), self._switch_settings_tab("settings")])
        
        self.btn_devices = AnimatedOutlineButton("Устройства")
        self.btn_devices.setStyleSheet(nav_button_style)
        self.btn_devices.clicked.connect(lambda: [self.stacked_widget.setCurrentIndex(1), self._switch_settings_tab("devices")])
        
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addWidget(self.btn_devices)
        
        main_layout.addLayout(nav_layout)
        
        self.face_widget = FaceWidget()
        main_layout.addWidget(self.face_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_start_assistant = AnimatedOutlineButton("Включить Мику")
        self.btn_start_assistant.setStyleSheet(nav_button_style)
        self.btn_start_assistant.clicked.connect(self.restart_assistant)
        self.btn_start_assistant.hide()
        main_layout.addWidget(self.btn_start_assistant, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return widget

    def _switch_settings_tab(self, tab_name):
        if tab_name == "settings":
            self.settings_stacked.setCurrentIndex(0)
        elif tab_name == "devices":
            self.settings_stacked.setCurrentIndex(1)
        elif tab_name == "bulb_settings":
            self.settings_stacked.setCurrentIndex(2)

    def restart_assistant(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            try:
                self.thread.started.disconnect()
            except Exception:
                pass
            self.thread.quit()
            self.thread.wait()
        self.thread = QThread()
        self.assistant = VoiceAssistant()
        self.assistant.stopped.connect(self.on_assistant_stopped)
        self.assistant.state_changed.connect(self.on_assistant_state_changed)
        self.assistant.moveToThread(self.thread)
        self.thread.started.connect(self.assistant.start)
        self.thread.start()
        self.btn_start_assistant.hide()
        self.load_settings_to_ui()

    def _populate_devices(self, combobox, is_input=True):
        combobox.clear()
        saved_index = self.assistant.selected_mic if is_input else self.assistant.selected_speaker
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if (is_input and dev['max_input_channels'] > 0) or (not is_input and dev['max_output_channels'] > 0):
                    name = dev['name']
                    combobox.addItem(name, userData=i)
                    if i == saved_index:
                        combobox.setCurrentIndex(combobox.count()-1)
        except Exception as e:
            print(f"Ошибка при получении устройств: {str(e)}")

    def create_settings_page(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
        nav_button_style = """
            QPushButton { background-color: #1A1A1A; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #2E2E2E; }
        """
        
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(15)
        
        mic_layout = QVBoxLayout()
        mic_label = QLabel("Выберите микрофон:")
        mic_label.setStyleSheet("color: white; font-size: 14px;")
        self.mic_combobox = QComboBox()
        self.mic_combobox.setStyleSheet("QComboBox { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; }")
        self._populate_devices(self.mic_combobox, is_input=True)
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combobox)
        
        api_layout = QVBoxLayout()
        api_label = QLabel("API ключ нейросети:")
        api_label.setStyleSheet("color: white; font-size: 14px;")
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        
        speaker_layout = QVBoxLayout()
        speaker_label = QLabel("Выберите динамики:")
        speaker_label.setStyleSheet("color: white; font-size: 14px;")
        self.speaker_combobox = QComboBox()
        self.speaker_combobox.setStyleSheet("QComboBox { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; }")
        self._populate_devices(self.speaker_combobox, is_input=False)
        speaker_layout.addWidget(speaker_label)
        speaker_layout.addWidget(self.speaker_combobox)
        
        volume_layout = QVBoxLayout()
        volume_label = QLabel("Громкость голоса Мики:")
        volume_label.setStyleSheet("color: white; font-size: 14px;")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(getattr(self.assistant, 'voice_volume', 1.0) * 100))
        self.volume_slider.setStyleSheet("QSlider { background-color: #2E2E2E; }")
        self.volume_value_label = QLabel(f"{int(getattr(self.assistant, 'voice_volume', 1.0) * 100)}%")
        self.volume_value_label.setStyleSheet("color: white;")
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value_label)
        
        token_layout = QVBoxLayout()

        top_label_layout = QHBoxLayout()
        info_button_token = QPushButton("i")
        info_button_token.setFixedSize(20, 20)
        info_button_token.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        def show_token_info():
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import Qt
            msg = QMessageBox()
            msg.setWindowTitle("Информация")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText('Токен получен автоматически после заполнения данных лампочки Kojima.')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            msg.exec()
        info_button_token.clicked.connect(show_token_info)
        top_label_layout.addWidget(info_button_token)

        token_label = QLabel("Токен управления ACCESS_TOKEN:")
        token_label.setStyleSheet("color: white; font-size: 14px;")
        top_label_layout.addWidget(token_label)
        top_label_layout.addStretch()

        token_layout.addLayout(top_label_layout)

        self.token_input = QLineEdit(getattr(self.assistant, 'access_token', ''))
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setStyleSheet("QLineEdit { background-color: #2E2E2E; color: white; padding: 8px; border-radius: 4px; border: 1px solid #444; }")
        token_layout.addWidget(self.token_input)
        
        sensitivity_layout = QVBoxLayout()
        sensitivity_label = QLabel("Чувствительность микрофона:")
        sensitivity_label.setStyleSheet("color: white; font-size: 14px;")
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(10, 10000)
        self.sensitivity_slider.setValue(int(getattr(self.assistant, 'silence_threshold', 1000) * 10000))
        self.sensitivity_slider.setStyleSheet("QSlider { background-color: #2E2E2E; }")
        self.sensitivity_value_label = QLabel(f"{getattr(self.assistant, 'silence_threshold', 100):.2f}")
        self.sensitivity_value_label.setStyleSheet("color: white;")
        
        self.sensitivity_slider.valueChanged.connect(self._update_sensitivity_label)
        sensitivity_layout.addWidget(sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addWidget(self.sensitivity_value_label)
        
        music_sensitivity_layout = QVBoxLayout()
        music_sensitivity_label = QLabel("Чувствительность режима музыки:")
        music_sensitivity_label.setStyleSheet("color: white; font-size: 14px;")
        self.music_sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.music_sensitivity_slider.setRange(1, 1000)
        default_music_sensitivity = int(getattr(self.assistant, 'music_sensitivity_threshold', 0.0001) * 100000)
        self.music_sensitivity_slider.setValue(default_music_sensitivity)
        self.music_sensitivity_slider.setStyleSheet("QSlider { background-color: #2E2E2E; }")
        self.music_sensitivity_value_label = QLabel(f"{default_music_sensitivity / 100000:.5f}")
        self.music_sensitivity_value_label.setStyleSheet("color: white;")
        self.music_sensitivity_slider.valueChanged.connect(self._update_music_sensitivity_label)
        music_sensitivity_layout.addWidget(music_sensitivity_label)
        music_sensitivity_layout.addWidget(self.music_sensitivity_slider)
        music_sensitivity_layout.addWidget(self.music_sensitivity_value_label)
        
        settings_layout.addLayout(mic_layout)
        settings_layout.addLayout(speaker_layout)
        settings_layout.addLayout(volume_layout)
        settings_layout.addLayout(api_layout)
        settings_layout.addLayout(token_layout)
        settings_layout.addLayout(sensitivity_layout)
        settings_layout.addLayout(music_sensitivity_layout)
        settings_layout.addStretch()
        
        btn_back = AnimatedOutlineButton("Назад")
        btn_back.setStyleSheet("""
            QPushButton { background-color: #1A1A1A; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #2E2E2E; }
        """)
        btn_back.clicked.connect(lambda: [self.stacked_widget.setCurrentIndex(0), self.save_settings()])
        
        main_layout.addLayout(settings_layout)
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.load_settings_to_ui()
        return widget

    def _update_sensitivity_label(self, value):
        self.sensitivity_value_label.setText(f"{value / 100:.2f}")

    def _update_volume_label(self, value):
        self.volume_value_label.setText(f"{value}%")

    def _update_music_sensitivity_label(self, value):
        self.music_sensitivity_value_label.setText(f"{value / 100000:.5f}")

    def save_settings(self):
        mic_index = self.mic_combobox.currentData() if self.mic_combobox.currentData() is not None else 0
        speaker_index = self.speaker_combobox.currentData() if self.speaker_combobox.currentData() is not None else 0
        device_id = self.bulb_device_id_input.text()
        access_token = self.token_input.text()
        client_id = self.client_id_input.text() if hasattr(self, 'client_id_input') else ''
        client_secret = self.client_secret_input.text() if hasattr(self, 'client_secret_input') else ''
        silence_threshold = self.sensitivity_slider.value() / 100.0
        api_key = self.api_input.text()
        music_sensitivity_threshold = self.music_sensitivity_slider.value() / 100000.0
        voice_volume = self.volume_slider.value() / 100.0

        self.assistant.update_settings(
            mic_index=mic_index,
            speaker_index=speaker_index,
            device_id=device_id,
            access_token=access_token,
            silence_threshold=silence_threshold,
            api_key=api_key,
            music_sensitivity_threshold=music_sensitivity_threshold,
            voice_volume=voice_volume
        )
        if hasattr(self.assistant, 'client_id'):
            self.assistant.client_id = client_id
        if hasattr(self.assistant, 'client_secret'):
            self.assistant.client_secret = client_secret
        self.assistant._save_settings()
        

    def load_settings_to_ui(self):
        if os.path.exists(self.assistant.CONFIG_FILE):
            try:
                with open(self.assistant.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mic_index = data.get("mic_index", 0)
                    speaker_index = data.get("speaker_index", 0)
                    device_id = data.get("device_id", "")
                    access_token = data.get("access_token", "")
                    silence_threshold = data.get("silence_threshold", 0.2)
                    api_key = data.get("api_key", "")
                    music_sensitivity_threshold = data.get("music_sensitivity_threshold", 0.0001)
                    voice_volume = data.get("voice_volume", 1.0)

                    for i in range(self.mic_combobox.count()):
                        if self.mic_combobox.itemData(i) == mic_index:
                            self.mic_combobox.setCurrentIndex(i)
                            break
                    for i in range(self.speaker_combobox.count()):
                        if self.speaker_combobox.itemData(i) == speaker_index:
                            self.speaker_combobox.setCurrentIndex(i)
                            break
                    if hasattr(self, 'bulb_device_id_input'):
                        self.bulb_device_id_input.setText(device_id)
                    else:
                        print("")
                    self.token_input.setText(access_token)
                    self.sensitivity_slider.setValue(int(silence_threshold * 100))
                    self.sensitivity_value_label.setText(f"{silence_threshold:.2f}")
                    self.api_input.setText(api_key)
                    self.music_sensitivity_slider.setValue(int(music_sensitivity_threshold * 100000))
                    self.music_sensitivity_value_label.setText(f"{music_sensitivity_threshold:.5f}")
                    self.volume_slider.setValue(int(voice_volume * 100))
                    self.volume_value_label.setText(f"{int(voice_volume * 100)}%")
                   
            except Exception as e:
                print(f"Ошибка загрузки настроек в UI: {str(e)}")

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("images/MikaIcon.ico")))
    window = AssistantUI()
    window.show()
    sys.exit(app.exec())
