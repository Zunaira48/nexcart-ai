import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { useCart } from "../context/useCart";
import { updateCartItem, removeCartItem } from "../services/cartService";
import { checkout } from "../services/orderService";
import "./Cart.css";

function Cart() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const { cart, loaded, setCart, refreshCart } = useCart();
  const [checkingOut, setCheckingOut] = useState(false);
  const [checkoutError, setCheckoutError] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);
  [user, navigate];

  async function handleQuantityChange(itemId, quantity) {
    if (quantity < 1) return;
    const updated = await updateCartItem(itemId, quantity);
    setCart(updated);
  }

  const handleRemove = async (itemId) => {
    const updated = await removeCartItem(itemId);
    setCart(updated);
  };

  const handleCheckout = async () => {
    setCheckingOut(true);
    setCheckoutError(null);
    try {
      const order = await checkout();
      await refreshCart();
      navigate(`/orders/${order.id}`);
    } catch (err) {
      setCheckoutError(err.response?.data?.detail || "Checkout failed.");
    } finally {
      setCheckingOut(false);
    }
  };

  if (!loaded) {
    return <p className="container">Loading cart...</p>;
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

      {checkoutError && <p className="auth-error">{checkoutError}</p>}

      <button className="cart-checkout-btn" onClick={handleCheckout} disabled={checkingOut}>
        {checkingOut ? "Placing order..." : "Place Order"}
      </button>
    </div>
  );
}

export default Cart;