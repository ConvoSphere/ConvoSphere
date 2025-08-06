import React from "react";
import { Modal, Typography, Space } from "antd";
import ModernButton from "../ModernButton";

const { Text } = Typography;

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ open, onClose }) => (
  <Modal
    title="Chat Settings"
    open={open}
    onCancel={onClose}
    footer={[
      <ModernButton key="close" variant="secondary" onClick={onClose}>
        Close
      </ModernButton>,
    ]}
    width={500}
  >
    <Space direction="vertical" style={{ width: "100%" }}>
      <div>
        <Text strong>Knowledge Base Integration:</Text>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">
            Configure how the Knowledge Base integrates with your chat
            experience.
          </Text>
        </div>
      </div>
      <div>
        <Text strong>Auto-Search:</Text>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">
            Automatically search for relevant documents when you type messages.
          </Text>
        </div>
      </div>
      <div>
        <Text strong>Context Management:</Text>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">
            Choose how many documents to include in the chat context and how to
            prioritize them.
          </Text>
        </div>
      </div>
    </Space>
  </Modal>
);

export default SettingsModal;
