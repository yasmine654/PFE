import { Outlet } from "react-router-dom";
import Sidebar from "../Components/Sidebar/Sidebar";
import Topbar from "../Components/Topbar/Topbar";
import "./Layout.css";

export default function Layout() {
  return (
    <div className="layout">

      <Sidebar />

      <div className="content">

        <Topbar />

        <div className="main">
          <Outlet />
        </div>

      </div>
    </div>
  );
}