import { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getCategories } from "../services/categoryService";
import ProductCard from "../components/ProductCard";
import {
  getProductsWithCount,
  smartSearchProducts,
  getRecommendations,
} from "../services/productService";
import { getSearchHistory, addSearchQuery } from "../utils/searchHistory";
import "./Home.css";

const PAGE_SIZE = 20;

function Home() {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  const [categories, setCategories] = useState([]);
  const [searchInput, setSearchInput] = useState("");
  const [listening, setListening] = useState(false);
  const resultsRef = useRef(null);

  const [filters, setFilters] = useState(() => ({
    search: "",
    categoryId: location.state?.categoryId ?? null,
    categoryName: location.state?.categoryName ?? null,
  }));

  const [now] = useState(() => Date.now());
  const [recommendations, setRecommendations] = useState([]);
  const recommendationsRef = useRef([]);

  const handleMicClick = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Ye browser voice search support nahi karta. Chrome try karo.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setSearchInput(transcript);
      setFilters({ search: transcript.trim(), categoryId: null, categoryName: null });
      addSearchQuery(transcript.trim());
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    recognition.start();
  };

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
        const sorted = [...withCounts].sort((a, b) => b.productCount - a.productCount);
        setCategories(sorted);
      } catch (err) {
        console.error("Failed to load categories", err);
      }
    }
    loadCategories();
  }, []);

  useEffect(() => {
    if (location.state?.categoryId) {
      window.history.replaceState({}, document.title); // state clear, back-button clean rahe
    }
  }, [location.state]);

  // First page of products — reloads (from scratch) whenever search or category filter changes
  useEffect(() => {
    async function loadProducts() {
      setLoading(true);
      try {
        if (filters.search) {
          // Smart search — semantic match, local model se, saara result ek sath aata hai
          const data = await smartSearchProducts(filters.search);
          setProducts(data);
          setTotal(data.length);
        } else {
          const { data, total } = await getProductsWithCount({
            category_id: filters.categoryId || undefined,
            skip: 0,
            limit: PAGE_SIZE,
          });
          setProducts(data);
          setTotal(total);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
  }, [filters]);

  // Recommendations — sirf tab dikhengi jab koi search/category filter active na ho
  useEffect(() => {
    const history = getSearchHistory();
    if (!filters.search && !filters.categoryId && history.length > 0) {
      getRecommendations(history)
        .then((data) => {
          recommendationsRef.current = data;
          setRecommendations(data);
        })
        .catch(() => {
          recommendationsRef.current = [];
          setRecommendations([]);
        });
    } else if (recommendationsRef.current.length > 0) {
      recommendationsRef.current = [];
      setRecommendations([]);
    }
  }, [filters]);

  const handleLoadMore = async () => {
    if (filters.search) return;
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
    addSearchQuery(searchInput.trim());
    resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
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
              className="hero-search-input"
              placeholder="Search for laptops, headphones, and more..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button
              type="button"
              className="hero-mic-btn"
              onClick={handleMicClick}
              aria-label="Search by voice"
            >
              {listening ? "🔴" : "🎤"}
            </button>
            <button type="submit" className="hero-search-btn">
              Search
            </button>
          </form>
        </div>
      </section>

      {recommendations.length > 0 && (
        <section className="categories-rail">
          <h2 className="section-heading">Recommended for you</h2>
          <div className="product-grid">
            {recommendations.map((product) => (
              <ProductCard key={product.id} product={product} isNew={false} />
            ))}
          </div>
        </section>
      )}

      <div className="container">
        {/* ---------------- Categories ---------------- */}
        {categories.length > 0 && (
          <section className="categories-rail">
            <h2 className="section-heading">Shop by category</h2>
            <div className="categories-grid">
              {categories.slice(0, 9).map((category) => (
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
              {categories.length > 9 && (
                <button className="category-tile category-tile-more" onClick={() => navigate("/categories")}>
                  <span className="category-tile-name">More categories</span>
                  <span className="category-tile-count">{categories.length - 9} more →</span>
                </button>
              )}
            </div>
          </section>
        )}

        {/* ---------------- Product Grid ---------------- */}
        <section className="products-section" ref={resultsRef}>
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