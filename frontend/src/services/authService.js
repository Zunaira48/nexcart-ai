import api from "./api";

export const registerUser = async (fullName, email, password) => {
  const response = await api.post("/auth/register", {
    full_name: fullName,
    email,
    password,
  });
  return response.data;
};

export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", { email, password });
  return response.data; // { access_token, token_type }
};

export const getCurrentUser = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};

export const forgotPassword = async (email) => {
  const response = await api.post("/auth/forgot-password", { email });
  return response.data;
};

export const resetPassword = async (token, newPassword) => {
  const response = await api.post("/auth/reset-password", { token, new_password: newPassword });
  return response.data;
};

export const verifyEmail = async (token) => {
  const response = await api.get("/auth/verify-email", { params: { token } });
  return response.data;
};

export const resendVerification = async (email) => {
  const response = await api.post("/auth/resend-verification", { email });
  return response.data;
};