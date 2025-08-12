import React from "react";
import { Tabs } from "antd";
import {
  UserOutlined,
  SettingOutlined,
  DashboardOutlined,
  SafetyOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import UserManagement from "./components/UserManagement";
import SystemConfig from "./components/SystemConfig";
import SystemStats from "./components/SystemStats";
import AuditLogs from "./components/AuditLogs";

const { TabPane } = Tabs;

const Admin: React.FC = () => {
  const { t } = useTranslation();

  const tabs = [
    {
      key: "users",
      label: (
        <span>
          <UserOutlined />
          {t("admin.tabs.users")}
        </span>
      ),
      children: <UserManagement />,
    },
    {
      key: "stats",
      label: (
        <span>
          <DashboardOutlined />
          {t("admin.tabs.statistics")}
        </span>
      ),
      children: <SystemStats />,
    },
    {
      key: "config",
      label: (
        <span>
          <SettingOutlined />
          {t("admin.tabs.configuration")}
        </span>
      ),
      children: <SystemConfig />,
    },
    {
      key: "audit",
      label: (
        <span>
          <SafetyOutlined />
          {t("admin.tabs.audit_logs")}
        </span>
      ),
      children: <AuditLogs />,
    },
  ];

  return (
    <div style={{ padding: "24px" }}>
      <Tabs
        defaultActiveKey="users"
        type="card"
        size="large"
        items={tabs}
        style={{ minHeight: "calc(100vh - 200px)" }}
      />
    </div>
  );
};

export default Admin;
