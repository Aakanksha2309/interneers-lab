/**
 * An administrative hub for category lifecycle management.
 * Handles CRUD operations, real-time inventory valuation per category,
 * and dynamic health-status indicators based on stock levels.
 */
import React, { useEffect, useState } from "react";
import {
  fetchCategories,
  deleteCategory,
  updateCategory,
  createCategory,
} from "../../services/api";
import { Category, Product } from "../../type";
import { FiTrash2, FiFolder, FiArrowRight, FiEdit2 } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import "./ManageCategories.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import CategoryModal from "../../components/CategoryModal/CategoryModal";

interface ManageCategoriesProps {
  products: Product[];
}

const ManageCategories = ({ products }: ManageCategoriesProps) => {
  // ---State Manangement ---
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal specific states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(
    null,
  );
  const [tempData, setTempData] = useState({ title: "", description: "" });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const navigate = useNavigate();

  // Handlers for Modal
  const handleOpenCreate = () => {
    setModalMode("create");
    setTempData({ title: "", description: "" });
    setIsModalOpen(true);
  };

  const handleEdit = (category: Category) => {
    setModalMode("edit");
    setSelectedCategoryId(category.id);
    setTempData({
      title: category.title,
      description: category.description || "",
    });
    setFormMessage(null);
    setIsModalOpen(true);
  };

  const [formMessage, setFormMessage] = useState<{
    type: "error" | "success";
    text: string;
  } | null>(null);

  // Updates local state directly for "Edit"
  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormMessage(null);

    try {
      if (modalMode === "create") {
        const response = await createCategory(tempData);
        await loadCategories();

        setFormMessage({
          type: "success",
          text: response.message,
        });
      } else {
        const response = await updateCategory(selectedCategoryId!, tempData);
        const updatedCat = response.category;

        // Update the local list state so the UI changes instantly
        setCategories((prev) =>
          prev.map((cat) => (cat.id === updatedCat.id ? updatedCat : cat)),
        );

        setFormMessage({
          type: "success",
          text: response.message,
        });
      }

      // Briefly show success message before closing
      setTimeout(() => {
        setIsModalOpen(false);
        setFormMessage(null);
      }, 1000);
    } catch (err: any) {
      const serverMessage =
        err.response?.data?.error ||
        err.response?.data?.message ||
        "Operation failed.";
      setFormMessage({ type: "error", text: serverMessage });
    } finally {
      setIsSubmitting(false);
    }
  };
  //Calculates the total financial value of all products in a specific category
  const getCategoryValue = (categoryId: string) => {
    return products
      .filter((p) => String(p.category_id) === String(categoryId))
      .reduce(
        (sum, p) =>
          sum + Number(p.selling_price) * Number(p.warehouse_quantity),
        0,
      );
  };

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await fetchCategories();
      setCategories(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const handleDelete = async (id: string, title: string) => {
    if (window.confirm(`Delete category "${title}"?`)) {
      try {
        await deleteCategory(id);
        setCategories((prev) => prev.filter((c) => c.id !== id));
      } catch (err) {
        alert("Action failed: Category might have linked products.");
      }
    }
  };
  // Returns status based on the inventory of a catgeory products
  const getCategoryStatusClass = (categoryId: string) => {
    const catProducts = products.filter(
      (p) => String(p.category_id) === String(categoryId),
    );
    if (catProducts.length === 0) return "status-none";
    if (catProducts.some((p) => Number(p.warehouse_quantity) <= 0))
      return "status-critical";
    if (catProducts.some((p) => Number(p.warehouse_quantity) < 10))
      return "status-warning";
    return "status-healthy";
  };

  if (loading && categories.length === 0) {
    return (
      <LoadingSpinner
        message="Fetching your category catalog..."
        fullPage={true}
      />
    );
  }

  return (
    <div className="manage-categories-view">
      <header className="category-page-header">
        <div className="category-header-info">
          <h1>Manage Categories</h1>
          <p className="sub-heading">
            Currently managing {categories.length} product categories.
          </p>
        </div>
        <button className="create-cat-btn" onClick={handleOpenCreate}>
          + New Category
        </button>
      </header>

      {/* Header labels for the grid */}
      <div className="category-header-bar">
        <div className="header-item">Category</div>
        <div className="header-item">Description</div>
        <div className="header-item">Inventory</div>
        <div className="header-item">Potential Revenue</div>
        <div className="header-item header-actions">Actions</div>
      </div>

      <div className="category-grid">
        {categories.map((cat) => (
          <div
            key={cat.id}
            className={`category-tile ${getCategoryStatusClass(cat.id)}`}
          >
            <div className="tile-section main-info">
              <div className="tile-icon">
                <FiFolder size={20} />
              </div>
              <div className="tile-text">
                <h3>{cat.title}</h3>
                <div className="tile-dates-group">
                  <span className="tile-date">
                    Created:{" "}
                    {cat.created_at
                      ? new Date(cat.created_at).toLocaleDateString()
                      : "N/A"}
                  </span>
                  <span className="tile-date">
                    Updated:{" "}
                    {cat.updated_at
                      ? new Date(cat.updated_at).toLocaleDateString()
                      : "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {/* Description Snippet */}
            <div className="tile-section description-box">
              <p>{cat.description || "No description provided."}</p>
            </div>

            {/* Statistical Metadata */}
            <div className="tile-section stats-group">
              <div className="item-pill">
                <span className="pill-count">
                  {" "}
                  {(cat as any).product_count ?? 0}
                </span>
                <span className="pill-label">Items</span>
              </div>
              <div className="value-display">
                <span className="category-stat-value text-green">
                  ₹{getCategoryValue(cat.id).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Action buttons */}
            <div className="tile-section actions">
              <button
                className="action-btn view-btn"
                onClick={() => navigate(`/category/${cat.id}`)}
              >
                <FiArrowRight /> View
              </button>
              <button
                className="action-btn tile-edit-btn"
                onClick={() => handleEdit(cat)}
              >
                <FiEdit2 />
              </button>
              <button
                className="action-btn tile-delete-btn"
                onClick={() => handleDelete(cat.id, cat.title)}
              >
                <FiTrash2 />
              </button>
            </div>
          </div>
        ))}
      </div>

      <CategoryModal
        isOpen={isModalOpen}
        mode={modalMode}
        categoryData={tempData}
        setCategoryData={setTempData}
        isSubmitting={isSubmitting}
        onClose={() => {
          setIsModalOpen(false);
          setFormMessage(null);
        }}
        onSubmit={handleModalSubmit}
        message={formMessage}
      />
    </div>
  );
};

export default ManageCategories;
