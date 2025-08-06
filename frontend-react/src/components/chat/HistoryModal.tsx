import React from "react";
import { Modal, Typography } from "antd";
import ModernButton from "../ModernButton";

const { Text } = Typography;

interface HistoryModalProps {
  open: boolean;
  onClose: () => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ open, onClose }) => {
  return (
    <Modal
      title="Conversation History"
      open={open}
      onCancel={onClose}
      footer={[
        <ModernButton key="close" variant="secondary" onClick={onClose}>
          Close
        </ModernButton>,
      ]}
      width={800}
    >
      <div>
        <Text type="secondary">
          Conversation history feature coming soon...
        </Text>
      </div>
    </Modal>
  );
};

export default HistoryModal;
