import os

os.environ[
    "QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QTextEdit, QPushButton, QScrollArea, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from BackEnd.API.ai_task import ask_health_recommendations, generate_personal_prompt
from TaskListScreen import TaskScreen


class AIWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, description):
        super().__init__()
        self.description = description

    def run(self):
        result = ask_health_recommendations(self.description)
        self.finished.emit(result or {"text": "⚠️ Не удалось получить ответ от ИИ."})


class PromptWorker(QThread):
    def __init__(self, description):
        super().__init__()
        self.description = description

    def run(self):
        generate_personal_prompt(self.description)


class SetupScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AiMediScan - Setup")
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))
        self.setFixedSize(360, 640)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 4px 0;
            }
            QScrollBar::handle:vertical {
                background: #c4c4c4;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            QTextEdit QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 4px 0;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #c4c4c4;
                min-height: 20px;
                border-radius: 3px;
            }
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)

        self.initial_text = QLabel("Опиши состояние человека, за которым нужен уход.")
        self.initial_text.setWordWrap(True)
        self.initial_text.setFont(QFont("Arial", 13))
        self.initial_text.setStyleSheet("""
            background-color: #DFE8F7;
            border-radius: 12px;
            padding: 12px;
            font-size: 14px;
            color: #1a1a1a;
        """)
        self.layout.addWidget(self.initial_text)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.chat_widget)
        self.layout.addWidget(self.scroll, stretch=1)

        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(100)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.layout.addWidget(self.text_input)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.setFixedHeight(40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.send_btn.clicked.connect(self.handle_send)
        self.layout.addWidget(self.send_btn)

    def add_message(self, text, is_user=True):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet(f"""
            background-color: {'#3b82f6' if is_user else '#e6f0ff'};
            color: {'white' if is_user else 'black'};
            padding: 10px;
            border-radius: 14px;
        """)
        label.setMaximumWidth(240)

        wrapper = QHBoxLayout()
        if is_user:
            wrapper.addStretch()
            wrapper.addWidget(label)
        else:
            wrapper.addWidget(label)
            wrapper.addStretch()

        container = QWidget()
        container.setLayout(wrapper)
        self.chat_layout.addWidget(container)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def handle_send(self):
        description = self.text_input.toPlainText().strip()
        if not description:
            return

        self.add_message(description, is_user=True)
        self.text_input.clear()
        self.send_btn.setEnabled(False)

        self.worker = AIWorker(description)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.start()

    def on_ai_response(self, result):
        self.add_message(result.get("text", "⚠️ Нет текста в ответе."), is_user=False)

        # ✅ только после ответа — запускаем генерацию персонального промта
        self.prompt_worker = PromptWorker(self.worker.description)
        self.prompt_worker.start()

        self.text_input.hide()
        self.send_btn.hide()

        self.next_btn = QPushButton("Далее")
        self.next_btn.setFixedHeight(40)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.next_btn.clicked.connect(self.handle_next)
        self.layout.addWidget(self.next_btn)

    def handle_next(self):
        self.task_screen = TaskScreen()
        self.task_screen.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SetupScreen()
    window.show()
    sys.exit(app.exec_())