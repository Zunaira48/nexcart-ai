import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { getCategories } from "../../services/categoryService";
import { getProductById, createProduct, updateProduct } from "../../services/productService";
import "./Admin.css";

const emptyForm = {
  name: "",
  slug: "",
  description: "",
  price: "",
  stock_quantity: "",
  image_url: "",
  category_id: "",
};

function ProductForm() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function loadFormData() {
      try {
        const categoryData = await getCategories();
        setCategories(categoryData);

        if (isEditMode) {
          const product = await getProductById(id);
          setForm({
            name: product.name,
            slug: product.slug,
            description: product.description || "",
            price: product.price,
            stock_quantity: product.stock_quantity,
            image_url: product.image_url || "",
            category_id: product.category.id,
          });
        }
      } catch {
        setError("Failed to load form data.");
      } finally {
        setLoading(false);
      }
    }

    loadFormData();
  }, [id, isEditMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const payload = {
      ...form,
      price: parseFloat(form.price),
      stock_quantity: parseInt(form.stock_quantity, 10),
      category_id: parseInt(form.category_id, 10),
    };

    try {
      if (isEditMode) {
        await updateProduct(id, payload);
      } else {
        await createProduct(payload);
      }
      navigate("/admin");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save product.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p className="container">Loading product...</p>;
  }

  return (
    <div className="container admin-page">
      <Link to="/admin" className="admin-back-link">
        ← Back to Dashboard
      </Link>

      <h1 className="admin-title">{isEditMode ? "Edit Product" : "Add Product"}</h1>

      {error && <p className="auth-error">{error}</p>}

      <form className="admin-form-page" onSubmit={handleSubmit}>
        <label className="admin-label">
          Name
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>

        <label className="admin-label">
          Slug
          <input
            type="text"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
            required
          />
        </label>

        <label className="admin-label">
          Category
          <select
            value={form.category_id}
            onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            required
          >
            <option value="">Select category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label className="admin-label">
          Price
          <input
            type="number"
            step="0.01"
            value={form.price}
            onChange={(e) => setForm({ ...form, price: e.target.value })}
            required
          />
        </label>

        <label className="admin-label">
          Stock Quantity
          <input
            type="number"
            value={form.stock_quantity}
            onChange={(e) => setForm({ ...form, stock_quantity: e.target.value })}
            required
          />
        </label>

        <label className="admin-label">
          Image URL (optional)
          <input
            type="text"
            value={form.image_url}
            onChange={(e) => setForm({ ...form, image_url: e.target.value })}
          />
        </label>

        <label className="admin-label">
          Description
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>

        <button type="submit" className="admin-btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : isEditMode ? "Update Product" : "Create Product"}
        </button>
      </form>
    </div>
  );
}

export default ProductForm;