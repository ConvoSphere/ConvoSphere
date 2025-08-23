import React from "react";
import { Tabs } from "antd";
import {
  UserOutlined,
  SettingOutlined,
  DashboardOutlined,
  SafetyOutlined,
  TeamOutlined,
  ToolOutlined,
  ApiOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import UserManagement from "./admin/components/UserManagement";
import SystemConfig from "./admin/components/SystemConfig";
import SystemStats from "./admin/components/SystemStats";
import AuditLogs from "./admin/components/AuditLogs";
import DomainGroups from "./DomainGroups";
import Tools from "./tools/Tools";
import McpTools from "./McpTools";

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
    {
      key: "domain-groups",
      label: (
        <span>
          <TeamOutlined />
          {t("navigation.domain_groups")}
        </span>
      ),
      children: <DomainGroups />,
    },
    {
      key: "tools-admin",
      label: (
        <span>
          <ToolOutlined />
          {t("tools.title", "Tools")}
        </span>
      ),
      children: <Tools />,
    },
    {
      key: "mcp-tools-admin",
      label: (
        <span>
          <ApiOutlined />
          {t("navigation.mcp_tools")}
        </span>
      ),
      children: <McpTools />,
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
