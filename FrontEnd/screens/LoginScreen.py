import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QCheckBox

import json
import os

os.environ[
    "QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AiMediScan - Login")
        self.setFixedSize(350, 420)
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))  # <== добавляем логотип в окно
        self.setStyleSheet("background-color: #f9f9f9;")

        self.setup_ui()
        self.check_remember_me()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Заголовок
        logo = QLabel("AiMediScan")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Arial", 24, QFont.Bold))
        logo.setStyleSheet("color: #1A1A1A;")
        layout.addWidget(logo)

        # Поле ввода Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet(self.input_style())
        layout.addWidget(self.email_input)

        # Поле ввода Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(self.input_style())
        layout.addWidget(self.password_input)

        # Запомнить меня
        self.remember_checkbox = QCheckBox("Запомнить меня")
        self.remember_checkbox.setChecked(False)
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #444;
            }
        """)
        layout.addWidget(self.remember_checkbox)

        # Кнопка Log in
        login_btn = QPushButton("Log in")
        login_btn.setFixedHeight(40)
        login_btn.setStyleSheet("""
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
        login_btn.clicked.connect(self.login_action)
        layout.addWidget(login_btn)

        # Forgot password (теперь как кнопка)
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3b82f6;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        forgot_btn.clicked.connect(self.forgot_password_action)
        layout.addWidget(forgot_btn, alignment=Qt.AlignCenter)

        # Кнопка Sign up
        signup_btn = QPushButton("Sign up")
        signup_btn.setFixedHeight(40)
        signup_btn.setStyleSheet("""
            QPushButton {
                color: #3b82f6;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #3b82f6;
                border-radius: 12px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e0ecff;
            }
        """)
        signup_btn.clicked.connect(self.switch_to_signup)

        layout.addWidget(signup_btn)

        self.setLayout(layout)

    def input_style(self):
        return """
            QLineEdit {
                border: none;
                border-radius: 12px;
                padding: 10px;
                background-color: #f0f0f0;
                font-size: 14px;
            }
        """

    def login_action(self):
        raw_login = self.email_input.text().strip()
        login_value = self.normalize_phone(raw_login)

        if login_value is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный номер телефона.")
            return
        password_value = self.password_input.text().strip()

        # Проверка наличия данных
        if not login_value or not password_value:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            with open("../../database/user_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные пользователя:\n{e}")
            return

        if data.get("phone") == login_value and data.get("password") == password_value:
            print("✅ Успешный вход")
            # Сохраняем remember_me в json
            data["remember_me"] = self.remember_checkbox.isChecked()
            try:
                with open("../../database/user_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print("⚠️ Ошибка при обновлении флага remember_me:", e)
            self.open_setup_screen()
        else:
            QMessageBox.critical(self, "Неверные данные", "Неправильный номер телефона или пароль.")

    def open_setup_screen(self):
        from SetupScreen import SetupScreen  # <== подключаем SetupScreen
        self.setup_window = SetupScreen()
        self.setup_window.show()
        self.close()

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
            return None  # ❗ невалидный номер

    def check_remember_me(self):
        try:
            with open("../../database/user_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("remember_me") is True:
                from ChatScreen import ChatScreen
                self.chat_window = ChatScreen()
                self.chat_window.show()
                self.close()  # ❗ Закрываем LoginWindow
        except:
            pass

    def open_chat_screen(self):
        from ChatScreen import ChatScreen  # ✅ импорт нужного окна
        self.chat_window = ChatScreen()
        self.chat_window.show()
        self.close()  # ❗ закрываем LoginWindow


    def forgot_password_action(self):
        print("📧 Направить запрос на восстановление пароля")

    def switch_to_signup(self):
        from RegScreen import SignUpScreen  # lazy import внутри метода
        self.signup_window = SignUpScreen()
        self.signup_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
