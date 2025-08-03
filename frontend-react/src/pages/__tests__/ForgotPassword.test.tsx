import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n";
import ForgotPassword from "../ForgotPassword";
import * as authService from "../../services/auth";

// Mock the auth service
jest.mock("../../services/auth");
const mockForgotPassword = authService.forgotPassword as jest.MockedFunction<typeof authService.forgotPassword>;

// Mock the ModernUI components
jest.mock("../../components/ModernUI", () => ({
  ModernCard: ({ children, ...props }: any) => <div data-testid="modern-card" {...props}>{children}</div>,
  ModernFormItem: ({ children, ...props }: any) => <div data-testid="modern-form-item" {...props}>{children}</div>,
  ModernInput: ({ ...props }: any) => <input data-testid="modern-input" {...props} />,
  ModernButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="modern-button" onClick={onClick} {...props}>{children}</button>
  ),
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        {component}
      </I18nextProvider>
    </BrowserRouter>
  );
};

describe("ForgotPassword", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders forgot password form", () => {
    renderWithProviders(<ForgotPassword />);
    
    expect(screen.getByText("Passwort vergessen?")).toBeInTheDocument();
    expect(screen.getByText("Geben Sie Ihre E-Mail-Adresse ein und wir senden Ihnen einen Link zum Zurücksetzen Ihres Passworts.")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("ihre.email@beispiel.com")).toBeInTheDocument();
    expect(screen.getByText("Reset-E-Mail senden")).toBeInTheDocument();
    expect(screen.getByText("Zurück zur Anmeldung")).toBeInTheDocument();
  });

  it("shows email sent success state", async () => {
    mockForgotPassword.mockResolvedValue({
      success: true,
      message: "Password reset email sent"
    });

    renderWithProviders(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText("ihre.email@beispiel.com");
    const submitButton = screen.getByText("Reset-E-Mail senden");
    
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText("Überprüfen Sie Ihre E-Mail")).toBeInTheDocument();
      expect(screen.getByText("Wir haben Ihnen eine E-Mail mit einem Link zum Zurücksetzen Ihres Passworts gesendet.")).toBeInTheDocument();
    });
  });

  it("handles form submission with valid email", async () => {
    mockForgotPassword.mockResolvedValue({
      success: true,
      message: "Password reset email sent"
    });

    renderWithProviders(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText("ihre.email@beispiel.com");
    const submitButton = screen.getByText("Reset-E-Mail senden");
    
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockForgotPassword).toHaveBeenCalledWith("test@example.com");
    });
  });

  it("handles form submission error", async () => {
    mockForgotPassword.mockResolvedValue({
      success: false,
      message: "User not found"
    });

    renderWithProviders(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText("ihre.email@beispiel.com");
    const submitButton = screen.getByText("Reset-E-Mail senden");
    
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockForgotPassword).toHaveBeenCalledWith("test@example.com");
    });
  });

  it("validates email format", async () => {
    renderWithProviders(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText("ihre.email@beispiel.com");
    const submitButton = screen.getByText("Reset-E-Mail senden");
    
    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText("Bitte geben Sie eine gültige E-Mail-Adresse ein")).toBeInTheDocument();
    });
  });

  it("requires email field", async () => {
    renderWithProviders(<ForgotPassword />);
    
    const submitButton = screen.getByText("Reset-E-Mail senden");
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText("E-Mail ist erforderlich")).toBeInTheDocument();
    });
  });

  it("allows trying different email after success", async () => {
    mockForgotPassword.mockResolvedValue({
      success: true,
      message: "Password reset email sent"
    });

    renderWithProviders(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText("ihre.email@beispiel.com");
    const submitButton = screen.getByText("Reset-E-Mail senden");
    
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText("Überprüfen Sie Ihre E-Mail")).toBeInTheDocument();
    });
    
    const tryDifferentEmailButton = screen.getByText("Andere E-Mail-Adresse versuchen");
    fireEvent.click(tryDifferentEmailButton);
    
    expect(screen.getByText("Passwort vergessen?")).toBeInTheDocument();
  });
});