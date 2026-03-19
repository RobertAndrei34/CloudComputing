import { useEffect, useState } from "react";
import {
  searchBooks,
  getAllLocalBooks,
  getBookDetails,
  getFavorites,
  addFavorite,
  deleteFavorite,
  getHistory
} from "./api";
import SearchBar from "./components/SearchBar";
import BookCard from "./components/BookCard";
import FavoritesPanel from "./components/FavoritesPanel";
import "./styles.css";

export default function App() {
  const [books, setBooks] = useState([]);
  const [details, setDetails] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [history, setHistory] = useState([]);
  const [searchResult, setSearchResult] = useState(null);
  const [error, setError] = useState("");

  async function loadInitial() {
    try {
      const local = await getAllLocalBooks();
      setBooks(local.items || []);
      setFavorites(await getFavorites());
      setHistory(await getHistory());
    } catch (err) {
      setError("Failed to load initial data.");
    }
  }

  useEffect(() => {
    loadInitial();
  }, []);

  async function handleSearch(query) {
    setError("");
    try {
      const result = await searchBooks(query);
      setSearchResult(result);
      setHistory(await getHistory());
    } catch {
      setError("Search failed.");
    }
  }

  async function handleDetails(id) {
    setError("");
    try {
      const result = await getBookDetails(id);
      setDetails(result);
    } catch {
      setError("Failed to load details.");
    }
  }

  async function handleFavorite(payload) {
    try {
      await addFavorite(payload);
      setFavorites(await getFavorites());
    } catch {
      setError("Failed to save favorite.");
    }
  }

  async function handleDeleteFavorite(id) {
    try {
      await deleteFavorite(id);
      setFavorites(await getFavorites());
    } catch {
      setError("Failed to remove favorite.");
    }
  }

  return (
    <div className="container">
      <h1>Library Explorer</h1>
      <SearchBar onSearch={handleSearch} />

      {error && <div className="error-box">{error}</div>}

      <div className="layout">
        <div className="main">
          <section className="panel">
            <h2>Local Books</h2>
            {books.map((b) => (
              <BookCard
                key={b.id}
                book={b}
                onSelect={handleDetails}
                onFavorite={handleFavorite}
              />
            ))}
          </section>

          {searchResult && (
            <section className="panel">
              <h2>Search Aggregation</h2>
              <pre>{JSON.stringify(searchResult, null, 2)}</pre>
            </section>
          )}

          {details && (
            <section className="panel">
              <h2>Aggregated Details</h2>
              <pre>{JSON.stringify(details, null, 2)}</pre>
            </section>
          )}

          <section className="panel">
            <h2>Recent Search History</h2>
            {history.map((h) => (
              <div key={h.id} className="small-card">
                <span>{h.query}</span>
                <span>{h.created_at}</span>
              </div>
            ))}
          </section>
        </div>

        <FavoritesPanel favorites={favorites} onDelete={handleDeleteFavorite} />
      </div>
    </div>
  );
}