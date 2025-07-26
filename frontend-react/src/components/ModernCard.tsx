import React from "react";
import { Card as AntCard, CardProps as AntCardProps } from "antd";
import { useThemeStore } from "../store/themeStore";
import "./ModernCard.css";

export interface ModernCardProps extends Omit<AntCardProps, "size"> {
  variant?: "default" | "elevated" | "interactive" | "gradient" | "outlined";
  size?: "sm" | "md" | "lg" | "xl";
  loading?: boolean;
  hoverable?: boolean;
  children: React.ReactNode;
  className?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  cover?: React.ReactNode;
  actions?: React.ReactNode[];
}

const ModernCard: React.FC<ModernCardProps> = ({
  variant = "default",
  size = "md",
  loading = false,
  hoverable = true,
  children,
  className = "",
  header,
  footer,
  cover,
  actions,
  ...props
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const cardClasses = [
    "modern-card",
    `modern-card--${variant}`,
    `modern-card--${size}`,
    hoverable && "modern-card--hoverable",
    loading && "modern-card--loading",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const cardStyle: React.CSSProperties = {
    borderRadius: "16px",
    overflow: "hidden",
    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    position: "relative",
    ...(variant === "gradient" && {
      background: colors.colorGradientPrimary,
      color: "#FFFFFF",
    }),
  };

  const renderHeader = () => {
    if (!header) return null;

    return <div className="modern-card__header">{header}</div>;
  };

  const renderFooter = () => {
    if (!footer) return null;

    return <div className="modern-card__footer">{footer}</div>;
  };

  const renderActions = () => {
    if (!actions || actions.length === 0) return null;

    return (
      <div className="modern-card__actions">
        {actions.map((action, index) => (
          <div key={index} className="modern-card__action">
            {action}
          </div>
        ))}
      </div>
    );
  };

  return (
    <AntCard
      className={cardClasses}
      style={cardStyle}
      loading={loading}
      hoverable={hoverable}
      cover={cover}
      actions={actions}
      {...props}
    >
      {renderHeader()}
      <div className="modern-card__content">{children}</div>
      {renderFooter()}
      {renderActions()}
    </AntCard>
  );
};

export default ModernCard;
