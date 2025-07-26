import React from "react";
import { Button } from "antd";
import { useAuthStore } from "../store/authStore";
import { useNavigate } from "react-router-dom";

const LogoutButton: React.FC = () => {
  const logout = useAuthStore((s) => s.logout);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();

  if (!isAuthenticated) return null;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <Button onClick={handleLogout} type="default" danger>
      Logout
    </Button>
  );
};

export default LogoutButton;
