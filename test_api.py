import requests

BASE_URL = "http://localhost:8000/api"

# Get all books
books = requests.get(f"{BASE_URL}/books").json()
print("Books:", books)

# Add book
new_book = {
    "title": "Test", "author": "Author", "pages": 100,
    "price": 9.99, "isbn": "1234567890", "category": "Test"
}
added = requests.post(f"{BASE_URL}/books", json=new_book).json()
print("Added:", added)

# Get stats
stats = requests.get(f"{BASE_URL}/stats").json()
print("Stats:", stats)

# Delete
requests.delete(f"{BASE_URL}/books/{added['id']}")
print("Deleted!")
