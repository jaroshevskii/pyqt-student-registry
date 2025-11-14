import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDialog
)
import sqlite3

class NewStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати нового студента")
        self.setGeometry(350, 150, 350, 250)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.id_input = QLineEdit()
        self.pib_input = QLineEdit()
        self.address_input = QLineEdit()
        self.faculty_input = QLineEdit()
        self.email_input = QLineEdit()

        grid = QGridLayout()
        grid.addWidget(QLabel("ID студента:"), 0, 0)
        grid.addWidget(self.id_input, 0, 1)
        grid.addWidget(QLabel("ПІБ:"), 1, 0)
        grid.addWidget(self.pib_input, 1, 1)
        grid.addWidget(QLabel("Місце проживання:"), 2, 0)
        grid.addWidget(self.address_input, 2, 1)
        grid.addWidget(QLabel("Факультет:"), 3, 0)
        grid.addWidget(self.faculty_input, 3, 1)
        grid.addWidget(QLabel("Пошта:"), 4, 0)
        grid.addWidget(self.email_input, 4, 1)

        layout.addLayout(grid)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Додати")
        cancel_btn = QPushButton("Відмінити")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        cancel_btn.clicked.connect(self.reject)
        add_btn.clicked.connect(self.add_student)

    def add_student(self):
        id_ = self.id_input.text().strip()
        pib = self.pib_input.text().strip()
        address = self.address_input.text().strip()
        faculty = self.faculty_input.text().strip()
        email = self.email_input.text().strip()

        if not id_ or not pib:
            QMessageBox.warning(self, "Error", "Add Id and PIB")
            return

        try:
            conn = sqlite3.connect("banana.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    pib TEXT NOT NULL,
                    address TEXT,
                    faculty TEXT,
                    email TEXT
                )
            """)
            conn.commit()
            cursor.execute(
                "INSERT INTO students (id, pib, address, faculty, email) VALUES (?, ?, ?, ?, ?)",
                (id_, pib, address, faculty, email)
            )
            conn.commit()
            QMessageBox.information(self, "OK", "OK!!!")
            conn.close()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "ERROR", "This id is used")
            conn.close()

class StudentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Інформація про студента")
        self.setGeometry(400, 200, 360, 300)
        self.initUI()
        self.create_db()

    def initUI(self):
        main_layout = QVBoxLayout()
        id_layout = QHBoxLayout()
        id_label = QLabel("ID студента:")
        self.id_input = QLineEdit()
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        main_layout.addLayout(id_layout)

        form_layout = QGridLayout()
        pib_label = QLabel("ПІБ:")
        self.pib_input = QLineEdit()
        address_label = QLabel("Місце проживання:")
        self.address_input = QLineEdit()
        faculty_label = QLabel("Факультет:")
        self.faculty_input = QLineEdit()
        email_label = QLabel("Пошта:")
        self.email_input = QLineEdit()

        form_layout.addWidget(pib_label, 0, 0)
        form_layout.addWidget(self.pib_input, 0, 1)
        form_layout.addWidget(address_label, 1, 0)
        form_layout.addWidget(self.address_input, 1, 1)
        form_layout.addWidget(faculty_label, 2, 0)
        form_layout.addWidget(self.faculty_input, 2, 1)
        form_layout.addWidget(email_label, 3, 0)
        form_layout.addWidget(self.email_input, 3, 1)

        main_layout.addLayout(form_layout)
        button_layout = QHBoxLayout()
        new_btn = QPushButton("ДОДАТИ")
        delete_btn = QPushButton("Delete")
        edit_btn = QPushButton("Edit")
        button_layout.addWidget(new_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(edit_btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        new_btn.clicked.connect(self.open_new_student_dialog)

    def create_db(self):
        conn = sqlite3.connect("banana.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                pib TEXT NOT NULL,
                address TEXT,
                faculty TEXT,
                email TEXT
            )
        """)
        conn.commit()
        conn.close()

    def open_new_student_dialog(self):
        dialog = NewStudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.id_input.setText(dialog.id_input.text())
            self.pib_input.setText(dialog.pib_input.text())
            self.address_input.setText(dialog.address_input.text())
            self.faculty_input.setText(dialog.faculty_input.text())
            self.email_input.setText(dialog.email_input.text())
            QMessageBox.information(self, "Успіх", "Новий студент доданий!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentForm()
    window.show()
    sys.exit(app.exec_())

