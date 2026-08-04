import { useEffect, useState } from "react";
import { getProductsWithCount } from "../services/productService";
import { getCategories } from "../services/categoryService";
import ProductCard from "../components/ProductCard";
import "./Home.css";

const PAGE_SIZE = 20;

function Home() {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  const [categories, setCategories] = useState([]);
  const [searchInput, setSearchInput] = useState("");
  const [filters, setFilters] = useState({ search: "", categoryId: null, categoryName: null });

  const [now] = useState(() => Date.now());

  // Categories with real product counts — loaded once
  useEffect(() => {
    async function loadCategories() {
      try {
        const categoryData = await getCategories();
        const withCounts = await Promise.all(
          categoryData.map(async (category) => {
            const { total } = await getProductsWithCount({ category_id: category.id, limit: 1 });
            return { ...category, productCount: total };
          })
        );
        setCategories(withCounts);
      } catch {
        // The category rail is a nice-to-have; the page still works without it.
      }
    }
    loadCategories();
  }, []);

  // First page of products — reloads (from scratch) whenever search or category filter changes
  useEffect(() => {
    async function loadProducts() {
      try {
        const { data, total } = await getProductsWithCount({
          search: filters.search || undefined,
          category_id: filters.categoryId || undefined,
          skip: 0,
          limit: PAGE_SIZE,
        });
        setProducts(data);
        setTotal(total);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    loadProducts();
  }, [filters]);

  const handleLoadMore = async () => {
    setLoadingMore(true);
    try {
      const { data } = await getProductsWithCount({
        search: filters.search || undefined,
        category_id: filters.categoryId || undefined,
        skip: products.length,
        limit: PAGE_SIZE,
      });
      setProducts((prev) => [...prev, ...data]);
    } catch {
      // If "load more" fails, just leave the existing products visible.
    } finally {
      setLoadingMore(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setFilters({ search: searchInput.trim(), categoryId: null, categoryName: null });
  };

  const handleCategoryClick = (category) => {
    setSearchInput("");
    setFilters({ search: "", categoryId: category.id, categoryName: category.name });
  };

  const clearFilters = () => {
    setSearchInput("");
    setFilters({ search: "", categoryId: null, categoryName: null });
  };

  const isRecent = (createdAt) => {
    const days = (now - new Date(createdAt)) / (1000 * 60 * 60 * 24);
    return days <= 7;
  };

  const hasActiveFilter = Boolean(filters.search || filters.categoryId);
  const hasMore = products.length < total;
  const heading = filters.categoryName
    ? filters.categoryName
    : filters.search
    ? `Results for "${filters.search}"`
    : "All products";

  return (
    <div className="home-page">
      {/* ---------------- Hero ---------------- */}
      <section className="hero">
        <div className="container hero-inner">
          <span className="hero-eyebrow">Next generation e-commerce</span>
          <h1 className="hero-title">Everything you need, in one place.</h1>
          <p className="hero-subtitle">
            Real inventory, real prices, updated the moment they change.
          </p>

          <form className="hero-search" onSubmit={handleSearchSubmit}>
            <input
              type="text"
              placeholder="Search for laptops, headphones, and more..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button type="submit">Search</button>
          </form>
        </div>
      </section>

      <div className="container">
        {/* ---------------- Categories ---------------- */}
        {categories.length > 0 && (
          <section className="categories-rail">
            <h2 className="section-heading">Shop by category</h2>
            <div className="categories-grid">
              {categories.map((category) => (
                <button
                  key={category.id}
                  className={`category-tile ${
                    filters.categoryId === category.id ? "category-tile-active" : ""
                  }`}
                  onClick={() => handleCategoryClick(category)}
                >
                  <span className="category-tile-name">{category.name}</span>
                  <span className="category-tile-count">
                    {category.productCount} {category.productCount === 1 ? "item" : "items"}
                  </span>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* ---------------- Product Grid ---------------- */}
        <section className="products-section">
          <div className="products-section-header">
            <h2 className="section-heading">{heading}</h2>
            {hasActiveFilter && (
              <button className="clear-search" onClick={clearFilters}>
                Clear filter
              </button>
            )}
          </div>

          {loading && <p className="home-status">Loading products...</p>}
          {error && <p className="home-status home-error">Error: {error}</p>}

          {!loading && !error && products.length === 0 && (
            <p className="home-status">No products match this filter.</p>
          )}

          {!loading && !error && products.length > 0 && (
            <>
              <p className="products-count">
                Showing {products.length} of {total} products
              </p>
              <div className="product-grid">
                {products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    isNew={isRecent(product.created_at)}
                  />
                ))}
              </div>

              {hasMore && (
                <div className="load-more-wrapper">
                  <button
                    className="load-more-btn"
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                  >
                    {loadingMore ? "Loading..." : "Load More"}
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default Home;