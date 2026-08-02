import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { useCart } from "../context/useCart";
import "./Navbar.css";

function Navbar() {
  const { user, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const menuRef = useRef(null);
  const accountRef = useRef(null);

  // Bahar click hone par dono dropdowns band ho jayen
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
      if (accountRef.current && !accountRef.current.contains(e.target)) {
        setAccountOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setAccountOpen(false);
    navigate("/");
  };

  const handleSwitchAccount = () => {
    logout();
    setAccountOpen(false);
    navigate("/login");
  };

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <div className="navbar-left">
          <Link to="/" className="navbar-logo">
            NexCart <span>AI</span>
          </Link>

          <div className="navbar-menu" ref={menuRef}>
            <button
              className="navbar-icon-btn"
              onClick={() => setMenuOpen((open) => !open)}
              aria-label="Menu"
            >
              ☰
            </button>
            {menuOpen && (
              <div className="navbar-dropdown">
                <Link to="/" onClick={() => setMenuOpen(false)}>
                  Shop
                </Link>
                {user && (
                  <Link to="/orders" onClick={() => setMenuOpen(false)}>
                    Orders
                  </Link>
                )}
                {user && (
                  <Link to="/wishlist" onClick={() => setMenuOpen(false)}>
                   Wishlist
                  </Link>
                )}
                {user?.role === "admin" && (
                  <Link to="/admin" onClick={() => setMenuOpen(false)}>
                    Admin
                  </Link>
                )}
                <Link to="/settings" onClick={() => setMenuOpen(false)}>
                  Settings
                </Link>
              </div>
            )}
          </div>
        </div>

        <div className="navbar-right">
          {user ? (
            <div className="navbar-account" ref={accountRef}>
              <button
                className="navbar-account-btn"
                onClick={() => setAccountOpen((open) => !open)}
              >
                Hi, {user.full_name.split(" ")[0]} ▾
              </button>
              {accountOpen && (
                <div className="navbar-dropdown navbar-dropdown-right">
                  <button onClick={handleSwitchAccount}>Log in to another account</button>
                  <button onClick={handleLogout}>Logout</button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login">Login</Link>
          )}

          <Link to="/cart" className="navbar-cart-link">
            Cart{itemCount > 0 && <span className="navbar-cart-badge">{itemCount}</span>}
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Navbar;