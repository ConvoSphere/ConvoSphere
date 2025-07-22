import React, { useEffect, useState, useRef } from 'react';
import { Card, Row, Col, Tag, Spin, Alert } from 'antd';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

interface StatusData {
  system: {
    cpu_percent: number;
    ram: { [key: string]: any };
  };
  database: { healthy: boolean; info: any };
  redis: { healthy: boolean; info: any };
  weaviate: { healthy: boolean; info: any };
  tracing: { trace_id: string | null };
  status: string;
}

const MAX_POINTS = 60; // z.B. 5 Minuten bei 5s Intervall

const SystemStatus: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');
  const [data, setData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cpuHistory = useRef<{ time: string; cpu: number }[]>([]);
  const ramHistory = useRef<{ time: string; ram: number }[]>([]);

  useEffect(() => {
    if (!isAdmin) return;
    const timer: NodeJS.Timeout = setInterval(async () => {
      try {
        const res = await api.get('/users/admin/system-status');
        setData(res.data);
        const now = new Date().toLocaleTimeString();
        // CPU
        cpuHistory.current.push({ time: now, cpu: res.data.system.cpu_percent });
        if (cpuHistory.current.length > MAX_POINTS) cpuHistory.current.shift();
        // RAM
        ramHistory.current.push({ time: now, ram: res.data.system.ram.percent });
        if (ramHistory.current.length > MAX_POINTS) ramHistory.current.shift();
        setError(null);
      } catch {
        setError('Failed to load system status');
      } finally {
        setLoading(false);
      }
    }, 5000);
    
    // Initial fetch
    (async () => {
      try {
        const res = await api.get('/users/admin/system-status');
        setData(res.data);
        const now = new Date().toLocaleTimeString();
        // CPU
        cpuHistory.current.push({ time: now, cpu: res.data.system.cpu_percent });
        if (cpuHistory.current.length > MAX_POINTS) cpuHistory.current.shift();
        // RAM
        ramHistory.current.push({ time: now, ram: res.data.system.ram.percent });
        if (ramHistory.current.length > MAX_POINTS) ramHistory.current.shift();
        setError(null);
      } catch {
        setError('Failed to load system status');
      } finally {
        setLoading(false);
      }
    })();
    
    return () => clearInterval(timer);
  }, [isAdmin]);

  if (!isAdmin) return <Alert type="error" message="Access denied" showIcon style={{ margin: 32 }} />;
  if (loading) return <Spin style={{ margin: 64 }} />;
  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 32 }} />;
  if (!data) return null;

  const statusTag = (healthy: boolean) => (
    <Tag color={healthy ? 'green' : 'red'}>{healthy ? 'OK' : 'Fehler'}</Tag>
  );

  return (
    <Card title="Systemstatus & Performance" style={{ maxWidth: 1000, margin: 'auto' }}>
      <Row gutter={24}>
        <Col span={12}>
          <h4>CPU-Auslastung (%)</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={cpuHistory.current} margin={{ left: 0, right: 0, top: 8, bottom: 8 }}>
              <XAxis dataKey="time" minTickGap={20} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <CartesianGrid strokeDasharray="3 3" />
              <Line type="monotone" dataKey="cpu" stroke="#1890ff" dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
        <Col span={12}>
          <h4>RAM-Auslastung (%)</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={ramHistory.current} margin={{ left: 0, right: 0, top: 8, bottom: 8 }}>
              <XAxis dataKey="time" minTickGap={20} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <CartesianGrid strokeDasharray="3 3" />
              <Line type="monotone" dataKey="ram" stroke="#52c41a" dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
      <Row gutter={24} style={{ marginTop: 32 }}>
        <Col span={6}>
          <h4>Datenbank</h4>
          {statusTag(data.database.healthy)}
        </Col>
        <Col span={6}>
          <h4>Redis</h4>
          {statusTag(data.redis.healthy)}
        </Col>
        <Col span={6}>
          <h4>Weaviate</h4>
          {statusTag(data.weaviate.healthy)}
        </Col>
        <Col span={6}>
          <h4>Trace-ID</h4>
          <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{data.tracing.trace_id || '-'}</span>
        </Col>
      </Row>
      <Row style={{ marginTop: 32 }}>
        <Col span={24}>
          <h4>Systemstatus: {data.status === 'ok' ? <Tag color="green">OK</Tag> : <Tag color="orange">Degraded</Tag>}</h4>
        </Col>
      </Row>
    </Card>
  );
};

export default SystemStatus; 