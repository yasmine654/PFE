import "./Navbar.css";
import { NavLink } from "react-router-dom";

function Navbar({ isOpen, setIsOpen }) {
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
            <img src="/img_NavBar/dashboard_.png" alt="dashboard" />
            {isOpen && <h5>Dashboard</h5>}
          </NavLink>

          <NavLink to="/compute" className="icon-links">
            <img src="/img_NavBar/computer-16_ (3).png" alt="compute" />
            {isOpen && <h5>Compute</h5>}
          </NavLink>

          <NavLink to="/network" className="icon-links">
            <img src="/img_NavBar/network_.png" alt="network" />
            {isOpen && <h5>Network</h5>}
          </NavLink>

          <NavLink to="/storage" className="icon-links">
            <img src="/img_NavBar/storage_.png" alt="storage" />
            {isOpen && <h5>Storage</h5>}
          </NavLink>

          <NavLink to="/security" className="icon-links">
            <img src="/img_NavBar/security_.png" alt="security" />
            {isOpen && <h5>Security</h5>}
          </NavLink>

          <NavLink to="/vpn" className="icon-links">
            <img src="/img_NavBar/vpn-googleone_.png" alt="vpn" />
            {isOpen && <h5>VPN</h5>}
          </NavLink>

          <NavLink to="/anomalies" className="icon-links">
            <img src="/img_NavBar/danger-triangle_.png" alt="anomalies" />
            {isOpen && <h5>Anomalies</h5>}
          </NavLink>

          <NavLink to="/finops" className="icon-links">
            <img src="/img_NavBar/graph_ (1).png" alt="finops" />
            {isOpen && <h5>FinOps</h5>}
          </NavLink>
        </ul>
      </div>

      {/* FOOTER */}
      <NavLink to="/" className="accueil">
        <img src="/img_NavBar/house_.png" alt="accueil" />
        {isOpen && <h5>Accueil</h5>}
      </NavLink>

    </nav>
  );
}

export default Navbar;