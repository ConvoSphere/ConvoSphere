import React from "react";
import { Switch, Tooltip } from "antd";
import { SunOutlined, MoonOutlined } from "@ant-design/icons";
import { useThemeStore, type ThemeMode } from "../store/themeStore";

const ThemeSwitcher: React.FC = () => {
  const mode = useThemeStore((s: { mode: ThemeMode }) => s.mode);
  const toggleMode = useThemeStore(
    (s: { toggleMode: () => void }) => s.toggleMode,
  );
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return (
    <Tooltip
      title={`Switch to ${mode === "dark" ? "light" : "dark"} mode`}
      placement="bottom"
    >
      <Switch
        checked={mode === "dark"}
        onChange={toggleMode}
        checkedChildren={<MoonOutlined />}
        unCheckedChildren={<SunOutlined />}
        aria-label={`Toggle ${mode === "dark" ? "light" : "dark"} mode`}
        style={{
          backgroundColor:
            mode === "dark" ? colors.colorPrimary : colors.colorTextSecondary,
          borderColor: colors.colorBorder,
        }}
        className="theme-switch"
      />
    </Tooltip>
  );
};

export default ThemeSwitcher;
