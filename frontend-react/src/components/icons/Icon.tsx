/**
 * Icon Component
 *
 * A unified icon component that provides access to all categorized icons
 * with consistent styling and theming support.
 */

import React from "react";
import { useThemeStore } from "../../store/themeStore";
import type { IconProps } from "./types";
import { navigationIcons } from "./navigation";
import { actionIcons } from "./actions";
import { communicationIcons } from "./communication";
import { mediaIcons } from "./media";
import { systemIcons } from "./system";
import { dataIcons } from "./data";
import { feedbackIcons } from "./feedback";
import { textFormatIcons } from "./text-format";

// Combine all icon mappings
const allIcons = {
  ...navigationIcons,
  ...actionIcons,
  ...communicationIcons,
  ...mediaIcons,
  ...systemIcons,
  ...dataIcons,
  ...feedbackIcons,
  ...textFormatIcons,
};

const Icon: React.FC<IconProps> = ({
  name,
  size = "md",
  variant = "primary",
  className = "",
  style = {},
  onClick,
}) => {
  const { mode } = useThemeStore();

  // Get the icon component
  const IconComponent = allIcons[name];

  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  // Size mapping
  const sizeMap = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
  };

  // Get variant color based on theme
  const getVariantColor = () => {
    const isDark = mode === "dark";

    const colors = {
      primary: isDark ? "#1890ff" : "#1890ff",
      secondary: isDark ? "#8c8c8c" : "#595959",
      accent: isDark ? "#722ed1" : "#722ed1",
      success: isDark ? "#52c41a" : "#52c41a",
      warning: isDark ? "#faad14" : "#faad14",
      error: isDark ? "#ff4d4f" : "#ff4d4f",
      info: isDark ? "#13c2c2" : "#13c2c2",
      muted: isDark ? "#595959" : "#8c8c8c",
    };

    return colors[variant];
  };

  // Handle click events
  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  return (
    <IconComponent
      style={{
        fontSize: sizeMap[size],
        color: getVariantColor(),
        cursor: onClick ? "pointer" : "default",
        transition: "all 0.2s ease",
        ...style,
      }}
      className={className}
      onClick={handleClick}
    />
  );
};

export default Icon;
