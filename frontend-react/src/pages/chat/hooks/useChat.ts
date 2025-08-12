import { useState, useCallback, useRef, useEffect } from "react";
import { message } from "antd";
import { useTranslation } from "react-i18next";
import {
  ChatMessage,
  ChatThread,
  ChatSettings,
  ChatAssistant,
  ChatError,
  ChatFormData,
} from "../types/chat.types";

export const useChat = () => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [thread, setThread] = useState<ChatThread | null>(null);
  const [assistant, setAssistant] = useState<ChatAssistant | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<ChatError | null>(null);
  const [settings, setSettings] = useState<ChatSettings>({
    model: "gpt-3.5-turbo",
    temperature: 0.7,
    max_tokens: 4096,
    use_knowledge_base: true,
    use_tools: true,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const updateMessage = useCallback(
    (id: string, updates: Partial<ChatMessage>) => {
      setMessages((prev) =>
        prev.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg)),
      );
    },
    [],
  );

  const removeMessage = useCallback((id: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const sendMessage = useCallback(
    async (formData: ChatFormData) => {
      if (!formData.message.trim()) return;

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content: formData.message,
        timestamp: new Date().toISOString(),
        status: "sending",
      };

      addMessage(userMessage);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        status: "sending",
      };

      addMessage(assistantMessage);

      setIsLoading(true);
      setError(null);

      try {
        // Mock API call - replace with actual API call
        const response = await mockChatAPI(formData.message, settings);

        updateMessage(assistantMessage.id, {
          content: response.content,
          status: "sent",
          metadata: {
            model: settings.model,
            tokens: response.usage?.output_tokens,
            cost: 0.001, // Mock cost
          },
        });
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError({ message: errorMessage });
        updateMessage(assistantMessage.id, {
          status: "error",
          error: errorMessage,
        });
        message.error(t("chat.error_sending_message"));
      } finally {
        setIsLoading(false);
      }
    },
    [addMessage, updateMessage, settings, t],
  );

  const sendMessageStreaming = useCallback(
    async (formData: ChatFormData) => {
      if (!formData.message.trim()) return;

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content: formData.message,
        timestamp: new Date().toISOString(),
        status: "sent",
      };

      addMessage(userMessage);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        status: "sending",
      };

      addMessage(assistantMessage);

      setIsStreaming(true);
      setError(null);

      // Cancel previous request if any
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      try {
        // Mock streaming API call - replace with actual API call
        await mockStreamingAPI(
          formData.message,
          settings,
          (chunk: string) => {
            updateMessage(assistantMessage.id, {
              content:
                (messages.find((m) => m.id === assistantMessage.id)?.content ||
                  "") + chunk,
            });
          },
          abortControllerRef.current.signal,
        );

        updateMessage(assistantMessage.id, {
          status: "sent",
          metadata: {
            model: settings.model,
            tokens: 150, // Mock tokens
            cost: 0.001, // Mock cost
          },
        });
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          // Request was cancelled
          return;
        }

        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError({ message: errorMessage });
        updateMessage(assistantMessage.id, {
          status: "error",
          error: errorMessage,
        });
        message.error(t("chat.error_streaming_message"));
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [addMessage, updateMessage, settings, messages, t],
  );

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  const updateSettings = useCallback((newSettings: Partial<ChatSettings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  const loadThread = useCallback(
    async (threadId: string) => {
      setIsLoading(true);
      setError(null);

      try {
        // Mock API call - replace with actual API call
        const threadData = await mockLoadThreadAPI(threadId);
        setThread(threadData);
        setMessages(threadData.messages);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError({ message: errorMessage });
        message.error(t("chat.error_loading_thread"));
      } finally {
        setIsLoading(false);
      }
    },
    [t],
  );

  const saveThread = useCallback(async () => {
    if (!thread) return;

    try {
      // Mock API call - replace with actual API call
      await mockSaveThreadAPI({
        ...thread,
        messages,
        updated_at: new Date().toISOString(),
      });
      message.success(t("chat.thread_saved"));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError({ message: errorMessage });
      message.error(t("chat.error_saving_thread"));
    }
  }, [thread, messages, t]);

  const exportChat = useCallback(
    async (format: "json" | "txt" | "md" | "pdf") => {
      try {
        const exportData = {
          thread,
          messages,
          settings,
          assistant,
          export_date: new Date().toISOString(),
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
          type: "application/json",
        });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split("T")[0]}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);

        message.success(t("chat.export_successful"));
      } catch (err) {
        message.error(t("chat.error_exporting"));
      }
    },
    [thread, messages, settings, assistant, t],
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    messages,
    thread,
    assistant,
    isLoading,
    isStreaming,
    error,
    settings,
    addMessage,
    updateMessage,
    removeMessage,
    clearMessages,
    sendMessage,
    sendMessageStreaming,
    stopStreaming,
    updateSettings,
    loadThread,
    saveThread,
    exportChat,
  };
};

// Mock API functions - replace with actual API calls
const mockChatAPI = async (message: string, settings: ChatSettings) => {
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return {
    content: `This is a mock response to: "${message}". Model: ${settings.model}`,
    usage: {
      input_tokens: 50,
      output_tokens: 100,
    },
  };
};

const mockStreamingAPI = async (
  message: string,
  settings: ChatSettings,
  onChunk: (chunk: string) => void,
  signal: AbortSignal,
) => {
  const response = `This is a mock streaming response to: "${message}". Model: ${settings.model}. `;
  const words = response.split(" ");

  for (const word of words) {
    if (signal.aborted) break;
    onChunk(word + " ");
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
};

const mockLoadThreadAPI = async (threadId: string) => {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return {
    id: threadId,
    title: "Mock Thread",
    messages: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    user_id: "user-1",
  };
};

const mockSaveThreadAPI = async (thread: ChatThread) => {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return thread;
};
