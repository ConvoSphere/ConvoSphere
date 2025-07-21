import React, { useEffect, useState } from 'react';
import { Card, List, Button, Modal, Input, Form, message, Spin } from 'antd';
import { getAssistants, addAssistant, deleteAssistant } from '../services/assistants';

interface Assistant {
  id: number;
  name: string;
  description: string;
}

const Assistants: React.FC = () => {
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    getAssistants()
      .then(setAssistants)
      .catch(() => message.error('Failed to load assistants'))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = async () => {
    try {
      setAdding(true);
      const values = await form.validateFields();
      const newAssistant = await addAssistant(values);
      setAssistants(prev => [...prev, newAssistant]);
      setVisible(false);
      form.resetFields();
      message.success('Assistant added');
    } catch {
      message.error('Add failed');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: number) => {
    setDeleting(id);
    try {
      await deleteAssistant(id);
      setAssistants(prev => prev.filter(a => a.id !== id));
      message.success('Assistant deleted');
    } catch {
      message.error('Delete failed');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <Card title="Assistants" style={{ maxWidth: 700, margin: 'auto' }}>
      <Button type="primary" onClick={() => setVisible(true)} style={{ marginBottom: 16 }}>Add Assistant</Button>
      {loading ? <Spin style={{ marginTop: 32 }} /> : (
        <List
          bordered
          dataSource={assistants}
          renderItem={a => (
            <List.Item actions={[<Button danger loading={deleting === a.id} onClick={() => handleDelete(a.id)}>Delete</Button>]}> 
              <b>{a.name}</b> <span style={{ color: '#888', marginLeft: 8 }}>{a.description}</span>
            </List.Item>
          )}
        />
      )}
      <Modal
        open={visible}
        title="Add Assistant"
        onCancel={() => setVisible(false)}
        onOk={handleAdd}
        okText="Add"
        confirmLoading={adding}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}> <Input /> </Form.Item>
          <Form.Item name="description" label="Description"> <Input /> </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default Assistants; 