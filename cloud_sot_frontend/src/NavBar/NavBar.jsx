import "./Navbar.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";

function Navbar() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <nav className={isOpen ? "navbar open" : "navbar closed"}>

      {/* HEADER */}
      <div className="header">
        <div className="logo">
          {isOpen && "DJEZZY Cloud"}
        </div>

        <div className="toggle-btn" onClick={() => setIsOpen(!isOpen)}>
          <img 
                src="/img_NavBar/burger-bar.png" 
                alt="toggle"
                className={isOpen ? "arrow open" : "arrow"}
           />
        </div>
      </div>

      {/* TOP */}
      <div className="top">
        <ul className="nav-links">

          <NavLink to="/" className="icon-links">
            <img src="/img_NavBar/dashboard_.png"/>
            {isOpen && <h5>Dashboard</h5>}
          </NavLink>

          <NavLink to="/compute" className="icon-links">
            <img src="/img_NavBar/computer-16_ (3).png"/>
            {isOpen && <h5>Compute</h5>}
          </NavLink>

          <NavLink to="/network" className="icon-links">
            <img src="/img_NavBar/network_.png"/>
            {isOpen && <h5>Network</h5>}
          </NavLink>

          <NavLink to="/storage" className="icon-links">
            <img src="/img_NavBar/storage_.png"/>
            {isOpen && <h5>Storage</h5>}
          </NavLink>

          <NavLink to="/security" className="icon-links">
            <img src="/img_NavBar/security_.png"/>
            {isOpen && <h5>Security</h5>}
          </NavLink>

          <NavLink to="/vpn" className="icon-links">
            <img src="/img_NavBar/vpn-googleone_.png"/>
            {isOpen && <h5>VPN</h5>}
          </NavLink>

          <NavLink to="/anomalies" className="icon-links">
            <img src="/img_NavBar/danger-triangle_.png"/>
            {isOpen && <h5>Anomalies</h5>}
          </NavLink>

          <NavLink to="/finops" className="icon-links">
            <img src="/img_NavBar/graph_ (1).png"/>
            {isOpen && <h5>FinOps</h5>}
          </NavLink>

        </ul>
      </div>

      {/* FOOTER */}
      <NavLink to="/" className="accueil">
        <img src="/img_NavBar/house_.png"/>
        {isOpen && <h5>Accueil</h5>}
      </NavLink>

    </nav>
  );
}

export default Navbar;