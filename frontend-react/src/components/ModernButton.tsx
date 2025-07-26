import React from "react";
import { Button as AntButton, ButtonProps as AntButtonProps } from "antd";
import { useThemeStore } from "../store/themeStore";
import "./ModernButton.css";

export interface ModernButtonProps extends Omit<AntButtonProps, "type"> {
  variant?:
    | "primary"
    | "secondary"
    | "accent"
    | "ghost"
    | "dashed"
    | "gradient";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
  children: React.ReactNode;
  className?: string;
}

const ModernButton: React.FC<ModernButtonProps> = ({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  iconPosition = "left",
  children,
  className = "",
  ...props
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const getButtonType = (variant: string): AntButtonProps["type"] => {
    switch (variant) {
      case "primary":
        return "primary";
      case "secondary":
        return "default";
      case "accent":
        return "default";
      case "ghost":
        return "text";
      case "dashed":
        return "dashed";
      case "gradient":
        return "primary";
      default:
        return "default";
    }
  };

  const buttonClasses = [
    "modern-button",
    `modern-button--${variant}`,
    `modern-button--${size}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const buttonStyle: React.CSSProperties = {
    position: "relative",
    overflow: "hidden",
    borderRadius: "12px",
    fontWeight: 600,
    letterSpacing: "0.025em",
    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    border: "none",
    ...(variant === "gradient" && {
      background: colors.colorGradientPrimary,
      color: "#FFFFFF",
    }),
  };

  const iconStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    marginRight: iconPosition === "left" ? "8px" : "0",
    marginLeft: iconPosition === "right" ? "8px" : "0",
    transition: "transform 0.2s ease",
  };

  const renderIcon = () => {
    if (!icon) return null;

    return (
      <span style={iconStyle} className="modern-button__icon">
        {icon}
      </span>
    );
  };

  return (
    <AntButton
      type={getButtonType(variant)}
      size={size === "xs" ? "small" : size === "lg" ? "large" : "middle"}
      loading={loading}
      className={buttonClasses}
      style={buttonStyle}
      {...props}
    >
      {iconPosition === "left" && renderIcon()}
      <span className="modern-button__content">{children}</span>
      {iconPosition === "right" && renderIcon()}
    </AntButton>
  );
};

export default ModernButton;
