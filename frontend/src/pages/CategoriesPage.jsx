import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCategories } from "../services/categoryService";
import { getProductsWithCount } from "../services/productService";
import "./Home.css";
import "./CategoriesPage.css";

function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const categoryData = await getCategories();
        const withCounts = await Promise.all(
          categoryData.map(async (category) => {
            const { total } = await getProductsWithCount({ category_id: category.id, limit: 1 });
            return { ...category, productCount: total };
          })
        );
        withCounts.sort((a, b) => b.productCount - a.productCount);
        setCategories(withCounts);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const goToCategory = (category) => {
    navigate("/", { state: { categoryId: category.id, categoryName: category.name } });
  };

  return (
    <div className="categories-page container">
      <h1 className="section-heading">All categories</h1>
      {loading && <p className="home-status">Loading categories...</p>}
      {!loading && (
        <div className="categories-grid categories-grid-full">
          {categories.map((category) => (
            <button
              key={category.id}
              className="category-tile"
              onClick={() => goToCategory(category)}
            >
              <span className="category-tile-name">{category.name}</span>
              <span className="category-tile-count">
                {category.productCount} {category.productCount === 1 ? "item" : "items"}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default CategoriesPage;