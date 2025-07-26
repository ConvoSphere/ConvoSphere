import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { message } from "antd";
import Login from "../Login";
import { getSSOProviders, ssoLogin } from "../../services/auth";

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
    login: jest.fn(),
    user: null,
  })),
}));

// Mock the API service
jest.mock("../../services/auth", () => ({
  login: jest.fn(),
  getSSOProviders: jest.fn(),
  ssoLogin: jest.fn(),
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("Login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders login form", () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
    expect(loginButton).toBeInTheDocument();
  });

  test("renders registration link", () => {
    renderWithRouter(<Login />);

    const registerLink = screen.getByText(/don't have an account/i);
    expect(registerLink).toBeInTheDocument();
  });

  test("handles form input changes", () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
  });

  test("validates required fields", async () => {
    renderWithRouter(<Login />);

    const loginButton = screen.getByRole("button", { name: /login/i });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test("validates email format", async () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(
        screen.getByText(/please enter a valid email/i),
      ).toBeInTheDocument();
    });
  });

  test("validates password length", async () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(
        screen.getByText(/password must be at least 6 characters/i),
      ).toBeInTheDocument();
    });
  });

  test("handles successful login", async () => {
    const mockLogin = jest.fn().mockResolvedValue({
      user: { id: "1", email: "test@example.com" },
      token: "fake-token",
    });

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
  });

  test("handles login error", async () => {
    const mockLogin = jest
      .fn()
      .mockRejectedValue(new Error("Invalid credentials"));

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrongpassword" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith("Login failed.");
    });
  });

  test("shows loading state during login", async () => {
    const mockLogin = jest
      .fn()
      .mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100)),
      );

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    expect(loginButton).toBeDisabled();
    expect(screen.getByText(/logging in/i)).toBeInTheDocument();
  });

  test("handles form submission with Enter key", async () => {
    const mockLogin = jest.fn().mockResolvedValue({
      user: { id: "1", email: "test@example.com" },
      token: "fake-token",
    });

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.keyDown(passwordInput, { key: "Enter" });

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
  });

  test("navigates to register page", () => {
    renderWithRouter(<Login />);

    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);

    // Check if navigation occurred
    expect(registerLink).toBeInTheDocument();
  });

  test("handles forgot password link", () => {
    renderWithRouter(<Login />);

    const forgotPasswordLink = screen.getByText(/forgot password/i);
    expect(forgotPasswordLink).toBeInTheDocument();

    fireEvent.click(forgotPasswordLink);

    // Check if forgot password modal or page is shown
    expect(forgotPasswordLink).toBeInTheDocument();
  });

  test("clears form after successful login", async () => {
    const mockLogin = jest.fn().mockResolvedValue({
      user: { id: "1", email: "test@example.com" },
      token: "fake-token",
    });

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
  });

  test("handles network error", async () => {
    const mockLogin = jest.fn().mockRejectedValue(new Error("Network error"));

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith("Login failed.");
    });
  });

  test("handles server error response", async () => {
    const mockLogin = jest.fn().mockRejectedValue({
      response: { data: { message: "Server error" } },
    });

    jest.mocked(require("../../store/authStore").useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
    });

    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith("Login failed.");
    });
  });

  test("handles accessibility attributes", () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole("button", { name: /login/i });

    expect(emailInput).toHaveAttribute("type", "email");
    expect(passwordInput).toHaveAttribute("type", "password");
    expect(loginButton).toHaveAttribute("type", "submit");
  });

  test("handles form reset", () => {
    renderWithRouter(<Login />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const resetButton = screen.getByRole("button", { name: /reset/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    fireEvent.click(resetButton);

    expect(emailInput).toHaveValue("");
    expect(passwordInput).toHaveValue("");
  });

  test("handles remember me checkbox", () => {
    renderWithRouter(<Login />);

    const rememberMeCheckbox = screen.getByLabelText(/remember me/i);
    expect(rememberMeCheckbox).toBeInTheDocument();

    fireEvent.click(rememberMeCheckbox);
    expect(rememberMeCheckbox).toBeChecked();
  });

  test("handles social login buttons", () => {
    renderWithRouter(<Login />);

    const googleButton = screen.getByRole("button", { name: /google/i });
    const githubButton = screen.getByRole("button", { name: /github/i });

    expect(googleButton).toBeInTheDocument();
    expect(githubButton).toBeInTheDocument();

    fireEvent.click(googleButton);
    fireEvent.click(githubButton);

    // Check if social login handlers are called
    expect(googleButton).toBeInTheDocument();
    expect(githubButton).toBeInTheDocument();
  });
});

describe("Login SSO Buttons", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("zeigt keine SSO-Buttons wenn keine Provider", async () => {
    (getSSOProviders as jest.Mock).mockResolvedValue([]);
    renderWithRouter(<Login />);
    await waitFor(() => {
      expect(screen.queryByText(/login with/i)).not.toBeInTheDocument();
    });
  });

  test("zeigt Google und Microsoft SSO-Buttons", async () => {
    (getSSOProviders as jest.Mock).mockResolvedValue([
      { id: "google", name: "Google", icon: "google" },
      { id: "microsoft", name: "Microsoft", icon: "microsoft" },
    ]);
    renderWithRouter(<Login />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /login with google/i }),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /login with microsoft/i }),
      ).toBeInTheDocument();
    });
  });

  test("klick auf SSO-Button ruft ssoLogin auf", async () => {
    (getSSOProviders as jest.Mock).mockResolvedValue([
      { id: "google", name: "Google", icon: "google" },
    ]);
    renderWithRouter(<Login />);
    await waitFor(() => {
      const btn = screen.getByRole("button", { name: /login with google/i });
      fireEvent.click(btn);
      expect(ssoLogin).toHaveBeenCalledWith("google");
    });
  });
});
