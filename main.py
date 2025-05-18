import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
)
import os
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"

from PyQt5.QtCore import Qt


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AiMediScan - Вход")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Введите номер телефона:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона")

        self.password_label = QLabel("Придумайте пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Продолжить")
        self.login_button.clicked.connect(self.goto_patient_info)

        layout.addWidget(self.label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def goto_patient_info(self):
        if self.phone_input.text() and self.password_input.text():
            self.patient_info_page = PatientInfoPage()
            self.patient_info_page.show()
            self.close()


class PatientInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация о подопечном")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.instruction_label = QLabel(
            "Введите всю информацию о подопечном, чтобы ИИ смог расписать "
            "для него ежедневные задачи, и в дальнейшем использовал эти данные "
            "для индивидуального ответа."
        )
        self.instruction_label.setWordWrap(True)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Опишите состояние подопечного...")

        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.save_info)

        layout.addWidget(self.instruction_label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def save_info(self):
        description = self.text_input.toPlainText()
        if description:
            print("Описание подопечного сохранено:", description)
            self.close()  # можно заменить на переход к следующей странице


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginPage()
    login.show()
    sys.exit(app.exec_())
