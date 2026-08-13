const KEY = "nexcart_search_history";
const MAX_ITEMS = 5;

export const getSearchHistory = () => {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

export const addSearchQuery = (query) => {
  if (!query || !query.trim()) return;
  const history = getSearchHistory().filter((q) => q !== query);
  history.unshift(query);
  localStorage.setItem(KEY, JSON.stringify(history.slice(0, MAX_ITEMS)));
};