import React, { useState, useRef } from "react";
import { Select as AntSelect, SelectProps as AntSelectProps } from "antd";
import { DownOutlined, SearchOutlined, CloseOutlined } from "@ant-design/icons";
import { useThemeStore } from "../store/themeStore";
import "./ModernSelect.css";

export interface ModernSelectProps extends Omit<AntSelectProps, "size"> {
  variant?: "default" | "filled" | "outlined" | "ghost";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  status?: "default" | "success" | "warning" | "error";
  label?: string;
  helperText?: string;
  clearable?: boolean;
  searchable?: boolean;
  loading?: boolean;
  className?: string;
  onClear?: () => void;
}

const ModernSelect: React.FC<ModernSelectProps> = ({
  variant = "default",
  size = "md",
  status = "default",
  label,
  helperText,
  clearable = false,
  searchable = false,
  loading = false,
  className = "",
  onClear,
  children,
  ...props
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [isOpen, setIsOpen] = useState(false);
  const [hasValue, setHasValue] = useState(!!props.value);

  const selectClasses = [
    "modern-select",
    `modern-select--${variant}`,
    `modern-select--${size}`,
    `modern-select--${status}`,
    isOpen && "modern-select--open",
    hasValue && "modern-select--has-value",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const handleChange = (value: any, option: any) => {
    setHasValue(!!value);
    props.onChange?.(value, option);
  };

  const handleClear = () => {
    setHasValue(false);
    onClear?.();
  };

  const handleDropdownVisibleChange = (open: boolean) => {
    setIsOpen(open);
    props.onDropdownVisibleChange?.(open);
  };

  const selectStyle: React.CSSProperties = {
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
      borderBottom: "2px solid var(--colorBorder)",
      borderRadius: "0",
    }),
  };

  const dropdownStyle: React.CSSProperties = {
    borderRadius: "12px",
    boxShadow: "var(--shadow-lg)",
    border: "1px solid var(--colorBorder)",
    backgroundColor: "var(--colorBgContainer)",
  };

  return (
    <div className="modern-select-wrapper">
      {label && (
        <label className="modern-select__label">
          {label}
          {props.required && <span className="modern-select__required">*</span>}
        </label>
      )}

      <div className="modern-select__container">
        <AntSelect
          className={selectClasses}
          style={selectStyle}
          size={size === "xs" ? "small" : size === "lg" ? "large" : "middle"}
          allowClear={clearable}
          showSearch={searchable}
          loading={loading}
          suffixIcon={<DownOutlined className="modern-select__arrow" />}
          clearIcon={<CloseOutlined className="modern-select__clear" />}
          dropdownStyle={dropdownStyle}
          dropdownClassName="modern-select__dropdown"
          onChange={handleChange}
          onDropdownVisibleChange={handleDropdownVisibleChange}
          onClear={handleClear}
          {...props}
        >
          {children}
        </AntSelect>

        <div className="modern-select__focus-border" />
      </div>

      {helperText && (
        <div
          className={`modern-select__helper-text modern-select__helper-text--${status}`}
        >
          {helperText}
        </div>
      )}
    </div>
  );
};

export default ModernSelect;
