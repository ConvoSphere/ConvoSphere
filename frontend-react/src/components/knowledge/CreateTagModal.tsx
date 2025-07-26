import React from "react";
import { Modal, Form, Input, Button, Space, Select, ColorPicker } from "antd";

const { Option } = Select;

interface CreateTagModalProps {
  open: boolean;
  form: any;
  onFinish: (values: any) => void;
  onCancel: () => void;
}

const CreateTagModal: React.FC<CreateTagModalProps> = ({
  open,
  form,
  onFinish,
  onCancel,
}) => (
  <Modal title="Create New Tag" open={open} onCancel={onCancel} footer={null}>
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item
        name="name"
        label="Tag Name"
        rules={[
          { required: true, message: "Please enter a tag name" },
          { min: 2, message: "Tag name must be at least 2 characters" },
          { max: 50, message: "Tag name must be less than 50 characters" },
        ]}
      >
        <Input placeholder="Enter tag name" />
      </Form.Item>
      <Form.Item
        name="description"
        label="Description"
        rules={[
          { max: 200, message: "Description must be less than 200 characters" },
        ]}
      >
        <Input.TextArea
          placeholder="Enter tag description (optional)"
          rows={3}
        />
      </Form.Item>
      <Form.Item name="color" label="Color" initialValue="#1890ff">
        <ColorPicker />
      </Form.Item>
      <Form.Item name="is_system" valuePropName="checked" initialValue={false}>
        <Select placeholder="Tag Type">
          <Option value={false}>User Tag</Option>
          <Option value={true}>System Tag</Option>
        </Select>
      </Form.Item>
      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Create Tag
          </Button>
          <Button onClick={onCancel}>Cancel</Button>
        </Space>
      </Form.Item>
    </Form>
  </Modal>
);

export default CreateTagModal;
