import axios from "axios";

export async function searchGoogleBooksByTitle(title) {
  const response = await axios.get("https://www.googleapis.com/books/v1/volumes", {
    params: { q: `intitle:${title}`, maxResults: 1 }
  });

  const items = response.data.items || [];
  if (items.length === 0) return null;

  const volume = items[0].volumeInfo || {};

  return {
    title: volume.title || null,
    authors: volume.authors || [],
    description: volume.description || null,
    categories: volume.categories || [],
    pageCount: volume.pageCount || null,
    thumbnail: volume.imageLinks?.thumbnail || null,
    previewLink: volume.previewLink || null
  };
}