/**
 * Displays a single product card with basic info.
 * Also handles opening a modal to show more details.
 */
import React, { useState } from "react";
import "./Product.css";
import { MOCK_CATEGORIES } from "../../mockData";
import { Product as ProductType } from "../../type";
import ProductDetailModal from "../ProductModal/ProductDetailModal";

const Product = (props: ProductType) => {
  // controls modal open/close
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    name,
    category_id,
    warehouse_quantity,
    low_stock_threshold,
    selling_price,
    description,
    brand,
  } = props;

  // find category name from id
  const categoryObject = MOCK_CATEGORIES.find((cat) => cat.id === category_id);
  const categoryName = categoryObject ? categoryObject.title : "Unknown";

  // stock status checks
  const isLowStock =
    warehouse_quantity > 0 && warehouse_quantity <= low_stock_threshold;
  const outOfStock = warehouse_quantity === 0;

  // adding random image based on product name
  const imageUrl = `https://loremflickr.com/600/300/${name.split(" ")[0]}`;

  return (
    <>
      <div className="product-card">
        <div className="image-container">
          {/* gray out the image if the item is not in stock */}
          <img
            src={imageUrl}
            alt={name}
            className={outOfStock ? "grayscale-img" : ""}
          />
          {/* stock label */}
          <span
            className={`stock-badge ${
              outOfStock ? "out-of-stock" : isLowStock ? "low" : "in-stock"
            }`}
          >
            {outOfStock ? "Out of Stock" : `${warehouse_quantity} in stock`}
          </span>
        </div>

        <div className="product-info">
          <div className="info-header">
            <h3 className={`product-name ${outOfStock ? "faded-text" : ""}`}>
              {name}
            </h3>
            <span className="product-brand">{brand}</span>
          </div>
          {/* product description */}
          <p className="product-subtitle">
            {description || "No Description Available Currently..."}
          </p>

          <div className="price-category-row">
            {/* formatted price with two decimals */}
            <span className={`product-price ${outOfStock ? "faded-text" : ""}`}>
              ₹
              {Number(selling_price).toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
            <span className="category-tag">{categoryName}</span>
          </div>
          <button className="expand-btn" onClick={() => setIsModalOpen(true)}>
            View Details
          </button>
        </div>
      </div>

      {/* Conditionally render the modal when 'View Details' is clicked */}
      {isModalOpen && (
        <ProductDetailModal
          product={props}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
};

export default Product;
