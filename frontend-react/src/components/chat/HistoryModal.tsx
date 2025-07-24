import React from 'react';
import { Modal, Typography, Button } from 'antd';

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
        <Button key="close" onClick={onClose}>
          Close
        </Button>
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