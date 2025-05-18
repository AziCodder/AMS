import os

os.environ[
    "QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMessageBox


import json


class SignUpScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.setFixedSize(360, 500)
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))  # <== добавляем логотип в окно
        self.setStyleSheet("background-color: #f9f9f9;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 20)
        layout.setSpacing(20)

        title = QLabel("Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        self.name_input = self.create_input("Name")
        self.care_name_input = self.create_input("Care Recipient’s Name")
        self.phone_input = self.create_input("Phone Number")
        self.password_input = self.create_input("Password", is_password=True)

        layout.addWidget(self.name_input)
        layout.addWidget(self.care_name_input)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.password_input)

        signup_btn = QPushButton("Sign up")
        signup_btn.setFixedHeight(45)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-size: 16px;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        signup_btn.clicked.connect(self.handle_signup)
        layout.addWidget(signup_btn)

        # 🔽 Нижняя надпись и кнопка
        bottom_row = QHBoxLayout()
        note = QLabel("Уже есть аккаунт?")
        note.setFont(QFont("Arial", 10))
        login_btn = QPushButton("Войти")
        login_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #3b82f6; font-weight: bold; border: none; }")
        login_btn.clicked.connect(self.go_to_login)

        bottom_row.addStretch()
        bottom_row.addWidget(note)
        bottom_row.addSpacing(5)
        bottom_row.addWidget(login_btn)
        bottom_row.addStretch()

        # Всплывающее сообщение об успешной регистрации
        self.success_label = QLabel("✅ Вы успешно зарегистрировались!")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setStyleSheet("""
            QLabel {
                background-color: #d1fae5;
                color: #065f46;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
        """)
        self.success_label.setVisible(False)
        layout.insertWidget(0, self.success_label)  # сверху

        layout.addLayout(bottom_row)

    def create_input(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(40)
        input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: #f0f2f5;
                border-radius: 10px;
                padding-left: 12px;
                font-size: 14px;
            }
        """)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field

    def normalize_phone(self, phone_str):
        digits = ''.join(filter(str.isdigit, phone_str))

        if digits.startswith('8') and len(digits) == 11:
            return '+7' + digits[1:]
        elif digits.startswith('7') and len(digits) == 11:
            return '+7' + digits[1:]
        elif len(digits) == 10:
            return '+7' + digits
        elif digits.startswith('9') and len(digits) == 10:
            return '+7' + digits
        elif digits.startswith('') and len(digits) == 12:
            return '+' + digits
        elif digits.startswith('7') and len(digits) == 12:
            return '+' + digits
        else:
            return None  # ❌ номер некорректный

    def handle_signup(self):
        user_name = self.name_input.text().strip()
        care_name = self.care_name_input.text().strip()
        raw_phone = self.phone_input.text().strip()
        phone = self.normalize_phone(raw_phone)

        if phone is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный номер телефона.")
            return

        password = self.password_input.text().strip()

        if not user_name or not care_name or not phone or not password:
            print("⚠️ Все поля должны быть заполнены.")
            return

        data = {
            "user_name": user_name,
            "care_name": care_name,
            "phone": phone,
            "description": "",
            "password": password,
            "prompt": ""
        }

        try:
            with open("../../database/user_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("❌ Ошибка при сохранении:", e)
            return

        # Показать сообщение на 2.5 секунды
        self.success_label.setVisible(True)
        QTimer.singleShot(2500, self.go_to_login)

    def go_to_login(self):
        from LoginScreen import LoginWindow  # lazy import внутри метода
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignUpScreen()
    window.show()
    sys.exit(app.exec_())
