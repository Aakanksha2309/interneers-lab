/**
 * A reusable modal component for
 * creating or updating product categories.
 **/
import { FiX, FiFolderPlus, FiEdit3 } from "react-icons/fi";
import "./CategoryModal.css";

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  categoryData: { title: string; description: string };
  setCategoryData: (data: { title: string; description: string }) => void;
  isSubmitting: boolean;
  mode: "create" | "edit";
  message: { type: "error" | "success"; text: string } | null;
}

function CategoryModal({
  isOpen,
  onClose,
  onSubmit,
  categoryData,
  setCategoryData,
  isSubmitting,
  mode,
  message,
}: CategoryModalProps) {
  if (!isOpen) return null;

  return (
    <div className="cm-overlay">
      <div className="cm-modal">
        {/* ---Header Section --- */}
        <div className="cm-header">
          <div className="cm-header-left">
            <div className={`cm-icon ${mode}`}>
              {mode === "create" ? <FiFolderPlus /> : <FiEdit3 />}
            </div>
            <h2>{mode === "create" ? "Add New Category" : "Edit Category"}</h2>
          </div>
          <button
            className="cm-close-btn"
            onClick={onClose}
            type="button"
            aria-label="Close modal"
          >
            <FiX />
          </button>
        </div>

        {message && (
          <div className={`cm-alert cm-alert-${message.type}`}>
            {message.text}
          </div>
        )}
        <form onSubmit={onSubmit}>
          <div className="cm-body">
            {" "}
            <div className="cm-form-group">
              {" "}
              <label>Category Title *</label>
              <input
                className="cm-input"
                type="text"
                placeholder="e.g., Electronics, Beverages..."
                value={categoryData.title}
                onChange={(e) =>
                  setCategoryData({ ...categoryData, title: e.target.value })
                }
                required
                autoFocus
              />
            </div>
            <div className="cm-form-group">
              {" "}
              <label>Description</label>
              <textarea
                className="cm-textarea"
                placeholder="Describe what kind of products belong here..."
                value={categoryData.description}
                onChange={(e) =>
                  setCategoryData({
                    ...categoryData,
                    description: e.target.value,
                  })
                }
                rows={4}
              />
            </div>
          </div>

          <div className="cm-footer">
            {" "}
            <button type="button" className="cm-btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="cm-btn-save"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Processing..."
                : mode === "create"
                  ? "Create Category"
                  : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CategoryModal;
