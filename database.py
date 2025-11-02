# database.py - SQLite Database Models and Initialization

import sqlite3
import bcrypt
from datetime import datetime, timedelta
import os

DATABASE_NAME = 'library.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_database():
    """Initialize database with tables and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS transactions')
    cursor.execute('DROP TABLE IF EXISTS books')
    cursor.execute('DROP TABLE IF EXISTS students')
    cursor.execute('DROP TABLE IF EXISTS admins')
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            borrowed_books INTEGER DEFAULT 0,
            fine_amount REAL DEFAULT 0.0,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create books table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            pages INTEGER NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            available INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP NOT NULL,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            status TEXT NOT NULL,
            fine_amount REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    
    # Insert default admin accounts
    admin_password = hash_password('admin123')
    librarian_password = hash_password('lib@2025')
    
    cursor.execute('''
        INSERT INTO admins (username, password, name, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password, 'Admin User', 'admin'))
    
    cursor.execute('''
        INSERT INTO admins (username, password, name, role)
        VALUES (?, ?, ?, ?)
    ''', ('librarian', librarian_password, 'Librarian', 'admin'))
    
    # Insert default students
    student_password = hash_password('pass123')
    
    students_data = [
        ('S001', 'student1', student_password, 'Rahul Kumar', 'rahul@example.com', '9876543210'),
        ('S002', 'student2', student_password, 'Priya Sharma', 'priya@example.com', '9876543211'),
        ('S003', 'student3', student_password, 'Amit Patel', 'amit@example.com', '9876543212')
    ]
    
    for student in students_data:
        cursor.execute('''
            INSERT INTO students (id, username, password, name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', student)
    
    # Insert default books
    books_data = [
        ("The Lord of the Rings", "J.R.R. Tolkien", "9780618053267", 1178, 25.50, "Fantasy", 5, 5),
        ("The Hobbit", "J.R.R. Tolkien", "9780345339683", 310, 15.00, "Fantasy", 8, 8),
        ("Pride and Prejudice", "Jane Austen", "9780141439518", 279, 12.75, "Romance", 3, 3),
        ("1984", "George Orwell", "9780451524935", 328, 10.20, "Fiction", 4, 4),
        ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 324, 14.99, "Fiction", 6, 6),
        ("The C Programming Language", "Dennis Ritchie", "9780131101630", 272, 45.00, "Programming", 10, 10),
        ("Clean Code", "Robert C. Martin", "9780132350884", 464, 38.50, "Programming", 7, 7),
        ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "9780747532699", 223, 20.00, "Fantasy", 12, 12)
    ]
    
    for book in books_data:
        cursor.execute('''
            INSERT INTO books (title, author, isbn, pages, price, category, quantity, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', book)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"📁 Database file: {DATABASE_NAME}")
    print("\n🔐 Default Login Credentials:")
    print("Admin: username='admin', password='admin123'")
    print("Student: username='student1', password='pass123'")

if __name__ == '__main__':
    init_database()
