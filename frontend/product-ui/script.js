/**
 * Product Listing Page (Vanilla JS)
 * Handles product & category fetching, filters, pagination, and UI rendering.
 */

// Global store for pagination, categories, and active filters
const state = {
  currentPage: 1,
  categories: [],
  filters: {
    search: "",
    category: "",
    min_price: "",
    max_price: "",
    low_stock: false,
    expiry: "",
  },
};

// Populates category dropdown and triggers initial data load
async function initApp() {
  try {
    // Fetch all categories from backend
    const response = await fetch("http://localhost:8001/api/categories/");
    const categories = await response.json();

    // Store categories globally
    state.categories = categories;
    const titlesArray = categories.map((cat) => cat.title);
    console.log("Category Titles Array:", titlesArray);

    // Populate dropdown dynamically
    const select = document.getElementById("category-select");
    categories.forEach((cat) => {
      const option = document.createElement("option");
      option.value = cat.id;
      option.textContent = cat.title;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Initialization Error:", err);
  }
  // Load products after categories are ready
  fetchProducts();
}

// Builds query string from state and fetches products from Django
async function fetchProducts() {
  const listContainer = document.getElementById("product-list");
  // Helps construct URL
  const params = new URLSearchParams();

  params.append("page", state.currentPage);
  params.append("limit", 10);
  console.log(params.page);

  // Add filters if user has provided values
  if (state.filters.search) params.append("search", state.filters.search);
  if (state.filters.category) params.append("category_ids", state.filters.category);
  if (state.filters.min_price) params.append("min_price", state.filters.min_price);
  if (state.filters.max_price) params.append("max_price", state.filters.max_price);
  if (state.filters.low_stock) params.append("low_stock", "true");
  if (state.filters.expiry) params.append("expires_before", state.filters.expiry);

  try {
    // Call backend API with filters applied
    const response = await fetch(
      `http://localhost:8001/api/products/?${params.toString()}`
    );
    const result = await response.json();

    console.log("--- New Product Data Received ---");
    console.table(result.data);

    document.getElementById("product-count").textContent =
      `Found ${result.data.length} items`;

    renderUI(result.data);
    handlePaginationUI(result.pagination);
  } catch (error) {
    // Show fallback UI if backend is down
    listContainer.innerHTML = `<div class="error-msg">Backend Offline (Check Port 8001)</div>`;
  }
}

// Converts product data into UI cards dynamically
function renderUI(products) {
  const listContainer = document.getElementById("product-list");
  listContainer.innerHTML = "";

  if (products.length === 0) {
    listContainer.innerHTML =
      '<div class="empty-state">No products found.</div>';
    return;
  }

  // Formatter for INR currency display
  const rupee = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
  });

  products.forEach((p) => {
    // Check if product is low in stock
    const isLow = p.warehouse_quantity <= (p.low_stock_threshold || 10);

    // Find matching category title from stored categories
    const categoryMatch = state.categories.find((cat) => cat.id == p.category_id);
    const categoryTitle = categoryMatch ? categoryMatch.title : "General";

    // Modify Product display tile dynamically
    const card = document.createElement("div");
    card.className = `product-card ${isLow ? "low-stock-alert" : ""}`;
    card.innerHTML = `
      <div class="product-image-preview">
        <img src="${p.image_url}"
          onerror="this.src='https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=80&h=80'"
          alt="${p.name}">
      </div>
      <div class="info-section">
        <span class="category-tag">${categoryTitle}</span>
        <h3>${p.name}</h3>
        <p class="brand-subtext">Brand: ${p.brand}</p>
        <p class="description-subtext">Description: ${p.description}</p>
      </div>
      <div class="stats-section">
        <div class="price-text">${rupee.format(p.selling_price)}</div>
        <div class="stock-count" style="color: ${isLow ? "#d9534f" : "#28a745ff"}">
          Stock: <strong>${p.warehouse_quantity}</strong>
        </div>
        ${
          p.is_perishable
            ? `<small class="expiry-text">Expires: ${new Date(p.expiry_date).toLocaleDateString()}</small>`
            : ""
        }
      </div>
    `;
    // Add card to DOM
    listContainer.appendChild(card);
  });
}

// Handles enabling/disabling pagination buttons
function handlePaginationUI(pagination) {
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  const pageInfo = document.getElementById("page-info");

  // Show current page info
  pageInfo.textContent = `Page ${state.currentPage} of ${pagination.total_pages || 1}`;
  // Disable buttons when needed
  prevBtn.disabled = state.currentPage <= 1;
  nextBtn.disabled = state.currentPage >= pagination.total_pages;
}

// EVENT LISTENERS: Apply filters button → updates state and fetches new data
document.getElementById("apply-filters").addEventListener("click", () => {
  state.currentPage = 1;

  state.filters.search = document.getElementById("search-input").value;
  const selectedCategoryId = document.getElementById("category-select").value;
  state.filters.category = selectedCategoryId;

  console.log("Filtering by Category ID:", state.filters.category);

  state.filters.min_price = document.getElementById("min-price").value;
  state.filters.max_price = document.getElementById("max-price").value;
  state.filters.low_stock = document.getElementById("low-stock-toggle").checked;
  state.filters.expiry = document.getElementById("expiry-filter").value;
  fetchProducts();
});

// Next page button
document.getElementById("next-page").addEventListener("click", () => {
  state.currentPage++;
  fetchProducts();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Previous page button
document.getElementById("prev-page").addEventListener("click", () => {
  if (state.currentPage > 1) {
    state.currentPage--;
    fetchProducts();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

// Reset filters → reload entire page
document.getElementById("reset-filters").addEventListener("click", () => {
  window.location.reload();
});

// Start the app
initApp();
