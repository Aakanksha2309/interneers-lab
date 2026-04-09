import {Product} from './type';
import { Category } from './type';


export const MOCK_CATEGORIES: Category[] = [
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d0",
    title: "Electronics",
    description: "High-tech gadgets, entertainment systems, and accessories.",
    created_at: "2026-01-01T10:00:00Z",
    updated_at: "2026-01-01T10:00:00Z"
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d1",
    title: "Pantry",
    description: "Daily food essentials, fresh produce, and perishable goods.",
    created_at: "2026-01-01T10:00:00Z",
    updated_at: "2026-01-01T10:00:00Z"
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d2",
    title: "Home Office",
    description: "Furniture and tools designed for a productive workspace.",
    created_at: "2026-01-02T12:00:00Z",
    updated_at: "2026-01-02T12:00:00Z"
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d3",
    title: "Personal Care",
    description: "Health, beauty, and hygiene products for daily routines.",
    created_at: "2026-01-03T09:00:00Z",
    updated_at: "2026-01-03T09:00:00Z"
  }
];
export const MOCK_PRODUCTS: Product[] = [
  // ... (previous ones)
  {
    id: "65f3c2b3d4e5f6a7b8c9d033",
    name: "Ergonomic Desk Chair",
    brand: "SteelSeries",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d2", // Home Office
    warehouse_quantity: 8,
    low_stock_threshold: 5,
    is_perishable: false,
    cost_price: "120.00",
    selling_price: "249.99",
    created_at: "2026-02-10T10:00:00Z",
    updated_at: "2026-04-01T15:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d044",
    name: "Electric Toothbrush",
    brand: "Oral-B",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d3", // Personal Care
    warehouse_quantity: 2, // CRITICAL STOCK
    low_stock_threshold: 10,
    is_perishable: false,
    cost_price: "45.00",
    selling_price: "89.00",
    created_at: "2026-03-05T08:00:00Z",
    updated_at: "2026-03-05T08:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d055",
    name: "Organic Spinach",
    brand: "GreenLeaf",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 0, // OUT OF STOCK
    low_stock_threshold: 15,
    is_perishable: true,
    expiry_date: "2026-04-12T00:00:00Z",
    cost_price: "1.10",
    selling_price: "3.50",
    created_at: "2026-04-05T07:30:00Z",
    updated_at: "2026-04-05T07:30:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d066",
    name: "4K Projector",
    brand: "Lumina",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 12,
    low_stock_threshold: 3,
    is_perishable: false,
    cost_price: "600.00",
    selling_price: "1199.99",
    created_at: "2026-01-20T12:00:00Z",
    updated_at: "2026-03-28T10:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d077",
    name: "Whole Bean Coffee",
    brand: "DarkRoast",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 45,
    low_stock_threshold: 20,
    is_perishable: true,
    expiry_date: "2027-01-01T00:00:00Z",
    cost_price: "8.00",
    selling_price: "18.50",
    created_at: "2026-03-15T11:00:00Z",
    updated_at: "2026-03-15T11:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d088",
    name: "Laptop Stand",
    brand: "AluFlex",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d2", // Home Office
    warehouse_quantity: 60,
    low_stock_threshold: 15,
    is_perishable: false,
    cost_price: "12.00",
    selling_price: "34.99",
    created_at: "2026-02-25T09:00:00Z",
    updated_at: "2026-02-25T09:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d099",
    name: "Hydrating Face Mask",
    brand: "GlowUp",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d3", // Personal Care
    warehouse_quantity: 4, // LOW STOCK
    low_stock_threshold: 20,
    is_perishable: true,
    expiry_date: "2027-12-31T00:00:00Z",
    cost_price: "2.50",
    selling_price: "7.99",
    created_at: "2026-04-01T14:00:00Z",
    updated_at: "2026-04-01T14:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d110",
    name: "Smart LED Bulb",
    brand: "HueLight",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 110,
    low_stock_threshold: 25,
    is_perishable: false,
    cost_price: "5.00",
    selling_price: "14.00",
    created_at: "2026-03-10T16:00:00Z",
    updated_at: "2026-03-10T16:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d111",
    name: "Noise Cancelling Buds",
    brand: "AudioPro",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 9,
    low_stock_threshold: 10, // JUST UNDER THRESHOLD
    is_perishable: false,
    cost_price: "40.00",
    selling_price: "129.99",
    created_at: "2026-03-20T10:00:00Z",
    updated_at: "2026-04-08T12:00:00Z"
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d112",
    name: "Almond Butter",
    brand: "NuttyFix",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 30,
    low_stock_threshold: 10,
    is_perishable: true,
    expiry_date: "2026-10-15T00:00:00Z",
    cost_price: "4.00",
    selling_price: "9.50",
    created_at: "2026-04-02T08:00:00Z",
    updated_at: "2026-04-02T08:00:00Z"
  }
];