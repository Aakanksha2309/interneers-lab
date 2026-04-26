/*
 * Defines the shape of Product and Category data used in the app.
 */

export interface Product {
  id: string;
  name: string;
  brand: string;
  description?: string;
  category_id: string;
  warehouse_quantity: number;
  low_stock_threshold: number;
  is_perishable: boolean;
  expiry_date?: string;
  selling_price: string;
  cost_price: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse {
  status: string;
  data: Product[];
  pagination: {
    total_items: number;
    total_pages: number;
    current_page: number;
    has_next: boolean;
    has_prev: boolean;
    total_inventory_value:number;
  };
}

export interface Category {
  id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export type CategoryListResponse = Category[];

export interface ProductFilters {
  search?: string;
  brand?: string;
  category_ids?: string;
  min_price?: number;
  max_price?: number;
  low_stock?: boolean;
}
