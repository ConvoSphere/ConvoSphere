import React, { useState, useEffect } from "react";
import { Form as AntForm, FormProps as AntFormProps, FormInstance } from "antd";
import { useThemeStore } from "../store/themeStore";
import "./ModernForm.css";

export interface ModernFormProps extends Omit<AntFormProps, "size"> {
  variant?: "default" | "card" | "minimal";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  children: React.ReactNode;
  className?: string;
  onSubmit?: (values: any) => void;
  onValuesChange?: (changedValues: any, allValues: any) => void;
}

export interface ModernFormItemProps {
  label?: string;
  required?: boolean;
  help?: string;
  validateStatus?: "success" | "warning" | "error" | "validating";
  children: React.ReactNode;
  className?: string;
}

const ModernForm: React.FC<ModernFormProps> = ({
  variant = "default",
  size = "md",
  loading = false,
  children,
  className = "",
  onSubmit,
  onValuesChange,
  ...props
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [form] = AntForm.useForm();

  const formClasses = [
    "modern-form",
    `modern-form--${variant}`,
    `modern-form--${size}`,
    loading && "modern-form--loading",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const formStyle: React.CSSProperties = {
    width: "100%",
    ...(variant === "card" && {
      background: colors.colorBgContainer,
      border: `1px solid ${colors.colorBorder}`,
      borderRadius: "16px",
      padding: "24px",
      boxShadow: colors.boxShadow,
    }),
    ...(variant === "minimal" && {
      background: "transparent",
      border: "none",
      padding: 0,
    }),
  };

  const handleSubmit = (values: any) => {
    onSubmit?.(values);
  };

  const handleValuesChange = (changedValues: any, allValues: any) => {
    onValuesChange?.(changedValues, allValues);
  };

  return (
    <div className="modern-form-wrapper">
      <AntForm
        form={form}
        className={formClasses}
        style={formStyle}
        layout="vertical"
        onFinish={handleSubmit}
        onValuesChange={handleValuesChange}
        {...props}
      >
        {children}
      </AntForm>
    </div>
  );
};

// Modern Form Item Component
export const ModernFormItem: React.FC<ModernFormItemProps> = ({
  label,
  required = false,
  help,
  validateStatus,
  children,
  className = "",
}) => {
  const itemClasses = [
    "modern-form-item",
    validateStatus && `modern-form-item--${validateStatus}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={itemClasses}>
      {label && (
        <label className="modern-form-item__label">
          {label}
          {required && <span className="modern-form-item__required">*</span>}
        </label>
      )}

      <div className="modern-form-item__control">{children}</div>

      {help && (
        <div
          className={`modern-form-item__help modern-form-item__help--${validateStatus || "default"}`}
        >
          {help}
        </div>
      )}
    </div>
  );
};

// Modern Form Section Component
export const ModernFormSection: React.FC<{
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ title, description, children, className = "" }) => {
  const sectionClasses = ["modern-form-section", className]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={sectionClasses}>
      {(title || description) && (
        <div className="modern-form-section__header">
          {title && <h3 className="modern-form-section__title">{title}</h3>}
          {description && (
            <p className="modern-form-section__description">{description}</p>
          )}
        </div>
      )}

      <div className="modern-form-section__content">{children}</div>
    </div>
  );
};

// Modern Form Actions Component
export const ModernFormActions: React.FC<{
  children: React.ReactNode;
  className?: string;
  align?: "left" | "center" | "right";
}> = ({ children, className = "", align = "right" }) => {
  const actionsClasses = [
    "modern-form-actions",
    `modern-form-actions--${align}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={actionsClasses}>{children}</div>;
};

export default ModernForm;
