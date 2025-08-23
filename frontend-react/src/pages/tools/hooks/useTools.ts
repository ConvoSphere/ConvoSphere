import { message } from "antd";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getTools,
  createTool,
  updateTool as apiUpdateTool,
  deleteTool as apiDeleteTool,
  toggleToolEnabled,
} from "../../../services/tools";
import type { Tool } from "../types/tools.types";

export const useTools = () => {
  const queryClient = useQueryClient();

  const toolsQuery = useQuery({
    queryKey: ["tools"],
    queryFn: () => getTools(),
    staleTime: 10 * 60 * 1000,
  });

  const addToolMutation = useMutation({
    mutationFn: (tool: Tool) => createTool(tool as any),
    onSuccess: () => {
      message.success("Tool added successfully");
      queryClient.invalidateQueries({ queryKey: ["tools"] });
    },
    onError: (err: any) => {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      message.error(`Failed to add tool: ${errorMessage}`);
    },
  });

  const updateToolMutation = useMutation({
    mutationFn: ({
      toolId,
      updates,
    }: {
      toolId: number;
      updates: Partial<Tool>;
    }) => apiUpdateTool(String(toolId), updates as any),
    onSuccess: () => {
      message.success("Tool updated successfully");
      queryClient.invalidateQueries({ queryKey: ["tools"] });
    },
    onError: (err: any) => {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      message.error(`Failed to update tool: ${errorMessage}`);
    },
  });

  const deleteToolMutation = useMutation({
    mutationFn: (toolId: number) => apiDeleteTool(String(toolId)),
    onSuccess: () => {
      message.success("Tool deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["tools"] });
    },
    onError: (err: any) => {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      message.error(`Failed to delete tool: ${errorMessage}`);
    },
  });

  const toggleToolActive = async (tool: any) => {
    // Optimistic update
    const previous = queryClient.getQueryData<any>(["tools"]) || [];
    const updated = previous.map((t: any) =>
      t.id === tool.id ? { ...t, is_enabled: !t.is_enabled, isActive: !t.isActive } : t,
    );
    queryClient.setQueryData(["tools"], updated);

    try {
      const res = await toggleToolEnabled(String(tool.id));
      // Sync with server response
      const synced = (queryClient.getQueryData<any>(["tools"]) || []).map((t: any) =>
        t.id === tool.id
          ? { ...t, is_enabled: res.is_enabled, isActive: Boolean(res.is_enabled) }
          : t,
      );
      queryClient.setQueryData(["tools"], synced);
      message.success(res.is_enabled ? "Tool aktiviert" : "Tool deaktiviert");
    } catch (err: any) {
      // Revert on error
      queryClient.setQueryData(["tools"], previous);
      const msg = err?.response?.status === 403 ? "Nicht genügend Rechte" : "Toggle fehlgeschlagen";
      message.error(msg);
    }
  };

  return {
    tools: toolsQuery.data || [],
    loading: toolsQuery.isLoading,
    error: toolsQuery.error ? (toolsQuery.error as any).message : null,
    loadTools: () => queryClient.invalidateQueries({ queryKey: ["tools"] }),
    toggleToolActive,
    addTool: (tool: Tool) => addToolMutation.mutateAsync(tool),
    updateTool: (toolId: number, updates: Partial<Tool>) =>
      updateToolMutation.mutateAsync({ toolId, updates }),
    deleteTool: (toolId: number) => deleteToolMutation.mutateAsync(toolId),
  };
};
