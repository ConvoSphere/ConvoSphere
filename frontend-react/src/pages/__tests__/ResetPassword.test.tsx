import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n";
import ResetPassword from "../ResetPassword";
import * as authService from "../../services/auth";

// Mock the auth service
jest.mock("../../services/auth");
const mockResetPassword = authService.resetPassword as jest.MockedFunction<
  typeof authService.resetPassword
>;
const mockValidateResetToken =
  authService.validateResetToken as jest.MockedFunction<
    typeof authService.validateResetToken
  >;

// Mock the ModernUI components
jest.mock("../../components/ModernCard", () => ({
  ModernCard: ({ children, ...props }: any) => (
    <div data-testid="modern-card" {...props}>
      {children}
    </div>
  ),
}));
jest.mock("../../components/ModernForm", () => ({
  ModernFormItem: ({ children, ...props }: any) => (
    <div data-testid="modern-form-item" {...props}>
      {children}
    </div>
  ),
}));
jest.mock("../../components/ModernInput", () => ({
  ModernInput: ({ ...props }: any) => (
    <input data-testid="modern-input" {...props} />
  ),
}));
jest.mock("../../components/ModernButton", () => ({
  ModernButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="modern-button" onClick={onClick} {...props}>
      {children}
    </button>
  ),
}));

// Mock useSearchParams
const mockSearchParams = new URLSearchParams();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useSearchParams: () => [mockSearchParams],
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>{component}</I18nextProvider>
    </BrowserRouter>,
  );
};

describe("ResetPassword", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSearchParams.clear();
  });

  it("shows loading state when validating token", () => {
    mockValidateResetToken.mockImplementation(() => new Promise(() => {})); // Never resolves
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    expect(screen.getByText("Token wird validiert...")).toBeInTheDocument();
  });

  it("shows invalid token state when token is invalid", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: false,
      message: "Token is invalid or expired",
    });
    mockSearchParams.set("token", "invalid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Ungültiger Token")).toBeInTheDocument();
      expect(
        screen.getByText("Token abgelaufen oder ungültig"),
      ).toBeInTheDocument();
      expect(screen.getByText("Neuen Token anfordern")).toBeInTheDocument();
    });
  });

  it("shows invalid token state when no token provided", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: false,
      message: "Token is invalid or expired",
    });

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Ungültiger Token")).toBeInTheDocument();
    });
  });

  it("renders reset password form when token is valid", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
      expect(
        screen.getByText("Geben Sie Ihr neues Passwort ein."),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText("Ihr neues Passwort"),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText("Bestätigen Sie Ihr neues Passwort"),
      ).toBeInTheDocument();
    });
  });

  it("handles successful password reset", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockResetPassword.mockResolvedValue({
      success: true,
      message: "Password reset successfully",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
    });

    const passwordInput = screen.getByPlaceholderText("Ihr neues Passwort");
    const confirmPasswordInput = screen.getByPlaceholderText(
      "Bestätigen Sie Ihr neues Passwort",
    );
    const submitButton = screen.getByText("Passwort zurücksetzen");

    fireEvent.change(passwordInput, { target: { value: "NewPassword123!" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "NewPassword123!" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockResetPassword).toHaveBeenCalledWith(
        "valid-token",
        "NewPassword123!",
      );
      expect(
        screen.getByText("Passwort-Reset erfolgreich"),
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "Ihr Passwort wurde erfolgreich zurückgesetzt. Sie können sich jetzt mit Ihrem neuen Passwort anmelden.",
        ),
      ).toBeInTheDocument();
    });
  });

  it("handles password reset error", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockResetPassword.mockResolvedValue({
      success: false,
      message: "Invalid or expired token",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
    });

    const passwordInput = screen.getByPlaceholderText("Ihr neues Passwort");
    const confirmPasswordInput = screen.getByPlaceholderText(
      "Bestätigen Sie Ihr neues Passwort",
    );
    const submitButton = screen.getByText("Passwort zurücksetzen");

    fireEvent.change(passwordInput, { target: { value: "NewPassword123!" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "NewPassword123!" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockResetPassword).toHaveBeenCalledWith(
        "valid-token",
        "NewPassword123!",
      );
    });
  });

  it("validates password confirmation", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
    });

    const passwordInput = screen.getByPlaceholderText("Ihr neues Passwort");
    const confirmPasswordInput = screen.getByPlaceholderText(
      "Bestätigen Sie Ihr neues Passwort",
    );
    const submitButton = screen.getByText("Passwort zurücksetzen");

    fireEvent.change(passwordInput, { target: { value: "NewPassword123!" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "DifferentPassword123!" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("Passwörter stimmen nicht überein"),
      ).toBeInTheDocument();
    });
  });

  it("validates password requirements", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
    });

    const passwordInput = screen.getByPlaceholderText("Ihr neues Passwort");
    const confirmPasswordInput = screen.getByPlaceholderText(
      "Bestätigen Sie Ihr neues Passwort",
    );
    const submitButton = screen.getByText("Passwort zurücksetzen");

    fireEvent.change(passwordInput, { target: { value: "123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("Passwort muss mindestens 8 Zeichen lang sein"),
      ).toBeInTheDocument();
    });
  });

  it("requires password fields", async () => {
    mockValidateResetToken.mockResolvedValue({
      valid: true,
      message: "Token is valid",
    });
    mockSearchParams.set("token", "valid-token");

    renderWithProviders(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText("Passwort zurücksetzen")).toBeInTheDocument();
    });

    const submitButton = screen.getByText("Passwort zurücksetzen");
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Passwort ist erforderlich")).toBeInTheDocument();
      expect(
        screen.getByText("Passwort-Bestätigung ist erforderlich"),
      ).toBeInTheDocument();
    });
  });
});
