import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { getCategories, createCategory, updateCategory } from "../../services/categoryService";
import "./Admin.css";

function CategoryForm() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: "", slug: "" });
  const [loading, setLoading] = useState(isEditMode);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isEditMode) return;

    async function loadCategory() {
      try {
        const categories = await getCategories();
        const existing = categories.find((c) => c.id === Number(id));
        if (!existing) {
          setError("Category not found.");
          return;
        }
        setForm({ name: existing.name, slug: existing.slug });
      } catch {
        setError("Failed to load category.");
      } finally {
        setLoading(false);
      }
    }

    loadCategory();
  }, [id, isEditMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (isEditMode) {
        await updateCategory(id, form);
      } else {
        await createCategory(form.name, form.slug);
      }
      navigate("/admin");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save category.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p className="container">Loading category...</p>;
  }

  return (
    <div className="container admin-page">
      <Link to="/admin" className="admin-back-link">
        ← Back to Dashboard
      </Link>

      <h1 className="admin-title">{isEditMode ? "Edit Category" : "Add Category"}</h1>

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

        <button type="submit" className="admin-btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : isEditMode ? "Update Category" : "Create Category"}
        </button>
      </form>
    </div>
  );
}

export default CategoryForm;