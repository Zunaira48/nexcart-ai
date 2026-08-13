import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { useWishlist } from "../context/useWishlist";
import { proxiedImageUrl } from "../utils/imageProxy";
import "./ProductCard.css";

function ProductCard({ product, isNew }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const wishlisted = isWishlisted(product.id);
  const [imageFailed, setImageFailed] = useState(false);

  const handleWishlistClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) {
      navigate("/login");
      return;
    }
    toggleWishlist(product.id);
  };

  const showPlaceholder = !product.image_url || imageFailed;

  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className="product-card-image">
        {isNew && <span className="product-card-badge">New</span>}
        <button
          className={`product-card-wishlist ${wishlisted ? "product-card-wishlist-active" : ""}`}
          onClick={handleWishlistClick}
          aria-label="Toggle wishlist"
        >
          {wishlisted ? "♥" : "♡"}
        </button>
        {showPlaceholder ? (
          <div className="product-card-placeholder">{product.name}</div>
        ) : (
          <img
             src={proxiedImageUrl(product.image_url)}
             alt={product.name}
             onError={() => setImageFailed(true)}
/>
        )}
      </div>
      <div className="product-card-body">
        <span className="product-card-category">{product.category.name}</span>
        <h3 className="product-card-name">{product.name}</h3>
        <p className="product-card-price">${product.price}</p>
      </div>
    </Link>
  );
}

export default ProductCard;