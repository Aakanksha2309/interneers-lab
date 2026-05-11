/**
 * A unified search and filtering interface. Features a debounced search bar,
 * multi-select category dropdowns, and a secondary filter panel for price and stock.
 */
import { useState, useEffect, useRef } from "react";
import { Category, ProductFilters as ProductFiltersType } from "../../type";
import "./ProductFilters.css";

interface Props {
  filters: ProductFiltersType;
  categories: Category[];
  onChange: (updated: ProductFiltersType) => void;
  onReset: () => void;
  lockedCategoryId?: string | number;
}

const ProductFilters = ({
  filters,
  categories,
  onChange,
  onReset,
  lockedCategoryId,
}: Props) => {
  // --- Local UI State ---
  const [searchInput, setSearchInput] = useState(filters.search ?? "");
  const [minPriceInput, setMinPriceInput] = useState(
    filters.min_price !== undefined ? String(filters.min_price) : "",
  );
  const [maxPriceInput, setMaxPriceInput] = useState(
    filters.max_price !== undefined ? String(filters.max_price) : "",
  );
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [filtersDropdownOpen, setFiltersDropdownOpen] = useState(false);
  const [localBrand, setLocalBrand] = useState(filters.brand ?? "");
  const [localLowStock, setLocalLowStock] = useState(!!filters.low_stock);

  const categoryRef = useRef<HTMLDivElement>(null);
  const filtersRef = useRef<HTMLDivElement>(null);

  // Debounce search — waits 400ms after user stops typing before calling API
  useEffect(() => {
    const timer = setTimeout(() => {
      onChange({ ...filters, search: searchInput || undefined });
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Close dropdowns when clicking outside the component area
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        categoryRef.current &&
        !categoryRef.current.contains(e.target as Node)
      ) {
        setCategoryDropdownOpen(false);
      }
      if (
        filtersRef.current &&
        !filtersRef.current.contains(e.target as Node)
      ) {
        setFiltersDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  // Sync local state when parent resets
  useEffect(() => {
    setSearchInput(filters.search ?? "");
    setMinPriceInput(
      filters.min_price !== undefined ? String(filters.min_price) : "",
    );
    setMaxPriceInput(
      filters.max_price !== undefined ? String(filters.max_price) : "",
    );
    setLocalBrand(filters.brand ?? "");
    setLocalLowStock(!!filters.low_stock);
  }, [filters]);

  // --- Category helpers ---

  const selectedCategoryIds: string[] = filters.category_ids
    ? filters.category_ids.split(",").filter(Boolean)
    : [];

  const toggleCategory = (id: string) => {
    const updated = selectedCategoryIds.includes(id)
      ? selectedCategoryIds.filter((c) => c !== id)
      : [...selectedCategoryIds, id];
    onChange({
      ...filters,
      category_ids: updated.length > 0 ? updated.join(",") : undefined,
    });
  };

  const lockedCategory = lockedCategoryId
    ? categories.find(
        (c) => String(c.id ?? (c as any)._id) === String(lockedCategoryId),
      )
    : null;

  const categoryLabel = lockedCategory
    ? lockedCategory.title
    : selectedCategoryIds.length === 0
      ? "Category"
      : selectedCategoryIds.length === 1
        ? (categories.find((c) => c.id === selectedCategoryIds[0])?.title ??
          "1 selected")
        : `${selectedCategoryIds.length} categories`;

  /* --- Filter Application --- */
  const handleApplyAllFilters = () => {
    const min = minPriceInput !== "" ? parseFloat(minPriceInput) : undefined;
    const max = maxPriceInput !== "" ? parseFloat(maxPriceInput) : undefined;

    onChange({
      ...filters,
      brand: localBrand || undefined,
      low_stock: localLowStock || undefined,
      min_price: min,
      max_price: max,
    });

    setFiltersDropdownOpen(false);
  };

  const handlePriceKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleApplyAllFilters();
  };

  // ── Active filter counts ────────────────────────────────────────────

  const hasActiveFilters =
    !!filters.search ||
    !!filters.brand ||
    !!filters.category_ids ||
    filters.min_price !== undefined ||
    filters.max_price !== undefined ||
    !!filters.low_stock;

  // Count active secondary filters (brand + price + low stock) for badge
  const secondaryFilterCount = [
    !!filters.brand,
    filters.min_price !== undefined || filters.max_price !== undefined,
    !!filters.low_stock,
  ].filter(Boolean).length;

  return (
    <div className="filterbar">
      {/* ── Search input -─ */}
      <div className="filterbar-search">
        <svg className="filterbar-search-icon" viewBox="0 0 20 20" fill="none">
          <circle
            cx="8.5"
            cy="8.5"
            r="5.5"
            stroke="currentColor"
            strokeWidth="1.8"
          />
          <path
            d="M13 13l3.5 3.5"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
        <input
          className="filterbar-search-input"
          type="text"
          placeholder="Search products by name…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        {searchInput && (
          <button
            className="filterbar-search-clear"
            onClick={() => setSearchInput("")}
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      {/* --- Category pill dropdown ---*/}
      <div className="filterbar-pill-wrapper" ref={categoryRef}>
        <button
          className={`filterbar-pill${selectedCategoryIds.length > 0 || lockedCategoryId ? " is-active" : ""}${categoryDropdownOpen ? " is-open" : ""}${lockedCategoryId ? " is-locked" : ""}`}
          onClick={() => {
            if (lockedCategoryId) return;
            setCategoryDropdownOpen((p) => !p);
            setFiltersDropdownOpen(false);
          }}
          type="button"
        >
          {categoryLabel}
          <svg
            className={`filterbar-pill-chevron${categoryDropdownOpen ? " is-flipped" : ""}`}
            viewBox="0 0 20 20"
            fill="none"
          >
            <path
              d="M5 8l5 5 5-5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
        </button>

        {categoryDropdownOpen && (
          <div className="filterbar-dropdown">
            {categories.length === 0 && (
              <p className="filterbar-dropdown-empty">No categories found</p>
            )}
            {categories.map((cat) => (
              <label key={cat.id} className="filterbar-dropdown-option">
                <input
                  type="checkbox"
                  checked={selectedCategoryIds.includes(cat.id)}
                  onChange={() => toggleCategory(cat.id)}
                />
                <span>{cat.title}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* --- Filters pill --- */}
      <div className="filterbar-pill-wrapper" ref={filtersRef}>
        <button
          className={`filterbar-pill${secondaryFilterCount > 0 ? " is-active" : ""}${filtersDropdownOpen ? " is-open" : ""}`}
          onClick={() => {
            setFiltersDropdownOpen((p) => !p);
            setCategoryDropdownOpen(false);
          }}
          type="button"
        >
          {/* Filter icon */}
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
            <path
              d="M3 5h14M6 10h8M9 15h2"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
          Filters
          {secondaryFilterCount > 0 && (
            <span className="filterbar-pill-badge">{secondaryFilterCount}</span>
          )}
          <svg
            className={`filterbar-pill-chevron${filtersDropdownOpen ? " is-flipped" : ""}`}
            viewBox="0 0 20 20"
            fill="none"
          >
            <path
              d="M5 8l5 5 5-5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
        </button>

        {filtersDropdownOpen && (
          <div className="filterbar-dropdown filterbar-filters-panel">
            {/* Brand */}
            <div className="filters-panel-field">
              <label className="filters-panel-label">Brand</label>
              <input
                className="filters-panel-input"
                type="text"
                placeholder="e.g. Samsung"
                value={localBrand}
                onChange={(e) =>
                  onChange({ ...filters, brand: e.target.value || undefined })
                }
              />
            </div>

            {/* Price range */}
            <div className="filters-panel-field">
              <label className="filters-panel-label">Price Range (₹)</label>
              <div className="filters-panel-price-row">
                <input
                  className="filters-panel-input filters-panel-price-input"
                  type="number"
                  placeholder="Min"
                  min={0}
                  value={minPriceInput}
                  onChange={(e) => setMinPriceInput(e.target.value)}
                  onKeyDown={handlePriceKeyDown}
                />
                <span className="filters-panel-price-sep">–</span>
                <input
                  className="filters-panel-input filters-panel-price-input"
                  type="number"
                  placeholder="Max"
                  min={0}
                  value={maxPriceInput}
                  onChange={(e) => setMaxPriceInput(e.target.value)}
                  onKeyDown={handlePriceKeyDown}
                />
              </div>
            </div>

            {/* Low stock toggle */}
            <div className="filters-panel-field">
              <label className="filters-panel-label">Stock</label>
              <label className="filters-panel-toggle">
                <input
                  type="checkbox"
                  className="filters-panel-toggle-checkbox"
                  checked={localLowStock}
                  onChange={(e) => setLocalLowStock(e.target.checked)}
                />
                <span className="filters-panel-toggle-track">
                  <span className="filters-panel-toggle-thumb" />
                </span>
                <span className="filters-panel-toggle-text">
                  Low stock only
                </span>
              </label>
            </div>

            <div className="filter-panel-footer">
              <button
                className="filter-apply-btn"
                onClick={() => {
                  handleApplyAllFilters(); // triggers the onChange
                  setFiltersDropdownOpen(false); // Closes the dropdown
                }}
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Reset — only when filters are active */}
      <button
        className="filterbar-reset"
        onClick={onReset}
        type="button"
        style={{
          visibility: hasActiveFilters ? "visible" : "hidden",
          pointerEvents: hasActiveFilters ? "auto" : "none",
        }}
      >
        ✕ Reset
      </button>
    </div>
  );
};

export default ProductFilters;
