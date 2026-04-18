/**
 * Top navigation bar with basic links to switch between views.
 */
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  return (
    <header className="header">
      <div className="navbar-brand">
        {/* App logo and tagline */}
        <Link to="/" className="logo-link">
          <div className="logo">
            <span className="logo-black">Inv</span>
            <span className="logo-blue">Track</span>
          </div>
        </Link>

        <span className="navbar-tagline">
          Manage your products and inventory
        </span>
      </div>

      <div className="header-actions">
        {/* Navigation Links Grouped Together */}
        <Link to="/" className="nav-link">
          Dashboard
        </Link>
        <Link to="/about-us" className="nav-link">
          About Us
        </Link>
        <Link to="/add-product" className="add-button">
          + Add Product
        </Link>
      </div>
    </header>
  );
};

export default Navbar;
