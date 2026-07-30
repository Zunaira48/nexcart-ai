import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getProductById } from "../services/productService";
import "./ProductDetail.css";

function ProductDetail({ id }) {
  const [state, setState] = useState({ product: null, loading: true, error: null });
  const { product, loading, error } = state;

  useEffect(() => {
    getProductById(id)
      .then((data) => setState({ product: data, loading: false, error: null }))
      .catch((err) => setState({ product: null, loading: false, error: err.message }));
  }, [id]);

  if (loading) {
    return <p className="container detail-status">Loading product...</p>;
  }

  if (error) {
    return <p className="container detail-status detail-error">Error: {error}</p>;
  }

  return (
    <div className="container product-detail">
      <Link to="/" className="detail-back-link">
        ← Back to Shop
      </Link>

      <div className="detail-layout">
        <div className="detail-image">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} />
          ) : (
            <div className="detail-image-placeholder">No Image</div>
          )}
        </div>

        <div className="detail-info">
          <span className="detail-category">{product.category.name}</span>
          <h1 className="detail-name">{product.name}</h1>
          <p className="detail-price">${product.price}</p>

          {product.description && (
            <p className="detail-description">{product.description}</p>
          )}

          <button className="detail-add-to-cart">Add to Cart</button>
        </div>
      </div>
    </div>
  );
}

// Ye wrapper URL se :id nikal kar ProductDetail ko `key` ke sath render karta hai.
// Jab id badalta hai, React poora naya component banata hai — is liye state
// khud reset ho jati hai, manually setState karke reset karne ki zaroorat nahi.
function ProductDetailPage() {
  const { id } = useParams();
  return <ProductDetail key={id} id={id} />;
}

export default ProductDetailPage;