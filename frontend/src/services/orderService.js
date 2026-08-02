import api from "./api";

export const checkout = async () => {
  const response = await api.post("/orders/checkout");
  return response.data;
};

export const getOrders = async () => {
  const response = await api.get("/orders/");
  return response.data;
};

export const getOrderById = async (id) => {
  const response = await api.get(`/orders/${id}`);
  return response.data;
};