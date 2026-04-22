import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  FiLoader,
  FiMoreVertical,
  FiChevronRight,
  FiCheck,
  FiX,
} from "react-icons/fi";
import { Product, Category } from "../../type";
import ProductList from "../ProductList/ProductList";
import "./CategoryDetail.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import { TbCategory } from "react-icons/tb";

const CategoryDetail = ({ categories }: { categories: Category[] }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [categoryProducts, setCategoryProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMenu, setShowMenu] = useState(false);

  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [moveTarget, setMoveTarget] = useState<string>("");
  const [isMoving, setIsMoving] = useState(false);
  const [isMoveMode, setIsMoveMode] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const selectedCategory = categories.find(
    (c) => String(c.id || (c as any)._id) === moveTarget,
  );

  const category = categories?.find(
    (c) => String(c.id || (c as any)._id) === String(id),
  );
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(category?.title || "");
  const [editDesc, setEditDesc] = useState(category?.description || "");

  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };
  const toggleSelect = (productId: string) => {
    setSelectedIds((prev) =>
      prev.includes(productId)
        ? prev.filter((id) => id !== productId)
        : [...prev, productId],
    );
  };

  const handleBulkMove = async () => {
    if (!moveTarget || selectedIds.length === 0) return;
    setIsMoving(true);
    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/api/products/category/bulk-move/`,
        { product_ids: selectedIds, category_id: moveTarget },
      );
      const { moved, failed } = res.data;
      if (failed > 0) {
        showToast(`${moved} moved successfully, ${failed} failed.`, "error");
      } else {
        showToast(
          `${moved} product${moved > 1 ? "s" : ""} moved successfully!`,
          "success",
        );
      }
      setSelectedIds([]);
      setMoveTarget("");
      setIsMoveMode(false);
      loadData();
    } catch (err) {
      showToast("Bulk move failed. Please try again.", "error");
    } finally {
      setIsMoving(false);
    }
  };
  const handleSaveEdit = async () => {
    if (!editTitle.trim()) return alert("Category title is required.");

    try {
      await axios.patch(`http://127.0.0.1:8000/api/categories/${id}/`, {
        title: editTitle,
        description: editDesc,
      });
      setIsEditing(false);
      // reload ensures the parent state (categories prop) gets the fresh data
      window.location.reload();
    } catch (err) {
      alert("Failed to update category. Ensure the title is unique.");
    }
  };

  const handleDeleteCategory = async () => {
    if (
      !window.confirm(`Are you sure you want to delete "${category?.title}"?`)
    ) {
      return;
    }

    try {
      await axios.delete(`http://127.0.0.1:8000/api/categories/${id}/`);

      navigate("/categories");
    } catch (err) {
      console.error("Error deleting category:", err);
      alert(
        "Could not delete category. Check if products are still linked to it.",
      );
    }
  };
  const loadData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await axios.get(
        `http://127.0.0.1:8000/api/products/category/${id}/`,
      );
      setCategoryProducts(response.data);
      setError(null);
    } catch (err) {
      setError("Could not load products for this category.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadPageData = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const response = await axios.get(
          `http://127.0.0.1:8000/api/products/category/${id}/`,
        );
        setCategoryProducts(response.data);

        // Sync edit fields only when the category is found
        if (category) {
          setEditTitle(category.title);
          setEditDesc(category.description || "");
        }
        setError(null);
      } catch (err) {
        setError("Could not load products for this category.");
      } finally {
        setLoading(false);
      }
    };

    loadPageData();
  }, [id, category]);
  if (!category && !loading)
    return <div className="error-msg">Category not found</div>;

  const lowStockCount = categoryProducts.filter(
    (p) => p.warehouse_quantity <= p.low_stock_threshold,
  ).length;

  const totalValue = categoryProducts.reduce(
    (acc, curr) => acc + Number(curr.selling_price) * curr.warehouse_quantity,
    0,
  );

  if (!category && !loading)
    return <div className="error-msg">Category not found</div>;

  return (
    <div className="category-detail-view">
      {/* BREADCRUMB - Production Grade */}
      <nav className="breadcrumb">
        <span className="bc-link" onClick={() => navigate("/dashboard")}>
          Dashboard
        </span>
        <FiChevronRight className="bc-sep" />
        <span className="bc-link" onClick={() => navigate("/categories")}>
          Categories
        </span>
        <FiChevronRight className="bc-sep" />
        <span className="bc-current">{category?.title}</span>
      </nav>

      {/* REFINED HEADER */}
      <header className="cat-header-compact">
        <div className="cat-header-main">
          <div className="cat-info">
            {/* NEW: Small Super-heading instead of icon */}
            <div className="category-super-label">
              <span className="dot-indicator"></span>
              Product Category
            </div>

            <div className="title-with-icon">
              <TbCategory className="super-label-icon" />
              {isEditing ? (
                <input
                  className="edit-title-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  autoFocus
                />
              ) : (
                <h1 className="cat-title">{category?.title}</h1>
              )}
            </div>

            <div className="cat-desc-container">
              <span className="desc-heading">Category Description</span>
              {isEditing ? (
                <textarea
                  className="edit-desc-input"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                />
              ) : (
                <p className="cat-desc">{category?.description}</p>
              )}
            </div>

            {isEditing ? (
              <div className="edit-actions-row">
                <button className="btn-save-inline" onClick={handleSaveEdit}>
                  <FiCheck /> Save Changes
                </button>
                <button
                  className="btn-cancel-inline"
                  onClick={() => setIsEditing(false)}
                >
                  <FiX /> Cancel
                </button>
              </div>
            ) : (
              <>
                <div className="cat-meta-row">
                  <div className="meta-item">
                    <span className="meta-label">Created: </span>
                    <span className="meta-value">
                      {formatDate(category?.created_at)}
                    </span>
                  </div>
                  <span className="meta-dot">•</span>
                  <div className="meta-item">
                    <span className="meta-label">Updated: </span>
                    <span className="meta-value">
                      {formatDate(category?.updated_at)}
                    </span>
                  </div>
                </div>

                <div className="cat-stats-pills">
                  <span className="pill-blue">
                    Total Items: {categoryProducts.length}
                  </span>
                  {lowStockCount > 0 && (
                    <span className="pill-warn">
                      Low Stock: {lowStockCount}
                    </span>
                  )}
                  <span className="pill-green">
                    Total Value: ₹{totalValue.toLocaleString()}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="cat-header-actions">
          <button
            className={`btn-move-mode ${isMoveMode ? "active" : ""}`}
            onClick={() => {
              setIsMoveMode(!isMoveMode);
              setSelectedIds([]); // clear selection when toggling
            }}
          >
            {isMoveMode ? "Cancel Move" : "Move Products"}
          </button>
          <div className="menu-container">
            <button className="btn-icon" onClick={() => setShowMenu(!showMenu)}>
              <FiMoreVertical />
            </button>
            {showMenu && (
              <div className="dropdown-menu">
                <button
                  onClick={() => {
                    setIsEditing(true);
                    setShowMenu(false);
                  }}
                >
                  Edit Category
                </button>
                <button className="delete-opt" onClick={handleDeleteCategory}>
                  Delete Category
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {loading ? (
        <LoadingSpinner
          message="Fetching Category Inventory..."
          fullPage={true}
        />
      ) : error ? (
        <div className="error-state">{error}</div>
      ) : (
        <main className="product-grid-container inventory-workspace">
          <ProductList
            products={categoryProducts}
            categories={categories}
            currentPage={1}
            totalPages={1}
            onPageChange={() => {}}
            onDeleteSuccess={loadData}
            selectedIds={isMoveMode ? selectedIds : []}
            onToggleSelect={isMoveMode ? toggleSelect : undefined}
          />
          {/* BULK ACTION BAR — only appears when products are selected */}
          {selectedIds.length > 0 && (
            <div className="bulk-action-bar">
              <span className="bulk-count">
                {selectedIds.length} product{selectedIds.length > 1 ? "s" : ""}{" "}
                selected
              </span>
              // REPLACE WITH THIS
              <div className="bulk-dropdown-wrapper">
                <button
                  className="bulk-dropdown-trigger"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  type="button"
                >
                  <span>
                    {selectedCategory
                      ? selectedCategory.title
                      : "Move to category..."}
                  </span>
                  <span className="bulk-dropdown-arrow">▾</span>
                </button>
                {isDropdownOpen && (
                  <div className="bulk-dropdown-list">
                    {categories
                      .filter(
                        (c) => String(c.id || (c as any)._id) !== String(id),
                      )
                      .map((c) => (
                        <button
                          key={String(c.id || (c as any)._id)}
                          className="bulk-dropdown-item"
                          onClick={() => {
                            setMoveTarget(String(c.id || (c as any)._id));
                            setIsDropdownOpen(false);
                          }}
                        >
                          {c.title}
                        </button>
                      ))}
                  </div>
                )}
              </div>
              <button
                className="bulk-move-btn"
                onClick={handleBulkMove}
                disabled={!moveTarget || isMoving}
              >
                {isMoving ? "Moving..." : "Move products"}
              </button>
              <button
                className="bulk-cancel-btn"
                onClick={() => setSelectedIds([])}
              >
                Cancel
              </button>
            </div>
          )}
        </main>
      )}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === "success" ? "✓" : "✕"} {toast.message}
        </div>
      )}
    </div>
  );
};

export default CategoryDetail;
