import React from "react";
import { Spin, Progress, Skeleton } from "antd";
import { useThemeStore } from "../store/themeStore";
import "./LoadingStates.css";

export interface SkeletonCardProps {
  rows?: number;
  avatar?: boolean;
  title?: boolean;
  className?: string;
}

export interface LoadingSpinnerProps {
  size?: "small" | "default" | "large";
  text?: string;
  className?: string;
}

export interface ProgressIndicatorProps {
  percent?: number;
  status?: "active" | "exception" | "normal" | "success";
  size?: "small" | "default" | "large";
  showInfo?: boolean;
  className?: string;
}

// Modern Skeleton Card Component
export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  rows = 3,
  avatar = false,
  title = true,
  className = "",
}) => {
  const skeletonClasses = ["skeleton-card", className]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={skeletonClasses}>
      <Skeleton
        active
        avatar={avatar}
        title={title}
        paragraph={{ rows }}
        className="skeleton-card__content"
      />
    </div>
  );
};

// Modern Loading Spinner Component
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "default",
  text,
  className = "",
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const spinnerClasses = [
    "loading-spinner",
    `loading-spinner--${size}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const spinnerStyle: React.CSSProperties = {
    color: colors.colorPrimary,
  };

  return (
    <div className={spinnerClasses}>
      <Spin size={size} style={spinnerStyle} />
      {text && <div className="loading-spinner__text">{text}</div>}
    </div>
  );
};

// Modern Progress Indicator Component
export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  percent = 0,
  status = "active",
  size = "default",
  showInfo = true,
  className = "",
}) => {
  const progressClasses = [
    "progress-indicator",
    `progress-indicator--${size}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={progressClasses}>
      <Progress
        percent={percent}
        status={status}
        showInfo={showInfo}
        strokeColor={{
          "0%": "var(--colorPrimary)",
          "100%": "var(--colorSecondary)",
        }}
        className="progress-indicator__bar"
      />
    </div>
  );
};

// Skeleton List Component
export const SkeletonList: React.FC<{
  count?: number;
  className?: string;
}> = ({ count = 5, className = "" }) => {
  const listClasses = ["skeleton-list", className].filter(Boolean).join(" ");

  return (
    <div className={listClasses}>
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard
          key={index}
          rows={2}
          avatar={true}
          title={false}
          className="skeleton-list__item"
        />
      ))}
    </div>
  );
};

// Skeleton Grid Component
export const SkeletonGrid: React.FC<{
  rows?: number;
  cols?: number;
  className?: string;
}> = ({ rows = 3, cols = 3, className = "" }) => {
  const gridClasses = ["skeleton-grid", className].filter(Boolean).join(" ");

  return (
    <div className={gridClasses}>
      {Array.from({ length: rows * cols }).map((_, index) => (
        <SkeletonCard
          key={index}
          rows={2}
          avatar={false}
          title={true}
          className="skeleton-grid__item"
        />
      ))}
    </div>
  );
};

// Loading Overlay Component
export const LoadingOverlay: React.FC<{
  visible: boolean;
  text?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ visible, text, children, className = "" }) => {
  const overlayClasses = [
    "loading-overlay",
    visible && "loading-overlay--visible",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={overlayClasses}>
      {children}
      {visible && (
        <div className="loading-overlay__content">
          <LoadingSpinner text={text} />
        </div>
      )}
    </div>
  );
};

// Pulse Loading Component
export const PulseLoading: React.FC<{
  size?: "small" | "default" | "large";
  className?: string;
}> = ({ size = "default", className = "" }) => {
  const pulseClasses = ["pulse-loading", `pulse-loading--${size}`, className]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={pulseClasses}>
      <div className="pulse-loading__dot" />
      <div className="pulse-loading__dot" />
      <div className="pulse-loading__dot" />
    </div>
  );
};

// Wave Loading Component
export const WaveLoading: React.FC<{
  bars?: number;
  className?: string;
}> = ({ bars = 5, className = "" }) => {
  const waveClasses = ["wave-loading", className].filter(Boolean).join(" ");

  return (
    <div className={waveClasses}>
      {Array.from({ length: bars }).map((_, index) => (
        <div
          key={index}
          className="wave-loading__bar"
          style={{ animationDelay: `${index * 0.1}s` }}
        />
      ))}
    </div>
  );
};

// Shimmer Loading Component
export const ShimmerLoading: React.FC<{
  width?: string;
  height?: string;
  className?: string;
}> = ({ width = "100%", height = "20px", className = "" }) => {
  const shimmerClasses = ["shimmer-loading", className]
    .filter(Boolean)
    .join(" ");

  const shimmerStyle: React.CSSProperties = {
    width,
    height,
  };

  return (
    <div className={shimmerClasses} style={shimmerStyle}>
      <div className="shimmer-loading__content" />
    </div>
  );
};

export default LoadingSpinner;
