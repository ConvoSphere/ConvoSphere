import React, { Suspense } from "react";
import ProtectedRoute from "./ProtectedRoute";
import Layout from "./Layout";
import ErrorBoundary from "./ErrorBoundary";
import { Spin } from "antd";

const ProtectedLayoutRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <ProtectedRoute>
      <Layout>
        <ErrorBoundary>
          <Suspense
            fallback={
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "60vh",
                }}
              >
                <Spin size="large" />
              </div>
            }
          >
            {children}
          </Suspense>
        </ErrorBoundary>
      </Layout>
    </ProtectedRoute>
  );
};

export default ProtectedLayoutRoute;
