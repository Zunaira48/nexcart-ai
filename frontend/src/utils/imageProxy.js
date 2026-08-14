const API_BASE = import.meta.env.VITE_API_URL.replace(/\/$/, "");
export const proxiedImageUrl = (url) => {
  if (!url) return null;
  return `${API_BASE}/images/proxy?url=${encodeURIComponent(url)}`;
};