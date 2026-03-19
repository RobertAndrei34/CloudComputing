import express from "express";
import db from "../db.js";
import { getLocalBooks, getLocalBookById } from "../services/localApiService.js";
import { searchOpenLibraryByTitle } from "../services/openLibraryService.js";
import { searchGoogleBooksByTitle } from "../services/googleBooksService.js";

const router = express.Router();

router.get("/books", async (req, res) => {
  try {
    const local = await getLocalBooks();
    res.status(200).json(local);
  } catch (err) {
    res.status(502).json({
      error: "Failed to fetch books from local REST API",
      details: err.message
    });
  }
});

router.get("/books/:id/details", async (req, res) => {
  try {
    const localBook = await getLocalBookById(req.params.id);
    const title = localBook.title;

    const [openLibrary, googleBooks] = await Promise.allSettled([
      searchOpenLibraryByTitle(title),
      searchGoogleBooksByTitle(title)
    ]);

    res.status(200).json({
      localBook,
      openLibrary:
        openLibrary.status === "fulfilled" ? openLibrary.value : null,
      googleBooks:
        googleBooks.status === "fulfilled" ? googleBooks.value : null,
      warnings: [
        ...(openLibrary.status === "rejected"
          ? ["Open Library unavailable"]
          : []),
        ...(googleBooks.status === "rejected"
          ? ["Google Books unavailable"]
          : [])
      ]
    });
  } catch (err) {
    if (err.response?.status === 404) {
      return res.status(404).json({ error: "Book not found in local API" });
    }

    res.status(500).json({
      error: "Failed to aggregate book details",
      details: err.message
    });
  }
});

router.get("/search", async (req, res) => {
  const q = req.query.q?.trim();

  if (!q) {
    return res.status(400).json({ error: "Missing query parameter q" });
  }

  try {
    db.prepare("INSERT INTO search_history(query) VALUES (?)").run(q);

    const [openLibrary, googleBooks, localBooks] = await Promise.allSettled([
      searchOpenLibraryByTitle(q),
      searchGoogleBooksByTitle(q),
      getLocalBooks()
    ]);

    let filteredLocal = [];
    if (localBooks.status === "fulfilled") {
      const items = localBooks.value.items || [];
      filteredLocal = items.filter((b) =>
        b.title.toLowerCase().includes(q.toLowerCase())
      );
    }

    res.status(200).json({
      query: q,
      localMatches: filteredLocal,
      openLibrary: openLibrary.status === "fulfilled" ? openLibrary.value : null,
      googleBooks: googleBooks.status === "fulfilled" ? googleBooks.value : null,
      warnings: [
        ...(openLibrary.status === "rejected"
          ? ["Open Library unavailable"]
          : []),
        ...(googleBooks.status === "rejected"
          ? ["Google Books unavailable"]
          : []),
        ...(localBooks.status === "rejected"
          ? ["Local REST API unavailable"]
          : [])
      ]
    });
  } catch (err) {
    res.status(500).json({
      error: "Search aggregation failed",
      details: err.message
    });
  }
});

export default router;