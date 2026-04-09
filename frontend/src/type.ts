
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


export interface Category {
  id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}