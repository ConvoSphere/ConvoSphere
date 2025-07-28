import React from "react";
import { Typography } from "antd";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import DraggableDashboard from "../components/dashboard/DraggableDashboard";

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <div style={{ padding: "24px 0", minHeight: "100vh" }}>
      <DraggableDashboard />
    </div>
  );
};

export default Dashboard;
