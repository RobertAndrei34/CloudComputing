import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = "storage.sqlite"

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            author_id INTEGER NOT NULL,
            isbn TEXT UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(author_id) REFERENCES authors(id) ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_books_author_id ON books(author_id);
        CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
        """.strip())

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)

# ---------- Authors ----------
def create_author(name: str, country: Optional[str]) -> Dict[str, Any]:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO authors(name, country) VALUES(?, ?)",
            (name, country),
        )
        author_id = cur.lastrowid
        row = conn.execute("SELECT * FROM authors WHERE id = ?", (author_id,)).fetchone()
        return row_to_dict(row)

def get_author(author_id: int) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM authors WHERE id = ?", (author_id,)).fetchone()
        return row_to_dict(row) if row else None

def update_author(author_id: int, name: str, country: Optional[str]) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        exists = conn.execute("SELECT 1 FROM authors WHERE id = ?", (author_id,)).fetchone()
        if not exists:
            return None
        conn.execute(
            "UPDATE authors SET name = ?, country = ? WHERE id = ?",
            (name, country, author_id),
        )
        row = conn.execute("SELECT * FROM authors WHERE id = ?", (author_id,)).fetchone()
        return row_to_dict(row)

def delete_author(author_id: int) -> Tuple[str, Optional[str]]:
    """
    Returns (result, message):
      - ("deleted", None)
      - ("not_found", None)
      - ("conflict", "explanation")
    """
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM authors WHERE id = ?", (author_id,)).fetchone()
        if not row:
            return ("not_found", None)
        # conflict if books exist
        has_books = conn.execute("SELECT 1 FROM books WHERE author_id = ? LIMIT 1", (author_id,)).fetchone()
        if has_books:
            return ("conflict", "Author has books; delete/move books first.")
        conn.execute("DELETE FROM authors WHERE id = ?", (author_id,))
        return ("deleted", None)

# ---------- Books ----------
def create_book(title: str, year: Optional[int], author_id: int, isbn: Optional[str]) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
    """
    Returns (status, book, error):
      - ("created", book, None)
      - ("author_missing", None, msg)
      - ("isbn_conflict", None, msg)
    """
    with connect() as conn:
        author = conn.execute("SELECT 1 FROM authors WHERE id = ?", (author_id,)).fetchone()
        if not author:
            return ("author_missing", None, "author_id does not exist.")
        try:
            cur = conn.execute(
                "INSERT INTO books(title, year, author_id, isbn) VALUES(?, ?, ?, ?)",
                (title, year, author_id, isbn),
            )
        except sqlite3.IntegrityError as e:
            # isbn uniqueness conflict
            return ("isbn_conflict", None, f"Integrity error: {e}")
        book_id = cur.lastrowid
        row = conn.execute("""
            SELECT b.*, a.name AS author_name
            FROM books b JOIN authors a ON a.id = b.author_id
            WHERE b.id = ?
        """, (book_id,)).fetchone()
        return ("created", row_to_dict(row), None)

def get_book(book_id: int) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("""
            SELECT b.*, a.name AS author_name
            FROM books b JOIN authors a ON a.id = b.author_id
            WHERE b.id = ?
        """, (book_id,)).fetchone()
        return row_to_dict(row) if row else None

def list_books(
    q: Optional[str],
    author_id: Optional[int],
    year_from: Optional[int],
    year_to: Optional[int],
    limit: int,
    offset: int
) -> Dict[str, Any]:
    where = []
    params: List[Any] = []

    if q:
        where.append("LOWER(b.title) LIKE ?")
        params.append(f"%{q.lower()}%")
    if author_id is not None:
        where.append("b.author_id = ?")
        params.append(author_id)
    if year_from is not None:
        where.append("b.year >= ?")
        params.append(year_from)
    if year_to is not None:
        where.append("b.year <= ?")
        params.append(year_to)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with connect() as conn:
        total = conn.execute(f"""
            SELECT COUNT(*) AS c
            FROM books b
            {where_sql}
        """, params).fetchone()["c"]

        rows = conn.execute(f"""
            SELECT b.*, a.name AS author_name
            FROM books b JOIN authors a ON a.id = b.author_id
            {where_sql}
            ORDER BY b.id ASC
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [row_to_dict(r) for r in rows],
        }

def update_book(book_id: int, title: str, year: Optional[int], author_id: int, isbn: Optional[str]) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
    """
    Returns (status, book, error):
      - ("updated", book, None)
      - ("not_found", None, None)
      - ("author_missing", None, msg)
      - ("isbn_conflict", None, msg)
    """
    with connect() as conn:
        exists = conn.execute("SELECT 1 FROM books WHERE id = ?", (book_id,)).fetchone()
        if not exists:
            return ("not_found", None, None)

        author = conn.execute("SELECT 1 FROM authors WHERE id = ?", (author_id,)).fetchone()
        if not author:
            return ("author_missing", None, "author_id does not exist.")

        try:
            conn.execute(
                "UPDATE books SET title = ?, year = ?, author_id = ?, isbn = ? WHERE id = ?",
                (title, year, author_id, isbn, book_id),
            )
        except sqlite3.IntegrityError as e:
            return ("isbn_conflict", None, f"Integrity error: {e}")

        row = conn.execute("""
            SELECT b.*, a.name AS author_name
            FROM books b JOIN authors a ON a.id = b.author_id
            WHERE b.id = ?
        """, (book_id,)).fetchone()
        return ("updated", row_to_dict(row), None)

def delete_book(book_id: int) -> bool:
    with connect() as conn:
        exists = conn.execute("SELECT 1 FROM books WHERE id = ?", (book_id,)).fetchone()
        if not exists:
            return False
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return True