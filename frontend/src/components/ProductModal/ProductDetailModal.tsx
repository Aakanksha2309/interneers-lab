/**
 * Modal to show detailed information about a product.
 * Opens on top of the page and can be closed by clicking outside or the close button.
 */
import React, { useEffect } from "react";
import ReactDOM from "react-dom";
import { MdDelete } from "react-icons/md";
import { MOCK_CATEGORIES } from "../../mockData";
import { Product } from "../../type"; // import the type
import "./ProductDetailModal.css";

interface ProductDetailModalProps {
  product: Product; // single prop instead of listing every field
  onClose: () => void;
}

const ProductDetailModal = ({
  product,
  onClose,
}: ProductDetailModalProps): React.ReactElement => {
  // lock background scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    // restore scroll on close
    return () => {
      document.body.style.overflow = "unset";
    };
  }, []);
  const {
    id,
    name,
    category_id,
    warehouse_quantity,
    low_stock_threshold,
    selling_price,
    description,
    brand,
    expiry_date,
    cost_price,
    is_perishable,
  } = product;

  // get category name from id
  const categoryObject = MOCK_CATEGORIES.find((cat) => cat.id === category_id);
  const categoryName = categoryObject ? categoryObject.title : "Unknown";

  // stock checks
  const isLowStock =
    warehouse_quantity > 0 && warehouse_quantity <= low_stock_threshold;
  const outOfStock = warehouse_quantity === 0;

  //random image
  const imageUrl = `https://loremflickr.com/400/400/${name.split(" ")[0]}`;

  return ReactDOM.createPortal(
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        <div className="modal-image-container">
          <img src={imageUrl} alt={name} />
        </div>

        <div className="modal-body">
          <div className="info-header">
            <h3 className="product-name">{name}</h3>
            {/* stock label */}
            <span
              className={`stock-badge ${outOfStock ? "out-of-stock" : isLowStock ? "low" : "in-stock"}`}
            >
              {outOfStock ? "Out of Stock" : `${warehouse_quantity} in stock`}
            </span>
          </div>

          <div className="price-category-row">
            {/* formatted price */}
            <span className="product-price">
              ₹
              {Number(selling_price).toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
            <span className="category-tag">{categoryName}</span>
          </div>

          {/* product details */}
          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">SKU</span>
              <span className="detail-value">
                {id.substring(0, 8).toUpperCase()}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Brand</span>
              <span className="detail-value">{brand}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Stock Level</span>
              <span className="detail-value">{warehouse_quantity} units</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span
                className={`detail-value status-${warehouse_quantity < low_stock_threshold ? "low" : "ok"}`}
              >
                {warehouse_quantity <= low_stock_threshold &&
                warehouse_quantity > 0
                  ? "Low Stock"
                  : "In Stock"}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Selling Price</span>
              <span className="detail-value">
                ₹
                {Number(selling_price).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Cost Price</span>
              <span className="detail-value">
                ₹
                {Number(cost_price).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Total Value</span>
              <span className="detail-value">
                ₹
                {(Number(selling_price) * warehouse_quantity).toLocaleString(
                  "en-IN",
                  { minimumFractionDigits: 2, maximumFractionDigits: 2 },
                )}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Perishable</span>
              <span className="detail-value">
                {is_perishable ? "Yes" : "No"}
              </span>
            </div>

            {/* show expiry only if present */}
            {expiry_date && (
              <div className="detail-item">
                <span className="detail-label">Expiry Date</span>
                <span className="detail-value">
                  {new Date(expiry_date).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </span>
              </div>
            )}
          </div>

          {/* Product description */}
          <div className="description-section">
            <h5 className="section-title">Product Description</h5>
            <p className="description-text">
              {description ||
                "High-quality product curated for the InvTrack inventory system."}
            </p>
          </div>

          {/* action buttons */}
          <div className="card-actions">
            <button className="btn-primary">See Full Details</button>
            <button className="btn-icon">Edit</button>
            <button className="btn-icon btn-danger">
              <MdDelete className="delete-icon" />
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  ) as unknown as React.ReactElement;
};

export default ProductDetailModal;
