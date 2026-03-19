import express from "express";
import db from "../db.js";

const router = express.Router();

router.get("/", (req, res) => {
  try {
    const rows = db
      .prepare("SELECT * FROM favorites ORDER BY created_at DESC")
      .all();
    res.status(200).json(rows);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch favorites" });
  }
});

router.post("/", (req, res) => {
  const { local_book_id, title, author } = req.body;

  if (!title) {
    return res.status(422).json({ error: "Field 'title' is required" });
  }

  try {
    const result = db
      .prepare(
        "INSERT INTO favorites(local_book_id, title, author) VALUES (?, ?, ?)"
      )
      .run(local_book_id ?? null, title, author ?? null);

    const row = db
      .prepare("SELECT * FROM favorites WHERE id = ?")
      .get(result.lastInsertRowid);

    res.status(201).json(row);
  } catch (err) {
    res.status(500).json({ error: "Failed to save favorite" });
  }
});

router.delete("/:id", (req, res) => {
  try {
    const result = db
      .prepare("DELETE FROM favorites WHERE id = ?")
      .run(req.params.id);

    if (result.changes === 0) {
      return res.status(404).json({ error: "Favorite not found" });
    }

    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete favorite" });
  }
});

router.get("/history", (req, res) => {
  try {
    const rows = db
      .prepare("SELECT * FROM search_history ORDER BY created_at DESC LIMIT 20")
      .all();
    res.status(200).json(rows);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch search history" });
  }
});

export default router;