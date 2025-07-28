import React from "react";
import { Typography } from "antd";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import DashboardGrid from "../components/dashboard/DashboardGrid";

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <div style={{ padding: "24px 0", minHeight: "100vh" }}>
      <DashboardGrid />
    </div>
  );
};

export default Dashboard;
