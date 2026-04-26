/**
 * * This is the central hub for displaying and managing products.
 * It handles the heavy lifting for:
 * 1. Searching and filtering products.
 * 2. Bulk operations: allows users to select multiple items to move,
 * remove, or permanently delete them.
 * 3. CSV Uploads: manages the state and feedback for bulk imports.
 * 4. Contextual UI: adjusts its behavior based on whether the user
 * is on the main dashboard or inside a specific category detail page.
 */
import React, { useState, useEffect, useRef } from "react";
import ProductCard from "../ProductCard/Product";
import ProductFilters from "../ProductFilters/ProductFilters";
import { fetchProducts, bulkMoveProducts } from "../../services/api";
import {
  bulkRemoveFromCategory,
  bulkDeleteProducts,
  bulkUploadCSV,
} from "../../services/api";
import {
  Product,
  Category,
  ProductFilters as ProductFiltersType,
} from "../../type";
import "./ProductList.css";
import { FaBoxOpen } from "react-icons/fa";
import {
  FiPlus,
  FiChevronDown,
  FiArrowUpRight,
  FiX,
  FiTrash2,
  FiUpload,
} from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import axios from "axios";

interface ProductListProps {
  products: Product[];
  categories: Category[];
  currentPage: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onDeleteSuccess: () => void;
  hidePagination?: boolean;
  categoryTitle?: string;
  categoryId?: string | number;
  onToast?: (message: string, type: "success" | "error") => void;
}

type BulkMode = "move" | "remove" | "delete" | null;

const ProductList = ({
  products,
  categories,
  currentPage,
  totalPages,
  totalItems,
  onPageChange,
  onDeleteSuccess,
  hidePagination = false,
  categoryTitle,
  categoryId,
  onToast,
}: ProductListProps) => {
  const navigate = useNavigate();

  // --- Filtering & Display State ---
  const [filters, setFilters] = useState<ProductFiltersType>({});
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(products);
  const [filteredTotal, setFilteredTotal] = useState(totalItems);
  const [filteredPages, setFilteredPages] = useState(totalPages);
  const [filteredPage, setFilteredPage] = useState(1);
  const [filterLoading, setFilterLoading] = useState(false);

  // --- Bulk Operation State ---
  // Tracks if we are currently in 'move', 'remove', or 'delete' mode
  const [bulkMode, setBulkMode] = useState<BulkMode>(null);
  const [localSelectedIds, setLocalSelectedIds] = useState<string[]>([]);
  const [moveTarget, setMoveTarget] = useState("");
  const [isActioning, setIsActioning] = useState(false);

  // UI toggles for custom dropdown menus
  const [manageDropdownOpen, setManageDropdownOpen] = useState(false);
  const [moveCategoryDropdownOpen, setMoveCategoryDropdownOpen] =
    useState(false);

  const manageDropdownRef = useRef<HTMLDivElement>(null);
  const moveCategoryRef = useRef<HTMLDivElement>(null);

  // ── Derived ───────────────────────────────────────────────────
  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== undefined && v !== "" && v !== false,
  );

  const activeProducts = hasActiveFilters ? filteredProducts : products;
  const activePage = hasActiveFilters ? filteredPage : currentPage;
  const activePages = hasActiveFilters ? filteredPages : totalPages;
  const activeTotal = hasActiveFilters ? filteredTotal : totalItems;
  const itemsPerPage = 15;
  const startItem = (activePage - 1) * itemsPerPage + 1;
  const endItem = Math.min(activePage * itemsPerPage, activeTotal);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  // Filter out the current category
  const moveTargetCategories = categories.filter(
    (c) => String(c.id ?? (c as any)._id) !== String(categoryId),
  );
  const selectedMoveCategory = categories.find(
    (c) => String(c.id ?? (c as any)._id) === moveTarget,
  );

  // Effect: Fetch products when filters change
  useEffect(() => {
    if (!hasActiveFilters) {
      setFilteredProducts(products);
      setFilteredTotal(totalItems);
      setFilteredPages(totalPages);
      return;
    }
    const run = async () => {
      try {
        setFilterLoading(true);
        const filtersToApply = categoryId
          ? { ...filters, category_ids: String(categoryId) }
          : filters;
        const res = await fetchProducts(filtersToApply, filteredPage);
        setFilteredProducts(res.data);
        setFilteredTotal(res.pagination.total_items);
        setFilteredPages(res.pagination.total_pages);
      } catch (err) {
        console.error("Filter fetch error:", err);
      } finally {
        setFilterLoading(false);
      }
    };
    run();
  }, [filters, filteredPage]);

  // Sync when parent refreshes
  useEffect(() => {
    if (!hasActiveFilters) {
      setFilteredProducts(products);
      setFilteredTotal(totalItems);
      setFilteredPages(totalPages);
    }
  }, [products]);

  // Effect: Close dropdowns on outside click
  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (
        manageDropdownRef.current &&
        !manageDropdownRef.current.contains(e.target as Node)
      ) {
        setManageDropdownOpen(false);
      }
      if (
        moveCategoryRef.current &&
        !moveCategoryRef.current.contains(e.target as Node)
      ) {
        setMoveCategoryDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  // ---Handlers---
  const handlePickBulkMode = (mode: BulkMode) => {
    setManageDropdownOpen(false);
    setLocalSelectedIds([]);
    setMoveTarget("");
    setBulkMode(mode);
  };

  const handleCancelBulk = () => {
    setBulkMode(null);
    setLocalSelectedIds([]);
    setMoveTarget("");
  };

  const handleToggleSelect = (productId: string) => {
    setLocalSelectedIds((prev) =>
      prev.includes(productId)
        ? prev.filter((id) => id !== productId)
        : [...prev, productId],
    );
  };

  const toast = (message: string, type: "success" | "error") => {
    onToast?.(message, type);
  };

  // ---API Integration Handlers---
  const confirmBulkMove = async () => {
    if (!moveTarget || localSelectedIds.length === 0) return;
    setIsActioning(true);
    try {
      const res = await bulkMoveProducts(localSelectedIds, moveTarget);
      const { moved, failed } = res;
      if (failed > 0) {
        toast(`${moved} moved, ${failed} failed.`, "error");
      } else {
        toast(
          `${moved} product${moved > 1 ? "s" : ""} moved successfully!`,
          "success",
        );
      }
      handleCancelBulk();
      onDeleteSuccess();
    } catch {
      toast("Bulk move failed. Please try again.", "error");
    } finally {
      setIsActioning(false);
    }
  };

  const confirmBulkRemove = async () => {
    if (localSelectedIds.length === 0) return;
    if (
      !window.confirm(
        `Remove ${localSelectedIds.length} product(s) from this category? They will move to Uncategorized.`,
      )
    )
      return;
    try {
      await bulkRemoveFromCategory(localSelectedIds);
      toast(
        `${localSelectedIds.length} product(s) removed from category.`,
        "success",
      );
      handleCancelBulk();
      onDeleteSuccess();
    } catch {
      toast("Failed to remove products.", "error");
    }
  };

  const confirmBulkDelete = async () => {
    if (localSelectedIds.length === 0) return;
    if (
      !window.confirm(
        `Permanently delete ${localSelectedIds.length} product(s)? This cannot be undone.`,
      )
    )
      return;
    try {
      await bulkDeleteProducts(localSelectedIds);
      toast(`${localSelectedIds.length} product(s) deleted.`, "success");
      handleCancelBulk();
      onDeleteSuccess();
    } catch {
      toast("Failed to delete products.", "error");
    }
  };
  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await bulkUploadCSV(file);
      setUploadResult(result);
      onDeleteSuccess();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data) {
        setUploadResult(err.response.data);
      } else {
        toast("CSV upload failed.", "error");
      }
    }
    e.target.value = "";
  };

  return (
    <main className="inventory-container">
      <header className="list-header">
        <div className="header-content">
          <div className="title-section">
            <h2>Product Inventory</h2>
          </div>

          <div className="action-button-group">
            {!categoryTitle && (
              <>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  style={{ display: "none" }}
                  onChange={handleCSVUpload}
                />
                <button
                  className="btn-upload-csv"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <FiUpload size={15} /> Upload CSV
                </button>
              </>
            )}

            {/* Manage Products dropdown — only shown inside a category */}
            {categoryTitle && (
              <div className="manage-dropdown-wrapper" ref={manageDropdownRef}>
                <button
                  className={`btn-manage-products ${bulkMode ? "is-active" : ""}`}
                  onClick={() => setManageDropdownOpen((p) => !p)}
                  type="button"
                >
                  Manage Products <FiChevronDown />
                </button>

                {manageDropdownOpen && (
                  <div className="manage-dropdown-menu">
                    <button
                      className="manage-dropdown-item"
                      onClick={() => handlePickBulkMode("move")}
                    >
                      <FiArrowUpRight className="manage-item-icon move-icon" />
                      <div>
                        <div className="manage-item-title">
                          Move to Category
                        </div>
                        <div className="manage-item-desc">
                          Move selected products to another category
                        </div>
                      </div>
                    </button>

                    <button
                      className="manage-dropdown-item"
                      onClick={() => handlePickBulkMode("remove")}
                    >
                      <FiX className="manage-item-icon remove-icon" />
                      <div>
                        <div className="manage-item-title">
                          Remove from Category
                        </div>
                        <div className="manage-item-desc">
                          Move selected products to Uncategorized
                        </div>
                      </div>
                    </button>

                    <div className="manage-dropdown-divider" />

                    <button
                      className="manage-dropdown-item is-danger"
                      onClick={() => handlePickBulkMode("delete")}
                    >
                      <FiTrash2 className="manage-item-icon delete-icon" />
                      <div>
                        <div className="manage-item-title">Delete Products</div>
                        <div className="manage-item-desc">
                          Permanently delete selected products
                        </div>
                      </div>
                    </button>
                  </div>
                )}
              </div>
            )}

            <button
              className="add-button"
              onClick={() =>
                navigate("/add-product", {
                  state: {
                    from: categoryTitle ? "category" : "dashboard",
                    categoryTitle,
                    categoryId,
                  },
                })
              }
            >
              <FiPlus /> Add Product
            </button>
          </div>
        </div>
      </header>
      {/* Upload Feedback Banner*/}
      {uploadResult && (
        <div
          className={`upload-result-banner ${uploadResult.success === 0 ? "upload-all-failed" : ""}`}
        >
          {uploadResult.success > 0 && (
            <span>✓ {uploadResult.success} products added</span>
          )}
          {uploadResult.failed > 0 && (
            <span className="upload-failed">
              ✕ {uploadResult.failed} failed
            </span>
          )}
          {uploadResult.success === 0 && uploadResult.failed === 0 && (
            <span>CSV was empty — no products found.</span>
          )}
          <button
            className="upload-result-close"
            onClick={() => setUploadResult(null)}
          >
            ✕
          </button>
        </div>
      )}

      <ProductFilters
        filters={filters}
        categories={categories}
        onChange={(updated) => {
          setFilters(updated);
          setFilteredPage(1);
        }}
        onReset={() => {
          setFilters({});
          setFilteredPage(1);
        }}
        lockedCategoryId={categoryId}
      />

      <p className="product-count">
        {hidePagination ? (
          <>
            Showing <span>{activeProducts.length}</span> items
          </>
        ) : (
          <>
            Showing{" "}
            <span>
              {startItem}–{endItem}
            </span>{" "}
            of <span>{activeTotal}</span> items
          </>
        )}
      </p>

      {filterLoading ? (
        <div className="loading">Filtering…</div>
      ) : activeProducts.length > 0 ? (
        <div className="product-grid">
          {activeProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              categories={categories}
              onDeleteSuccess={onDeleteSuccess}
              selectedIds={bulkMode ? localSelectedIds : []}
              onToggleSelect={bulkMode ? handleToggleSelect : undefined}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state-container">
          <div className="empty-box">
            <FaBoxOpen />
          </div>
          <h3>No items in inventory</h3>
          <p>
            Couldn't find any products. Try adding a new item or clearing your
            filters.
          </p>
        </div>
      )}

      {!hidePagination && (
        <div className="pagination-bar">
          <button
            disabled={activePage <= 1}
            onClick={() =>
              hasActiveFilters
                ? setFilteredPage(activePage - 1)
                : onPageChange(activePage - 1)
            }
          >
            ← Prev
          </button>
          <span>
            Page {activePage} of {activePages}
          </span>
          <button
            disabled={activePage >= activePages}
            onClick={() =>
              hasActiveFilters
                ? setFilteredPage(activePage + 1)
                : onPageChange(activePage + 1)
            }
          >
            Next →
          </button>
        </div>
      )}

      {/* ── Bottom action panel: Move ───────────────────────────── */}
      {bulkMode === "move" && (
        <div className="bulk-bottom-panel">
          <div className="bulk-panel-left">
            <span className="bulk-panel-count">
              {localSelectedIds.length > 0
                ? `${localSelectedIds.length} product${localSelectedIds.length > 1 ? "s" : ""} selected`
                : "No products selected"}
            </span>
          </div>

          <div className="bulk-panel-right">
            <div className="bulk-category-picker" ref={moveCategoryRef}>
              <button
                className="bulk-category-btn"
                onClick={() => setMoveCategoryDropdownOpen((p) => !p)}
                type="button"
              >
                <span>
                  {selectedMoveCategory
                    ? selectedMoveCategory.title
                    : "Select category…"}
                </span>
                <FiChevronDown />
              </button>

              {moveCategoryDropdownOpen && (
                <div className="bulk-category-menu">
                  {moveTargetCategories.length === 0 ? (
                    <p className="bulk-category-empty">
                      No other categories found
                    </p>
                  ) : (
                    moveTargetCategories.map((c) => (
                      <button
                        key={String(c.id ?? (c as any)._id)}
                        className="bulk-category-option"
                        onClick={() => {
                          setMoveTarget(String(c.id ?? (c as any)._id));
                          setMoveCategoryDropdownOpen(false);
                        }}
                      >
                        {c.title}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            <button
              className="bulk-panel-confirm-btn"
              onClick={confirmBulkMove}
              disabled={
                !moveTarget || localSelectedIds.length === 0 || isActioning
              }
            >
              {isActioning ? "Moving…" : "Move Products"}
            </button>

            <button
              className="bulk-panel-cancel-btn"
              onClick={handleCancelBulk}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* ── Bottom action panel: Remove ─────────────────────────── */}
      {bulkMode === "remove" && (
        <div className="bulk-bottom-panel">
          <div className="bulk-panel-left">
            <span className="bulk-panel-count">
              {localSelectedIds.length > 0
                ? `${localSelectedIds.length} product${localSelectedIds.length > 1 ? "s" : ""} selected`
                : "No products selected"}
            </span>
          </div>
          <div className="bulk-panel-right">
            <button
              className="bulk-panel-confirm-btn is-amber"
              onClick={confirmBulkRemove}
              disabled={localSelectedIds.length === 0}
            >
              Remove from Category
            </button>
            <button
              className="bulk-panel-cancel-btn"
              onClick={handleCancelBulk}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* ── Bottom action panel: Delete ─────────────────────────── */}
      {bulkMode === "delete" && (
        <div className="bulk-bottom-panel is-danger">
          <div className="bulk-panel-left">
            <span className="bulk-panel-count">
              {localSelectedIds.length > 0
                ? `${localSelectedIds.length} product${localSelectedIds.length > 1 ? "s" : ""} selected`
                : "No products selected"}
            </span>
          </div>
          <div className="bulk-panel-right">
            <button
              className="bulk-panel-confirm-btn is-red"
              onClick={confirmBulkDelete}
              disabled={localSelectedIds.length === 0}
            >
              Delete Permanently
            </button>
            <button
              className="bulk-panel-cancel-btn"
              onClick={handleCancelBulk}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </main>
  );
};

export default ProductList;
