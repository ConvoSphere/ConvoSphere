import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, List, Button, Input, Modal, Form, message, Spin } from 'antd';
import { getMcpTools, runMcpTool } from '../services/mcpTools';

interface McpTool {
  id: number;
  name: string;
  description: string;
}

const McpTools: React.FC = () => {
  const { t } = useTranslation();
  const [tools, setTools] = useState<McpTool[]>([]);
  const [selected, setSelected] = useState<McpTool | null>(null);
  const [visible, setVisible] = useState(false);
  const [param, setParam] = useState('');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    getMcpTools()
      .then(setTools)
      .catch(() => message.error(t('mcp_tools.load_failed')))
      .finally(() => setLoading(false));
  }, []);

  const handleRun = async () => {
    if (!selected) return;
    setRunning(true);
    try {
      const result = await runMcpTool(selected.id, { param });
      message.success(`${t('mcp_tools.result')}: ${result.output || t('mcp_tools.success')}`);
      setVisible(false);
      setParam('');
    } catch {
      message.error(t('mcp_tools.execution_failed'));
    } finally {
      setRunning(false);
    }
  };

  return (
    <Card title={t('mcp_tools.title')} style={{ maxWidth: 700, margin: 'auto' }}>
      {loading ? <Spin style={{ marginTop: 32 }} /> : (
        <List
          bordered
          dataSource={tools}
          renderItem={tool => (
            <List.Item actions={[<Button onClick={() => { setSelected(tool); setVisible(true); }}>{t('common.run')}</Button>]}> 
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
        okText={t('common.run')}
        confirmLoading={running}
      >
        <Form layout="vertical">
          <Form.Item label={t('mcp_tools.parameter_label')}>
            <Input value={param} onChange={e => setParam(e.target.value)} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default McpTools; 