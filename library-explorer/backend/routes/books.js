import express from "express";
import {
  createLocalBook,
  updateLocalBook,
  deleteLocalBook
} from "../services/localApiService.js";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const created = await createLocalBook(req.body);
    res.status(201).json(created);
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({
      error: "Failed to create local book",
      details: err.response?.data || err.message
    });
  }
});

router.put("/:id", async (req, res) => {
  try {
    const updated = await updateLocalBook(req.params.id, req.body);
    res.status(200).json(updated);
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({
      error: "Failed to update local book",
      details: err.response?.data || err.message
    });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    await deleteLocalBook(req.params.id);
    res.status(204).send();
  } catch (err) {
    const status = err.response?.status || 500;
    res.status(status).json({
      error: "Failed to delete local book",
      details: err.response?.data || err.message
    });
  }
});

export default router;