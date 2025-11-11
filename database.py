# # database.py - Updated with 8-digit registration numbers

# import sqlite3
# import bcrypt
# from datetime import datetime, timedelta
# import os
# import random

# DATABASE_NAME = 'library.db'

# def get_db_connection():
#     """Get database connection"""
#     conn = sqlite3.connect(DATABASE_NAME)
#     conn.row_factory = sqlite3.Row
#     return conn

# def hash_password(password):
#     """Hash password using bcrypt"""
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# def verify_password(password, hashed):
#     """Verify password against hash"""
#     return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# def generate_registration_number():
#     """Generate unique 8-digit registration number"""
#     conn = get_db_connection()
    
#     while True:
#         # Generate random 8-digit number (10000000 to 99999999)
#         reg_no = str(random.randint(10000000, 99999999))
        
#         # Check if it already exists
#         existing = conn.execute('SELECT id FROM students WHERE registration_no = ?', (reg_no,)).fetchone()
        
#         if not existing:
#             conn.close()
#             return reg_no

# def get_next_transaction_id():
#     """Generate next transaction ID"""
#     conn = get_db_connection()
#     last_txn = conn.execute('SELECT transaction_id FROM transactions ORDER BY id DESC LIMIT 1').fetchone()
#     conn.close()
    
#     if not last_txn:
#         return 'TXN0001'
    
#     last_num = int(last_txn['transaction_id'][3:])
#     return f'TXN{str(last_num + 1).zfill(4)}'

# def init_database():
#     """Initialize database with tables and default data"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Drop existing tables
#     cursor.execute('DROP TABLE IF EXISTS transactions')
#     cursor.execute('DROP TABLE IF EXISTS books')
#     cursor.execute('DROP TABLE IF EXISTS students')
#     cursor.execute('DROP TABLE IF EXISTS admins')
    
#     # Create admins table
#     cursor.execute('''
#         CREATE TABLE admins (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             name TEXT NOT NULL,
#             role TEXT DEFAULT 'admin',
#             created_at TIMESTAMP DEFAULT CURRENT_timestamp
#         )
#     ''')
    
#     # Create students table with 8-digit registration_no
#     cursor.execute('''
#         CREATE TABLE students (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             registration_no TEXT UNIQUE NOT NULL,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             name TEXT NOT NULL,
#             email TEXT NOT NULL,
#             phone TEXT NOT NULL,
#             role TEXT DEFAULT 'student',
#             borrowed_books INTEGER DEFAULT 0,
#             fine_amount REAL DEFAULT 0,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Create books table
#     cursor.execute('''
#         CREATE TABLE books (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT NOT NULL,
#             author TEXT NOT NULL,
#             isbn TEXT UNIQUE NOT NULL,
#             pages INTEGER,
#             price REAL,
#             category TEXT,
#             quantity INTEGER DEFAULT 1,
#             available INTEGER DEFAULT 1,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Create transactions table
#     cursor.execute('''
#         CREATE TABLE transactions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             transaction_id TEXT UNIQUE NOT NULL,
#             student_id INTEGER NOT NULL,
#             student_registration_no TEXT NOT NULL,
#             book_id INTEGER NOT NULL,
#             borrow_date TIMESTAMP NOT NULL,
#             due_date TIMESTAMP NOT NULL,
#             return_date TIMESTAMP,
#             status TEXT DEFAULT 'borrowed',
#             fine_amount REAL DEFAULT 0,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (student_id) REFERENCES students(id),
#             FOREIGN KEY (book_id) REFERENCES books(id)
#         )
#     ''')
    
#     # Insert default admin accounts
#     admin_password = hash_password('admin123')
#     librarian_password = hash_password('lib@2025')
    
#     cursor.execute('''
#         INSERT INTO admins (username, password, name, role)
#         VALUES (?, ?, ?, ?)
#     ''', ('admin', admin_password, 'System Administrator', 'admin'))
    
#     cursor.execute('''
#         INSERT INTO admins (username, password, name, role)
#         VALUES (?, ?, ?, ?)
#     ''', ('librarian', librarian_password, 'Library Staff', 'admin'))
    
#     # Insert default students with 8-digit registration numbers
#     default_students = [
#         ('Rahul Kumar', 'rahul.kumar', 'pass123', 'rahul.kumar@college.edu', '9876543210'),
#         ('Priya Sharma', 'priya.sharma', 'pass123', 'priya.sharma@college.edu', '9876543211'),
#         ('Amit Patel', 'amit.patel', 'pass123', 'amit.patel@college.edu', '9876543212'),
#     ]
    
#     student_password = hash_password('pass123')
    
#     for name, username, _, email, phone in default_students:
#         reg_no = generate_registration_number()
#         cursor.execute('''
#             INSERT INTO students (registration_no, username, password, name, email, phone, role)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         ''', (reg_no, username, student_password, name, email, phone, 'student'))
    
#     # Insert default books
#     default_books = [
#         ('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', '9780439708180', 309, 12.99, 'Fantasy', 5, 5),
#         ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 310, 10.99, 'Fantasy', 3, 3),
#         ('1984', 'George Orwell', '9780451524935', 328, 9.99, 'Fiction', 4, 4),
#         ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 324, 11.99, 'Fiction', 6, 6),
#         ('Pride and Prejudice', 'Jane Austen', '9780141439518', 279, 8.99, 'Romance', 4, 4),
#         ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 180, 10.50, 'Fiction', 5, 5),
#     ]
    
#     cursor.executemany('''
#         INSERT INTO books (title, author, isbn, pages, price, category, quantity, available)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     ''', default_books)
    
#     conn.commit()
#     conn.close()
    
#     print('✅ Database initialized successfully!')
#     print('🔐 Default Admin Credentials:')
#     print("   Admin: username='admin', password='admin123'")
#     print("   Librarian: username='librarian', password='lib@2025'")
#     print('👥 Default Students:')
#     print("   All students have password='pass123'")
#     print('📚 6 default books added')

# if __name__ == '__main__':
#     if os.path.exists(DATABASE_NAME):
#         os.remove(DATABASE_NAME)
#         print(f'🗑️  Deleted existing database: {DATABASE_NAME}')
    
#     init_database()
# database.py - Updated with 8-digit registration numbers and WAL, auto-generated transaction code

import sqlite3
import bcrypt
from datetime import datetime, timedelta
import os
import random

DATABASE_NAME = 'library.db'


def get_db_connection():
    """Get database connection with optimized settings for concurrency."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout = 30000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except Exception as e:
        print(f"Warning: Could not set PRAGMA: {e}", flush=True)
    return conn


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_registration_number():
    """Generate unique 8-digit registration number"""
    conn = get_db_connection()
    try:
        while True:
            reg_no = str(random.randint(10000000, 99999999))
            existing = conn.execute('SELECT id FROM students WHERE registration_no = ?', (reg_no,)).fetchone()
            if not existing:
                return reg_no
    finally:
        conn.close()


def get_next_transaction_id():
    """Generate next transaction ID in form TXN0001 based on highest id."""
    conn = get_db_connection()
    try:
        last_id_row = conn.execute('SELECT MAX(id) as max_id FROM transactions').fetchone()
        max_id = last_id_row['max_id'] if last_id_row else None
        if not max_id:
            next_num = 1
        else:
            next_num = int(max_id) + 1
        return f'TXN{str(next_num).zfill(4)}'
    finally:
        conn.close()


def init_database():
    """Initialize database with tables and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS transactions')
    cursor.execute('DROP TABLE IF EXISTS books')
    cursor.execute('DROP TABLE IF EXISTS students')
    cursor.execute('DROP TABLE IF EXISTS admins')

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

    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_no TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            borrowed_books INTEGER DEFAULT 0,
            fine_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            pages INTEGER,
            price REAL,
            category TEXT,
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            student_id INTEGER NOT NULL,
            student_registration_no TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP NOT NULL,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'borrowed',
            fine_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    admin_password = hash_password('admin123')
    librarian_password = hash_password('lib@2025')

    cursor.execute('''
        INSERT INTO admins (username, password, name, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password, 'System Administrator', 'admin'))

    cursor.execute('''
        INSERT INTO admins (username, password, name, role)
        VALUES (?, ?, ?, ?)
    ''', ('librarian', librarian_password, 'Library Staff', 'admin'))

    default_students = [
        ('Rahul Kumar', 'rahul.kumar', 'pass123', 'rahul.kumar@college.edu', '9876543210'),
        ('Priya Sharma', 'priya.sharma', 'pass123', 'priya.sharma@college.edu', '9876543211'),
        ('Amit Patel', 'amit.patel', 'pass123', 'amit.patel@college.edu', '9876543212'),
    ]

    student_password = hash_password('pass123')

    for name, username, _, email, phone in default_students:
        reg_no = generate_registration_number()
        cursor.execute('''
            INSERT INTO students (registration_no, username, password, name, email, phone, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (reg_no, username, student_password, name, email, phone, 'student'))

    default_books = [
        ('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', '9780439708180', 309, 12.99, 'Fantasy', 5, 5),
        ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 310, 10.99, 'Fantasy', 3, 3),
        ('1984', 'George Orwell', '9780451524935', 328, 9.99, 'Fiction', 4, 4),
        ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 324, 11.99, 'Fiction', 6, 6),
        ('Pride and Prejudice', 'Jane Austen', '9780141439518', 279, 8.99, 'Romance', 4, 4),
        ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 180, 10.50, 'Fiction', 5, 5),
    ]

    cursor.executemany('''
        INSERT INTO books (title, author, isbn, pages, price, category, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', default_books)

    conn.commit()
    conn.close()

    print('✅ Database initialized successfully!')
    print('🔐 Default Admin Credentials:')
    print("   Admin: username='admin', password='admin123'")
    print("   Librarian: username='librarian', password='lib@2025'")
    print('👥 Default Students:')
    print("   All students have password='pass123'")
    print('📚 6 default books added')


if __name__ == '__main__':
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f'🗑️  Deleted existing database: {DATABASE_NAME}')
    init_database()
