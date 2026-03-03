import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Optional, Tuple

import db

API_PREFIX = "/api"

def json_response(handler: BaseHTTPRequestHandler, status: int, payload: Optional[Dict[str, Any]] = None) -> None:
    body = b""
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)
    else:
        handler.send_response(status)
        handler.end_headers()

def error(handler: BaseHTTPRequestHandler, status: int, code: str, message: str) -> None:
    json_response(handler, status, {"error": {"code": code, "message": message}})

def parse_json_body(handler: BaseHTTPRequestHandler) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    ctype = handler.headers.get("Content-Type", "")
    if "application/json" not in ctype:
        return None, "unsupported_media_type"

    length = handler.headers.get("Content-Length")
    if not length:
        return None, "empty_body"
    try:
        raw = handler.rfile.read(int(length))
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            return None, "invalid_json_object"
        return data, None
    except Exception:
        return None, "invalid_json"

def to_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None

def add_links_book(b: Dict[str, Any]) -> Dict[str, Any]:
    book_id = b.get("id")
    b["_links"] = {
        "self": {"href": f"{API_PREFIX}/books/{book_id}"},
        "collection": {"href": f"{API_PREFIX}/books"},
        "author": {"href": f"{API_PREFIX}/authors/{b.get('author_id')}"},
    }
    return b

def add_links_author(a: Dict[str, Any]) -> Dict[str, Any]:
    author_id = a.get("id")
    a["_links"] = {
        "self": {"href": f"{API_PREFIX}/authors/{author_id}"},
        "create_book": {"href": f"{API_PREFIX}/books"},
    }
    return a

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        # logs
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == f"{API_PREFIX}/books":
            qs = parse_qs(parsed.query)

            q = qs.get("q", [None])[0]
            author_id = to_int(qs.get("author_id", [None])[0])
            year_from = to_int(qs.get("year_from", [None])[0])
            year_to = to_int(qs.get("year_to", [None])[0])

            limit = to_int(qs.get("limit", ["20"])[0]) or 20
            offset = to_int(qs.get("offset", ["0"])[0]) or 0
            limit = max(1, min(limit, 100))
            offset = max(0, offset)

            result = db.list_books(q, author_id, year_from, year_to, limit, offset)
            result["items"] = [add_links_book(b) for b in result["items"]]
            json_response(self, 200, result)
            return

        if path.startswith(f"{API_PREFIX}/books/"):
            book_id = to_int(path.split("/")[-1])
            if book_id is None:
                error(self, 400, "bad_request", "Invalid book id.")
                return
            book = db.get_book(book_id)
            if not book:
                error(self, 404, "not_found", "Book not found.")
                return
            json_response(self, 200, add_links_book(book))
            return

        error(self, 404, "not_found", "Route not found.")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == f"{API_PREFIX}/authors":
            data, err = parse_json_body(self)
            if err == "unsupported_media_type":
                error(self, 415, "unsupported_media_type", "Use Content-Type: application/json.")
                return
            if err:
                error(self, 400, "bad_request", "Invalid or empty JSON body.")
                return

            name = data.get("name")
            country = data.get("country")
            if not isinstance(name, str) or not name.strip():
                error(self, 422, "validation_error", "Field 'name' is required (string).")
                return
            if country is not None and not isinstance(country, str):
                error(self, 422, "validation_error", "Field 'country' must be a string or null.")
                return

            author = db.create_author(name.strip(), country)
            author = add_links_author(author)
            # 201 Created
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Location", f"{API_PREFIX}/authors/{author['id']}")
            body = json.dumps(author, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == f"{API_PREFIX}/books":
            data, err = parse_json_body(self)
            if err == "unsupported_media_type":
                error(self, 415, "unsupported_media_type", "Use Content-Type: application/json.")
                return
            if err:
                error(self, 400, "bad_request", "Invalid or empty JSON body.")
                return

            title = data.get("title")
            year = data.get("year")
            author_id = data.get("author_id")
            isbn = data.get("isbn")

            if not isinstance(title, str) or not title.strip():
                error(self, 422, "validation_error", "Field 'title' is required (string).")
                return

            if year is not None:
                if not isinstance(year, int):
                    error(self, 422, "validation_error", "Field 'year' must be an integer or null.")
                    return

            if not isinstance(author_id, int):
                error(self, 422, "validation_error", "Field 'author_id' is required (integer).")
                return

            if isbn is not None and not isinstance(isbn, str):
                error(self, 422, "validation_error", "Field 'isbn' must be a string or null.")
                return

            status, book, msg = db.create_book(title.strip(), year, author_id, isbn)
            if status == "author_missing":
                error(self, 422, "validation_error", msg or "Invalid author_id.")
                return
            if status == "isbn_conflict":
                error(self, 409, "conflict", msg or "ISBN must be unique.")
                return

            book = add_links_book(book)  # type: ignore
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Location", f"{API_PREFIX}/books/{book['id']}")
            body = json.dumps(book, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        error(self, 404, "not_found", "Route not found.")

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # PUT /api/authors/{id}
        if path.startswith(f"{API_PREFIX}/authors/"):
            author_id = to_int(path.split("/")[-1])
            if author_id is None:
                error(self, 400, "bad_request", "Invalid author id.")
                return

            data, err = parse_json_body(self)
            if err == "unsupported_media_type":
                error(self, 415, "unsupported_media_type", "Use Content-Type: application/json.")
                return
            if err:
                error(self, 400, "bad_request", "Invalid or empty JSON body.")
                return

            name = data.get("name")
            country = data.get("country")
            if not isinstance(name, str) or not name.strip():
                error(self, 422, "validation_error", "Field 'name' is required (string).")
                return
            if country is not None and not isinstance(country, str):
                error(self, 422, "validation_error", "Field 'country' must be a string or null.")
                return

            updated = db.update_author(author_id, name.strip(), country)
            if not updated:
                error(self, 404, "not_found", "Author not found.")
                return
            json_response(self, 200, add_links_author(updated))
            return

        # PUT /api/books/{id}
        if path.startswith(f"{API_PREFIX}/books/"):
            book_id = to_int(path.split("/")[-1])
            if book_id is None:
                error(self, 400, "bad_request", "Invalid book id.")
                return

            data, err = parse_json_body(self)
            if err == "unsupported_media_type":
                error(self, 415, "unsupported_media_type", "Use Content-Type: application/json.")
                return
            if err:
                error(self, 400, "bad_request", "Invalid or empty JSON body.")
                return

            title = data.get("title")
            year = data.get("year")
            author_id = data.get("author_id")
            isbn = data.get("isbn")

            if not isinstance(title, str) or not title.strip():
                error(self, 422, "validation_error", "Field 'title' is required (string).")
                return
            if year is not None and not isinstance(year, int):
                error(self, 422, "validation_error", "Field 'year' must be an integer or null.")
                return
            if not isinstance(author_id, int):
                error(self, 422, "validation_error", "Field 'author_id' is required (integer).")
                return
            if isbn is not None and not isinstance(isbn, str):
                error(self, 422, "validation_error", "Field 'isbn' must be a string or null.")
                return

            status, book, msg = db.update_book(book_id, title.strip(), year, author_id, isbn)
            if status == "not_found":
                error(self, 404, "not_found", "Book not found.")
                return
            if status == "author_missing":
                error(self, 422, "validation_error", msg or "Invalid author_id.")
                return
            if status == "isbn_conflict":
                error(self, 409, "conflict", msg or "ISBN must be unique.")
                return

            json_response(self, 200, add_links_book(book))  # type: ignore
            return

        error(self, 404, "not_found", "Route not found.")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith(f"{API_PREFIX}/books/"):
            book_id = to_int(path.split("/")[-1])
            if book_id is None:
                error(self, 400, "bad_request", "Invalid book id.")
                return
            ok = db.delete_book(book_id)
            if not ok:
                error(self, 404, "not_found", "Book not found.")
                return
            # 204 No Content (idempotent delete semantics)
            json_response(self, 204, None)
            return

        if path.startswith(f"{API_PREFIX}/authors/"):
            author_id = to_int(path.split("/")[-1])
            if author_id is None:
                error(self, 400, "bad_request", "Invalid author id.")
                return
            result, msg = db.delete_author(author_id)
            if result == "not_found":
                error(self, 404, "not_found", "Author not found.")
                return
            if result == "conflict":
                error(self, 409, "conflict", msg or "Conflict.")
                return
            json_response(self, 204, None)
            return

        error(self, 404, "not_found", "Route not found.")

def run(host: str = "127.0.0.1", port: int = 8080) -> None:
    db.init_db()
    httpd = HTTPServer((host, port), Handler)
    print(f"Listening on http://{host}:{port}{API_PREFIX}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()