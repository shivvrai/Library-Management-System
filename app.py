# app.py - Flask Backend with SQLite Database Integration

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from database import get_db_connection, hash_password, verify_password
import os
import re
from datetime import datetime, timedelta
from functools import wraps
from flask_jwt_extended import get_jwt
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'library-system-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Constants
FINE_PER_DAY = 10
MAX_BOOKS_PER_STUDENT = 3
RETURN_DAYS = 7

# ==================== Utility Functions ====================

def validate_isbn13(isbn):
    """Simple ISBN-13 validation - accepts any 13-digit number"""
    isbn = re.sub(r'[-\s]', '', isbn)
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    return True

def row_to_dict(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)

def rows_to_dict_list(rows):
    """Convert list of sqlite3.Row to list of dictionaries"""
    return [dict(row) for row in rows]

def calculate_fine(due_date_str):
    """Calculate fine based on due date"""
    if isinstance(due_date_str, str):
        due_date = datetime.fromisoformat(due_date_str)
    else:
        due_date = due_date_str
    
    today = datetime.now()
    if today > due_date:
        days_overdue = (today - due_date).days
        return days_overdue * FINE_PER_DAY
    return 0

# Role decorator (JWT temporarily bypassed for testing)
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # JWT TEMPORARILY BYPASSED FOR TESTING
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ==================== Authentication Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        
        # Check admin credentials
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        
        if admin:
            if verify_password(password, admin['password']):
                # Use username as identity (string), pass other data as additional_claims
                access_token = create_access_token(
                    identity=username,
                    additional_claims={
                        'role': admin['role'],
                        'name': admin['name']
                    }
                )
                conn.close()
                return jsonify({
                    'success': True,
                    'token': access_token,
                    'user': {
                        'username': username,
                        'role': admin['role'],
                        'name': admin['name']
                    }
                }), 200
        
        # Check student credentials
        student = conn.execute('SELECT * FROM students WHERE username = ?', (username,)).fetchone()
        
        if student:
            if verify_password(password, student['password']):
                # Use username as identity (string), pass other data as additional_claims
                access_token = create_access_token(
                    identity=username,
                    additional_claims={
                        'role': student['role'],
                        'id': student['id'],
                        'name': student['name']
                    }
                )
                conn.close()
                return jsonify({
                    'success': True,
                    'token': access_token,
                    'user': {
                        'username': username,
                        'role': student['role'],
                        'id': student['id'],
                        'name': student['name'],
                        'borrowed_books': student['borrowed_books'],
                        'fine_amount': student['fine_amount']
                    }
                }), 200
        
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

# ==================== Admin Routes ====================

@app.route('/api/admin/books', methods=['GET'])
@role_required('admin')
def admin_get_books():
    try:
        conn = get_db_connection()
        books = conn.execute('SELECT * FROM books ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify(rows_to_dict_list(books)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch books', 'details': str(e)}), 500

@app.route('/api/admin/books', methods=['POST'])
@role_required('admin')
def admin_add_book():
    try:
        data = request.get_json()
        
        # Validate required fields - FIXED TO HANDLE 0 VALUES
        required_fields = ['title', 'author', 'pages', 'price', 'isbn', 'category', 'quantity']
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ''):
                return jsonify({'error': f'{field} is required'}), 400
        
        isbn = data['isbn'].strip()
        if not validate_isbn13(isbn):
            return jsonify({'error': 'Invalid ISBN-13 format'}), 400
        
        conn = get_db_connection()
        
        # Check for duplicate ISBN or title
        existing = conn.execute(
            'SELECT id FROM books WHERE isbn = ? OR title = ?',
            (isbn, data['title'].strip())
        ).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'error': 'Book with this ISBN or title already exists'}), 400
        
        # Insert new book
        quantity = int(data['quantity'])
        cursor = conn.execute('''
            INSERT INTO books (title, author, isbn, pages, price, category, quantity, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'].strip(),
            data['author'].strip(),
            isbn,
            int(data['pages']),
            round(float(data['price']), 2),
            data['category'].strip(),
            quantity,
            quantity
        ))
        
        conn.commit()
        
        # Fetch the newly created book
        new_book = conn.execute('SELECT * FROM books WHERE id = ?', (cursor.lastrowid,)).fetchone()
        conn.close()
        
        return jsonify({'success': True, 'book': row_to_dict(new_book)}), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to add book', 'details': str(e)}), 500

@app.route('/api/admin/books/<int:book_id>', methods=['PUT'])
@role_required('admin')
def admin_update_book(book_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        # Check if book exists
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if 'title' in data:
            update_fields.append('title = ?')
            update_values.append(data['title'].strip())
        
        if 'author' in data:
            update_fields.append('author = ?')
            update_values.append(data['author'].strip())
        
        if 'pages' in data:
            update_fields.append('pages = ?')
            update_values.append(int(data['pages']))
        
        if 'price' in data:
            update_fields.append('price = ?')
            update_values.append(round(float(data['price']), 2))
        
        if 'category' in data:
            update_fields.append('category = ?')
            update_values.append(data['category'].strip())
        
        if 'quantity' in data:
            new_quantity = int(data['quantity'])
            diff = new_quantity - book['quantity']
            update_fields.append('quantity = ?')
            update_fields.append('available = ?')
            update_values.append(new_quantity)
            update_values.append(max(0, book['available'] + diff))
        
        if update_fields:
            update_values.append(book_id)
            query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
        
        # Fetch updated book
        updated_book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        conn.close()
        
        return jsonify({'success': True, 'book': row_to_dict(updated_book)}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update book', 'details': str(e)}), 500

@app.route('/api/admin/books/<int:book_id>', methods=['DELETE'])
@role_required('admin')
def admin_delete_book(book_id):
    try:
        conn = get_db_connection()
        
        # Check if book exists
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        # Check if book is currently borrowed
        borrowed = conn.execute(
            'SELECT id FROM transactions WHERE book_id = ? AND status = ?',
            (book_id, 'borrowed')
        ).fetchone()
        
        if borrowed:
            conn.close()
            return jsonify({'error': 'Cannot delete book that is currently borrowed'}), 400
        
        # Delete the book
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Book deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete book', 'details': str(e)}), 500

@app.route('/api/admin/students', methods=['GET'])
@role_required('admin')
def admin_get_students():
    try:
        conn = get_db_connection()
        students = conn.execute('SELECT * FROM students ORDER BY created_at DESC').fetchall()
        conn.close()
        
        student_list = []
        for student in students:
            student_dict = row_to_dict(student)
            # Don't send password to frontend
            student_dict.pop('password', None)
            student_list.append(student_dict)
        
        return jsonify(student_list), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch students', 'details': str(e)}), 500

@app.route('/api/admin/transactions', methods=['GET'])
@role_required('admin')
def admin_get_transactions():
    try:
        conn = get_db_connection()
        transactions = conn.execute('''
            SELECT 
                t.*,
                b.title as book_title,
                s.name as student_name
            FROM transactions t
            LEFT JOIN books b ON t.book_id = b.id
            LEFT JOIN students s ON t.student_id = s.id
            ORDER BY t.created_at DESC
        ''').fetchall()
        conn.close()
        
        enriched_transactions = []
        for trans in transactions:
            trans_dict = row_to_dict(trans)
            if trans_dict['status'] == 'borrowed':
                trans_dict['fine'] = calculate_fine(trans_dict['due_date'])
            else:
                trans_dict['fine'] = trans_dict.get('fine_amount', 0)
            enriched_transactions.append(trans_dict)
        
        return jsonify(enriched_transactions), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch transactions', 'details': str(e)}), 500

@app.route('/api/admin/overdue', methods=['GET'])
@role_required('admin')
def admin_get_overdue():
    try:
        conn = get_db_connection()
        today = datetime.now()
        
        overdue_transactions = conn.execute('''
            SELECT 
                t.*,
                b.title as book_title,
                s.name as student_name,
                s.id as student_id
            FROM transactions t
            LEFT JOIN books b ON t.book_id = b.id
            LEFT JOIN students s ON t.student_id = s.id
            WHERE t.status = ? AND t.due_date < ?
            ORDER BY t.due_date ASC
        ''', ('borrowed', today.isoformat())).fetchall()
        conn.close()
        
        overdue_list = []
        for trans in overdue_transactions:
            trans_dict = row_to_dict(trans)
            due_date = datetime.fromisoformat(trans_dict['due_date'])
            days_overdue = (today - due_date).days
            fine = days_overdue * FINE_PER_DAY
            
            trans_dict['days_overdue'] = days_overdue
            trans_dict['fine'] = fine
            overdue_list.append(trans_dict)
        
        return jsonify(overdue_list), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch overdue books', 'details': str(e)}), 500

@app.route('/api/admin/return/<int:transaction_id>', methods=['POST'])
@role_required('admin')
def admin_process_return(transaction_id):
    try:
        conn = get_db_connection()
        
        # Get transaction
        trans = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
        if not trans:
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404
        
        if trans['status'] != 'borrowed':
            conn.close()
            return jsonify({'error': 'Book already returned'}), 400
        
        # Calculate fine
        fine = calculate_fine(trans['due_date'])
        
        # Update transaction
        conn.execute('''
            UPDATE transactions
            SET status = ?, return_date = ?, fine_amount = ?
            WHERE id = ?
        ''', ('returned', datetime.now().isoformat(), fine, transaction_id))
        
        # Update book availability
        conn.execute('''
            UPDATE books
            SET available = available + 1
            WHERE id = ?
        ''', (trans['book_id'],))
        
        # Update student
        conn.execute('''
            UPDATE students
            SET borrowed_books = borrowed_books - 1,
                fine_amount = fine_amount + ?
            WHERE id = ?
        ''', (fine, trans['student_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'fine': fine,
            'message': f'Book returned. Fine: ₹{fine}' if fine > 0 else 'Book returned successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process return', 'details': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@role_required('admin')
def admin_get_stats():
    try:
        conn = get_db_connection()
        
        total_books = conn.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
        total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
        active_borrows = conn.execute(
            'SELECT COUNT(*) as count FROM transactions WHERE status = ?',
            ('borrowed',)
        ).fetchone()['count']
        
        # Get overdue count
        today = datetime.now().isoformat()
        overdue_count = conn.execute(
            'SELECT COUNT(*) as count FROM transactions WHERE status = ? AND due_date < ?',
            ('borrowed', today)
        ).fetchone()['count']
        
        # Get total fines
        total_fines = conn.execute('SELECT SUM(fine_amount) as total FROM students').fetchone()['total'] or 0
        total_transactions = conn.execute('SELECT COUNT(*) as count FROM transactions').fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'total_books': total_books,
            'total_students': total_students,
            'active_borrows': active_borrows,
            'overdue_books': overdue_count,
            'total_fines': round(total_fines, 2),
            'total_transactions': total_transactions
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500

# ==================== Student Routes ====================

@app.route('/api/student/books/available', methods=['GET'])
@jwt_required()
def student_get_available_books():
    try:
        conn = get_db_connection()
        books = conn.execute('SELECT * FROM books WHERE available > 0 ORDER BY title ASC').fetchall()
        conn.close()
        return jsonify(rows_to_dict_list(books)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch books', 'details': str(e)}), 500

@app.route('/api/student/borrow', methods=['POST'])
@jwt_required()
def student_borrow_book():
    try:
        identity = get_jwt_identity()  # This is the username string
        claims = get_jwt()  # Get the full JWT payload
        student_id = claims.get('id')
        
        data = request.get_json()
        book_id = data.get('book_id')
        
        conn = get_db_connection()
        
        # Get student and book
        student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        
        if not student or not book:
            conn.close()
            return jsonify({'error': 'Student or book not found'}), 404
        
        # Validate borrowing rules
        if student['borrowed_books'] >= MAX_BOOKS_PER_STUDENT:
            conn.close()
            return jsonify({'error': f'Cannot borrow more than {MAX_BOOKS_PER_STUDENT} books at a time'}), 400
        
        if book['available'] <= 0:
            conn.close()
            return jsonify({'error': 'Book is not available'}), 400
        
        # Check for overdue books
        today = datetime.now().isoformat()
        overdue = conn.execute(
            'SELECT id FROM transactions WHERE student_id = ? AND status = ? AND due_date < ?',
            (student_id, 'borrowed', today)
        ).fetchone()
        
        if overdue:
            conn.close()
            return jsonify({'error': 'Cannot borrow. You have overdue books. Please return them first.'}), 400
        
        if student['fine_amount'] > 0:
            conn.close()
            return jsonify({'error': f'Cannot borrow. Please pay pending fine of ₹{student["fine_amount"]}'}), 400
        
        # ✅ NEW: Check if student already has this specific book borrowed
        already_borrowed = conn.execute('''
            SELECT id FROM transactions
            WHERE student_id = ? AND book_id = ? AND status = ?
        ''', (student_id, book_id, 'borrowed')).fetchone()
        
        if already_borrowed:
            conn.close()
            return jsonify({'error': f'You already have this book borrowed. Please return it before borrowing again.'}), 400
        
        # Create transaction
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=RETURN_DAYS)
        
        cursor = conn.execute('''
            INSERT INTO transactions (student_id, book_id, borrow_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, book_id, borrow_date.isoformat(), due_date.isoformat(), 'borrowed'))
        
        # Update book availability
        conn.execute('UPDATE books SET available = available - 1 WHERE id = ?', (book_id,))
        
        # Update student borrowed count
        conn.execute('UPDATE students SET borrowed_books = borrowed_books + 1 WHERE id = ?', (student_id,))
        
        conn.commit()
        
        # Get created transaction
        transaction = conn.execute('SELECT * FROM transactions WHERE id = ?', (cursor.lastrowid,)).fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Book borrowed successfully',
            'transaction': row_to_dict(transaction),
            'due_date': due_date.strftime('%Y-%m-%d')
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to borrow book', 'details': str(e)}), 500

@app.route('/api/student/my-books', methods=['GET'])
@jwt_required()
def student_get_my_books():
    try:
        identity = get_jwt_identity()  # This is now the username string
        claims = get_jwt()  # Get the full JWT payload
        student_id = claims.get('id')
        role = claims.get('role')
        
        conn = get_db_connection()
        
        my_books_data = conn.execute('''
            SELECT 
                t.*,
                b.title, b.author, b.isbn, b.category, b.pages, b.price
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.student_id = ? AND t.status = ?
            ORDER BY t.due_date ASC
        ''', (student_id, 'borrowed')).fetchall()
        
        conn.close()
        
        my_books = []
        today = datetime.now()
        
        for item in my_books_data:
            item_dict = row_to_dict(item)
            due_date = datetime.fromisoformat(item_dict['due_date'])
            days_remaining = (due_date - today).days
            fine = calculate_fine(item_dict['due_date'])
            
            # Build book object
            book = {
                'id': item_dict['book_id'],
                'title': item_dict['title'],
                'author': item_dict['author'],
                'isbn': item_dict['isbn'],
                'category': item_dict['category'],
                'pages': item_dict['pages'],
                'price': item_dict['price']
            }
            
            my_books.append({
                'transaction_id': item_dict['id'],
                'book': book,
                'borrow_date': item_dict['borrow_date'],
                'due_date': item_dict['due_date'],
                'days_remaining': days_remaining,
                'is_overdue': days_remaining < 0,
                'fine': fine
            })
        
        return jsonify(my_books), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch borrowed books', 'details': str(e)}), 500

@app.route('/api/student/return/<int:transaction_id>', methods=['POST'])
@jwt_required()
def student_return_book(transaction_id):
    try:
        identity = get_jwt_identity()  # This is now the username string
        claims = get_jwt()  # Get the full JWT payload
        student_id = claims.get('id')
        role = claims.get('role')
        
        conn = get_db_connection()
        
        # Get transaction
        trans = conn.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
        if not trans:
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404
        
        if trans['student_id'] != student_id:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        if trans['status'] != 'borrowed':
            conn.close()
            return jsonify({'error': 'Book already returned'}), 400
        
        # Calculate fine
        fine = calculate_fine(trans['due_date'])
        
        # Update transaction
        conn.execute('''
            UPDATE transactions
            SET status = ?, return_date = ?, fine_amount = ?
            WHERE id = ?
        ''', ('returned', datetime.now().isoformat(), fine, transaction_id))
        
        # Update book availability
        conn.execute('UPDATE books SET available = available + 1 WHERE id = ?', (trans['book_id'],))
        
        # Update student
        update_query = 'UPDATE students SET borrowed_books = borrowed_books - 1'
        params = [student_id]
        
        if fine > 0:
            update_query += ', fine_amount = fine_amount + ?'
            params.insert(0, fine)
        
        update_query += ' WHERE id = ?'
        conn.execute(update_query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'fine': fine,
            'message': f'Book returned successfully. Fine: ₹{fine}' if fine > 0 else 'Book returned successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to return book', 'details': str(e)}), 500

# Add this AFTER the @app.route('/api/student/return/<int:transaction_id>') route

@app.route('/api/student/fines', methods=['GET'])
@jwt_required()
def student_get_fines():
    try:
        identity = get_jwt_identity()  # This is now the username string
        claims = get_jwt()  # Get the full JWT payload
        student_id = claims.get('id')
        role = claims.get('role')
        
        conn = get_db_connection()
        student = conn.execute('SELECT borrowed_books, fine_amount FROM students WHERE id = ?', (student_id,)).fetchone()
        conn.close()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        return jsonify({
            'borrowed_books': student['borrowed_books'],
            'fine_amount': student['fine_amount']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get fines', 'details': str(e)}), 500




# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Library Management System API',
        'version': '2.0.0',
        'database': 'SQLite',
        'roles': ['admin', 'student']
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
