import React from 'react';
import { Card, Switch, Select, Form } from 'antd';

const Settings: React.FC = () => {
  return (
    <Card title="Settings" style={{ maxWidth: 500, margin: 'auto' }}>
      <Form layout="vertical">
        <Form.Item label="Language">
          <Select defaultValue="en" style={{ width: 160 }}>
            <Select.Option value="en">English</Select.Option>
            <Select.Option value="de">Deutsch</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item label="Theme">
          <Switch checkedChildren="Dark" unCheckedChildren="Light" defaultChecked={false} />
        </Form.Item>
        <Form.Item label="Notifications">
          <Switch defaultChecked />
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Settings; 