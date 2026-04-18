import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import "./ProductPage.css";
import { Product } from "../../type";
import { FiEdit2, FiTrash2 } from "react-icons/fi";
import axios from "axios";
import {
  fetchCategories,
  updateProduct,
  fetchProductDetail,
  deleteProduct,
} from "../../services/api";

interface UpdateResponse {
  message: string;
  product: Product;
}

const ImagePlaceholder = () => (
  <div className="img-placeholder">
    <svg width="72" height="72" viewBox="0 0 80 80" fill="none">
      <rect x="10" y="20" width="60" height="44" rx="6" stroke="#94a3b8" strokeWidth="2"/>
      <circle cx="30" cy="36" r="7" stroke="#94a3b8" strokeWidth="2"/>
      <path d="M10 52l16-14 12 12 10-8 22 18" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  </div>
);

const ProductPage = ({ categories = [] }: { categories: any[] }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [isEditing, setIsEditing] = useState(searchParams.get("edit") === "true");
  const [product, setProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState<Partial<Product>>({});
  const [loading, setLoading] = useState(true);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [imgError, setImgError] = useState(false);

  const formatCurrency = (num: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(num);

  const formatDate = (dateString: string) => {
    const d = new Date(dateString);
    return (
      d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) +
      " · " +
      d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
    );
  };

  useEffect(() => {
    const getPageData = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const [productData] = await Promise.all([fetchProductDetail(id), fetchCategories()]);
        setProduct(productData);
        setFormData({
          ...productData,
          expiry_date: productData.expiry_date
            ? new Date(productData.expiry_date).toISOString().split("T")[0]
            : "",
        });
      } catch (err) {
        console.log("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    getPageData();
  }, [id]);

  useEffect(() => {
    setIsEditing(searchParams.get("edit") === "true");
  }, [searchParams]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setGlobalError(null);
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => { const n = { ...prev }; delete n[name]; return n; });
    }
  };

  const handleBooleanChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value === "true";
    setFormData((prev) => ({ ...prev, is_perishable: val, expiry_date: val ? prev.expiry_date : "" }));
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm("Are you sure you want to delete this product? This cannot be undone.")) return;
    try {
      await deleteProduct(id);
      navigate("/");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data)
        setGlobalError(err.response.data.error || "Failed to delete product.");
      else setGlobalError("Something went wrong. Please try again.");
    }
  };

  const handleSave = async () => {
    if (!id) return;
    setFieldErrors({}); setGlobalError(null);
    try {
      const response = (await updateProduct(id, formData as any)) as unknown as UpdateResponse;
      const newProductData = response.product;
      if (newProductData) {
        setProduct(newProductData);
        setFormData({
          ...newProductData,
          expiry_date: newProductData.expiry_date
            ? new Date(newProductData.expiry_date).toISOString().split("T")[0]
            : "",
        });
        setIsEditing(false);
        setSearchParams({});
        alert("Product updated successfully!");
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.data) {
        const data = err.response.data;
        if (data.error) setGlobalError(data.error);
        else setFieldErrors(data);
      } else setGlobalError("Something went wrong. Please try again.");
    }
  };

  const handleCancel = () => {
    setIsEditing(false); setSearchParams({});
    setFormData(product as Product); setFieldErrors({}); setGlobalError(null);
  };

  const handleEnterEditMode = () => {
    setIsEditing(true); setSearchParams({ edit: "true" });
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!product) return <div className="error">Product not found</div>;

  const isPerishable = isEditing ? formData.is_perishable : product.is_perishable;
  const currentData = isEditing ? formData : product;

  const profitMargin =
    product.cost_price && product.selling_price
      ? (((Number(product.selling_price) - Number(product.cost_price)) / Number(product.selling_price)) * 100).toFixed(1)
      : null;

  const isLowStock = product.warehouse_quantity <= product.low_stock_threshold;

  const categoryTitle =
    categories?.find((c) => String(c.id) === String(product.category_id))?.title || "Uncategorized";

  return (
    <div className="product-page-wrapper">
      <div className="product-page-container">

        {/* PAGE HEADER */}
        <header className="page-header">
          <h1 className="page-heading">Product Details</h1>
          {/* <div className="page-header-actions">
            {isEditing ? (
              <>
                <button className="btn-primary" onClick={handleSave}>Save Changes</button>
                <button className="btn-secondary" onClick={handleCancel}>Cancel</button>
              </>
            ) : (
              <>
                <button className="btn-primary" onClick={handleEnterEditMode}>
                  <FiEdit2 size={13} /> Edit Product
                </button>
                <button className="btn-danger" onClick={handleDelete}>
                  <FiTrash2 size={13} /> Delete
                </button>
              </>
            )}
          </div> */}
        </header>

        {/* CONTENT GRID */}
        <div className="product-content-grid">

          {/* SIDEBAR */}
          <aside className="product-sidebar">
            <div className="main-image-card">
              {imgError ? (
                <ImagePlaceholder />
              ) : (
                <img
                  src={`https://loremflickr.com/600/600/${product?.name?.split(" ")[0] || "product"}`}
                  alt={product?.name || "Product image"}
                  onError={() => setImgError(true)}
                />
              )}
            </div>

            {/* SIDEBAR META CARD */}
            <div className="status-info-card">
              <div className="info-row">
                <span className="lbl">SKU</span>
                <span className="val">{product.id || product.id.substring(0, 8).toUpperCase()}</span>
              </div>
              <div className="info-row">
                <span className="lbl">Availability</span>
                <span className={`status-pill ${product.warehouse_quantity > 0 ? "in-stock" : "out"}`}>
                  {product.warehouse_quantity > 0 ? "In Stock" : "Out of Stock"}
                </span>
              </div>
              <div className="info-row">
                <span className="lbl">Perishable</span>
                <span className={`status-pill ${product.is_perishable ? "perishable-yes" : "perishable-no"}`}>
                  {product.is_perishable ? "Yes" : "No"}
                </span>
              </div>
              {product.is_perishable && product.expiry_date && (
                <div className="info-row">
                  <span className="lbl">Expiry</span>
                  <span className="val">
                    {new Date(product.expiry_date).toLocaleDateString("en-IN", {
                      day: "numeric", month: "short", year: "numeric",
                    })}
                  </span>
                </div>
              )}
            </div>
          </aside>

          {/* MAIN COLUMN */}
          <div className="main-col">
          

            {/* NAME + CATEGORY */}
            {!isEditing && (
              <section className="product-top-bar">
                <div className="name-category-row">
                  <h2 className="product-main-title">{product.name}</h2>
                  <span className="val-tag">{categoryTitle}</span>
                  <div className="page-header-actions">
                    {isEditing ? (
                     <>
                     <button className="btn-primary" onClick={handleSave}>Save Changes</button>
                     <button className="btn-secondary" onClick={handleCancel}>Cancel</button>
                     </>
                     ) : (
                     <>
                    <button className="btn-primary" onClick={handleEnterEditMode}>
                     <FiEdit2 size={13} /> Edit Product
                    </button>
                    <button className="btn-danger" onClick={handleDelete}>
                     <FiTrash2 size={13} /> Delete
                    </button>
                  </>
                )}
          </div>
                </div>
                <div className="basic-meta-row">
                  <span className="basic-meta-item">
                    <span className="basic-meta-label">Brand: </span>
                    {product.brand || "—"}
                  </span>
                  <span className="meta-dot">&bull;</span>
                  <span className="basic-meta-item">
                    <span className="basic-meta-label">Created: </span>
                    {formatDate(product.created_at)}
                  </span>
                </div>
              </section>
            )}
              {!isEditing && (
        <>
    {product.warehouse_quantity === 0 ? (
       <div className="stock-banner critical-alert">
        <span className="alert-dot red-dot"></span>
        <p><strong>Out of Stock</strong> — This product is currently unavailable for fulfillment.</p>
      </div>
    ) : isLowStock ? (
      <div className="stock-banner warning-alert">
        <span className="alert-dot amber-dot"></span>
        <p><strong>Low Stock</strong> — {product.warehouse_quantity} units remaining (Threshold: {product.low_stock_threshold}).</p>
      </div>
    ) : null}
  </>
)}

            {/* MAIN PANEL — READ VIEW */}
            {!isEditing && (
              <main className="product-details-main">
                {globalError && <div className="error-banner">{globalError}</div>}

                {/* STATS */}
                <div className="panel-section-head">Inventory &amp; Pricing</div>
                <div className="stat-grid">
                  <div className="stat-cell">
                    <span className="stat-label">Stock Qty</span>
                    <span className="stat-value">{product.warehouse_quantity} units</span>
                  </div>
                  <div className="stat-cell">
                    <span className="stat-label">Selling Price</span>
                    <span className="stat-value highlight">{formatCurrency(Number(product.selling_price))}</span>
                  </div>
                  <div className="stat-cell">
                    <span className="stat-label">Cost Price</span>
                    <span className={`stat-value ${!product.cost_price ? "muted" : ""}`}>
                      {product.cost_price ? formatCurrency(Number(product.cost_price)) : "—"}
                    </span>
                  </div>
                  <div className="stat-cell">
                    <span className="stat-label">Profit Margin</span>
                    <span className={`stat-value ${profitMargin ? "green" : "muted"}`}>
                      {profitMargin ? `${profitMargin}%` : "—"}
                    </span>
                  </div>
                  <div className="stat-cell">
                    <span className="stat-label">Inventory Value</span>
                    <span className={`stat-value ${!product.cost_price ? "muted" : ""}`}>
                      {product.cost_price
                        ? formatCurrency((product.warehouse_quantity || 0) * Number(product.cost_price))
                        : "—"}
                    </span>
                  </div>
                  <div className="stat-cell">
                    <span className="stat-label">Potential Revenue</span>
                    <span className="stat-value highlight">
                      {formatCurrency((product.warehouse_quantity || 0) * Number(product.selling_price))}
                    </span>
                  </div>
                </div>

                {/* DESCRIPTION */}
                <section className="description-section">
                  <h4>Description</h4>
                  <p className="val-desc">
                    {product.description || "No additional description available."}
                  </p>
                </section>

                {/* FOOTER TIMESTAMPS — single location only */}
                <div className="meta-footer">
                  <span className="meta-item">Last updated: <span>{formatDate(product.updated_at)}</span></span>
                  <span className="meta-item">Created: <span>{formatDate(product.created_at)}</span></span>
                </div>
              </main>
            )}

            {/* EDIT PANEL */}
            {isEditing && (
              <main className="product-details-main">
                {globalError && <div className="error-banner">{globalError}</div>}

                <div className="edit-form-wrapper">

                  {/* BASIC INFO */}
                  <div className="edit-section-label">Basic Info</div>
                  <div className="edit-form-grid">
                    <div className={`field ${fieldErrors.name ? "has-error" : ""}`}>
                      <label>Product Name</label>
                      <input name="name" value={formData.name ?? ""} onChange={handleInputChange}
                        className={fieldErrors.name ? "input-error" : ""} placeholder="Product name"/>
                      {fieldErrors.name && <span className="error-text">{fieldErrors.name[0]}</span>}
                    </div>
                    <div className={`field ${fieldErrors.brand ? "has-error" : ""}`}>
                      <label>Brand:</label>
                      <input name="brand" value={formData.brand ?? ""} onChange={handleInputChange}
                        className={fieldErrors.brand ? "input-error" : ""}/>
                      {fieldErrors.brand && <span className="error-text">{fieldErrors.brand[0]}</span>}
                    </div>
                    <div className={`field ${fieldErrors.category_id ? "has-error" : ""}`}>
                      <label>Category</label>
                      <select name="category_id" value={formData.category_id} onChange={handleInputChange}
                        className={fieldErrors.category_id ? "input-error" : ""}>
                        <option value="">Select category</option>
                        {(categories || []).map((c) => (
                          <option key={c.id} value={c.id}>{c.title}</option>
                        ))}
                      </select>
                      {fieldErrors.category_id && <span className="error-text">{fieldErrors.category_id[0]}</span>}
                    </div>
                    <div className="field full">
                      <label>Description</label>
                      <textarea name="description" rows={3} value={formData.description ?? ""}
                        onChange={handleInputChange}
                        className={fieldErrors.description ? "input-error" : ""}/>
                      {fieldErrors.description && <span className="error-text">{fieldErrors.description[0]}</span>}
                    </div>
                  </div>

                  {/* PRICING */}
                  <div className="edit-section-label">Pricing</div>
                  <div className="edit-form-grid">
                    <div className={`field ${fieldErrors.selling_price ? "has-error" : ""}`}>
                      <label>Selling Price (₹)</label>
                      <input name="selling_price" type="number" value={formData.selling_price ?? ""}
                        onChange={handleInputChange}
                        className={fieldErrors.selling_price ? "input-error" : ""}/>
                      {fieldErrors.selling_price && <span className="error-text">{fieldErrors.selling_price[0]}</span>}
                    </div>
                    <div className={`field ${fieldErrors.cost_price ? "has-error" : ""}`}>
                      <label>Cost Price (₹)</label>
                      <input name="cost_price" type="number" value={formData.cost_price ?? ""}
                        onChange={handleInputChange}
                        className={fieldErrors.cost_price ? "input-error" : ""}/>
                      {fieldErrors.cost_price && <span className="error-text">{fieldErrors.cost_price[0]}</span>}
                    </div>
                  </div>

                  {/* INVENTORY */}
                  <div className="edit-section-label">Inventory</div>
                  <div className="edit-form-grid-3">
                    <div className={`field ${fieldErrors.warehouse_quantity ? "has-error" : ""}`}>
                      <label>Stock Qty</label>
                      <input name="warehouse_quantity" type="number" value={formData.warehouse_quantity ?? ""}
                        onChange={handleInputChange}
                        className={fieldErrors.warehouse_quantity ? "input-error" : ""}/>
                      {fieldErrors.warehouse_quantity && <span className="error-text">{fieldErrors.warehouse_quantity[0]}</span>}
                    </div>
                    <div className="field">
                      <label>Low Stock Threshold</label>
                      <input name="low_stock_threshold" type="number" value={formData.low_stock_threshold ?? ""}
                        onChange={handleInputChange}/>
                    </div>
                    <div className="field">
                      <label>Perishable</label>
                      <select name="is_perishable" value={String(formData.is_perishable)} onChange={handleBooleanChange}>
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                      </select>
                    </div>
                    {isPerishable && (
                      <div className={`field ${fieldErrors.expiry_date ? "has-error" : ""}`}>
                        <label>Expiry Date</label>
                        <input type="date" name="expiry_date" value={formData.expiry_date || ""}
                          onChange={handleInputChange}
                          className={fieldErrors.expiry_date ? "input-error" : ""}/>
                        {fieldErrors.expiry_date && <span className="error-text">{fieldErrors.expiry_date[0]}</span>}
                      </div>
                    )}
                  </div>

                </div>
              </main>
            )}

          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;