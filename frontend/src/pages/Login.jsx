import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser, getCurrentUser } from "../services/authService";
import { useAuth } from "../context/useAuth";
import "./Auth.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const { access_token } = await loginUser(email, password);
      localStorage.setItem("access_token", access_token); // api.js interceptor ko turant milna chahiye
      const userData = await getCurrentUser();
      login(access_token, userData);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Log in to continue shopping</p>

        {error && <p className="auth-error">{error}</p>}

        <label className="auth-label">
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label className="auth-label">
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        <Link to="/forgot-password" className="auth-forgot-link">
          Forgot password?
        </Link>

        <button type="submit" className="auth-submit" disabled={submitting}>
          {submitting ? "Logging in..." : "Log In"}
        </button>

        <p className="auth-switch">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </form>
    </div>
  );
}

export default Login;