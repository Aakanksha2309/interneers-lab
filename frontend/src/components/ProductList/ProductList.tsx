/**
 * Displays list of products in a grid.
 * Shows an empty state if no products are available.
 */
import React from "react";
import ProductCard from "../ProductCard/Product";
import { Product, Category } from "../../type";
import "./ProductList.css";
import { FaBoxOpen } from "react-icons/fa";
import { FiPlus } from "react-icons/fi";
import { useNavigate } from "react-router-dom";

interface ProductListProps {
  products: Product[];
  categories: Category[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onDeleteSuccess: () => void;
  selectedIds?: string[];
  onToggleSelect?: (id: string) => void;
}

const ProductList = ({
  products,
  categories,
  currentPage,
  totalPages,
  onPageChange,
  onDeleteSuccess,
  selectedIds,
  onToggleSelect,
}: ProductListProps) => {
  const navigate = useNavigate();

  return (
    <main className="inventory-container">
      <header className="list-header">
        <div className="header-content">
          <div className="title-section">
            <h2>Product Inventory</h2>
            {/* total product count */}
            <p className="product-count">
              Showing<span>{products.length}</span>items
            </p>
          </div>
          <button
            className="add-button"
            onClick={() => navigate("/add-product")}
          >
            <FiPlus /> Add Product
          </button>
        </div>
      </header>

      {products.length > 0 ? (
        <div className="product-grid">
          {/* render each product card */}
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              categories={categories}
              onDeleteSuccess={onDeleteSuccess}
              selectedIds={selectedIds}
              onToggleSelect={onToggleSelect}
            />
          ))}
        </div>
      ) : (
        // empty state when there ar eno products
        <div className="empty-state-container">
          <div className="empty-box">
            <FaBoxOpen />
          </div>
          <h3>No items in inventory</h3>
          <p>
            Couldn't find any products.Try adding a new item or clearing your
            filters
          </p>
        </div>
      )}
      <div className="pagination-bar">
        <button
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
        >
          ← Prev
        </button>

        <span>
          Page {currentPage} of {totalPages}
        </span>

        <button
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
        >
          Next →
        </button>
      </div>
    </main>
  );
};

export default ProductList;
