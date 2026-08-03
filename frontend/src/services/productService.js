import api from "./api";

export const getProducts = async (params = {}) => {
  const response = await api.get("/products/", { params });
  return response.data;
};

export const getProductById = async (id) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};


export const createProduct = async (data) => {
  const response = await api.post("/products/", data);
  return response.data;
};

export const updateProduct = async (id, data) => {
  const response = await api.put(`/products/${id}`, data);
  return response.data;
};

export const deleteProduct = async (id) => {
  await api.delete(`/products/${id}`);
};

export const getProductsWithCount = async (params = {}) => {
  const response = await api.get("/products/", { params });
  const total = Number(response.headers["x-total-count"] || 0);
  return { data: response.data, total };
};
export const getProductsPage = async (skip = 0, limit = 20) => {
  const response = await api.get("/products/", { params: { skip, limit } });
  const totalCount = Number(response.headers["x-total-count"] || 0);
  return { products: response.data, totalCount };
};