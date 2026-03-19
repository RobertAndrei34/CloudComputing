import axios from "axios";

const LOCAL_API = "http://127.0.0.1:8080/api";

export async function getLocalBooks() {
  const response = await axios.get(`${LOCAL_API}/books`);
  return response.data;
}

export async function getLocalBookById(id) {
  const response = await axios.get(`${LOCAL_API}/books/${id}`);
  return response.data;
}

export async function createLocalBook(payload) {
  const response = await axios.post(`${LOCAL_API}/books`, payload, {
    headers: { "Content-Type": "application/json" }
  });
  return response.data;
}

export async function updateLocalBook(id, payload) {
  const response = await axios.put(`${LOCAL_API}/books/${id}`, payload, {
    headers: { "Content-Type": "application/json" }
  });
  return response.data;
}

export async function deleteLocalBook(id) {
  await axios.delete(`${LOCAL_API}/books/${id}`);
}