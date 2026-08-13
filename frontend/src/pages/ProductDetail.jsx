import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getProductById } from "../services/productService";
import "./ProductDetail.css";
import { addToCart } from "../services/cartService";
import { useAuth } from "../context/useAuth";
import { useCart } from "../context/useCart";
import { useWishlist } from "../context/useWishlist";
import { getProductReviews, submitReview, getReviewSummary } from "../services/reviewService";
import StarRating from "../components/StarRating";


function ProductDetail({ id }) {
  const [state, setState] = useState({ product: null, loading: true, error: null });
  const { product, loading, error } = state;
  const { user } = useAuth();
  const { setCart } = useCart();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const navigate = useNavigate();

  const [adding, setAdding] = useState(false);
  const [addMessage, setAddMessage] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [myRating, setMyRating] = useState(0);
  const [myComment, setMyComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getProductById(id)
      .then((data) => setState({ product: data, loading: false, error: null }))
      .catch((err) => setState({ product: null, loading: false, error: err.message }));
  }, [id]);

  useEffect(() => {
    getProductReviews(id)
      .then((data) => {
        setReviews(data);
        if (data.length >= 3) {
          setSummaryLoading(true);
          getReviewSummary(id)
            .then(setSummary)
            .catch(() => setSummary(null))
            .finally(() => setSummaryLoading(false));
        }
      })
      .finally(() => setReviewsLoading(false));
  }, [id]);

  if (loading) {
    return <p className="container detail-status">Loading product...</p>;
  }

  if (error) {
    return <p className="container detail-status detail-error">Error: {error}</p>;
  }

  // Is point tak `product` guaranteed non-null hai — is liye product.id
  // safely use ho sakta hai.
  const wishlisted = isWishlisted(product.id);

  const handleWishlistToggle = () => {
    if (!user) {
      navigate("/login");
      return;
    }
    toggleWishlist(product.id);
  };

  const handleAddToCart = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    setAdding(true);
    setAddMessage(null);
    try {
      const updated = await addToCart(product.id, 1);
      setCart(updated);
      setAddMessage("Added to cart!");
    } catch {
      setAddMessage("Could not add to cart.");
    } finally {
      setAdding(false);
    }
  };

  const handleSubmitReview = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (myRating === 0) return;

    setSubmitting(true);
    try {
      await submitReview(product.id, myRating, myComment || null);
      const updated = await getProductReviews(id);
      setReviews(updated);
      setMyRating(0);
      setMyComment("");
    } catch {
      // silently fail for now — could show an error message here later
    } finally {
      setSubmitting(false);
    }
  };

  const averageRating =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
      : null;

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

          <div className="detail-actions">
            <button className="detail-add-to-cart" onClick={handleAddToCart} disabled={adding}>
              {adding ? "Adding..." : "Add to Cart"}
            </button>
            <button className="detail-wishlist-btn" onClick={handleWishlistToggle}>
              {wishlisted ? "♥ Wishlisted" : "♡ Add to Wishlist"}
            </button>
          </div>
          {addMessage && <p className="detail-add-message">{addMessage}</p>}
        </div>
      </div>

      <div className="reviews-section">
        <h2 className="reviews-heading">
          Customer Reviews
          {averageRating && (
            <span className="reviews-average">
              <StarRating value={Math.round(averageRating)} readOnly /> {averageRating} out of 5
              ({reviews.length} {reviews.length === 1 ? "review" : "reviews"})
            </span>
          )}
        </h2>

        {summaryLoading && <p className="detail-status">AI summary ban rahi hai...</p>}
        {summary && (
          <div className="ai-summary-card">
            <p className="ai-summary-badge">✨ AI Summary</p>
            <p className="ai-summary-text">{summary.summary}</p>
            {summary.pros.length > 0 && (
              <div className="ai-summary-list">
                <strong>👍 Customers liked:</strong>
                <ul>
                  {summary.pros.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
            {summary.cons.length > 0 && (
              <div className="ai-summary-list">
                <strong>👎 Common concerns:</strong>
                <ul>
                  {summary.cons.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {user && (
          <div className="review-form">
            <p className="review-form-label">Leave a review</p>
            <StarRating value={myRating} onChange={setMyRating} />
            <textarea
              className="review-textarea"
              placeholder="Share your thoughts about this product (optional)"
              value={myComment}
              onChange={(e) => setMyComment(e.target.value)}
            />
            <button
              className="detail-add-to-cart"
              onClick={handleSubmitReview}
              disabled={myRating === 0 || submitting}
            >
              {submitting ? "Submitting..." : "Submit Review"}
            </button>
          </div>
        )}

        {reviewsLoading ? (
          <p className="detail-status">Loading reviews...</p>
        ) : reviews.length === 0 ? (
          <p className="detail-status">No reviews yet. Be the first to review this product.</p>
        ) : (
          <div className="reviews-list">
            {reviews.map((review) => (
              <div className="review-item" key={review.id}>
                <div className="review-item-header">
                  <StarRating value={review.rating} readOnly />
                  <span className="review-author">{review.user.full_name}</span>
                  <span className="review-date">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
                {review.comment && <p className="review-comment">{review.comment}</p>}
              </div>
            ))}
          </div>
        )}
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