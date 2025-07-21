import React, { useEffect, useState } from 'react';
import { Card, List, Input, Button, Upload, message, Spin } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { getDocuments, uploadDocument } from '../services/documents';

const KnowledgeBase: React.FC = () => {
  const [docs, setDocs] = useState<{ id: number; name: string; uploaded: string }[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    getDocuments()
      .then(setDocs)
      .catch(() => message.error('Failed to load documents'))
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const doc = await uploadDocument(file);
      setDocs(prev => [...prev, doc]);
      message.success(`${file.name} uploaded`);
    } catch {
      message.error('Upload failed');
    } finally {
      setUploading(false);
    }
    return false; // Prevent default upload
  };

  const filteredDocs = docs.filter(doc => doc.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <Card title="Knowledge Base" style={{ maxWidth: 700, margin: 'auto' }}>
      <Input.Search
        placeholder="Search documents..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ marginBottom: 16 }}
      />
      <Upload beforeUpload={handleUpload} showUploadList={false} disabled={uploading}>
        <Button icon={<UploadOutlined />} loading={uploading}>Upload Document</Button>
      </Upload>
      {loading ? <Spin style={{ marginTop: 32 }} /> : (
        <List
          style={{ marginTop: 24 }}
          bordered
          dataSource={filteredDocs}
          renderItem={doc => (
            <List.Item>
              <b>{doc.name}</b> <span style={{ color: '#888', marginLeft: 8 }}>({doc.uploaded})</span>
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

export default KnowledgeBase; 