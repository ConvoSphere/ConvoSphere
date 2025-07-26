import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, List, Button, Spin, message } from 'antd';
import { getConversations, getConversation } from '../services/conversations';

interface Conversation {
  id: number;
  title: string;
  lastMessage: string;
  date: string;
}

const Conversations: React.FC = () => {
  const { t } = useTranslation();
  const [convos, setConvos] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingConv, setLoadingConv] = useState(false);
  const [convDetail, setConvDetail] = useState<any>(null);

  useEffect(() => {
    getConversations()
      .then(setConvos)
      .catch(() => message.error(t('conversations.load_failed')))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = async (id: number) => {
    setSelected(id);
    setLoadingConv(true);
    try {
      const detail = await getConversation(id);
      setConvDetail(detail);
    } catch {
      message.error(t('conversations.load_detail_failed'));
      setConvDetail(null);
    } finally {
      setLoadingConv(false);
    }
  };

  return (
    <Card title={t('conversations.title')} style={{ maxWidth: 700, margin: 'auto' }}>
      {loading ? <Spin style={{ marginTop: 32 }} /> : (
        <List
          bordered
          dataSource={convos}
          renderItem={c => (
            <List.Item
              actions={[<Button type={selected === c.id ? 'primary' : 'default'} onClick={() => handleSelect(c.id)}>{t('common.open')}</Button>]}
            >
              <b>{c.title}</b> <span style={{ color: '#888', marginLeft: 8 }}>{c.lastMessage}</span> <span style={{ float: 'right', color: '#aaa' }}>{c.date}</span>
            </List.Item>
          )}
        />
      )}
      {selected && (
        <div style={{ marginTop: 24 }}>
          {loadingConv ? <Spin /> : (
            <pre style={{ background: '#f7f7f7', padding: 16 }}>{JSON.stringify(convDetail, null, 2)}</pre>
          )}
        </div>
      )}
    </Card>
  );
};

export default Conversations; 