from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os
import re
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'library-system-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Admin credentials (change in production)
ADMIN_CREDENTIALS = {
    'admin': 'admin123',
    'librarian': 'lib@2025'
}

# In-memory database for books
books = [
    {
        "id": 1,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "pages": 1178,
        "price": 25.50,
        "isbn": "9780618053267",
        "category": "Fantasy",
        "quantity": 5
    },
    {
        "id": 2,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "pages": 310,
        "price": 15.00,
        "isbn": "9780345339683",
        "category": "Fantasy",
        "quantity": 8
    },
    {
        "id": 3,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "pages": 279,
        "price": 12.75,
        "isbn": "9780141439518",
        "category": "Romance",
        "quantity": 3
    }
]

current_id = 4


# ==================== Utility Functions ====================

def validate_isbn13(isbn):
    """Validate ISBN-13 format and check digit"""
    isbn = re.sub(r'[-\s]', '', isbn)
    
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    
    total = 0
    for i in range(12):
        total += int(isbn[i]) * (1 if i % 2 == 0 else 3)
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[12])


def check_duplicate_book(isbn, title, book_id=None):
    """Check if book with same ISBN or title already exists"""
    for book in books:
        if book_id and book['id'] == book_id:
            continue
        if book['isbn'] == isbn or book['title'].lower() == title.lower():
            return True
    return False


def get_book_by_id(book_id):
    """Get book by ID"""
    for book in books:
        if book['id'] == book_id:
            return book
    return None


# ==================== Authentication Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            access_token = create_access_token(identity=username)
            return jsonify({
                'success': True,
                'token': access_token,
                'user': {
                    'username': username,
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token"""
    try:
        current_user = get_jwt_identity()
        return jsonify({'valid': True, 'user': current_user}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint"""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


# ==================== Book Management Routes ====================

@app.route('/api/books', methods=['GET'])
@jwt_required()
def get_books():
    """Get all books"""
    try:
        search_term = request.args.get('search', '').lower()
        category_filter = request.args.get('category', '').lower()
        
        filtered_books = books
        
        if search_term:
            filtered_books = [
                b for b in filtered_books
                if search_term in b['title'].lower() or
                   search_term in b['author'].lower() or
                   search_term in b['isbn'].lower()
            ]
        
        if category_filter:
            filtered_books = [
                b for b in filtered_books
                if b['category'].lower() == category_filter
            ]
        
        return jsonify(filtered_books), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch books', 'details': str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    """Get single book by ID"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify(book), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch book', 'details': str(e)}), 500


@app.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
    """Add new book"""
    global current_id
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'author', 'pages', 'price', 'isbn', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate and clean ISBN
        isbn = data['isbn'].strip()
        if not validate_isbn13(isbn):
            return jsonify({'error': 'Invalid ISBN-13 format or check digit'}), 400
        
        # Check for duplicate
        if check_duplicate_book(isbn, data['title']):
            return jsonify({'error': 'Book with this ISBN or title already exists'}), 400
        
        # Validate numeric fields
        try:
            pages = int(data['pages'])
            price = float(data['price'])
            quantity = int(data.get('quantity', 1))
            
            if pages <= 0 or price <= 0 or quantity <= 0:
                return jsonify({'error': 'Pages, price, and quantity must be positive numbers'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid numeric values'}), 400
        
        # Create new book
        new_book = {
            'id': current_id,
            'title': data['title'].strip(),
            'author': data['author'].strip(),
            'pages': pages,
            'price': round(price, 2),
            'isbn': isbn,
            'category': data['category'].strip(),
            'quantity': quantity
        }
        
        books.append(new_book)
        current_id += 1
        
        return jsonify({
            'success': True,
            'message': 'Book added successfully',
            'book': new_book
        }), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add book', 'details': str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """Update existing book"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.get_json()
        
        # Validate ISBN if provided
        if 'isbn' in data:
            isbn = data['isbn'].strip()
            if not validate_isbn13(isbn):
                return jsonify({'error': 'Invalid ISBN-13 format'}), 400
            
            if check_duplicate_book(isbn, data.get('title', book['title']), book_id):
                return jsonify({'error': 'Another book with this ISBN already exists'}), 400
        
        # Update fields
        if 'title' in data:
            book['title'] = data['title'].strip()
        if 'author' in data:
            book['author'] = data['author'].strip()
        if 'pages' in data:
            book['pages'] = int(data['pages'])
        if 'price' in data:
            book['price'] = round(float(data['price']), 2)
        if 'isbn' in data:
            book['isbn'] = data['isbn'].strip()
        if 'category' in data:
            book['category'] = data['category'].strip()
        if 'quantity' in data:
            book['quantity'] = int(data['quantity'])
        
        return jsonify({
            'success': True,
            'message': 'Book updated successfully',
            'book': book
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update book', 'details': str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """Delete book by ID"""
    global books
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        books = [b for b in books if b['id'] != book_id]
        
        return jsonify({
            'success': True,
            'message': 'Book deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete book', 'details': str(e)}), 500


# ==================== Statistics Route ====================

@app.route('/api/books/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get library statistics"""
    try:
        if not books:
            return jsonify({
                'total_books': 0,
                'total_quantity': 0,
                'total_value': 0,
                'avg_pages': 0,
                'avg_price': 0,
                'categories': 0,
                'most_expensive': None,
                'least_expensive': None,
                'longest_book': None,
                'shortest_book': None
            }), 200
        
        total_books = len(books)
        total_quantity = sum(b.get('quantity', 1) for b in books)
        total_value = sum(b['price'] * b.get('quantity', 1) for b in books)
        avg_pages = round(sum(b['pages'] for b in books) / total_books, 2)
        avg_price = round(sum(b['price'] for b in books) / total_books, 2)
        categories = len(set(b['category'] for b in books))
        
        prices = [b['price'] for b in books]
        pages = [b['pages'] for b in books]
        
        most_expensive_book = max(books, key=lambda x: x['price'])
        least_expensive_book = min(books, key=lambda x: x['price'])
        longest_book = max(books, key=lambda x: x['pages'])
        shortest_book = min(books, key=lambda x: x['pages'])
        
        return jsonify({
            'total_books': total_books,
            'total_quantity': total_quantity,
            'total_value': round(total_value, 2),
            'avg_pages': avg_pages,
            'avg_price': round(avg_price, 2),
            'categories': categories,
            'most_expensive': {
                'title': most_expensive_book['title'],
                'price': most_expensive_book['price']
            },
            'least_expensive': {
                'title': least_expensive_book['title'],
                'price': least_expensive_book['price']
            },
            'longest_book': {
                'title': longest_book['title'],
                'pages': longest_book['pages']
            },
            'shortest_book': {
                'title': shortest_book['title'],
                'pages': shortest_book['pages']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to calculate stats', 'details': str(e)}), 500


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Library Management System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': ['/api/auth/login', '/api/auth/verify', '/api/auth/logout'],
            'books': ['/api/books', '/api/books/<id>'],
            'stats': '/api/books/stats',
            'health': '/api/health'
        }
    }), 200


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)