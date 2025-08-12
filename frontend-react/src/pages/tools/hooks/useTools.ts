import { message } from "antd";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getTools,
  createTool,
  updateTool as apiUpdateTool,
  deleteTool as apiDeleteTool,
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

  const toggleToolActive = async (tool: Tool) => {
    // Optimistic update pattern
    const previous = queryClient.getQueryData<Tool[]>(["tools"]);
    const updated =
      previous?.map((t) =>
        t.id === tool.id ? ({ ...t, isActive: !tool.isActive } as any) : t,
      ) || [];
    queryClient.setQueryData(["tools"], updated);
    message.success(tool.isActive ? "Tool deactivated" : "Tool activated");
    // TODO: call backend if such endpoint exists; otherwise keep as UI only
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
