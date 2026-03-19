import express from "express";
import cors from "cors";
import "./db.js";

import dashboardRoutes from "./routes/dashboard.js";
import favoritesRoutes from "./routes/favorites.js";
import booksRoutes from "./routes/books.js";

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.get("/api/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

app.use("/api/dashboard", dashboardRoutes);
app.use("/api/favorites", favoritesRoutes);
app.use("/api/manage-books", booksRoutes);

app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(PORT, () => {
  console.log(`Backend running at http://localhost:${PORT}`);
});