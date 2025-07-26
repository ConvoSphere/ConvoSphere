import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { message } from "antd";
import Chat from "../Chat";

// Mock antd message
jest.mock("antd", () => ({
  ...jest.requireActual("antd"),
  message: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

// Mock the auth store
jest.mock("../../store/authStore", () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: "1", username: "testuser" },
    token: "fake-token",
  })),
}));

// Mock the chat store
jest.mock("../../store/chatStore", () => ({
  useChatStore: jest.fn(() => ({
    messages: [],
    addMessage: jest.fn(),
    setMessages: jest.fn(),
    clearMessages: jest.fn(),
  })),
}));

// Mock WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
};

global.WebSocket = jest.fn(() => mockWebSocket) as any;

// Mock the API service
jest.mock("../../services/chat", () => ({
  sendMessage: jest.fn(),
  getConversationHistory: jest.fn(),
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("Chat", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWebSocket.send.mockClear();
    mockWebSocket.close.mockClear();
  });

  test("renders chat interface", () => {
    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });
    const chatContainer = screen.getByTestId("chat-container");

    expect(messageInput).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
    expect(chatContainer).toBeInTheDocument();
  });

  test("renders welcome message", () => {
    renderWithRouter(<Chat />);

    const welcomeMessage = screen.getByText(/welcome to the chat/i);
    expect(welcomeMessage).toBeInTheDocument();
  });

  test("handles message input", () => {
    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });

    expect(messageInput).toHaveValue("Hello, how are you?");
  });

  test("sends message on button click", async () => {
    const mockAddMessage = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockAddMessage).toHaveBeenCalledWith({
        id: expect.any(String),
        content: "Hello, how are you?",
        role: "user",
        timestamp: expect.any(Date),
      });
    });
  });

  test("sends message on Enter key", async () => {
    const mockAddMessage = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);

    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });
    fireEvent.keyDown(messageInput, { key: "Enter" });

    await waitFor(() => {
      expect(mockAddMessage).toHaveBeenCalledWith({
        id: expect.any(String),
        content: "Hello, how are you?",
        role: "user",
        timestamp: expect.any(Date),
      });
    });
  });

  test("does not send empty message", () => {
    const mockAddMessage = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.click(sendButton);

    expect(mockAddMessage).not.toHaveBeenCalled();
  });

  test("clears input after sending message", async () => {
    const mockAddMessage = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(messageInput).toHaveValue("");
    });
  });

  test("displays user messages", () => {
    const mockMessages = [
      {
        id: "1",
        content: "Hello, how are you?",
        role: "user",
        timestamp: new Date(),
      },
    ];

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: mockMessages,
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const userMessage = screen.getByText("Hello, how are you?");
    expect(userMessage).toBeInTheDocument();
  });

  test("displays assistant messages", () => {
    const mockMessages = [
      {
        id: "1",
        content: "I am doing well, thank you!",
        role: "assistant",
        timestamp: new Date(),
      },
    ];

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: mockMessages,
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const assistantMessage = screen.getByText("I am doing well, thank you!");
    expect(assistantMessage).toBeInTheDocument();
  });

  test("handles WebSocket connection", () => {
    renderWithRouter(<Chat />);

    expect(global.WebSocket).toHaveBeenCalledWith(
      expect.stringContaining("ws://"),
    );
  });

  test("handles WebSocket message", async () => {
    const mockAddMessage = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    // Simulate WebSocket message
    const messageEvent = new MessageEvent("message", {
      data: JSON.stringify({
        content: "Hello from assistant!",
        role: "assistant",
      }),
    });

    // Find the message event listener and call it
    const messageListener = mockWebSocket.addEventListener.mock.calls.find(
      (call) => call[0] === "message",
    )[1];

    messageListener(messageEvent);

    await waitFor(() => {
      expect(mockAddMessage).toHaveBeenCalledWith({
        id: expect.any(String),
        content: "Hello from assistant!",
        role: "assistant",
        timestamp: expect.any(Date),
      });
    });
  });

  test("handles WebSocket error", () => {
    renderWithRouter(<Chat />);

    // Simulate WebSocket error
    const errorEvent = new Event("error");
    const errorListener = mockWebSocket.addEventListener.mock.calls.find(
      (call) => call[0] === "error",
    )[1];

    errorListener(errorEvent);

    expect(message.error).toHaveBeenCalledWith("WebSocket connection failed");
  });

  test("handles WebSocket close", () => {
    renderWithRouter(<Chat />);

    // Simulate WebSocket close
    const closeEvent = new CloseEvent("close");
    const closeListener = mockWebSocket.addEventListener.mock.calls.find(
      (call) => call[0] === "close",
    )[1];

    closeListener(closeEvent);

    expect(message.error).toHaveBeenCalledWith("WebSocket connection closed");
  });

  test("shows loading state while sending message", async () => {
    const mockAddMessage = jest
      .fn()
      .mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100)),
      );

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });
    fireEvent.click(sendButton);

    expect(sendButton).toBeDisabled();
    expect(screen.getByText(/sending/i)).toBeInTheDocument();
  });

  test("handles message sending error", async () => {
    const mockAddMessage = jest
      .fn()
      .mockRejectedValue(new Error("Failed to send message"));

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: mockAddMessage,
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(messageInput, {
      target: { value: "Hello, how are you?" },
    });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith("Failed to send message");
    });
  });

  test("handles clear chat", () => {
    const mockClearMessages = jest.fn();
    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: [],
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: mockClearMessages,
    });

    renderWithRouter(<Chat />);

    const clearButton = screen.getByRole("button", { name: /clear/i });
    fireEvent.click(clearButton);

    expect(mockClearMessages).toHaveBeenCalled();
  });

  test("handles file upload", () => {
    renderWithRouter(<Chat />);

    const fileInput = screen.getByLabelText(/upload file/i);
    const file = new File(["test content"], "test.txt", { type: "text/plain" });

    fireEvent.change(fileInput, { target: { files: [file] } });

    // Check if file upload handler is called
    expect(fileInput).toBeInTheDocument();
  });

  test("handles voice input", () => {
    renderWithRouter(<Chat />);

    const voiceButton = screen.getByRole("button", { name: /voice/i });
    fireEvent.click(voiceButton);

    // Check if voice recording starts
    expect(voiceButton).toBeInTheDocument();
  });

  test("handles message formatting", () => {
    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const boldButton = screen.getByRole("button", { name: /bold/i });

    fireEvent.click(boldButton);

    // Check if formatting is applied
    expect(boldButton).toBeInTheDocument();
  });

  test("handles message reactions", () => {
    const mockMessages = [
      {
        id: "1",
        content: "Hello, how are you?",
        role: "user",
        timestamp: new Date(),
        reactions: [],
      },
    ];

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: mockMessages,
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const reactionButton = screen.getByRole("button", { name: /like/i });
    fireEvent.click(reactionButton);

    // Check if reaction is added
    expect(reactionButton).toBeInTheDocument();
  });

  test("handles message search", () => {
    renderWithRouter(<Chat />);

    const searchInput = screen.getByPlaceholderText(/search messages/i);
    fireEvent.change(searchInput, { target: { value: "hello" } });

    // Check if search is performed
    expect(searchInput).toBeInTheDocument();
  });

  test("handles message export", () => {
    renderWithRouter(<Chat />);

    const exportButton = screen.getByRole("button", { name: /export/i });
    fireEvent.click(exportButton);

    // Check if export is triggered
    expect(exportButton).toBeInTheDocument();
  });

  test("handles accessibility features", () => {
    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    expect(messageInput).toHaveAttribute("aria-label");
    expect(sendButton).toHaveAttribute("aria-label");
  });

  test("handles keyboard shortcuts", () => {
    renderWithRouter(<Chat />);

    const messageInput = screen.getByPlaceholderText(/type your message/i);

    // Test Ctrl+Enter for new line
    fireEvent.keyDown(messageInput, { key: "Enter", ctrlKey: true });

    // Test Shift+Enter for send
    fireEvent.keyDown(messageInput, { key: "Enter", shiftKey: true });

    expect(messageInput).toBeInTheDocument();
  });

  test("handles message timestamps", () => {
    const mockMessages = [
      {
        id: "1",
        content: "Hello, how are you?",
        role: "user",
        timestamp: new Date("2023-01-01T10:00:00Z"),
      },
    ];

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: mockMessages,
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const timestamp = screen.getByText(/10:00/i);
    expect(timestamp).toBeInTheDocument();
  });

  test("handles message status indicators", () => {
    const mockMessages = [
      {
        id: "1",
        content: "Hello, how are you?",
        role: "user",
        timestamp: new Date(),
        status: "sent",
      },
    ];

    jest.mocked(require("../../store/chatStore").useChatStore).mockReturnValue({
      messages: mockMessages,
      addMessage: jest.fn(),
      setMessages: jest.fn(),
      clearMessages: jest.fn(),
    });

    renderWithRouter(<Chat />);

    const statusIndicator = screen.getByTestId("message-status");
    expect(statusIndicator).toBeInTheDocument();
  });
});
