import os

os.environ[
    "QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"

from datetime import datetime
import json
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QScrollArea, QFrame, QLineEdit, QDialog, QTimeEdit, QMenu, QAction,
    QCheckBox, QDateEdit
)
from PyQt5.QtCore import Qt, QTime, QDate
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMessageBox


class TaskScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task List")
        self.setFixedSize(400, 660)
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))
        self.setStyleSheet("""
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }

            
            QWidget {
                background-color: #f9f9f9;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 10px 0 10px 0;
            }
            QScrollBar::handle:vertical {
                background: #d0d0d0;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.current_date = QDate.currentDate()
        self.tasks_by_date = self.load_tasks()
        self.recurring_exclusions = self.tasks_by_date.get("recurring_exclusions", {})
        self.recurring_status = self.tasks_by_date.get("recurring_status", {})
        self.tasks = self.get_tasks_for_date(self.current_date)

        self.init_ui()

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r", encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_tasks(self):
        self.tasks_by_date["recurring_exclusions"] = self.recurring_exclusions
        self.tasks_by_date["recurring_status"] = self.recurring_status
        with open("tasks.json", "w", encoding='utf-8') as f:
            json.dump(self.tasks_by_date, f, indent=4, ensure_ascii=False)

    def get_tasks_for_date(self, date):
        date_str = date.toString("yyyy-MM-dd")
        tasks = self.tasks_by_date.get(date_str, [])

        recurring = []
        excluded_titles = self.recurring_exclusions.get(date_str, [])

        for task_list in self.tasks_by_date.values():
            if isinstance(task_list, list):  # пропускаем "recurring_exclusions"
                for t in task_list:
                    if t.get("recurring") and t["title"] not in excluded_titles and t not in tasks:
                        task_copy = t.copy()
                        status = self.recurring_status.get(date_str, {}).get(task_copy["title"])
                        if status:
                            task_copy["done"] = status.get("done", False)
                            task_copy["done_at"] = status.get("done_at")
                        else:
                            task_copy["done"] = False
                        recurring.append(task_copy)

        return tasks + recurring

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("←")
        next_btn = QPushButton("→")
        self.date_btn = QPushButton(self.current_date.toString("MMMM dd, yyyy"))
        self.date_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #444;
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.date_btn.clicked.connect(self.show_date_picker)

        prev_btn.clicked.connect(self.prev_day)
        next_btn.clicked.connect(self.next_day)

        nav_layout.addWidget(prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.date_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        self.layout.addLayout(nav_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.task_container)
        self.layout.addWidget(self.scroll, stretch=1)

        bottom_buttons = QHBoxLayout()

        self.chat_btn = QPushButton("AI Chat")
        self.chat_btn.setFixedSize(90, 40)
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.chat_btn.clicked.connect(self.open_chat)

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(50, 50)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-size: 30px;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.add_btn.clicked.connect(self.add_task_dialog)

        bottom_buttons.addWidget(self.chat_btn, alignment=Qt.AlignLeft)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.add_btn, alignment=Qt.AlignRight)
        self.layout.addLayout(bottom_buttons)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.refresh_tasks()

    def refresh_tasks(self):
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.tasks.sort(key=lambda x: datetime.strptime(x["time"], "%H:%M"))
        for task in self.tasks:
            self.task_layout.addWidget(self.build_task_widget(task))

    def show_date_picker(self):
        picker = QDateEdit()
        picker.setCalendarPopup(True)
        picker.setDate(self.current_date)
        picker.calendarWidget().setGridVisible(True)
        picker.setWindowFlags(Qt.Popup)
        picker.setStyleSheet("QDateEdit { background-color: white; }")

        def on_date_chosen():
            self.current_date = picker.date()
            self.update_for_date()
            picker.deleteLater()

        picker.dateChanged.connect(on_date_chosen)
        picker.move(self.mapToGlobal(self.date_btn.pos()) + self.date_btn.rect().center())
        picker.show()
        picker.setFocus()

    def build_task_widget(self, task):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        container.setStyleSheet("background-color: white; border-radius: 12px;")

        check_btn = QPushButton()
        check_btn.setFixedSize(20, 20)
        check_btn.setStyleSheet(
            "QPushButton { border: 2px solid #3b82f6; border-radius: 10px; background-color: %s; }" %
            ("#3b82f6" if task.get("done") else "white")
        )
        if task.get("done"):
            check_btn.setText("✓")
            check_btn.setStyleSheet(check_btn.styleSheet() + "color: white; font-weight: bold;")
        check_btn.clicked.connect(lambda _, t=task: self.mark_done(t))
        layout.addWidget(check_btn)

        info_layout = QVBoxLayout()
        title = QLabel(task["title"])
        title.setFont(QFont("Arial", 12, QFont.Bold))
        time_label = QLabel(task["time"])
        time_label.setFont(QFont("Arial", 10))
        time_label.setStyleSheet("color: #555;")
        info_layout.addWidget(title)
        info_layout.addWidget(time_label)

        if task.get("done") and task.get("done_at"):
            done_at = QLabel(f"Done at {task['done_at']}")
            done_at.setFont(QFont("Arial", 9))
            done_at.setStyleSheet("color: gray;")
            info_layout.addWidget(done_at)

        layout.addLayout(info_layout)

        menu_btn = QPushButton("⋮")
        menu_btn.setStyleSheet("border: none; font-size: 18px;")
        menu_btn.setFixedWidth(30)

        def show_menu():
            menu = QMenu()
            edit_action = QAction("Edit")
            delete_action = QAction("Delete")
            edit_action.triggered.connect(lambda: self.edit_task(task))
            delete_action.triggered.connect(lambda: self.delete_task(task))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            menu.exec_(menu_btn.mapToGlobal(menu_btn.rect().bottomRight()))

        menu_btn.clicked.connect(show_menu)

        layout.addStretch()
        layout.addWidget(menu_btn)

        return container

    def mark_done(self, task):
        date_str = self.current_date.toString("yyyy-MM-dd")

        if task.get("recurring"):
            self.recurring_status.setdefault(date_str, {})
            if not task.get("done"):
                self.recurring_status[date_str][task["title"]] = {
                    "done": True,
                    "done_at": datetime.now().strftime("%H:%M")
                }
            else:
                self.recurring_status[date_str][task["title"]] = {
                    "done": False
                }
        else:
            if not task.get("done"):
                task["done"] = True
                task["done_at"] = datetime.now().strftime("%H:%M")
            else:
                task["done"] = False
                task.pop("done_at", None)

        self.save_tasks()
        self.update_for_date()

    def delete_task(self, task):
        if task.get("recurring"):
            msg = QMessageBox(self)
            msg.setWindowTitle("Удаление задачи")
            msg.setText("Эта задача является постоянной.\nУдалить её только на сегодня или из всех дней?")
            msg.addButton("Только сегодня", QMessageBox.AcceptRole)
            msg.addButton("Из всех дней", QMessageBox.DestructiveRole)
            msg.addButton("Отмена", QMessageBox.RejectRole)
            result = msg.exec_()

            if result == 0:  # Только сегодня
                date_str = self.current_date.toString("yyyy-MM-dd")
                self.recurring_exclusions.setdefault(date_str, []).append(task["title"])

            elif result == 1:  # Из всех дней
                for date_str in list(self.tasks_by_date):
                    self.tasks_by_date[date_str] = [
                        t for t in self.tasks_by_date[date_str]
                        if not (t["title"] == task["title"] and t.get("recurring"))
                    ]
            else:
                return  # Отмена
        else:
            date_str = self.current_date.toString("yyyy-MM-dd")
            self.tasks_by_date[date_str] = [
                t for t in self.tasks_by_date.get(date_str, []) if t != task
            ]

        self.save_tasks()
        self.update_for_date()

    def edit_task(self, task):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout(dialog)

        title_input = QLineEdit(task["title"])
        time_input = QTimeEdit()
        t = datetime.strptime(task["time"], "%H:%M")
        time_input.setTime(QTime(t.hour, t.minute))
        recurring_checkbox = QCheckBox("Постоянная")
        recurring_checkbox.setChecked(task.get("recurring", False))

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(
            lambda: self.save_edit(task, title_input.text(), time_input.time(), recurring_checkbox.isChecked(), dialog))

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("Time:"))
        layout.addWidget(time_input)
        layout.addWidget(recurring_checkbox)
        layout.addWidget(save_btn)
        dialog.exec_()

    def save_edit(self, task, new_title, new_time, recurring, dialog):
        task["title"] = new_title
        task["time"] = new_time.toString("HH:mm")
        task["recurring"] = recurring
        self.save_tasks()
        dialog.accept()
        self.update_for_date()

    def add_task_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Task")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout(dialog)

        title_input = QLineEdit()
        time_input = QTimeEdit()
        time_input.setTime(QTime.currentTime())
        date_input = QDateEdit()
        date_input.setDate(self.current_date)
        recurring_checkbox = QCheckBox("Постоянная")

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(lambda: self.add_task(title_input.text(), time_input.time(), date_input.date(),
                                                      recurring_checkbox.isChecked(), dialog))

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("Time:"))
        layout.addWidget(time_input)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(date_input)
        layout.addWidget(recurring_checkbox)
        layout.addWidget(add_btn)
        dialog.exec_()

    def add_task(self, title, time_obj, date_obj, recurring, dialog):
        if title:
            date_str = date_obj.toString("yyyy-MM-dd")
            task = {
                "title": title,
                "time": time_obj.toString("HH:mm"),
                "done": False,
                "recurring": recurring,
                "source": "human"  # 👈 добавлено
            }
            self.tasks_by_date.setdefault(date_str, []).append(task)
            self.save_tasks()
            dialog.accept()
            self.update_for_date()

    def open_chat(self):
        from ChatScreen import ChatScreen
        self.chat_window = ChatScreen()
        self.chat_window.show()
        self.hide()

    def prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self.update_for_date()

    def next_day(self):
        self.current_date = self.current_date.addDays(1)
        self.update_for_date()

    def update_for_date(self):
        self.date_btn.setText(self.current_date.toString("MMMM dd, yyyy"))
        self.tasks = self.get_tasks_for_date(self.current_date)
        self.refresh_tasks()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskScreen()
    window.show()
    sys.exit(app.exec_())
