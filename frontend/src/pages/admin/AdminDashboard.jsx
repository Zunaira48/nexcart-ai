import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCategories, deleteCategory } from "../../services/categoryService";
import { getProducts, deleteProduct } from "../../services/productService";
import "./Admin.css";

function AdminDashboard() {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [productSearch, setProductSearch] = useState("");

  const loadData = async () => {
    try {
      const [categoryData, productData] = await Promise.all([
        getCategories(),
        getProducts({ limit: 100, search: productSearch || undefined }),
      ]);
      setCategories(categoryData);
      setProducts(productData);
    } catch {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productSearch]);

  const handleDeleteCategory = async (id) => {
    if (!confirm("Delete this category? This cannot be undone.")) return;
    setError(null);
    try {
      await deleteCategory(id);
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete category.");
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!confirm("Delete this product? This cannot be undone.")) return;
    setError(null);
    try {
      await deleteProduct(id);
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete product.");
    }
  };

  if (loading) {
    return <p className="container">Loading dashboard...</p>;
  }

  return (
    <div className="container admin-page">
      <h1 className="admin-title">Admin Dashboard</h1>
      <Link to="/admin/orders" className="admin-btn-secondary" style={{ marginBottom: "2rem", display: "inline-block" }}>
       Manage Orders
      </Link>
      {error && <p className="auth-error">{error}</p>}

      {/* ---------------- Categories ---------------- */}
      <section className="admin-section">
        <div className="admin-section-header">
          <h2>Categories</h2>
          <Link to="/admin/categories/new" className="admin-btn-primary">
            + Add Category
          </Link>
        </div>

        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Slug</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => (
              <tr key={category.id}>
                <td>{category.name}</td>
                <td>{category.slug}</td>
                <td className="admin-row-actions">
                  <Link to={`/admin/categories/${category.id}/edit`}>Edit</Link>
                  <button onClick={() => handleDeleteCategory(category.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ---------------- Products ---------------- */}
      <section className="admin-section">
        <div className="admin-section-header">
          <h2>Products</h2>
          <Link to="/admin/products/new" className="admin-btn-primary">
            + Add Product
          </Link>
        </div>

        <input
          type="text"
          placeholder="Search products by name..."
          value={productSearch}
          onChange={(e) => setProductSearch(e.target.value)}
          className="admin-search-input"
        />

        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.category.name}</td>
                <td>${product.price}</td>
                <td>{product.stock_quantity}</td>
                <td className="admin-row-actions">
                  <Link to={`/admin/products/${product.id}/edit`}>Edit</Link>
                  <button onClick={() => handleDeleteProduct(product.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default AdminDashboard;