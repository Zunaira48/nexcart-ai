import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getOrderById } from "../services/orderService";
import "./Orders.css";

function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadOrder() {
      try {
        const data = await getOrderById(id);
        setOrder(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadOrder();
  }, [id]);

  if (loading) return <p className="container">Loading order...</p>;
  if (error) return <p className="container detail-error">{error}</p>;

  return (
    <div className="container orders-page">
      <Link to="/orders" className="admin-back-link">
        ← Back to Orders
      </Link>

      <h1 className="admin-title">Order #{order.id}</h1>
      <p className="order-detail-meta">
        Placed on {new Date(order.created_at).toLocaleDateString()} ·{" "}
        <span className={`order-status order-status-${order.status}`}>{order.status}</span>
      </p>

      <div className="order-items">
        {order.items.map((item) => (
          <div className="order-item-row" key={item.id}>
            <div>
              <span className="order-item-name">{item.product_name}</span>
              <p className="order-item-price">
                ${item.unit_price} each × {item.quantity}
              </p>
            </div>
            <p className="order-item-subtotal">
              ${(item.unit_price * item.quantity).toFixed(2)}
            </p>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <span>Total</span>
        <span className="cart-total-amount">${order.total}</span>
      </div>
    </div>
  );
}

export default OrderDetail;