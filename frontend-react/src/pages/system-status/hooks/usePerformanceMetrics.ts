import { useState, useEffect } from 'react';
import { message } from 'antd';

interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

export const usePerformanceMetrics = () => {
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [loading, setLoading] = useState(false);

  const fetchPerformanceData = async (range: string = timeRange) => {
    try {
      setLoading(true);
      
      const response = await fetch(`/api/v1/monitoring/performance?range=${range}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: PerformanceData[] = await response.json();
      setPerformanceData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      message.error(`Failed to fetch performance data: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range);
    fetchPerformanceData(range);
  };

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  return {
    performanceData,
    timeRange,
    loading,
    fetchPerformanceData,
    handleTimeRangeChange,
  };
};