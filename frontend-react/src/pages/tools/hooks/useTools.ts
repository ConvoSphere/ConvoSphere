import { useState, useEffect } from 'react';
import { message } from 'antd';
import { getTools } from '../../../services/tools';
import type { Tool } from '../types/tools.types';

export const useTools = () => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTools = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const toolsData = await getTools();
      setTools(toolsData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      message.error(`Failed to load tools: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleToolActive = async (tool: Tool) => {
    try {
      const updatedTool = { ...tool, isActive: !tool.isActive };
      setTools((prev) => prev.map((t) => (t.id === tool.id ? updatedTool : t)));
      message.success(
        tool.isActive
          ? 'Tool deactivated'
          : 'Tool activated'
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      message.error(`Failed to toggle tool: ${errorMessage}`);
    }
  };

  const addTool = async (tool: Tool) => {
    try {
      // In a real implementation, this would call an API
      const newTool = { ...tool, id: Date.now() };
      setTools((prev) => [...prev, newTool]);
      message.success('Tool added successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      message.error(`Failed to add tool: ${errorMessage}`);
    }
  };

  const updateTool = async (toolId: number, updates: Partial<Tool>) => {
    try {
      setTools((prev) => prev.map((t) => (t.id === toolId ? { ...t, ...updates } : t)));
      message.success('Tool updated successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      message.error(`Failed to update tool: ${errorMessage}`);
    }
  };

  const deleteTool = async (toolId: number) => {
    try {
      setTools((prev) => prev.filter((t) => t.id !== toolId));
      message.success('Tool deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      message.error(`Failed to delete tool: ${errorMessage}`);
    }
  };

  useEffect(() => {
    loadTools();
  }, []);

  return {
    tools,
    loading,
    error,
    loadTools,
    toggleToolActive,
    addTool,
    updateTool,
    deleteTool,
  };
};