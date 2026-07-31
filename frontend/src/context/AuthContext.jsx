import { useEffect, useState } from "react";
import { AuthContext } from "./AuthContextObject";
import { getCurrentUser } from "../services/authService";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const data = await getCurrentUser();
        setUser(data);
      } catch {
        localStorage.removeItem("access_token");
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  const login = (token, userData) => {
    localStorage.setItem("access_token", token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}