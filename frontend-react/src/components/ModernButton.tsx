import React from "react";
import { Button, ButtonProps } from "antd";

interface ModernButtonProps extends ButtonProps {
  children: React.ReactNode;
}

const ModernButton: React.FC<ModernButtonProps> = ({ children, ...props }) => {
  return (
    <Button
      {...props}
      style={{
        borderRadius: "8px",
        fontWeight: 500,
        ...props.style,
      }}
    >
      {children}
    </Button>
  );
};

export default ModernButton;
