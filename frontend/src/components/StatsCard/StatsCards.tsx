/**
 * Shows quick stats based on product data
 */
import React from "react";
import { Product } from "../../type";
import "./StatsCards.css";
import { FaClock, FaExclamationTriangle, FaRupeeSign } from "react-icons/fa";
import { MdInventory } from "react-icons/md";

interface StatsCardsProps {
  products: Product[];
}

const StatsCards = ({ products }: StatsCardsProps) => {
  // total number of products
  const totalProducts = products.length;

  //products that are low in stock
  const lowStockItems = products.filter(
    (p) =>
      p.warehouse_quantity <= p.low_stock_threshold && p.warehouse_quantity > 0,
  ).length;

  // products expiring within 30 days
  const expiringSoon = products.filter((p) => {
    if (!p.is_perishable || !p.expiry_date) return false;
    const days = Math.ceil(
      (new Date(p.expiry_date).getTime() - new Date().getTime()) /
        (1000 * 60 * 60 * 24),
    );
    return days <= 30 && days > 0;
  }).length;

  // total inventory value
  const totalInventoryValue = products.reduce((acc, p) => {
    return acc + Number(p.selling_price) * p.warehouse_quantity;
  }, 0);

  // data used to render each stat card
  const stats = [
    {
      label: "Total Products",
      value: totalProducts,
      subtitle: "items in system",
      icon: <MdInventory />,
      accent: "blue",
    },
    {
      label: "Low Stock Items",
      value: lowStockItems,
      subtitle: "need restocking",
      icon: <FaExclamationTriangle />,
      accent: "orange",
    },
    {
      label: "Expiring Soon",
      value: expiringSoon,
      subtitle: "within 30 days",
      icon: <FaClock />,
      accent: "amber",
    },
    {
      label: "Inventory Value",
      value: `₹${totalInventoryValue.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`,
      subtitle: "total stock value",
      icon: <FaRupeeSign />,
      accent: "green",
    },
  ];

  return (
    <div className="stats-grid">
      {/* render each stat card */}
      {stats.map((stat) => (
        <div key={stat.label} className={`stat-card accent-${stat.accent}`}>
          <div className="stat-header">
            <span className="stat-icon">{stat.icon}</span>
            <span className="stat-label">{stat.label}</span>
          </div>
          <div className="stat-value">{stat.value}</div>
          <div className="stat-subtitle">{stat.subtitle}</div>
        </div>
      ))}
    </div>
  );
};

export default StatsCards;
