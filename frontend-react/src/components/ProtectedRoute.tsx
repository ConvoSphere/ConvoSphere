import React, { useEffect, useState } from "react";
import { useAuthStore } from "../store/authStore";
import { Navigate } from "react-router-dom";
import { Spin } from "antd";

const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: "admin" | "super_admin" }> = ({
  children,
  requiredRole,
}) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const validateToken = useAuthStore((s) => s.validateToken);
  const refreshTokenIfNeeded = useAuthStore((s) => s.refreshTokenIfNeeded);
  const user = useAuthStore((s) => s.user);
  const [isValidating, setIsValidating] = useState(true);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    const validateAuth = async () => {
      try {
        // First check if we have a token
        if (!isAuthenticated) {
          setIsValid(false);
          setIsValidating(false);
          return;
        }

        // Validate the token
        const tokenValid = validateToken();
        if (!tokenValid) {
          // Try to refresh the token
          const refreshSuccess = await refreshTokenIfNeeded();
          setIsValid(refreshSuccess);
        } else {
          setIsValid(true);
        }
      } catch (error) {
        console.error("Token validation error:", error);
        setIsValid(false);
      } finally {
        setIsValidating(false);
      }
    };

    validateAuth();
  }, [isAuthenticated, validateToken, refreshTokenIfNeeded]);

  if (isValidating) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (!isValid) {
    return <Navigate to="/login" replace />;
  }

  // Admin role guard when required
  if (requiredRole) {
    const isAdminUser = user && (user.role === "admin" || user.role === "super_admin");
    if (!isAdminUser) {
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
