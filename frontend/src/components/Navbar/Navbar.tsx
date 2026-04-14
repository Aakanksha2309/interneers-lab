/**
 * Top navigation bar with basic links to switch between views.
 */
import "./Navbar.css";

interface NavbarProps {
  // function passed from App to change current view
  onNavigate: (view: "dashboard" | "add-product" | "about-us") => void;
}

const Navbar = ({ onNavigate }: NavbarProps) => {
  return (
    <header className="header">
      <div className="navbar-brand">
        {/* App logo and tagline */}
        <div className="logo">
          <span className="logo-black">Inv</span>
          <span className="logo-blue">Track</span>
        </div>
        <span className="navbar-tagline">
          Manage your products and inventory
        </span>
      </div>

      <div className="header-actions">
        {/* Navigation Links Grouped Together */}
        <button className="nav-link" onClick={() => onNavigate("dashboard")}>
          Dashboard
        </button>
        <button className="nav-link" onClick={() => onNavigate("about-us")}>
          About Us
        </button>
        <button
          className="add-button"
          onClick={() => onNavigate("add-product")}
        >
          + Add Product
        </button>
      </div>
    </header>
  );
};

export default Navbar;
