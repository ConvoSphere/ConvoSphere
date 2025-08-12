import React from "react";
import { Card, CardProps } from "antd";

interface ModernCardProps extends CardProps {
  children: React.ReactNode;
}

const ModernCard: React.FC<ModernCardProps> = ({ children, ...props }) => {
  return (
    <Card
      {...props}
      style={{
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
        border: "1px solid #f0f0f0",
        ...props.style,
      }}
    >
      {children}
    </Card>
  );
};

export default ModernCard;
