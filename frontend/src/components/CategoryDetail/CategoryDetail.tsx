/**
 * A dedicated view for inspecting and managing categories.
 **/
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FiMoreVertical, FiChevronRight, FiCheck, FiX } from "react-icons/fi";
import { Product, Category } from "../../type";
import ProductList from "../ProductList/ProductList";
import "./CategoryDetail.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import { TbCategory } from "react-icons/tb";
import {
  fetchProductsByCategory,
  updateCategory,
  deleteCategory,
} from "../../services/api";

const CategoryDetail = ({
  categories,
  onStatsRefresh,
}: {
  categories: Category[];
  onStatsRefresh?: () => void;
}) => {
  // Routing & Navigation Hooks
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  // Local UI & Data State
  const [categoryProducts, setCategoryProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMenu, setShowMenu] = useState(false);

  const category = categories?.find(
    (c) => String(c.id ?? (c as any)._id) === String(id),
  );
  const categoryId = category
    ? String(category.id ?? (category as any)._id)
    : undefined;
  //Inline Editing State
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(category?.title || "");
  const [editDesc, setEditDesc] = useState(category?.description || "");

  //Feedback System
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
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };
  // Refreshes local product list data
  const loadData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await fetchProductsByCategory(id);
      setCategoryProducts(response);
      setError(null);
    } catch {
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
        const response = await fetchProductsByCategory(id);
        setCategoryProducts(response);
        if (category) {
          setEditTitle(category.title);
          setEditDesc(category.description || "");
        }
        setError(null);
      } catch {
        setError("Could not load products for this category.");
      } finally {
        setLoading(false);
      }
    };
    loadPageData();
  }, [id, category]);

  /* API Interaction Handlers */
  const handleSaveEdit = async () => {
    if (!editTitle.trim()) return alert("Category title is required.");
    try {
      await updateCategory(id!, { title: editTitle, description: editDesc });
      setIsEditing(false);
      window.location.reload();
    } catch {
      alert("Failed to update category. Ensure the title is unique.");
    }
  };

  const handleDeleteCategory = async () => {
    if (
      !window.confirm(`Are you sure you want to delete "${category?.title}"?`)
    )
      return;
    try {
      await deleteCategory(id!);
      navigate("/categories");
    } catch {
      alert(
        "Could not delete category. Check if products are still linked to it.",
      );
    }
  };

  if (!category && !loading)
    return <div className="error-msg">Category not found</div>;

  /* Derived Calculatiom */
  const lowStockCount = categoryProducts.filter(
    (p) => p.warehouse_quantity <= p.low_stock_threshold,
  ).length;

  const totalValue = categoryProducts.reduce(
    (acc, curr) => acc + Number(curr.selling_price) * curr.warehouse_quantity,
    0,
  );

  return (
    <div className="category-detail-view">
      {/* BREADCRUMB */}
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

      {/* CATEGORY HEADER */}
      <header className="cat-header-compact">
        <div className="cat-header-main">
          <div className="cat-info">
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

        {/* Menu Dropdown */}
        <div className="cat-header-actions">
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
            totalItems={categoryProducts.length}
            onPageChange={() => {}}
            onDeleteSuccess={() => {
              loadData(); // refreshes category products
              onStatsRefresh?.(); // refreshes dashboard stats
            }}
            hidePagination={true}
            categoryTitle={category?.title}
            categoryId={categoryId}
            onToast={showToast}
          />
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
