import { studentAPI } from '../../utils/api'
import { formatDate, calculateDaysRemaining, getDueDateStatus } from '../../utils/dateUtils'

const MyBooks = ({ books, onReturn }) => {
  const handleReturn = async (transactionId) => {
    try {
      await studentAPI.returnBook(transactionId)
      alert('✅ Book returned successfully!')
      onReturn()
    } catch (error) {
      alert('❌ Failed to return book')
    }
  }

  if (books.length === 0) {
    return (
      <div className="my-books">
        <div className="empty-state">
          <p>📚 You haven't borrowed any books yet</p>
        </div>
      </div>
    )
  }

  return (
    <div className="my-books">
      <h2>My Borrowed Books</h2>
      <div className="borrowed-books-list">
        {books.map(item => {
          const daysLeft = calculateDaysRemaining(item.due_date)
          const status = getDueDateStatus(daysLeft)

          return (
            <div key={item.transaction_id} className={`borrowed-book-card status-${status}`}>
              <div className="book-info">
                <h3>{item.book.title}</h3>
                <p className="author">by {item.book.author}</p>
              </div>
              <div className="due-info">
                <p><strong>Borrow Date:</strong> {formatDate(item.borrow_date)}</p>
                <p><strong>Due Date:</strong> {formatDate(item.due_date)}</p>
                <p className={`days-remaining ${status}`}>
                  {daysLeft >= 0
                    ? `✅ ${daysLeft} days remaining`
                    : `⚠️ ${Math.abs(daysLeft)} days overdue`
                  }
                </p>
                {item.fine > 0 && (
                  <p className="fine">💰 Fine: ₹{item.fine}</p>
                )}
              </div>
              <button
                onClick={() => handleReturn(item.id)}
                className="btn btn-success"
              >
                ✓ Return Book
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default MyBooks
