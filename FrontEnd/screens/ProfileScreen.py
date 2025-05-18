import sys
import json
import os
from shutil import copyfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QScrollArea,
    QLineEdit, QTextEdit, QFileDialog, QDialog
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QBitmap
from PyQt5.QtCore import Qt
from PIL import Image

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "C:/Users/Абдул-Азиз/Desktop/AiMediScan/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms"


class EditProfileDialog(QDialog):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile")
        self.setFixedSize(300, 400)
        self.user_data = user_data
        self.new_avatar_path = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.name_input = QLineEdit(self.user_data.get("user_name", ""))
        self.name_input.setPlaceholderText("Your Name")
        layout.addWidget(self.name_input)

        self.care_input = QLineEdit(self.user_data.get("care_name", ""))
        self.care_input.setPlaceholderText("Care Recipient")
        layout.addWidget(self.care_input)

        self.phone_input = QLineEdit(self.user_data.get("phone", ""))
        self.phone_input.setPlaceholderText("Phone")
        layout.addWidget(self.phone_input)

        self.description_input = QTextEdit(self.user_data.get("description", ""))
        self.description_input.setPlaceholderText("Description")
        layout.addWidget(self.description_input)

        self.avatar_btn = QPushButton("Upload New Photo")
        self.avatar_btn.clicked.connect(self.choose_avatar)
        layout.addWidget(self.avatar_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 8px; height: 32px;")
        layout.addWidget(save_btn)

    def choose_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Avatar", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.new_avatar_path = file_path

    def get_updated_data(self):
        return {
            "user_name": self.name_input.text().strip() or "Имя",
            "care_name": self.care_input.text().strip() or "Имя подопечного",
            "phone": self.phone_input.text().strip() or "+1 234 567 8900",
            "description": self.description_input.toPlainText().strip() or "Описание"
        }


class UserProfileScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Profile")
        self.setFixedSize(360, 500)
        self.setWindowIcon(QIcon("../assets/AMS logo.png"))
        self.setStyleSheet("background-color: #f9f9f9;")
        self.user_data = self.load_user_data()
        self.init_ui()
        self.update_profile_view()

    def load_user_data(self):
        try:
            with open("../../database/user_data.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignTop)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.avatar_label, alignment=Qt.AlignHCenter)

        self.name_label = QLabel()
        self.name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.name_label)

        self.care_label = QLabel()
        self.care_label.setFont(QFont("Arial", 11))
        self.care_label.setStyleSheet("color: #555;")
        self.care_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.care_label)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("color: #ddd;")
        self.layout.addWidget(line1)

        self.phone_label = QLabel()
        self.phone_label.setFont(QFont("Arial", 12))
        self.phone_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.phone_label)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color: #ddd;")
        self.layout.addWidget(line2)

        description_container = QFrame()
        description_container.setFixedHeight(120)
        desc_layout = QVBoxLayout(description_container)
        desc_layout.setContentsMargins(8, 8, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 4px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(130,130,130,0.6);
                min-height: 20px;
                border-radius: 3px;
            }
        """)

        self.desc_label = QLabel()
        self.desc_label.setFont(QFont("Arial", 11))
        self.desc_label.setStyleSheet("color: #333; padding-right: 12px;")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.desc_label.setMaximumWidth(280)

        desc_widget = QWidget()
        desc_layout_inner = QVBoxLayout(desc_widget)
        desc_layout_inner.setContentsMargins(10, 10, 10, 10)
        desc_layout_inner.addWidget(self.desc_label)

        scroll.setWidget(desc_widget)
        desc_layout.addWidget(scroll)
        self.layout.addWidget(description_container)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedHeight(40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        edit_btn.clicked.connect(self.open_edit_dialog)
        self.layout.addWidget(edit_btn)

    def create_circular_pixmap(self, path, size=100):
        pixmap = QPixmap(path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        mask = QBitmap(size, size)
        mask.fill(Qt.color0)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        pixmap.setMask(mask)
        return pixmap

    def update_profile_view(self):
        self.avatar_label.setPixmap(self.create_circular_pixmap("../assets/avatar.png", 100))
        self.name_label.setText(self.user_data.get("user_name", "Имя"))
        self.care_label.setText(f"Care Recipient: {self.user_data.get('care_name', 'Имя подопечного')}")
        self.phone_label.setText(self.user_data.get("phone", "+1 234 567 8900"))
        self.desc_label.setText(self.user_data.get("description", "Описание"))

    def open_edit_dialog(self):
        dialog = EditProfileDialog(self, self.user_data)
        if dialog.exec_():
            self.user_data.update(dialog.get_updated_data())
            try:
                with open("../../database/user_data.json", "w", encoding="utf-8") as f:
                    json.dump(self.user_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print("Error saving user data:", e)

            if dialog.new_avatar_path:
                try:
                    img = Image.open(dialog.new_avatar_path).convert("RGB")
                    img = img.resize((100, 100))
                    img.save("../assets/avatar.png", format="PNG")
                except Exception as e:
                    print("Error saving avatar:", e)

            self.update_profile_view()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UserProfileScreen()
    window.show()
    sys.exit(app.exec_())
