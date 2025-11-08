import sqlite3

conn = sqlite3.connect('students.db')
conn.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    age INTEGER,
    gender TEXT,
    address TEXT
)
''')
conn.commit()
conn.close()
print("✅ Database created successfully (no enrollment_date, no status)!")
