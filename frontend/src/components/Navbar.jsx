import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import "./Navbar.css";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-logo">
          NexCart <span>AI</span>
        </Link>
        <nav className="navbar-links">
          <Link to="/">Shop</Link>
          <Link to="/cart">Cart</Link>
          {user?.role === "admin" && <Link to="/admin">Admin</Link>}
          {user ? (
            <>
              <span className="navbar-username">Hi, {user.full_name.split(" ")[0]}</span>
              <button className="navbar-logout" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Navbar;