import React, { useState, useRef, forwardRef } from "react";
import { Input as AntInput, InputProps as AntInputProps } from "antd";
import {
  EyeOutlined,
  EyeInvisibleOutlined,
  ClearOutlined,
} from "@ant-design/icons";

import "./ModernInput.css";

export interface ModernInputProps extends Omit<AntInputProps, "size"> {
  variant?: "default" | "filled" | "outlined" | "ghost";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  status?: "default" | "success" | "warning" | "error";
  label?: string;
  helperText?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  clearable?: boolean;
  showPasswordToggle?: boolean;
  className?: string;
  onClear?: () => void;
}

const ModernInput = forwardRef<HTMLInputElement, ModernInputProps>(
  (
    {
      variant = "default",
      size = "md",
      status = "default",
      label,
      helperText,
      prefix,
      suffix,
      clearable = false,
      showPasswordToggle = false,
      className = "",
      onClear,
      value,
      onChange,
      ...props
    },
    ref,
  ) => {
    
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);
    const [hasValue, setHasValue] = useState(!!value);
    const inputRef = useRef<HTMLInputElement>(null);

    const inputClasses = [
      "modern-input",
      `modern-input--${variant}`,
      `modern-input--${size}`,
      `modern-input--${status}`,
      isFocused && "modern-input--focused",
      hasValue && "modern-input--has-value",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      props.onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      props.onBlur?.(e);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setHasValue(!!e.target.value);
      onChange?.(e);
    };

    const handleClear = () => {
      if (inputRef.current) {
        inputRef.current.value = "";
        setHasValue(false);
        onClear?.();
        // Trigger change event
        const event = new Event("input", { bubbles: true });
        inputRef.current.dispatchEvent(event);
      }
    };

    const togglePasswordVisibility = () => {
      setShowPassword(!showPassword);
    };

    const getInputType = () => {
      if (showPasswordToggle && props.type === "password") {
        return showPassword ? "text" : "password";
      }
      return props.type;
    };

    const renderSuffix = () => {
      const suffixElements = [];

      if (clearable && hasValue) {
        suffixElements.push(
          <ClearOutlined
            key="clear"
            className="modern-input__clear"
            onClick={handleClear}
          />,
        );
      }

      if (showPasswordToggle && props.type === "password") {
        suffixElements.push(
          <button
            key="password-toggle"
            type="button"
            className="modern-input__password-toggle"
            onClick={togglePasswordVisibility}
          >
            {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
          </button>,
        );
      }

      if (suffix) {
        suffixElements.push(
          <span key="custom-suffix" className="modern-input__custom-suffix">
            {suffix}
          </span>,
        );
      }

      return suffixElements.length > 0 ? suffixElements : undefined;
    };

    const inputStyle: React.CSSProperties = {
      borderRadius: "12px",
      border: "1px solid var(--colorBorder)",
      transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      fontSize: "var(--font-size-base)",
      fontWeight: "var(--font-weight-normal)",
      ...(variant === "filled" && {
        backgroundColor: "var(--colorBgElevated)",
        borderColor: "transparent",
      }),
      ...(variant === "ghost" && {
        backgroundColor: "transparent",
        borderColor: "transparent",
      }),
    };

    return (
      <div className="modern-input-wrapper">
        {label && (
          <label className="modern-input__label">
            {label}
            {props.required && (
              <span className="modern-input__required">*</span>
            )}
          </label>
        )}

        <div className="modern-input__container">
          <AntInput
            ref={ref || inputRef}
            className={inputClasses}
            style={inputStyle}
            size={size === "xs" ? "small" : size === "lg" ? "large" : "middle"}
            prefix={prefix}
            suffix={renderSuffix()}
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            type={getInputType()}
            {...props}
          />

          <div className="modern-input__focus-border" />
        </div>

        {helperText && (
          <div
            className={`modern-input__helper-text modern-input__helper-text--${status}`}
          >
            {helperText}
          </div>
        )}
      </div>
    );
  },
);

ModernInput.displayName = "ModernInput";

export default ModernInput;
