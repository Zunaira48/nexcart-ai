import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { useWishlist } from "../context/useWishlist";
import ProductCard from "../components/ProductCard";
import "./Wishlist.css";

function Wishlist() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const { items, loaded } = useWishlist();

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  if (!loaded) {
    return <p className="container">Loading wishlist...</p>;
  }

  if (items.length === 0) {
    return (
      <div className="container wishlist-page">
        <h1 className="admin-title">Your Wishlist</h1>
        <p className="cart-empty">
          Your wishlist is empty. <Link to="/">Browse products</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="container wishlist-page">
      <h1 className="admin-title">Your Wishlist</h1>
      <div className="product-grid">
        {items.map((item) => (
          <ProductCard key={item.id} product={item.product} />
        ))}
      </div>
    </div>
  );
}

export default Wishlist;