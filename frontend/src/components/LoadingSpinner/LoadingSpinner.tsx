import React from "react";
import { FiLoader } from "react-icons/fi";
import "./LoadingSpinner.css";

interface LoadingSpinnerProps {
  message?: string; // Optional text to show below spinner
  size?: "small" | "large"; // Control the size
  fullPage?: boolean; // Center in the middle of the screen
}

const LoadingSpinner = ({
  message = "Loading...",
  size = "large",
  fullPage = true,
}: LoadingSpinnerProps) => {
  return (
    <div className={`spinner-container ${fullPage ? "full-page" : ""}`}>
      <div className={`spinner-wrapper ${size}`}>
        <FiLoader className="spin-icon" />
      </div>
      {message && <p className="spinner-text">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
