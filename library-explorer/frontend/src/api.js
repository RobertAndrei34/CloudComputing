import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:3001/api"
});

export async function searchBooks(query) {
  const res = await api.get(`/dashboard/search?q=${encodeURIComponent(query)}`);
  return res.data;
}

export async function getAllLocalBooks() {
  const res = await api.get("/dashboard/books");
  return res.data;
}

export async function getBookDetails(id) {
  const res = await api.get(`/dashboard/books/${id}/details`);
  return res.data;
}

export async function getFavorites() {
  const res = await api.get("/favorites");
  return res.data;
}

export async function addFavorite(payload) {
  const res = await api.post("/favorites", payload);
  return res.data;
}

export async function deleteFavorite(id) {
  await api.delete(`/favorites/${id}`);
}

export async function getHistory() {
  const res = await api.get("/favorites/history");
  return res.data;
}