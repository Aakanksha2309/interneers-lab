/**
 * AddProduct — form for creating a new product.
 **/

import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import {
  FiPackage,
  FiAlertCircle,
  FiChevronDown,
  FiChevronRight,
  FiHome,
} from "react-icons/fi";
import "./AddProduct.css";
import { createProduct } from "../../services/api";

const AddProduct = ({
  categories,
  onSuccess,
}: {
  categories: any[];
  onSuccess: () => void;
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const fromCategory = location.state?.from === "category";
  const categoryTitle = location.state?.categoryTitle;

  const [formData, setFormData] = useState({
    name: "",
    brand: "",
    category_id: "",
    description: "",
    warehouse_quantity: "" as any,
    low_stock_threshold: "" as any,
    is_perishable: "false",
    expiry_date: "",
    cost_price: "",
    selling_price: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pre-fill category if user navigated here from a category detail page
  useEffect(() => {
    if (location.state?.from === "category" && location.state?.categoryId) {
      setFormData((prev) => ({
        ...prev,
        category_id: String(location.state.categoryId),
      }));
    }
  }, [location.state]);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsSubmitting(true);

    try {
      const dataToSubmit: any = {
        ...formData,
        is_perishable: formData.is_perishable === "true",
      };

      // Data Sanitization: Convert numeric strings
      if (formData.warehouse_quantity !== "") {
        dataToSubmit.warehouse_quantity = parseInt(formData.warehouse_quantity);
      } else {
        delete dataToSubmit.warehouse_quantity;
      }
      if (formData.low_stock_threshold !== "") {
        dataToSubmit.low_stock_threshold = parseInt(
          formData.low_stock_threshold,
        );
      } else {
        delete dataToSubmit.low_stock_threshold;
      }
      if (formData.cost_price !== "") {
        dataToSubmit.cost_price = parseFloat(formData.cost_price);
      } else {
        // If user leaves it blank, remove it so the DB doesn't get an empty string or error
        delete dataToSubmit.cost_price;
      }

      // Format Fix: Handle Expiry Date formatting
      if (dataToSubmit.is_perishable) {
        if (dataToSubmit.expiry_date) {
          dataToSubmit.expiry_date = `${dataToSubmit.expiry_date}T23:59:59`;
        }
      } else {
        delete dataToSubmit.expiry_date;
      }

      const response = await createProduct(dataToSubmit);

      if (response) {
        if (onSuccess) onSuccess();
        alert(`Product created successfully! ID: ${response.id}`);
        navigate("/");
      }
    } catch (err: any) {
      if (err.response && err.response.data) {
        const data = err.response.data;
        const newErrors: Record<string, string> = {};

        // Handle Global Errors
        if (data.non_field_errors) {
          newErrors["non_field_errors"] = Array.isArray(data.non_field_errors)
            ? data.non_field_errors[0]
            : data.non_field_errors;
        } else if (data.error && typeof data.error === "string") {
          newErrors["non_field_errors"] = data.error;
        }

        // Map every other field error dynamically
        Object.keys(data).forEach((key) => {
          if (key !== "non_field_errors" && key !== "error") {
            let errorMsg = Array.isArray(data[key]) ? data[key][0] : data[key];

            if (
              key === "expiry_date" &&
              (errorMsg.includes("null") ||
                errorMsg.includes("blank") ||
                errorMsg.includes("required"))
            ) {
              errorMsg = "Please provide an expiry date for perishable items.";
            }

            newErrors[key] = errorMsg;
          }
        });

        // Fallback: If there are errors but none mapped to 'non_field_errors'
        if (
          Object.keys(newErrors).length > 0 &&
          !newErrors["non_field_errors"]
        ) {
          const firstKey = Object.keys(newErrors)[0];
          console.log(`Backend validation failed for: ${firstKey}`);
        }

        setErrors(newErrors);
      } else {
        setErrors({
          non_field_errors: "Network error: Is the backend running?",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="add-product-page-root">
      <nav className="breadcrumbs">
        <span onClick={() => navigate("/")}>
          <FiHome /> Dashboard
        </span>

        {/* If we came from a category, show 'Categories' AND the specific 'Category Name' */}
        {location.state?.from === "category" && (
          <>
            <FiChevronRight className="separator" />
            <span
              className="breadcrumb-link"
              onClick={() => navigate("/categories")}
            >
              Categories
            </span>

            <FiChevronRight className="separator" />
            <span className="breadcrumb-link" onClick={() => navigate(-1)}>
              {location.state.categoryTitle || "Category Details"}
            </span>
          </>
        )}

        <FiChevronRight className="separator" />
        <span className="current">Create Product</span>
      </nav>
      <div className="add-product-container">
        {/* SINGLE UNIFIED CARD */}
        <form onSubmit={handleSubmit} className="modern-form form-card">
          {errors.non_field_errors && (
            <div className="form-global-error">
              <FiAlertCircle />
              <span>{errors.non_field_errors}</span>
            </div>
          )}
          {/* INTERNAL SECTION 1: BASIC DETAILS */}
          <section className="form-section">
            <div className="card-header">
              <FiPackage className="header-icon" />
              <h3>Basic Information</h3>
            </div>

            <div className="form-grid">
              <div
                className={`input-group span-2 ${errors.name ? "has-error" : ""}`}
              >
                <label>Product Name *</label>
                <input
                  type="text"
                  placeholder="e.g. Organic Milk"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
                {errors.name && (
                  <span className="error-text">{errors.name}</span>
                )}
              </div>

              <div className={`input-group ${errors.brand ? "has-error" : ""}`}>
                <label>Brand *</label>
                <input
                  type="text"
                  placeholder="Brand name"
                  value={formData.brand}
                  onChange={(e) =>
                    setFormData({ ...formData, brand: e.target.value })
                  }
                />
                {errors.brand && (
                  <span className="error-text">{errors.brand}</span>
                )}
              </div>

              <div
                className={`input-group ${errors.category_id ? "has-error" : ""}`}
              >
                <label>Category * </label>
                <div className="select-wrapper">
                  <select
                    value={formData.category_id}
                    onChange={(e) =>
                      setFormData({ ...formData, category_id: e.target.value })
                    }
                  >
                    <option value="">Select Category</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.title}
                      </option>
                    ))}
                  </select>
                  <FiChevronDown className="select-icon" />
                </div>
              </div>
            </div>

            <div className="form-divider" />

            {/* INTERNAL SECTION 2: INVENTORY & PRICING */}
            <div className="card-header">
              <FiAlertCircle className="header-icon" />
              <h3>Stock & Pricing</h3>
            </div>

            <div className="form-grid">
              <div
                className={`input-group ${errors.warehouse_quantity ? "has-error" : ""}`}
              >
                <label>Warehouse Quantity</label>
                <input
                  type="number"
                  placeholder="0"
                  value={formData.warehouse_quantity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      warehouse_quantity: e.target.value,
                    })
                  }
                />
                {errors.warehouse_quantity && (
                  <span className="error-text">
                    {errors.warehouse_quantity}
                  </span>
                )}
              </div>

              <div
                className={`input-group ${errors.low_stock_threshold ? "has-error" : ""}`}
              >
                <label>Low Stock Threshold</label>
                <input
                  type="number"
                  placeholder="10"
                  value={formData.low_stock_threshold}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      low_stock_threshold: e.target.value,
                    })
                  }
                />
                {errors.low_stock_threshold && (
                  <span className="error-text">
                    {errors.low_stock_threshold}
                  </span>
                )}
              </div>

              <div
                className={`input-group ${errors.selling_price ? "has-error" : ""}`}
              >
                <label>Selling Price *</label>
                <input
                  type="number"
                  step="10"
                  value={formData.selling_price}
                  onChange={(e) =>
                    setFormData({ ...formData, selling_price: e.target.value })
                  }
                />
                {errors.selling_price && (
                  <span className="error-text">{errors.selling_price}</span>
                )}
              </div>

              <div
                className={`input-group ${errors.cost_price ? "has-error" : ""}`}
              >
                <label>Cost Price</label>
                <input
                  type="number"
                  step="10"
                  placeholder="0.00"
                  value={formData.cost_price}
                  onChange={(e) =>
                    setFormData({ ...formData, cost_price: e.target.value })
                  }
                />
                {errors.cost_price && (
                  <span className="error-text">{errors.cost_price}</span>
                )}
              </div>

              <div
                className={`input-group ${errors.is_perishable ? "has-error" : ""}`}
              >
                <label>Is Perishable? *</label>
                <div className="select-wrapper">
                  <select
                    value={formData.is_perishable.toString()}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        is_perishable: e.target.value,
                      })
                    }
                  >
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                  </select>
                  <FiChevronDown className="select-icon" />
                </div>
                {errors.is_perishable && (
                  <span className="error-text">{errors.is_perishable}</span>
                )}
              </div>

              <div
                className={`input-group span-2 ${formData.is_perishable === "false" ? "disabled-input" : ""}`}
              >
                <label>Expiry Date</label>
                <input
                  type="date"
                  disabled={formData.is_perishable === "false"}
                  value={formData.expiry_date}
                  onChange={(e) =>
                    setFormData({ ...formData, expiry_date: e.target.value })
                  }
                />
                {errors.expiry_date && (
                  <span className="error-text">{errors.expiry_date}</span>
                )}
              </div>
            </div>

            <div className="input-group span-full">
              <label>Description</label>
              <textarea
                placeholder="Enter product details, specifications, or notes..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={4}
              />
              {errors.description && (
                <span className="error-text">{errors.description}</span>
              )}
            </div>
          </section>

          {/* ACTIONS WITHIN THE CARD CONTAINER FOOTER */}
          <footer className="form-actions">
            <button
              type="button"
              className="btn-discard"
              onClick={() => navigate(-1)}
            >
              Discard
            </button>
            <button type="submit" className="btn-save" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Save Product"}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};

export default AddProduct;
