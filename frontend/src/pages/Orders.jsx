import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getOrders } from "../services/orderService";
import "./Orders.css";

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await getOrders();
        setOrders(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, []);

  if (loading) return <p className="container">Loading orders...</p>;
  if (error) return <p className="container detail-error">{error}</p>;

  if (orders.length === 0) {
    return (
      <div className="container orders-page">
        <h1 className="admin-title">Your Orders</h1>
        <p className="cart-empty">
          You haven't placed any orders yet. <Link to="/">Browse products</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="container orders-page">
      <h1 className="admin-title">Your Orders</h1>

      <div className="orders-list">
        {orders.map((order) => (
          <Link to={`/orders/${order.id}`} className="order-row" key={order.id}>
            <div>
              <span className="order-row-id">Order #{order.id}</span>
              <span className="order-row-date">
                {new Date(order.created_at).toLocaleDateString()}
              </span>
            </div>
            <span className={`order-status order-status-${order.status}`}>{order.status}</span>
            <span className="order-row-total">${order.total}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Orders;