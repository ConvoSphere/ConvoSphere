import React from "react";
import { Spin, Skeleton, Card, Space, Typography } from "antd";
import { LoadingOutlined, ReloadOutlined } from "@ant-design/icons";
import { useThemeStore } from "../store/themeStore";

const { Title, Text } = Typography;

interface LoadingSpinnerProps {
  size?: "small" | "default" | "large";
  text?: string;
  tip?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "default",
  text,
  tip,
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        gap: 16,
      }}
    >
      <Spin
        size={size}
        indicator={
          <LoadingOutlined
            style={{ fontSize: 24, color: colors.colorPrimary }}
            spin
          />
        }
        tip={tip}
      />
      {text && (
        <Text type="secondary" style={{ textAlign: "center" }}>
          {text}
        </Text>
      )}
    </div>
  );
};

interface LoadingCardProps {
  title?: string;
  rows?: number;
  avatar?: boolean;
  paragraph?: boolean;
  active?: boolean;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({
  title = true,
  rows = 3,
  avatar = false,
  paragraph = true,
  active = true,
}) => {
  return (
    <Card>
      <Skeleton
        active={active}
        avatar={avatar}
        paragraph={paragraph ? { rows } : false}
        title={title}
      />
    </Card>
  );
};

interface LoadingGridProps {
  count?: number;
  columns?: number;
  cardProps?: LoadingCardProps;
}

export const LoadingGrid: React.FC<LoadingGridProps> = ({
  count = 6,
  columns = 3,
  cardProps,
}) => {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: 16,
      }}
    >
      {Array.from({ length: count }).map((_, index) => (
        <LoadingCard key={index} {...cardProps} />
      ))}
    </div>
  );
};

interface LoadingTableProps {
  columns?: number;
  rows?: number;
  showHeader?: boolean;
}

export const LoadingTable: React.FC<LoadingTableProps> = ({
  columns = 5,
  rows = 5,
  showHeader = true,
}) => {
  return (
    <div style={{ width: "100%" }}>
      {showHeader && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap: 16,
            padding: "12px 16px",
            borderBottom: "1px solid #f0f0f0",
            backgroundColor: "#fafafa",
          }}
        >
          {Array.from({ length: columns }).map((_, index) => (
            <Skeleton.Input key={index} size="small" style={{ height: 20 }} />
          ))}
        </div>
      )}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap: 16,
            padding: "12px 16px",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton.Input
              key={colIndex}
              size="small"
              style={{ height: 16 }}
            />
          ))}
        </div>
      ))}
    </div>
  );
};

interface LoadingListProps {
  count?: number;
  avatar?: boolean;
  title?: boolean;
  paragraph?: boolean;
}

export const LoadingList: React.FC<LoadingListProps> = ({
  count = 5,
  avatar = true,
  title = true,
  paragraph = true,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          style={{
            padding: "16px",
            border: "1px solid #f0f0f0",
            borderRadius: 8,
          }}
        >
          <Skeleton
            active
            avatar={avatar}
            title={title}
            paragraph={paragraph ? { rows: 1 } : false}
          />
        </div>
      ))}
    </div>
  );
};

interface LoadingOverlayProps {
  visible: boolean;
  text?: string;
  children: React.ReactNode;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  visible,
  text = "Loading...",
  children,
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  if (!visible) {
    return <>{children}</>;
  }

  return (
    <div style={{ position: "relative" }}>
      {children}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(255, 255, 255, 0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          borderRadius: 8,
        }}
      >
        <div style={{ textAlign: "center" }}>
          <Spin
            size="large"
            indicator={
              <LoadingOutlined
                style={{ fontSize: 32, color: colors.colorPrimary }}
                spin
              />
            }
          />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">{text}</Text>
          </div>
        </div>
      </div>
    </div>
  );
};

interface LoadingButtonProps {
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: "primary" | "default" | "dashed" | "link" | "text";
  size?: "large" | "middle" | "small";
  icon?: React.ReactNode;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  children,
  onClick,
  disabled,
  type = "default",
  size = "middle",
  icon,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        padding:
          size === "large"
            ? "12px 24px"
            : size === "small"
              ? "6px 12px"
              : "8px 16px",
        border: type === "primary" ? "none" : "1px solid #d9d9d9",
        borderRadius: 6,
        backgroundColor: type === "primary" ? "#1890ff" : "#fff",
        color: type === "primary" ? "#fff" : "#000",
        cursor: disabled || loading ? "not-allowed" : "pointer",
        opacity: disabled || loading ? 0.6 : 1,
        display: "flex",
        alignItems: "center",
        gap: 8,
        fontSize: size === "large" ? 16 : size === "small" ? 12 : 14,
      }}
    >
      {loading ? <LoadingOutlined style={{ fontSize: 14 }} /> : icon}
      {children}
    </button>
  );
};

interface LoadingStateProps {
  loading: boolean;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
  onRetry?: () => void;
  children: React.ReactNode;
  loadingComponent?: React.ReactNode;
  errorComponent?: React.ReactNode;
  emptyComponent?: React.ReactNode;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  loading,
  error,
  empty = false,
  emptyText = "No data available",
  onRetry,
  children,
  loadingComponent,
  errorComponent,
  emptyComponent,
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  if (loading) {
    return loadingComponent ? (
      <>{loadingComponent}</>
    ) : (
      <LoadingSpinner text="Loading data..." />
    );
  }

  if (error) {
    return errorComponent ? (
      <>{errorComponent}</>
    ) : (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 20px",
          gap: 16,
        }}
      >
        <Text type="danger" style={{ textAlign: "center" }}>
          {error}
        </Text>
        {onRetry && (
          <button
            onClick={onRetry}
            style={{
              padding: "8px 16px",
              border: "1px solid #d9d9d9",
              borderRadius: 6,
              backgroundColor: "#fff",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <ReloadOutlined />
            Retry
          </button>
        )}
      </div>
    );
  }

  if (empty) {
    return emptyComponent ? (
      <>{emptyComponent}</>
    ) : (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 20px",
          gap: 16,
        }}
      >
        <Text type="secondary" style={{ textAlign: "center" }}>
          {emptyText}
        </Text>
      </div>
    );
  }

  return <>{children}</>;
};

// HOC for adding loading state to components
export const withLoading = <P extends object>(
  Component: React.ComponentType<P>,
  loadingProps: {
    loadingKey: keyof P;
    errorKey?: keyof P;
    emptyKey?: keyof P;
  },
) => {
  return React.forwardRef<any, P>((props, ref) => {
    const loading = props[loadingProps.loadingKey] as boolean;
    const error = loadingProps.errorKey
      ? (props[loadingProps.errorKey] as string)
      : null;
    const empty = loadingProps.emptyKey
      ? (props[loadingProps.emptyKey] as boolean)
      : false;

    return (
      <LoadingState loading={loading} error={error} empty={empty}>
        <Component {...props} ref={ref} />
      </LoadingState>
    );
  });
};
