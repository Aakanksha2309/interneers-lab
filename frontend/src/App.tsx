/**
 * Controls which page is shown and ties main components together.
 */
import React, { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar/Navbar";
import ProductList from "./components/ProductList/ProductList";
import StatsCards from "./components/StatsCard/StatsCards";
import { MOCK_PRODUCTS } from "./mockData";

function App() {
  // Track which page is active (Dashboard is the default)
  const [currentView, setCurrentView] = useState<
    "dashboard" | "add-product" | "about-us"
  >("dashboard");
  // Changes the view based on what was clicked in the Navbar
  const handleNavigation = (view: "dashboard" | "add-product" | "about-us") => {
    setCurrentView(view);
  };

  return (
    <div className="App">
      <Navbar onNavigate={handleNavigation} />
      <main className="main-content">
        {/* Main Dashboard: Shows stats and the product grid */}
        {currentView === "dashboard" && (
          <div className="dashboard-view">
            <h1>Inventory Dashboard</h1>

            <StatsCards products={MOCK_PRODUCTS} />
            <ProductList products={MOCK_PRODUCTS} />
          </div>
        )}
        {/* Temporary view for pages */}
        {currentView === "add-product" && <h1>Add New Product</h1>}
        {currentView === "about-us" && (
          <section>
            <h1>About InvTrack</h1>
            <p>This system helps you manage stock with ease.</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
