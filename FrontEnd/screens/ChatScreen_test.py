import os
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"
import sys
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QScrollArea, QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from BackEnd.API.chat_ai import ask_health_question


class ChatScreen(QWidget):
    ai_response_ready = pyqtSignal(str)  # ✅ сигнал для обновления UI из потока

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AiMediScan - Chat")
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))
        self.setFixedSize(390, 660)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 10px 0 10px 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #c4c4c4;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.init_ui()

        self.typing_animation_timer = QTimer()
        self.typing_animation_timer.timeout.connect(self.update_typing_animation)
        self.typing_dots = 0

        self.ai_response_ready.connect(self.display_ai_response)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 🔷 Верхняя панель
        header_wrapper = QWidget()
        header_wrapper.setStyleSheet("background-color: #4C8CD9;")
        header_layout = QVBoxLayout(header_wrapper)
        header_layout.setContentsMargins(10, 8, 10, 8)

        top_row = QHBoxLayout()

        task_button = QPushButton("Task")
        task_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        task_button.clicked.connect(self.open_task_screen)

        title = QLabel("AiMediScan")
        title.setFont(QFont("Arial", 15, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)

        top_row.addWidget(task_button, alignment=Qt.AlignLeft)
        top_row.addStretch()
        top_row.addWidget(title, alignment=Qt.AlignCenter)
        top_row.addStretch()
        top_row.addSpacing(50)

        self.typing_label = QLabel("Печатает...")
        self.typing_label.setFont(QFont("Arial", 11, QFont.StyleItalic))
        self.typing_label.setStyleSheet("color: white;")
        self.typing_label.setAlignment(Qt.AlignCenter)
        self.typing_label.setVisible(False)

        header_layout.addLayout(top_row)
        header_layout.addWidget(self.typing_label)
        layout.addWidget(header_wrapper)

        # 🔽 Чат
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.chat_widget)
        layout.addWidget(self.scroll, stretch=1)

        # 🔽 Поле ввода
        input_background = QWidget()
        input_background.setStyleSheet("background-color: #DFE8F8;")
        bottom = QHBoxLayout(input_background)
        bottom.setContentsMargins(12, 10, 12, 15)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 20px;
                padding: 10px 14px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.input_field.setFixedHeight(42)

        send_button = QPushButton("→")
        send_button.setFixedSize(42, 42)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 21px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        send_button.clicked.connect(self.handle_send)

        bottom.addWidget(self.input_field)
        bottom.addSpacing(8)
        bottom.addWidget(send_button)
        layout.addWidget(input_background)

    def handle_send(self):
        text = self.input_field.text().strip()
        if text:
            self.add_user_message(text)
            self.input_field.clear()

            self.typing_label.setVisible(True)
            self.typing_dots = 0
            self.typing_label.setText("Печатает")
            self.typing_animation_timer.start(500)

            thread = threading.Thread(target=self.get_ai_response, args=(text,))
            thread.start()

    def update_typing_animation(self):
        self.typing_dots = (self.typing_dots + 1) % 4
        self.typing_label.setText("Печатает" + "." * self.typing_dots)

    def get_ai_response(self, user_text):
        try:
            response = ask_health_question(user_text)
            response_type = response.get('response_type', '')
            ai_text = ""

            if response_type == 'diagnosis':
                diagnosis = response.get('diagnosis', '')
                ai_text = response.get('text', '')
                if diagnosis:
                    ai_text += f"\n\nПредположительный диагноз: {diagnosis}"
            elif response_type == 'advice':
                ai_text = response.get('text', '')
            else:
                ai_text = "Произошла ошибка. Попробуйте снова."
        except Exception as e:
            ai_text = f"Ошибка: {str(e)}"

        self.ai_response_ready.emit(ai_text)  # ✅ Обновление UI через сигнал

    def display_ai_response(self, text):
        self.typing_label.setVisible(False)
        self.typing_animation_timer.stop()
        self.add_ai_message(text)
        self.scroll_to_bottom()

    def add_user_message(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("""
            background-color: #3b82f6;
            color: white;
            padding: 10px;
            border-radius: 16px;
        """)
        label.setMaximumWidth(260)

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(label)

        container = QWidget()
        container.setLayout(wrapper)
        self.chat_layout.addWidget(container)

    def add_ai_message(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("""
            background-color: #e6f0ff;
            color: black;
            padding: 10px;
            border-radius: 16px;
        """)
        label.setMaximumWidth(260)

        wrapper = QHBoxLayout()
        wrapper.addWidget(label)
        wrapper.addStretch()

        container = QWidget()
        container.setLayout(wrapper)
        self.chat_layout.addWidget(container)

    def scroll_to_bottom(self):
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def open_task_screen(self):
        from TaskListScreen import TaskScreen
        self.task_window = TaskScreen()
        self.task_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatScreen()
    window.show()
    sys.exit(app.exec_())
