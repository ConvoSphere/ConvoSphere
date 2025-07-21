import React, { useEffect, useState } from 'react';
import { Card, List, Button, Input, Modal, Form, message, Spin } from 'antd';
import { getMcpTools, runMcpTool } from '../services/mcpTools';

interface McpTool {
  id: number;
  name: string;
  description: string;
}

const McpTools: React.FC = () => {
  const [tools, setTools] = useState<McpTool[]>([]);
  const [selected, setSelected] = useState<McpTool | null>(null);
  const [visible, setVisible] = useState(false);
  const [param, setParam] = useState('');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    getMcpTools()
      .then(setTools)
      .catch(() => message.error('Failed to load MCP tools'))
      .finally(() => setLoading(false));
  }, []);

  const handleRun = async () => {
    if (!selected) return;
    setRunning(true);
    try {
      const result = await runMcpTool(selected.id, { param });
      message.success(`Result: ${result.output || 'Success'}`);
      setVisible(false);
      setParam('');
    } catch {
      message.error('MCP Tool execution failed');
    } finally {
      setRunning(false);
    }
  };

  return (
    <Card title="MCP Tools" style={{ maxWidth: 700, margin: 'auto' }}>
      {loading ? <Spin style={{ marginTop: 32 }} /> : (
        <List
          bordered
          dataSource={tools}
          renderItem={tool => (
            <List.Item actions={[<Button onClick={() => { setSelected(tool); setVisible(true); }}>Run</Button>]}> 
              <b>{tool.name}</b> <span style={{ color: '#888', marginLeft: 8 }}>{tool.description}</span>
            </List.Item>
          )}
        />
      )}
      <Modal
        open={visible}
        title={selected?.name}
        onCancel={() => setVisible(false)}
        onOk={handleRun}
        okText="Run"
        confirmLoading={running}
      >
        <Form layout="vertical">
          <Form.Item label="Parameter (Platzhalter)">
            <Input value={param} onChange={e => setParam(e.target.value)} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default McpTools; 