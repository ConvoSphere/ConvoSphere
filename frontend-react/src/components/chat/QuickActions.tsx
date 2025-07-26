import React from "react";
import { Card, Space, Button } from "antd";
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
      <Button
        type="text"
        icon={<HistoryOutlined />}
        onClick={onShowHistory}
        style={{ textAlign: "left", width: "100%" }}
      >
        View Conversation History
      </Button>
      <Button
        type="text"
        icon={<ExportOutlined />}
        onClick={onExportConversation}
        style={{ textAlign: "left", width: "100%" }}
      >
        Export Conversation
      </Button>
      <Button
        type="text"
        icon={<ShareAltOutlined />}
        onClick={onShareConversation}
        style={{ textAlign: "left", width: "100%" }}
      >
        Share Conversation
      </Button>
      <Button
        type="text"
        icon={<SettingOutlined />}
        onClick={onShowSettings}
        style={{ textAlign: "left", width: "100%" }}
      >
        Chat Settings
      </Button>
    </Space>
  </Card>
);

export default QuickActions;
