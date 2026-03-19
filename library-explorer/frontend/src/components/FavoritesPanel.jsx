export default function FavoritesPanel({ favorites, onDelete }) {
  return (
    <div className="panel">
      <h2>Favorites</h2>
      {favorites.length === 0 ? (
        <p>No favorites yet.</p>
      ) : (
        favorites.map((f) => (
          <div key={f.id} className="small-card">
            <div>
              <strong>{f.title}</strong>
              <div>{f.author}</div>
            </div>
            <button onClick={() => onDelete(f.id)}>Remove</button>
          </div>
        ))
      )}
    </div>
  );
}