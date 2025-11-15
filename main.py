import sys
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any
from enum import Enum, auto
import sqlite3
from PyQt5.QtWidgets import (
  QApplication, QWidget, QLabel, QLineEdit, QPushButton,
  QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDialog
)


# ============================================================================
# State Management (Redux-like)
# ============================================================================

@dataclass
class Student:
  """Student model"""
  id: int
  pib: str
  address: str = ""
  faculty: str = ""
  email: str = ""


@dataclass
class AppState:
  """Application state"""
  current_student: Optional[Student] = None
  students: Dict[int, Student] = field(default_factory=dict)
  error: Optional[str] = None


class ActionType(Enum):
  """Action types for state mutations"""
  ADD_STUDENT = auto()
  UPDATE_STUDENT = auto()
  DELETE_STUDENT = auto()
  LOAD_STUDENT = auto()
  SET_ERROR = auto()
  CLEAR_ERROR = auto()


@dataclass
class Action:
  """Action to dispatch state changes"""
  type: ActionType
  payload: Any = None


class Store:
  """Redux-like store for centralized state management"""
  
  def __init__(self, initial_state: AppState):
    self._state = initial_state
    self._listeners: list[Callable[[AppState], None]] = []
  
  @property
  def state(self) -> AppState:
    """Get current state (read-only)"""
    return self._state
  
  def dispatch(self, action: Action) -> None:
    """Dispatch action to update state"""
    self._state = self._reducer(self._state, action)
    self._notify_listeners()
  
  def subscribe(self, listener: Callable[[AppState], None]) -> Callable[[], None]:
    """Subscribe to state changes"""
    self._listeners.append(listener)
    return lambda: self._listeners.remove(listener)
  
  def _reducer(self, state: AppState, action: Action) -> AppState:
    """Reduce state based on action"""
    if action.type == ActionType.ADD_STUDENT:
      student = action.payload
      new_students = state.students.copy()
      new_students[student.id] = student
      return AppState(
        current_student=student,
        students=new_students,
        error=None
      )
    
    elif action.type == ActionType.UPDATE_STUDENT:
      student = action.payload
      new_students = state.students.copy()
      new_students[student.id] = student
      return AppState(
        current_student=student,
        students=new_students,
        error=None
      )
    
    elif action.type == ActionType.DELETE_STUDENT:
      student_id = action.payload
      new_students = state.students.copy()
      new_students.pop(student_id, None)
      return AppState(
        current_student=None,
        students=new_students,
        error=None
      )
    
    elif action.type == ActionType.LOAD_STUDENT:
      student = action.payload
      return AppState(
        current_student=student,
        students=state.students,
        error=None
      )
    
    elif action.type == ActionType.SET_ERROR:
      return AppState(
        current_student=state.current_student,
        students=state.students,
        error=action.payload
      )
    
    elif action.type == ActionType.CLEAR_ERROR:
      return AppState(
        current_student=state.current_student,
        students=state.students,
        error=None
      )
    
    return state
  
  def _notify_listeners(self) -> None:
    """Notify all listeners of state change"""
    for listener in self._listeners:
      listener(self._state)


# ============================================================================
# Database Layer
# ============================================================================

class DatabaseService:
  """Database service for student operations"""
  
  def __init__(self, db_name: str = "banana.db"):
    self.db_name = db_name
    self._init_database()
  
  def _init_database(self) -> None:
    """Initialize database schema"""
    with sqlite3.connect(self.db_name) as conn:
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
  
  def create_student(self, student: Student) -> bool:
    """Create new student record"""
    try:
      with sqlite3.connect(self.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
          "INSERT INTO students (id, pib, address, faculty, email) VALUES (?, ?, ?, ?, ?)",
          (student.id, student.pib, student.address, student.faculty, student.email)
        )
        conn.commit()
      return True
    except sqlite3.IntegrityError:
      return False
  
  def get_student(self, student_id: int) -> Optional[Student]:
    """Get student by ID"""
    with sqlite3.connect(self.db_name) as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
      row = cursor.fetchone()
      if row:
        return Student(*row)
    return None
  
  def update_student(self, student: Student) -> bool:
    """Update existing student"""
    with sqlite3.connect(self.db_name) as conn:
      cursor = conn.cursor()
      cursor.execute(
        "UPDATE students SET pib = ?, address = ?, faculty = ?, email = ? WHERE id = ?",
        (student.pib, student.address, student.faculty, student.email, student.id)
      )
      conn.commit()
      return cursor.rowcount > 0
  
  def delete_student(self, student_id: int) -> bool:
    """Delete student by ID"""
    with sqlite3.connect(self.db_name) as conn:
      cursor = conn.cursor()
      cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
      conn.commit()
      return cursor.rowcount > 0


# ============================================================================
# UI Components
# ============================================================================

class NewStudentDialog(QDialog):
  """Dialog for adding new students"""
  
  def __init__(self, store: Store, db_service: DatabaseService, parent: Optional[QWidget] = None):
    super().__init__(parent)
    self.store = store
    self.db_service = db_service
    self.setWindowTitle("Додати нового студента")
    self.setGeometry(350, 150, 350, 250)
    self._init_ui()
  
  def _init_ui(self) -> None:
    """Initialize UI components"""
    layout = QVBoxLayout()
    
    # Input fields
    self.id_input = QLineEdit()
    self.pib_input = QLineEdit()
    self.address_input = QLineEdit()
    self.faculty_input = QLineEdit()
    self.email_input = QLineEdit()
    
    # Grid layout for form
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
    
    # Buttons
    btn_layout = QHBoxLayout()
    add_btn = QPushButton("Додати")
    cancel_btn = QPushButton("Відмінити")
    btn_layout.addWidget(add_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    
    self.setLayout(layout)
    
    # Connect signals
    cancel_btn.clicked.connect(self.reject)
    add_btn.clicked.connect(self._handle_add_student)
  
  def _handle_add_student(self) -> None:
    """Handle add student action"""
    # Validate input
    id_text = self.id_input.text().strip()
    pib = self.pib_input.text().strip()
    
    if not id_text or not pib:
      QMessageBox.warning(self, "Помилка", "ID та ПІБ є обов'язковими полями")
      return
    
    try:
      student_id = int(id_text)
    except ValueError:
      QMessageBox.warning(self, "Помилка", "ID повинен бути числом")
      return
    
    # Create student object
    student = Student(
      id=student_id,
      pib=pib,
      address=self.address_input.text().strip(),
      faculty=self.faculty_input.text().strip(),
      email=self.email_input.text().strip()
    )
    
    # Save to database
    if self.db_service.create_student(student):
      # Dispatch action to update state
      self.store.dispatch(Action(ActionType.ADD_STUDENT, student))
      QMessageBox.information(self, "Успіх", "Студент успішно доданий!")
      self.accept()
    else:
      QMessageBox.warning(self, "Помилка", "Студент з таким ID вже існує")


class StudentForm(QWidget):
  """Main form for student management"""
  
  def __init__(self, store: Store, db_service: DatabaseService):
    super().__init__()
    self.store = store
    self.db_service = db_service
    self.setWindowTitle("Інформація про студента")
    self.setGeometry(400, 200, 360, 300)
    self._init_ui()
    
    # Subscribe to state changes
    self.store.subscribe(self._on_state_change)
  
  def _init_ui(self) -> None:
    """Initialize UI components"""
    main_layout = QVBoxLayout()
    
    # ID input
    id_layout = QHBoxLayout()
    id_label = QLabel("ID студента:")
    self.id_input = QLineEdit()
    id_layout.addWidget(id_label)
    id_layout.addWidget(self.id_input)
    main_layout.addLayout(id_layout)
    
    # Form fields
    form_layout = QGridLayout()
    self.pib_input = QLineEdit()
    self.address_input = QLineEdit()
    self.faculty_input = QLineEdit()
    self.email_input = QLineEdit()
    
    form_layout.addWidget(QLabel("ПІБ:"), 0, 0)
    form_layout.addWidget(self.pib_input, 0, 1)
    form_layout.addWidget(QLabel("Місце проживання:"), 1, 0)
    form_layout.addWidget(self.address_input, 1, 1)
    form_layout.addWidget(QLabel("Факультет:"), 2, 0)
    form_layout.addWidget(self.faculty_input, 2, 1)
    form_layout.addWidget(QLabel("Пошта:"), 3, 0)
    form_layout.addWidget(self.email_input, 3, 1)
    
    main_layout.addLayout(form_layout)
    
    # Buttons
    button_layout = QHBoxLayout()
    self.new_btn = QPushButton("ДОДАТИ")
    self.search_btn = QPushButton("ПОШУК")
    self.delete_btn = QPushButton("ВИДАЛИТИ")
    self.edit_btn = QPushButton("РЕДАГУВАТИ")
    
    button_layout.addWidget(self.new_btn)
    button_layout.addWidget(self.search_btn)
    button_layout.addWidget(self.delete_btn)
    button_layout.addWidget(self.edit_btn)
    
    main_layout.addLayout(button_layout)
    self.setLayout(main_layout)
    
    # Connect signals
    self.new_btn.clicked.connect(self._handle_new_student)
    self.search_btn.clicked.connect(self._handle_search_student)
    self.delete_btn.clicked.connect(self._handle_delete_student)
    self.edit_btn.clicked.connect(self._handle_edit_student)
  
  def _handle_new_student(self) -> None:
    """Handle new student action"""
    dialog = NewStudentDialog(self.store, self.db_service, self)
    dialog.exec_()
  
  def _handle_search_student(self) -> None:
    """Handle search student action"""
    id_text = self.id_input.text().strip()
    
    if not id_text:
      QMessageBox.warning(self, "Помилка", "Введіть ID студента")
      return
    
    try:
      student_id = int(id_text)
    except ValueError:
      QMessageBox.warning(self, "Помилка", "ID повинен бути числом")
      return
    
    student = self.db_service.get_student(student_id)
    
    if student:
      self.store.dispatch(Action(ActionType.LOAD_STUDENT, student))
    else:
      QMessageBox.information(self, "Не знайдено", "Студент з таким ID не знайдений")
      self._clear_form()
  
  def _handle_delete_student(self) -> None:
    """Handle delete student action"""
    if not self.store.state.current_student:
      QMessageBox.warning(self, "Помилка", "Спочатку завантажте студента")
      return
    
    reply = QMessageBox.question(
      self, 
      "Підтвердження", 
      "Ви впевнені, що хочете видалити цього студента?",
      QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
      student_id = self.store.state.current_student.id
      if self.db_service.delete_student(student_id):
        self.store.dispatch(Action(ActionType.DELETE_STUDENT, student_id))
        QMessageBox.information(self, "Успіх", "Студент видалений")
        self._clear_form()
      else:
        QMessageBox.warning(self, "Помилка", "Не вдалося видалити студента")
  
  def _handle_edit_student(self) -> None:
    """Handle edit student action"""
    if not self.store.state.current_student:
      QMessageBox.warning(self, "Помилка", "Спочатку завантажте студента")
      return
    
    pib = self.pib_input.text().strip()
    if not pib:
      QMessageBox.warning(self, "Помилка", "ПІБ є обов'язковим полем")
      return
    
    updated_student = Student(
      id=self.store.state.current_student.id,
      pib=pib,
      address=self.address_input.text().strip(),
      faculty=self.faculty_input.text().strip(),
      email=self.email_input.text().strip()
    )
    
    if self.db_service.update_student(updated_student):
      self.store.dispatch(Action(ActionType.UPDATE_STUDENT, updated_student))
      QMessageBox.information(self, "Успіх", "Дані студента оновлені")
    else:
      QMessageBox.warning(self, "Помилка", "Не вдалося оновити дані студента")
  
  def _on_state_change(self, state: AppState) -> None:
    """Handle state changes"""
    if state.current_student:
      self._display_student(state.current_student)
  
  def _display_student(self, student: Student) -> None:
    """Display student data in form"""
    self.id_input.setText(str(student.id))
    self.pib_input.setText(student.pib)
    self.address_input.setText(student.address)
    self.faculty_input.setText(student.faculty)
    self.email_input.setText(student.email)
  
  def _clear_form(self) -> None:
    """Clear form fields"""
    self.id_input.clear()
    self.pib_input.clear()
    self.address_input.clear()
    self.faculty_input.clear()
    self.email_input.clear()


# ============================================================================
# Application Entry Point
# ============================================================================

def main() -> None:
  """Application entry point"""
  app = QApplication(sys.argv)
  
  # Initialize store and services
  store = Store(AppState())
  db_service = DatabaseService()
  
  # Create and show main window
  window = StudentForm(store, db_service)
  window.show()
  
  sys.exit(app.exec_())


if __name__ == "__main__":
  main()
