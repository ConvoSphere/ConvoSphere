import React from "react";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useNavigate } from "react-router-dom";
import ModernButton from "./ModernButton";

const LogoutButton: React.FC = () => {
  const { t } = useTranslation();
  const logout = useAuthStore((s) => s.logout);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const navigate = useNavigate();

  if (!isAuthenticated) return null;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <ModernButton
      variant="ghost"
      size="sm"
      onClick={handleLogout}
      danger
      style={{
        color: colors.colorError,
        borderColor: colors.colorError,
      }}
      aria-label={t("auth.logout")}
    >
      {t("auth.logout", "Logout")}
    </ModernButton>
  );
};

export default LogoutButton;
