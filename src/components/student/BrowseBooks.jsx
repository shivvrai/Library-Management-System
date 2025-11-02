import { studentAPI } from '../../utils/api'
import BookCard from './BookCard'

const BrowseBooks = ({ books, fines, onBorrow }) => {
  const handleBorrow = async (bookId) => {
    if (fines.borrowed_books >= 3) {
      alert('❌ You can only borrow up to 3 books at a time')
      return
    }

    try {
      await studentAPI.borrowBook(bookId)
      alert('✅ Book borrowed successfully!')
      onBorrow()
    } catch (error) {
      alert('❌ Failed to borrow book')
    }
  }

  return (
    <div className="browse-books">
      <h2>Available Books</h2>
      <div className="books-grid">
        {books.map(book => (
          <BookCard
            key={book.id}
            book={book}
            onBorrow={handleBorrow}
            borrowDisabled={fines.borrowed_books >= 3}
          />
        ))}
      </div>
    </div>
  )
}

export default BrowseBooks
