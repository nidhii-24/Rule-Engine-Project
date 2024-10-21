// frontend/src/components/Navbar.js

import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css'; // Optional: For styling

const Navbar = () => {
  return (
    <nav className="navbar">
      <h2>Rule Engine</h2>
      <ul>
        <li><Link to="/">Create Rule</Link></li>
        <li><Link to="/combine">Combine Rules</Link></li>
        <li><Link to="/evaluate">Evaluate Rule</Link></li>
        <li><Link to="/modify">Modify Rule</Link></li>
        <li><Link to="/attributes">Attribute Catalog</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;
