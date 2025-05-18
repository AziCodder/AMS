import sys
import json
import os
from PyQt5.QtWidgets import QApplication

# Установка пути к плагинам (для правильной работы интерфейса)
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"

# Импортируем нужные экраны
from LoginScreen import LoginWindow
from ChatScreen import ChatScreen

def main():
    app = QApplication(sys.argv)

    # Попытка открыть user_data.json
    user_data_path = "../../database/user_data.json"
    start_window = None

    try:
        with open(user_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Если remember_me = True и данные пользователя валидны — открываем ChatScreen
        if data.get("remember_me") is True and data.get("phone") and data.get("password"):
            start_window = ChatScreen()
        else:
            start_window = LoginWindow()
    except Exception as e:
        print("Ошибка загрузки user_data.json:", e)
        start_window = LoginWindow()

    start_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
