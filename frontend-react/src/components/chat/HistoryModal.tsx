import React from 'react';
import { Modal, Button, Typography, List } from 'antd';

const { Text } = Typography;

interface HistoryModalProps {
  open: boolean;
  conversationHistory: any[];
  onClose: () => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ open, conversationHistory, onClose }) => (
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
    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
      {conversationHistory.length === 0 ? (
        <Text type="secondary">No conversation history available</Text>
      ) : (
        <List
          dataSource={conversationHistory}
          renderItem={(item, index) => (
            <List.Item>
              <List.Item.Meta
                title={`Message ${index + 1}`}
                description={
                  <div>
                    <Text type="secondary">{item.timestamp}</Text>
                    <br />
                    <Text>{item.content}</Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  </Modal>
);

export default HistoryModal;