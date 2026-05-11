/**
 * AboutUs — static page describing InvTrack's core features.
 */
import React from "react";
import "./AboutUs.css";
import { FiPackage, FiGrid, FiBarChart2, FiZap } from "react-icons/fi";

// Feature cards
const features = [
  {
    icon: <FiPackage />,
    title: "Track Everything",
    desc: "Monitor stock levels, set low-stock alerts, and never run out of critical items again.",
  },
  {
    icon: <FiGrid />,
    title: "Organize by Category",
    desc: "Group products into categories, move them in bulk, and keep your inventory structured.",
  },
  {
    icon: <FiBarChart2 />,
    title: "Instant Insights",
    desc: "See total inventory value, expiring products, and low stock counts at a glance.",
  },
  {
    icon: <FiZap />,
    title: "Bulk Operations",
    desc: "Upload products via CSV, delete or move items in bulk — built for speed.",
  },
];

const AboutUs = () => {
  return (
    <div className="about-page">
      <div className="about-hero">
        <h1>
          About <span className="brand-highlight">InvTrack</span>
        </h1>
        <p className="about-tagline">
          Simple, fast inventory management for modern teams.
        </p>
      </div>

      <div className="about-grid">
        {features.map((f) => (
          <div className="about-card" key={f.title}>
            <span className="about-icon">{f.icon}</span>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>

      <div className="about-footer-note">
        Built with React · Django · MongoDB
      </div>
    </div>
  );
};

export default AboutUs;
