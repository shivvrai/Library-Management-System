const StudentManager = ({ students }) => {
  return (
    <div className="student-manager">
      <h2>Students Management</h2>
      <table className="students-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Borrowed</th>
            <th>Fine</th>
          </tr>
        </thead>
        <tbody>
          {students.map(student => (
            <tr key={student.id}>
              <td>{student.id}</td>
              <td>{student.name}</td>
              <td>{student.email}</td>
              <td>{student.phone}</td>
              <td><span className="badge">{student.borrowed_books}</span></td>
              <td className={student.fine_amount > 0 ? 'fine' : ''}>₹{student.fine_amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default StudentManager
