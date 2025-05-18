from PyQt5.QtWidgets import QApplication, QStackedWidget
from screens.ChatScreen_test import ChatScreen
from screens.TaskListScreen import TaskScreen
import sys

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(390, 660)

        self.chat_screen = ChatScreen(self)
        self.task_screen = TaskScreen(self)

        self.addWidget(self.chat_screen)
        self.addWidget(self.task_screen)

        self.setCurrentWidget(self.chat_screen)

    def go_to_chat(self):
        self.setCurrentWidget(self.chat_screen)

    def go_to_tasks(self):
        self.setCurrentWidget(self.task_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
