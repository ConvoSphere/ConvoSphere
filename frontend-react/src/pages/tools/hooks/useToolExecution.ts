import { useState } from 'react';
import { message } from 'antd';
import { runTool } from '../../../services/tools';
import type { Tool, ToolExecution } from '../types/tools.types';

export const useToolExecution = () => {
  const [executions, setExecutions] = useState<ToolExecution[]>([]);
  const [running, setRunning] = useState(false);
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [visible, setVisible] = useState(false);

  const executeTool = async (tool: Tool, parameters: Record<string, any>) => {
    setRunning(true);
    
    try {
      const result = await runTool(tool.id, parameters);

      const newExecution: ToolExecution = {
        id: Date.now().toString(),
        toolId: tool.id,
        toolName: tool.name,
        parameters,
        result,
        status: "success",
        executionTime: Math.random() * 5 + 0.5,
        timestamp: new Date().toISOString(),
      };

      setExecutions((prev) => [newExecution, ...prev]);
      setVisible(false);
      setSelectedTool(null);
      
      message.success('Tool executed successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      
      const failedExecution: ToolExecution = {
        id: Date.now().toString(),
        toolId: tool.id,
        toolName: tool.name,
        parameters,
        result: null,
        status: "error",
        executionTime: 0,
        timestamp: new Date().toISOString(),
        error: errorMessage,
      };

      setExecutions((prev) => [failedExecution, ...prev]);
      message.error(`Tool execution failed: ${errorMessage}`);
    } finally {
      setRunning(false);
    }
  };

  const openExecutionModal = (tool: Tool) => {
    setSelectedTool(tool);
    setVisible(true);
  };

  const closeExecutionModal = () => {
    setVisible(false);
    setSelectedTool(null);
  };

  const clearExecutionHistory = () => {
    setExecutions([]);
    message.success('Execution history cleared');
  };

  const getExecutionStats = () => {
    const total = executions.length;
    const successful = executions.filter(e => e.status === 'success').length;
    const failed = executions.filter(e => e.status === 'error').length;
    const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : '0';

    return {
      total,
      successful,
      failed,
      successRate,
    };
  };

  return {
    executions,
    running,
    selectedTool,
    visible,
    executeTool,
    openExecutionModal,
    closeExecutionModal,
    clearExecutionHistory,
    getExecutionStats,
  };
};