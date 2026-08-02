import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAllOrdersAdmin, updateOrderStatus } from "../../services/orderService";
import "./Admin.css";

const STATUS_OPTIONS = ["pending", "processing", "shipped", "delivered", "cancelled"];

function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  const loadOrders = async () => {
    try {
      const data = await getAllOrdersAdmin();
      setOrders(data);
    } catch {
      setError("Failed to load orders.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadOrders();
  }, []);

  const handleStatusChange = async (orderId, newStatus) => {
    setUpdatingId(orderId);
    setError(null);
    try {
      await updateOrderStatus(orderId, newStatus);
      setOrders((prev) =>
        prev.map((order) =>
          order.id === orderId ? { ...order, status: newStatus } : order
        )
      );
    } catch {
      setError("Could not update order status.");
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) return <p className="container">Loading orders...</p>;

  return (
    <div className="container admin-page">
      <Link to="/admin" className="admin-back-link">
        ← Back to Dashboard
      </Link>
      <h1 className="admin-title">Manage Orders</h1>

      {error && <p className="auth-error">{error}</p>}

      <table className="admin-table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Customer</th>
            <th>Total</th>
            <th>Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id}>
              <td>#{order.id}</td>
              <td>
                {order.user.full_name}
                <br />
                <span className="admin-row-subtext">{order.user.email}</span>
              </td>
              <td>${order.total}</td>
              <td>{new Date(order.created_at).toLocaleDateString()}</td>
              <td>
                <select
                  value={order.status}
                  disabled={updatingId === order.id}
                  onChange={(e) => handleStatusChange(order.id, e.target.value)}
                  className={`order-status-select order-status-${order.status}`}
                >
                  {STATUS_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminOrders;