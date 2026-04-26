/**
 * Temporary mock data for products and categories.
 * Used for testing UI and features before connecting to the backend.
 */
import { Product } from "./type";
import { Category } from "./type";

export const MOCK_CATEGORIES: Category[] = [
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d0",
    title: "Electronics",
    description: "High-tech gadgets, entertainment systems, and accessories.",
    created_at: "2026-01-01T10:00:00Z",
    updated_at: "2026-01-01T10:00:00Z",
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d1",
    title: "Pantry",
    description: "Daily food essentials, fresh produce, and perishable goods.",
    created_at: "2026-01-01T10:00:00Z",
    updated_at: "2026-01-01T10:00:00Z",
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d2",
    title: "Home Office",
    description: "Furniture and tools designed for a productive workspace.",
    created_at: "2026-01-02T12:00:00Z",
    updated_at: "2026-01-02T12:00:00Z",
  },
  {
    id: "65f2b1a2c3d4e5f6a7b8c9d3",
    title: "Personal Care",
    description: "Health, beauty, and hygiene products for daily routines.",
    created_at: "2026-01-03T09:00:00Z",
    updated_at: "2026-01-03T09:00:00Z",
  },
];
export const MOCK_PRODUCTS: Product[] = [
  {
    id: "65f3c2b3d4e5f6a7b8c9d001",
    name: "Desk Chair",
    brand: "SteelSeries",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d2", // Home Office
    warehouse_quantity: 8,
    low_stock_threshold: 5,
    is_perishable: false,
    cost_price: "12000.00",
    selling_price: "18500.00",
    created_at: "2026-02-10T10:00:00Z",
    updated_at: "2026-04-01T15:00:00Z",
    description:
      "High-back breathable mesh chair with adjustable lumbar support and synchronized tilt mechanism for all-day comfort.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d002",
    name: "Mechanical Keyboard",
    brand: "Keychron",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 3,
    low_stock_threshold: 10, // LOW STOCK
    is_perishable: false,
    cost_price: "4500.00",
    selling_price: "7200.00",
    created_at: "2026-03-05T08:00:00Z",
    updated_at: "2026-03-05T08:00:00Z",
    description:
      "Wireless mechanical keyboard with Gateron switches and customizable RGB backlighting. Compatible with Mac and Windows.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d003",
    name: "Organic Baby Spinach",
    brand: "GreenLeaf",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 0, // OUT OF STOCK
    low_stock_threshold: 15,
    is_perishable: true,
    expiry_date: "2026-04-20T00:00:00Z",
    cost_price: "80.00",
    selling_price: "150.00",
    created_at: "2026-04-05T07:30:00Z",
    updated_at: "2026-04-05T07:30:00Z",
    description:
      "Farm-fresh, triple-washed organic spinach. Rich in iron and vitamins. Keep refrigerated for maximum freshness.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d004",
    name: "Ultra-Wide Monitor",
    brand: "Samsung",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 12,
    low_stock_threshold: 5,
    is_perishable: false,
    cost_price: "22000.00",
    selling_price: "34999.00",
    created_at: "2026-01-20T12:00:00Z",
    updated_at: "2026-03-28T10:00:00Z",
    description:
      "34-inch curved productivity monitor with 144Hz refresh rate and dual-input multitasking support.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d005",
    name: "Whole Bean Coffee",
    brand: "Blue Tokai",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 45,
    low_stock_threshold: 20,
    is_perishable: true,
    expiry_date: "2027-01-01T00:00:00Z",
    cost_price: "450.00",
    selling_price: "790.00",
    created_at: "2026-03-15T11:00:00Z",
    updated_at: "2026-03-15T11:00:00Z",
    description:
      "Medium-dark roast Arabica beans with notes of dark chocolate and roasted nuts. Sourced from high-altitude estates.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d006",
    name: "Laptop Stand",
    brand: "AluFlex",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d2", // Home Office
    warehouse_quantity: 60,
    low_stock_threshold: 15,
    is_perishable: false,
    cost_price: "850.00",
    selling_price: "1599.00",
    created_at: "2026-02-25T09:00:00Z",
    updated_at: "2026-02-25T09:00:00Z",
    description:
      "Aluminum foldable stand with 6 adjustable angles to improve posture and laptop cooling airflow.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d007",
    name: "Moisturizing Sunscreen",
    brand: "Neutrogena",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d3", // Personal Care
    warehouse_quantity: 4, // LOW STOCK
    low_stock_threshold: 15,
    is_perishable: true,
    expiry_date: "2027-06-30T00:00:00Z",
    cost_price: "350.00",
    selling_price: "675.00",
    created_at: "2026-04-01T14:00:00Z",
    updated_at: "2026-04-01T14:00:00Z",
    description:
      "Broad-spectrum SPF 50 sunscreen with a non-greasy finish. Water-resistant for up to 80 minutes.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d008",
    name: "Noise Cancelling Buds",
    brand: "Sony",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 25,
    low_stock_threshold: 10,
    is_perishable: false,
    cost_price: "12000.00",
    selling_price: "19990.00",
    created_at: "2026-03-20T10:00:00Z",
    updated_at: "2026-04-08T12:00:00Z",
    description:
      "Industry-leading noise cancellation with dual noise sensor technology and 30-hour battery life.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d009",
    name: "Almond Butter",
    brand: "NuttyFix",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 30,
    low_stock_threshold: 10,
    is_perishable: true,
    expiry_date: "2026-10-15T00:00:00Z",
    cost_price: "320.00",
    selling_price: "550.00",
    created_at: "2026-04-02T08:00:00Z",
    updated_at: "2026-04-02T08:00:00Z",
    description:
      "100% roasted almonds with zero added sugar or oils. High protein and keto-friendly snack option.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d010",
    name: "Electric Kettle",
    brand: "Philips",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 18,
    low_stock_threshold: 5,
    is_perishable: false,
    cost_price: "1100.00",
    selling_price: "2199.00",
    created_at: "2026-03-10T16:00:00Z",
    updated_at: "2026-03-10T16:00:00Z",
    description:
      "1.5L fast-boil kettle with food-grade stainless steel and automatic shut-off safety feature.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d011",
    name: "Yoga Mat",
    brand: "Lululemon",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d3", // Personal Care/Fitness
    warehouse_quantity: 0, // OUT OF STOCK
    low_stock_threshold: 8,
    is_perishable: false,
    cost_price: "2500.00",
    selling_price: "4800.00",
    created_at: "2026-01-15T10:00:00Z",
    updated_at: "2026-04-10T09:00:00Z",
    description:
      "5mm thick natural rubber mat with superior grip and cushioning for high-intensity workouts.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d012",
    name: "Wireless Mouse",
    brand: "Logitech",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 55,
    low_stock_threshold: 15,
    is_perishable: false,
    cost_price: "1800.00",
    selling_price: "3299.00",
    created_at: "2026-02-20T11:00:00Z",
    updated_at: "2026-02-20T11:00:00Z",
    description:
      "Ergonomic vertical mouse designed to reduce wrist strain. Includes programmable buttons and dual connectivity.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d013",
    name: "Oat Milk (Barista Edition)",
    brand: "Oatly",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d1", // Pantry
    warehouse_quantity: 6, // LOW STOCK
    low_stock_threshold: 24,
    is_perishable: true,
    expiry_date: "2026-08-12T00:00:00Z",
    cost_price: "180.00",
    selling_price: "350.00",
    created_at: "2026-04-01T09:00:00Z",
    updated_at: "2026-04-01T09:00:00Z",
    description:
      "Creamy plant-based milk designed to froth perfectly for lattes and cappuccinos.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d014",
    name: "Smart LED Bulb",
    brand: "Philips Hue",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d0", // Electronics
    warehouse_quantity: 110,
    low_stock_threshold: 25,
    is_perishable: false,
    cost_price: "850.00",
    selling_price: "1899.00",
    created_at: "2026-03-10T16:00:00Z",
    updated_at: "2026-03-10T16:00:00Z",
    description:
      "16 million colors and tunable white light. Controlled via app or voice using Alexa/Google Home.",
  },
  {
    id: "65f3c2b3d4e5f6a7b8c9d015",
    name: "Desk Mat (Large)",
    brand: "DeltaHub",
    category_id: "65f2b1a2c3d4e5f6a7b8c9d2", // Home Office
    warehouse_quantity: 22,
    low_stock_threshold: 10,
    is_perishable: false,
    cost_price: "1200.00",
    selling_price: "2450.00",
    created_at: "2026-02-28T14:00:00Z",
    updated_at: "2026-02-28T14:00:00Z",
    description:
      "Anti-slip felt desk pad that protects your workspace and provides a smooth surface for mouse movement.",
  },
];
