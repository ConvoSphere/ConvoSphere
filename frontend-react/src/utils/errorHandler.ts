import React from "react";
import { message, notification } from "antd";
import { useTranslation } from "react-i18next";

export interface ErrorInfo {
  code?: string;
  message: string;
  details?: string;
  endpoint?: string;
  timestamp: Date;
  userAction?: string;
}

export interface ErrorRecovery {
  action: string;
  description: string;
  handler?: () => void;
}

export class AppError extends Error {
  public code: string;
  public details?: string;
  public endpoint?: string;
  public userAction?: string;
  public recovery?: ErrorRecovery;

  constructor(
    message: string,
    code: string = "UNKNOWN_ERROR",
    details?: string,
    endpoint?: string,
    userAction?: string,
    recovery?: ErrorRecovery,
  ) {
    super(message);
    this.name = "AppError";
    this.code = code;
    this.details = details;
    this.endpoint = endpoint;
    this.userAction = userAction;
    this.recovery = recovery;
  }
}

export const ErrorCodes = {
  // Network errors
  NETWORK_ERROR: "NETWORK_ERROR",
  TIMEOUT_ERROR: "TIMEOUT_ERROR",
  CONNECTION_REFUSED: "CONNECTION_REFUSED",

  // Authentication errors
  UNAUTHORIZED: "UNAUTHORIZED",
  FORBIDDEN: "FORBIDDEN",
  TOKEN_EXPIRED: "TOKEN_EXPIRED",
  INVALID_CREDENTIALS: "INVALID_CREDENTIALS",

  // API errors
  API_ERROR: "API_ERROR",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  NOT_FOUND: "NOT_FOUND",
  CONFLICT: "CONFLICT",
  RATE_LIMIT: "RATE_LIMIT",

  // File errors
  FILE_TOO_LARGE: "FILE_TOO_LARGE",
  INVALID_FILE_TYPE: "INVALID_FILE_TYPE",
  UPLOAD_FAILED: "UPLOAD_FAILED",

  // Processing errors
  PROCESSING_ERROR: "PROCESSING_ERROR",
  TIMEOUT: "TIMEOUT",

  // General errors
  UNKNOWN_ERROR: "UNKNOWN_ERROR",
  INTERNAL_ERROR: "INTERNAL_ERROR",
} as const;

export const getErrorMessage = (error: any, t: any): string => {
  if (error instanceof AppError) {
    return error.message;
  }

  // Handle axios errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        return data?.detail || t("errors.bad_request", "Invalid request");
      case 401:
        return t(
          "errors.unauthorized",
          "You are not authorized to perform this action",
        );
      case 403:
        return t("errors.forbidden", "Access denied");
      case 404:
        return t("errors.not_found", "Resource not found");
      case 409:
        return t("errors.conflict", "Resource conflict");
      case 422:
        return data?.detail || t("errors.validation_error", "Validation error");
      case 429:
        return t(
          "errors.rate_limit",
          "Too many requests. Please try again later",
        );
      case 500:
        return t("errors.server_error", "Server error. Please try again later");
      case 502:
      case 503:
      case 504:
        return t(
          "errors.service_unavailable",
          "Service temporarily unavailable",
        );
      default:
        return data?.detail || t("errors.unknown", "An unknown error occurred");
    }
  }

  // Handle network errors
  if (error.request) {
    if (error.code === "ECONNABORTED") {
      return t("errors.timeout", "Request timed out. Please try again");
    }
    if (error.code === "ERR_NETWORK") {
      return t(
        "errors.network_error",
        "Network error. Please check your connection",
      );
    }
    return t("errors.connection_error", "Connection error. Please try again");
  }

  // Handle other errors
  if (error.message) {
    return error.message;
  }

  return t("errors.unknown", "An unknown error occurred");
};

export const getErrorRecovery = (
  error: any,
  t: any,
): ErrorRecovery | undefined => {
  if (error instanceof AppError && error.recovery) {
    return error.recovery;
  }

  // Handle specific error types
  if (error.response) {
    const status = error.response.status;

    switch (status) {
      case 401:
        return {
          action: t("errors.recovery.login", "Login"),
          description: t("errors.recovery.login_desc", "Please log in again"),
          handler: () => {
            // Redirect to login
            window.location.href = "/login";
          },
        };
      case 403:
        return {
          action: t("errors.recovery.contact_admin", "Contact Admin"),
          description: t(
            "errors.recovery.contact_admin_desc",
            "Contact your administrator for access",
          ),
        };
      case 429:
        return {
          action: t("errors.recovery.wait", "Wait"),
          description: t(
            "errors.recovery.wait_desc",
            "Please wait a few minutes before trying again",
          ),
        };
      case 500:
      case 502:
      case 503:
      case 504:
        return {
          action: t("errors.recovery.retry", "Retry"),
          description: t(
            "errors.recovery.retry_desc",
            "Try again in a few moments",
          ),
          handler: () => {
            // Retry the last action
            window.location.reload();
          },
        };
    }
  }

  if (error.code === "ECONNABORTED" || error.code === "ERR_NETWORK") {
    return {
      action: t("errors.recovery.check_connection", "Check Connection"),
      description: t(
        "errors.recovery.check_connection_desc",
        "Check your internet connection and try again",
      ),
    };
  }

  return undefined;
};

export const handleError = (
  error: any,
  context: string = "general",
  showNotification: boolean = true,
  showMessage: boolean = true,
  t?: (key: string, defaultValue?: string) => string,
): ErrorInfo => {
  const errorMessage = getErrorMessage(
    error,
    t || ((key: string, defaultValue?: string) => defaultValue || key),
  );
  const recovery = getErrorRecovery(
    error,
    t || ((key: string, defaultValue?: string) => defaultValue || key),
  );

  const errorInfo: ErrorInfo = {
    code: error.code || ErrorCodes.UNKNOWN_ERROR,
    message: errorMessage,
    details: error.details || error.stack,
    endpoint: error.config?.url || error.endpoint,
    timestamp: new Date(),
    userAction: context,
  };

  // Log error for debugging
  console.error(`[${context}] Error:`, errorInfo);
  console.error("Original error:", error);

  // Show user-friendly messages
  if (showMessage) {
    message.error(errorMessage);
  }

  if (showNotification && recovery) {
    notification.error({
      message: errorMessage,
      description: recovery.description,
      duration: 0,
      btn: recovery.handler
        ? {
            text: recovery.action,
            onClick: recovery.handler,
          }
        : undefined,
    });
  }

  return errorInfo;
};

export const createAppError = (
  message: string,
  code: string = ErrorCodes.UNKNOWN_ERROR,
  details?: string,
  endpoint?: string,
  userAction?: string,
  recovery?: ErrorRecovery,
): AppError => {
  return new AppError(message, code, details, endpoint, userAction, recovery);
};

// Specific error creators
export const createNetworkError = (
  endpoint: string,
  details?: string,
): AppError => {
  return createAppError(
    "Network error occurred",
    ErrorCodes.NETWORK_ERROR,
    details,
    endpoint,
    "network_request",
    {
      action: "Retry",
      description: "Check your connection and try again",
      handler: () => window.location.reload(),
    },
  );
};

export const createAuthError = (endpoint: string): AppError => {
  return createAppError(
    "Authentication required",
    ErrorCodes.UNAUTHORIZED,
    "User is not authenticated",
    endpoint,
    "authentication",
    {
      action: "Login",
      description: "Please log in to continue",
      handler: () => {
        window.location.href = "/login";
      },
    },
  );
};

export const createValidationError = (
  field: string,
  message: string,
): AppError => {
  return createAppError(
    `Validation error: ${field}`,
    ErrorCodes.VALIDATION_ERROR,
    message,
    undefined,
    "form_validation",
  );
};

export const createFileError = (
  fileType: string,
  details?: string,
): AppError => {
  return createAppError(
    `File error: ${fileType}`,
    ErrorCodes.FILE_TOO_LARGE,
    details,
    undefined,
    "file_upload",
  );
};

// Error boundary helper
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>,
) => {
  return class ErrorBoundary extends React.Component<
    P,
    { hasError: boolean; error?: Error }
  > {
    constructor(props: P) {
      super(props);
      this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error) {
      return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
      handleError(error, "error_boundary", true, false);
    }

    resetError = () => {
      this.setState({ hasError: false, error: undefined });
    };

    render() {
      if (this.state.hasError) {
        if (fallback) {
          return React.createElement(fallback, {
            error: this.state.error!,
            resetError: this.resetError,
          });
        }

        return React.createElement(
          "div",
          { style: { padding: 20, textAlign: "center" } },
          React.createElement("h3", null, "Something went wrong"),
          React.createElement(
            "button",
            { onClick: this.resetError },
            "Try again",
          ),
        );
      }

      return React.createElement(Component, this.props);
    }
  };
};
