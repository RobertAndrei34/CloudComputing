export default function BookCard({ book, onSelect, onFavorite }) {
  return (
    <div className="card">
      <h3>{book.title}</h3>
      <p><strong>Author:</strong> {book.author_name || book.author || "Unknown"}</p>
      {book.year && <p><strong>Year:</strong> {book.year}</p>}
      <div className="actions">
        {onSelect && <button onClick={() => onSelect(book.id)}>Details</button>}
        {onFavorite && (
          <button
            onClick={() =>
              onFavorite({
                local_book_id: book.id,
                title: book.title,
                author: book.author_name || "Unknown"
              })
            }
          >
            Save Favorite
          </button>
        )}
      </div>
    </div>
  );
}