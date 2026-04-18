/**
 * Controls which page is shown and ties main components together.
 */
import React, { useState, useEffect, useCallback } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar/Navbar";
import ProductList from "./components/ProductList/ProductList";
import StatsCards from "./components/StatsCard/StatsCards";
import ProductPage from "./components/ProductPage/ProductPage";
import { fetchInventory, fetchCategories } from "./services/api";
import { Product, PaginatedResponse } from "type";

function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadAllData = useCallback(async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      const [prodRes, catRes] = await Promise.all([
        fetchInventory(page),
        fetchCategories(),
      ]);

      console.log("Category response:", catRes);
      console.log("Product response:", prodRes);

      setProducts(prodRes?.data || []);
      setTotalPages(prodRes?.pagination?.total_pages || 1);
      setCurrentPage(prodRes?.pagination?.current_page || 1);
      setCategories(Array.isArray(catRes) ? catRes : (catRes.data ?? [])); // Store real categories from Django
      setTotalItems(prodRes?.pagination?.total_items || 0);
    } catch (err) {
      console.error("Fetch error:", err);
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    loadAllData(1);
  }, [loadAllData]);

  if (loading && products.length === 0)
    return <div className="loading">Syncing with Django...</div>;
  if (error) return <div className="error">{error}</div>;
  return (
    <BrowserRouter>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
                <div className="dashboard-view">
                  <h1>Inventory Dashboard</h1>

                  <StatsCards products={products} />
                  <ProductList
                    products={products}
                    categories={categories}
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={loadAllData}
                    onDeleteSuccess={() => loadAllData(currentPage)}
                  />
                </div>
              }
            />
            <Route
              path="/product/:id"
              element={<ProductPage categories={categories} />}
            />
            <Route path="/add-product" element={<h1> Add New Product</h1>} />
            <Route
              path="/about-us"
              element={
                <section>
                  <h1>About InvTrack</h1>
                  <p>This system helps you manage stock with ease.</p>
                </section>
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
