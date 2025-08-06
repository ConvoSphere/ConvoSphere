import React from "react";
import { Card, Space } from "antd";
import ModernButton from "../ModernButton";
import {
  HistoryOutlined,
  ExportOutlined,
  ShareAltOutlined,
  SettingOutlined,
} from "@ant-design/icons";

interface QuickActionsProps {
  onShowHistory: () => void;
  onExportConversation: () => void;
  onShareConversation: () => void;
  onShowSettings: () => void;
}

const QuickActions: React.FC<QuickActionsProps> = ({
  onShowHistory,
  onExportConversation,
  onShareConversation,
  onShowSettings,
}) => (
  <Card size="small" title="Quick Actions" style={{ marginBottom: "16px" }}>
    <Space direction="vertical" style={{ width: "100%" }}>
      <ModernButton
        variant="ghost"
        icon={<HistoryOutlined />}
        onClick={onShowHistory}
        style={{ textAlign: "left", width: "100%" }}
      >
        View Conversation History
      </ModernButton>
      <ModernButton
        variant="ghost"
        icon={<ExportOutlined />}
        onClick={onExportConversation}
        style={{ textAlign: "left", width: "100%" }}
      >
        Export Conversation
      </ModernButton>
      <ModernButton
        variant="ghost"
        icon={<ShareAltOutlined />}
        onClick={onShareConversation}
        style={{ textAlign: "left", width: "100%" }}
      >
        Share Conversation
      </ModernButton>
      <ModernButton
        variant="ghost"
        icon={<SettingOutlined />}
        onClick={onShowSettings}
        style={{ textAlign: "left", width: "100%" }}
      >
        Chat Settings
      </ModernButton>
    </Space>
  </Card>
);

export default QuickActions;
