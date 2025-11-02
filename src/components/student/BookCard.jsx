const BookCard = ({ book, onBorrow, borrowDisabled }) => {
  return (
    <div className="book-card">
      <h3>{book.title}</h3>
      <p className="author">by {book.author}</p>
      <div className="book-details">
        <p><strong>Category:</strong> {book.category}</p>
        <p><strong>Pages:</strong> {book.pages}</p>
        <p><strong>Price:</strong> ${book.price}</p>
        <p><strong>ISBN:</strong> {book.isbn}</p>
      </div>
      <p className="availability">
        {book.available > 0 ? '✅ Available' : '❌ Not Available'}
      </p>
      <button
        onClick={() => onBorrow(book.id)}
        disabled={book.available <= 0 || borrowDisabled}
        className="btn btn-primary"
      >
        📚 Borrow
      </button>
    </div>
  )
}

export default BookCard
