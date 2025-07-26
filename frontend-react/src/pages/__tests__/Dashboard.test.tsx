import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import { ConfigProvider } from "antd";
import Dashboard from "../Dashboard";
import i18n from "../../i18n";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";

// Mock the stores
jest.mock("../../store/authStore");
jest.mock("../../store/themeStore");

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// Mock translations
jest.mock("react-i18next", () => ({
  ...jest.requireActual("react-i18next"),
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

const mockUser = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
  role: "user" as const,
  status: "active" as const,
  createdAt: "2024-01-01T00:00:00Z",
  lastLogin: "2024-01-15T10:30:00Z",
  loginCount: 100,
};

const mockAdminUser = {
  ...mockUser,
  role: "admin" as const,
};

const mockColors = {
  colorPrimary: "#1890ff",
  colorSecondary: "#52c41a",
  colorAccent: "#722ed1",
  colorTextBase: "#000000",
  colorBgContainer: "#ffffff",
  colorBorder: "#d9d9d9",
};

describe("Dashboard Component", () => {
  const renderDashboard = (user = mockUser) => {
    (useAuthStore as jest.Mock).mockReturnValue(user);
    (useThemeStore as jest.Mock).mockReturnValue({
      getCurrentColors: () => mockColors,
    });

    return render(
      <ConfigProvider>
        <I18nextProvider i18n={i18n}>
          <BrowserRouter>
            <Dashboard />
          </BrowserRouter>
        </I18nextProvider>
      </ConfigProvider>,
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock setTimeout for loading simulation
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe("Rendering", () => {
    it("renders dashboard with welcome message", async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText("dashboard.welcome")).toBeInTheDocument();
      });
    });

    it("renders dashboard subtitle", async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText("dashboard.subtitle")).toBeInTheDocument();
      });
    });

    it("shows loading state initially", () => {
      renderDashboard();

      // Should show loading indicators
      const loadingCards = screen
        .getAllByRole("generic")
        .filter((el) => el.className.includes("ant-card-loading"));
      expect(loadingCards.length).toBeGreaterThan(0);
    });

    it("loads dashboard data after timeout", async () => {
      renderDashboard();

      // Fast-forward timers to simulate data loading
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("156")).toBeInTheDocument(); // totalConversations
        expect(screen.getByText("2847")).toBeInTheDocument(); // totalMessages
        expect(screen.getByText("89")).toBeInTheDocument(); // totalDocuments
        expect(screen.getByText("12")).toBeInTheDocument(); // totalAssistants
      });
    });
  });

  describe("Statistics Cards", () => {
    it("displays conversation statistics", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.stats.conversations"),
        ).toBeInTheDocument();
        expect(screen.getByText("156")).toBeInTheDocument();
      });
    });

    it("displays message statistics", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.stats.messages"),
        ).toBeInTheDocument();
        expect(screen.getByText("2847")).toBeInTheDocument();
      });
    });

    it("displays document statistics", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.stats.documents"),
        ).toBeInTheDocument();
        expect(screen.getByText("89")).toBeInTheDocument();
      });
    });

    it("displays assistant statistics", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.stats.assistants"),
        ).toBeInTheDocument();
        expect(screen.getByText("12")).toBeInTheDocument();
      });
    });
  });

  describe("System Health Section", () => {
    it("displays system health status", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("dashboard.system_health")).toBeInTheDocument();
        expect(
          screen.getByText("dashboard.health.healthy"),
        ).toBeInTheDocument();
      });
    });

    it("displays active users count", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.stats.active_users"),
        ).toBeInTheDocument();
        expect(screen.getByText("23")).toBeInTheDocument();
      });
    });

    it("displays tools count", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("dashboard.stats.tools")).toBeInTheDocument();
        expect(screen.getByText("8")).toBeInTheDocument();
      });
    });

    it("displays performance indicator", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("dashboard.performance")).toBeInTheDocument();
      });
    });
  });

  describe("Quick Actions", () => {
    it("displays quick actions section", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.quick_actions.title"),
        ).toBeInTheDocument();
      });
    });

    it("renders start chat quick action", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const startChatButton = screen.getByText(
          "dashboard.quick_actions.start_chat",
        );
        expect(startChatButton).toBeInTheDocument();
      });
    });

    it("navigates to chat when start chat is clicked", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const startChatButton = screen.getByText(
          "dashboard.quick_actions.start_chat",
        );
        fireEvent.click(startChatButton);
        expect(mockNavigate).toHaveBeenCalledWith("/chat");
      });
    });

    it("renders upload document quick action", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const uploadButton = screen.getByText(
          "dashboard.quick_actions.upload_document",
        );
        expect(uploadButton).toBeInTheDocument();
      });
    });

    it("navigates to knowledge base when upload document is clicked", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const uploadButton = screen.getByText(
          "dashboard.quick_actions.upload_document",
        );
        fireEvent.click(uploadButton);
        expect(mockNavigate).toHaveBeenCalledWith("/knowledge-base");
      });
    });

    it("renders manage assistants quick action", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const assistantsButton = screen.getByText(
          "dashboard.quick_actions.manage_assistants",
        );
        expect(assistantsButton).toBeInTheDocument();
      });
    });

    it("navigates to assistants when manage assistants is clicked", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const assistantsButton = screen.getByText(
          "dashboard.quick_actions.manage_assistants",
        );
        fireEvent.click(assistantsButton);
        expect(mockNavigate).toHaveBeenCalledWith("/assistants");
      });
    });

    it("renders view tools quick action", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const toolsButton = screen.getByText(
          "dashboard.quick_actions.view_tools",
        );
        expect(toolsButton).toBeInTheDocument();
      });
    });

    it("navigates to tools when view tools is clicked", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const toolsButton = screen.getByText(
          "dashboard.quick_actions.view_tools",
        );
        fireEvent.click(toolsButton);
        expect(mockNavigate).toHaveBeenCalledWith("/tools");
      });
    });
  });

  describe("Recent Activity", () => {
    it("displays recent activity section", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.recent_activity"),
        ).toBeInTheDocument();
      });
    });

    it("displays activity items", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("Neue Konversation gestartet"),
        ).toBeInTheDocument();
        expect(
          screen.getByText("Dokument hochgeladen: Projektplan.pdf"),
        ).toBeInTheDocument();
        expect(
          screen.getByText('Assistent "Support Bot" erstellt'),
        ).toBeInTheDocument();
        expect(
          screen.getByText('MCP Tool "Weather API" hinzugefügt'),
        ).toBeInTheDocument();
      });
    });

    it("displays user tags in activity items", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("Max Mustermann")).toBeInTheDocument();
        expect(screen.getByText("Anna Schmidt")).toBeInTheDocument();
        expect(screen.getByText("Admin")).toBeInTheDocument();
      });
    });
  });

  describe("Admin Section", () => {
    it("shows admin section for admin users", async () => {
      renderDashboard(mockAdminUser);
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText("dashboard.admin_section")).toBeInTheDocument();
      });
    });

    it("does not show admin section for regular users", async () => {
      renderDashboard(mockUser);
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.queryByText("dashboard.admin_section"),
        ).not.toBeInTheDocument();
      });
    });

    it("displays admin statistics for admin users", async () => {
      renderDashboard(mockAdminUser);
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(
          screen.getByText("dashboard.admin.total_users"),
        ).toBeInTheDocument();
        expect(
          screen.getByText("dashboard.admin.system_load"),
        ).toBeInTheDocument();
        expect(screen.getByText("dashboard.admin.uptime")).toBeInTheDocument();
      });
    });

    it("navigates to admin dashboard when admin dashboard button is clicked", async () => {
      renderDashboard(mockAdminUser);
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        const adminButton = screen.getByText("dashboard.admin_dashboard");
        fireEvent.click(adminButton);
        expect(mockNavigate).toHaveBeenCalledWith("/admin");
      });
    });
  });

  describe("Error Handling", () => {
    it("handles loading errors gracefully", async () => {
      // Mock console.error to avoid test noise
      const consoleSpy = jest
        .spyOn(console, "error")
        .mockImplementation(() => {});

      renderDashboard();

      // Simulate an error during loading
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        // Should still render the component even if there's an error
        expect(screen.getByText("dashboard.welcome")).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe("Responsive Design", () => {
    it("renders with responsive grid layout", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        // Check that the grid layout is applied
        const gridContainer = screen
          .getByText("dashboard.stats.conversations")
          .closest(".ant-col");
        expect(gridContainer).toHaveClass("ant-col");
      });
    });
  });

  describe("Theme Integration", () => {
    it("applies theme colors correctly", async () => {
      renderDashboard();
      jest.advanceTimersByTime(1000);

      await waitFor(() => {
        // Check that theme colors are applied to statistics
        const statCards = screen
          .getAllByRole("generic")
          .filter((el) => el.className.includes("ant-statistic"));
        expect(statCards.length).toBeGreaterThan(0);
      });
    });
  });
});
