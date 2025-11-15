# Student Database Manager

A simple desktop application for managing student records built with PyQt5 and SQLite.

## Features

- 📝 Add new student records
- 🗄️ SQLite database storage
- 🖥️ User-friendly GUI interface
- 🔍 Student information management (ID, Name, Address, Faculty, Email)

## Screenshots

*Add screenshots here*

## Requirements

- Python 3.6+
- PyQt5

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/student-db-manager.git
cd student-db-manager
```

2. Install dependencies:
```bash
pip install PyQt5
```

## Usage

Run the application:
```bash
python main.py
```

### Adding a Student

1. Click the **"ДОДАТИ"** (Add) button
2. Fill in the student details:
   - ID студента (Student ID) - required
   - ПІБ (Full Name) - required
   - Місце проживання (Address) - optional
   - Факультет (Faculty) - optional
   - Пошта (Email) - optional
3. Click **"Додати"** to save

## Database

The application creates a SQLite database file named `banana.db` in the same directory as the script.

### Database Schema

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    pib TEXT NOT NULL,
    address TEXT,
    faculty TEXT,
    email TEXT
)
```

## Planned Features

- [ ] Edit existing student records
- [ ] Delete student records
- [ ] Search functionality
- [ ] View all students in a table
- [ ] Export data to CSV
- [ ] Input validation improvements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for educational purposes.

## Author

Your Name

## Acknowledgments

Built with PyQt5 for educational purposes.