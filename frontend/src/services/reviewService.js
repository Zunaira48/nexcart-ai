import api from "./api";

export const getProductReviews = async (productId) => {
  const response = await api.get(`/reviews/product/${productId}`);
  return response.data;
};

export const submitReview = async (productId, rating, comment) => {
  const response = await api.post(`/reviews/product/${productId}`, {
    rating,
    comment,
  });
  return response.data;
};

export const deleteReview = async (reviewId) => {
  await api.delete(`/reviews/${reviewId}`);
};