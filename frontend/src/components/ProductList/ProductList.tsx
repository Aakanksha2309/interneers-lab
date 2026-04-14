/**
 * Displays list of products in a grid.
 * Shows an empty state if no products are available.
 */
import React from "react";
import ProductCard from "../ProductCard/Product";
import { Product } from "../../type";
import "./ProductList.css";
import { FaBoxOpen } from "react-icons/fa";

interface ProductListProps {
  products: Product[];
}

const ProductList = ({ products }: ProductListProps) => {
  return (
    <main className="inventory-container">
      <header className="list-header">
        <div className="header-content">
          <h2>Product Inventory</h2>
          {/* total product count */}
          <p className="product-count">
            Showing<span>{products.length}</span>items
          </p>
        </div>
      </header>

      {products.length > 0 ? (
        <div className="product-grid">
          {/* render each product card */}
          {products.map((product) => (
            <ProductCard key={product.id} {...product} />
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
    </main>
  );
};

export default ProductList;
