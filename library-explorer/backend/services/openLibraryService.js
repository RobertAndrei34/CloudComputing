import axios from "axios";

export async function searchOpenLibraryByTitle(title) {
  const response = await axios.get("https://openlibrary.org/search.json", {
    params: { title }
  });

  const docs = response.data.docs || [];
  if (docs.length === 0) return null;

  const first = docs[0];

  return {
    title: first.title || null,
    author: first.author_name?.[0] || null,
    firstPublishYear: first.first_publish_year || null,
    subjects: first.subject?.slice(0, 5) || [],
    coverUrl: first.cover_i
      ? `https://covers.openlibrary.org/b/id/${first.cover_i}-M.jpg`
      : null
  };
}