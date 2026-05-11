/**
 * Shows quick stats based on product data
 */
import React from "react";
import { Product } from "../../type";
import "./StatsCards.css";
import { FaClock, FaExclamationTriangle, FaRupeeSign } from "react-icons/fa";
import { MdInventory } from "react-icons/md";

interface StatsCardsProps {
  totalItems: number;
  lowStockCount: number;
  expiringSoonCount: number;
  inventoryValue: number;
}

const StatsCards = ({
  totalItems,
  lowStockCount,
  expiringSoonCount,
  inventoryValue,
}: StatsCardsProps) => {
  // data used to render each stat card
  const stats = [
    {
      label: "Total Products",
      value: totalItems,
      subtitle: "items in system",
      icon: <MdInventory />,
      accent: "blue",
    },
    {
      label: "Low Stock Items",
      value: lowStockCount,
      subtitle: "need restocking",
      icon: <FaExclamationTriangle />,
      accent: "orange",
    },
    {
      label: "Expiring Soon",
      value: expiringSoonCount,
      subtitle: "within 30 days",
      icon: <FaClock />,
      accent: "amber",
    },
    {
      label: "Inventory Value",
      value: `₹${inventoryValue.toLocaleString("en-IN", {
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
