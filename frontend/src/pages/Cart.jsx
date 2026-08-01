import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { getCart, updateCartItem, removeCartItem } from "../services/cartService";
import "./Cart.css";

function Cart() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    async function loadCart() {
      try {
        const data = await getCart();
        setCart(data);
      } catch {
        setError("Failed to load cart.");
      } finally {
        setLoading(false);
      }
    }

    loadCart();
  }, [user, navigate]);

  const handleQuantityChange = async (itemId, quantity) => {
    if (quantity < 1) return;
    try {
      const updated = await updateCartItem(itemId, quantity);
      setCart(updated);
    } catch {
      setError("Could not update quantity.");
    }
  };

  const handleRemove = async (itemId) => {
    try {
      const updated = await removeCartItem(itemId);
      setCart(updated);
    } catch {
      setError("Could not remove item.");
    }
  };

  if (loading) {
    return <p className="container">Loading cart...</p>;
  }

  if (error) {
    return <p className="container detail-error">{error}</p>;
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container cart-page">
        <h1 className="admin-title">Your Cart</h1>
        <p className="cart-empty">
          Your cart is empty. <Link to="/">Browse products</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="container cart-page">
      <h1 className="admin-title">Your Cart</h1>

      <div className="cart-items">
        {cart.items.map((item) => (
          <div className="cart-item" key={item.id}>
            <div className="cart-item-image">
              {item.product.image_url ? (
                <img src={item.product.image_url} alt={item.product.name} />
              ) : (
                <div className="cart-item-placeholder">No Image</div>
              )}
            </div>

            <div className="cart-item-info">
              <Link to={`/products/${item.product.id}`} className="cart-item-name">
                {item.product.name}
              </Link>
              <p className="cart-item-price">${item.product.price}</p>
            </div>

            <div className="cart-item-quantity">
              <button onClick={() => handleQuantityChange(item.id, item.quantity - 1)}>-</button>
              <span>{item.quantity}</span>
              <button onClick={() => handleQuantityChange(item.id, item.quantity + 1)}>+</button>
            </div>

            <p className="cart-item-subtotal">
              ${(item.product.price * item.quantity).toFixed(2)}
            </p>

            <button className="cart-item-remove" onClick={() => handleRemove(item.id)}>
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <span>Total</span>
        <span className="cart-total-amount">${cart.total}</span>
      </div>
    </div>
  );
}

export default Cart;