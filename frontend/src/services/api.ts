/**
 * api.ts — all HTTP calls to the Django backend.
 */

import {
  Product,
  PaginatedResponse,
  Category,
  CategoryListResponse,
  ProductFilters,
} from "../type";
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api/products/";
const CAT_URL = "http://127.0.0.1:8000/api/categories/";

// ── Product Endpoints ─────────────────────────────────────────

// Paginated full product list — used by the dashboard
export const fetchInventory = async (
  page: number,
): Promise<PaginatedResponse> => {
  const response = await axios.get(`${BASE_URL}?page=${page}`);
  return response.data;
};

// Paginated list with active filters — used by ProductList when filters are applied
export const fetchProducts = async (
  filters: ProductFilters,
  page: number = 1,
): Promise<PaginatedResponse> => {
  const params = new URLSearchParams();
  params.append("page", String(page));
  if (filters.search) params.append("search", filters.search);
  if (filters.brand) params.append("brand", filters.brand);
  if (filters.category_ids) params.append("category_ids", filters.category_ids);
  if (filters.min_price !== undefined)
    params.append("min_price", String(filters.min_price));
  if (filters.max_price !== undefined)
    params.append("max_price", String(filters.max_price));
  if (filters.low_stock) params.append("low_stock", "true");

  const response = await axios.get(`${BASE_URL}?${params.toString()}`);
  return response.data;
};

// Single product by ID — used by ProductPage
export const fetchProductDetail = async (id: string): Promise<Product> => {
  const response = await axios.get(`${BASE_URL}${id}/`);
  return response.data;
};

// Partial update (PATCH) — used by ProductPage edit form
export const updateProduct = async (
  id: string,
  data: Partial<Product>,
): Promise<any> => {
  const response = await axios.patch(`${BASE_URL}${id}/`, data);
  return response.data;
};

// Creates a new product
export const createProduct = async (data: any): Promise<{ id: string }> => {
  const response = await axios.post(BASE_URL, data);
  return response.data;
};

// Hard delete — used by ProductPage and ProductDetailModal
export const deleteProduct = async (id: string): Promise<void> => {
  await axios.delete(`${BASE_URL}${id}/`);
};

// ── Category Endpoints ────────────────────────────────────────

// Full category list — passed down from App.tsx to all components
export const fetchCategories = async (): Promise<Category[]> => {
  const response = await axios.get(CAT_URL);
  return response.data;
};

// Single category by ID
export const fetchCategoryDetail = async (id: string): Promise<Category> => {
  const response = await axios.get(`${CAT_URL}${id}/`);
  return response.data;
};

export const createCategory = async (data: {
  title: string;
  description?: string;
}): Promise<{ id: string; message: string }> => {
  const response = await axios.post(CAT_URL, data);
  return response.data;
};

export const updateCategory = async (
  id: string,
  data: any,
): Promise<{ message: string; category: Category }> => {
  const response = await axios.patch(`${CAT_URL}${id}/`, data);
  return response.data;
};

export const deleteCategory = async (id: string): Promise<void> => {
  await axios.delete(`${CAT_URL}${id}/`);
};

// Products scoped to a single category — used by CategoryDetail
export const fetchProductsByCategory = async (
  id: string,
): Promise<Product[]> => {
  const response = await axios.get(`${BASE_URL}category/${id}/`);
  return response.data;
};

// ── Stats Endpoints ───────────────────────────────────────────

// Hits the filter API with low_stock=true and reads total count from pagination metadata
export const fetchLowStockCount = async (): Promise<number> => {
  const response = await axios.get(`${BASE_URL}?low_stock=true&page=1`);
  return response.data.pagination.total_items;
};

// Computes expiring product count from pagination metadata
export const fetchExpiringSoonCount = async (): Promise<number> => {
  const thirtyDaysFromNow = new Date();
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
  const dateStr = thirtyDaysFromNow.toISOString().split("T")[0];
  const response = await axios.get(
    `${BASE_URL}?expires_before=${dateStr}&page=1`,
  );
  return response.data.pagination.total_items;
};

// ── Bulk Operations ───────────────────────────────────────────

// Moves selected products to Uncategorized
export const bulkRemoveFromCategory = async (productIds: string[]) => {
  const response = await axios.post(`${BASE_URL}category/bulk-remove/`, {
    product_ids: productIds,
  });
  return response.data;
};

// Permanently deletes selected products
export const bulkDeleteProducts = async (productIds: string[]) => {
  const response = await axios.post(`${BASE_URL}bulk-delete/`, {
    product_ids: productIds,
  });
  return response.data;
};

// Multipart POST — sends CSV file to backend for bulk product creation
export const bulkUploadCSV = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(`${BASE_URL}bulk-upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Moves selected products to a different category
export const bulkMoveProducts = async (
  productIds: string[],
  categoryId: string,
) => {
  const response = await axios.post(`${BASE_URL}category/bulk-move/`, {
    product_ids: productIds,
    category_id: categoryId,
  });
  return response.data;
};
