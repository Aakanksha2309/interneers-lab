/**
 * Modal to show detailed information about a product.
 * Opens on top of the page and can be closed by clicking outside or the close button.
 */
import React, { useEffect } from "react";
import ReactDOM from "react-dom";
import { useNavigate } from "react-router-dom";
import { MdDelete } from "react-icons/md";
import { Product, Category } from "../../type"; // import the type
import "./ProductDetailModal.css";
import { deleteProduct } from "services/api";
import axios from "axios";

interface ProductDetailModalProps {
  product: Product; // single prop instead of listing every field
  categories: Category[];
  onClose: () => void;
  onDeleteSuccess: () => void;
}

const ProductDetailModal = ({
  product,
  categories,
  onClose,
  onDeleteSuccess,
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
  const categoryObject = categories.find((cat) => cat.id === category_id);
  const categoryName = categoryObject ? categoryObject.title : "Unknown";

  // stock checks
  const isLowStock =
    warehouse_quantity > 0 && warehouse_quantity <= low_stock_threshold;
  const outOfStock = warehouse_quantity === 0;

  //random image
  const imageUrl = `https://loremflickr.com/400/400/${name.split(" ")[0]}`;

  const navigate = useNavigate();
  const handleNavigation = (mode: "view" | "edit") => {
    // 1. CRITICAL: Clean up the UI before leaving
    onClose();

    // 2. Determine path based on mode
    const path =
      mode === "edit" ? `/product/${id}?edit=true` : `/product/${id}`;

    // 3. Execute navigation
    navigate(path);
  };

  const [deleteError, setDeleteError] = React.useState<string | null>(null);
  const [isDeleting, setIsDeleting] = React.useState(false);

  const handleDelete = async () => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${name}"? This cannot be undone.`,
    );
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteProduct(id);
      onClose();
      onDeleteSuccess(); // triggers list refresh in App.tsx
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data) {
        setDeleteError(err.response.data.error || "Failed to delete product.");
      } else {
        setDeleteError("Something went wrong. Please try again.");
      }
    } finally {
      setIsDeleting(false);
    }
  };

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
          {deleteError && <p className="modal-delete-error">{deleteError}</p>}
          {/* action buttons */}
          <div className="card-actions">
            <button
              className="btn-primary"
              onClick={() => handleNavigation("view")}
            >
              See Full Details
            </button>
            <button
              className="btn-icon"
              onClick={() => handleNavigation("edit")}
            >
              Edit
            </button>
            <button
              className="btn-icon btn-danger"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <MdDelete className="delete-icon" />
              {isDeleting ? "Deleting..." : ""}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  ) as unknown as React.ReactElement;
};

export default ProductDetailModal;
