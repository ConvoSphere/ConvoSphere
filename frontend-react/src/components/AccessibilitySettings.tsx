import React from "react";
import {
  Card,
  Switch,
  Space,
  Typography,
  Divider,
  Button,
  Tooltip,
  Alert,
  List,
} from "antd";
import {
  EyeOutlined,
  FontSizeOutlined,
  PlayCircleOutlined,
  AudioOutlined,
  KeyboardOutlined,
  FocusOutlined,
  InfoCircleOutlined,
  ResetOutlined,
} from "@ant-design/icons";
import { useAccessibility } from "./AccessibilityProvider";
import { useThemeStore } from "../store/themeStore";

const { Title, Text, Paragraph } = Typography;

const AccessibilitySettings: React.FC = () => {
  const { settings, toggleSetting, updateSettings } = useAccessibility();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const handleReset = () => {
    updateSettings({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      screenReader: false,
      keyboardNavigation: true,
      focusIndicators: true,
    });
  };

  const accessibilityFeatures = [
    {
      key: "highContrast",
      title: "High Contrast",
      description: "Increase contrast for better visibility",
      icon: <EyeOutlined />,
      tooltip:
        "Makes text and backgrounds more distinct for better readability",
    },
    {
      key: "largeText",
      title: "Large Text",
      description: "Increase font size throughout the application",
      icon: <FontSizeOutlined />,
      tooltip: "Makes all text larger for easier reading",
    },
    {
      key: "reducedMotion",
      title: "Reduced Motion",
      description: "Disable animations and transitions",
      icon: <PlayCircleOutlined />,
      tooltip: "Removes animations that might cause motion sensitivity issues",
    },
    {
      key: "screenReader",
      title: "Screen Reader Support",
      description: "Enable enhanced screen reader announcements",
      icon: <AudioOutlined />,
      tooltip: "Provides additional context for screen reader users",
    },
    {
      key: "keyboardNavigation",
      title: "Keyboard Navigation",
      description: "Enable keyboard shortcuts and navigation",
      icon: <KeyboardOutlined />,
      tooltip: "Allows full navigation using keyboard only",
    },
    {
      key: "focusIndicators",
      title: "Focus Indicators",
      description: "Show clear focus indicators",
      icon: <FocusOutlined />,
      tooltip: "Makes it clear which element is currently focused",
    },
  ];

  const keyboardShortcuts = [
    { key: "Ctrl/Cmd + H", description: "Navigate to home page" },
    { key: "Ctrl/Cmd + N", description: "Navigate to next focusable element" },
    {
      key: "Ctrl/Cmd + P",
      description: "Navigate to previous focusable element",
    },
    { key: "Escape", description: "Clear focus or close modals" },
    { key: "Tab", description: "Navigate between interactive elements" },
    { key: "Shift + Tab", description: "Navigate backwards between elements" },
  ];

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <Title
        level={2}
        style={{ color: colors.colorTextBase, marginBottom: "24px" }}
      >
        Accessibility Settings
      </Title>

      <Alert
        message="Accessibility Features"
        description="Configure these settings to make the application more accessible for your needs. Changes are saved automatically and persist across sessions."
        type="info"
        icon={<InfoCircleOutlined />}
        style={{ marginBottom: "24px" }}
      />

      <Card
        style={{
          backgroundColor: colors.colorBgContainer,
          border: `1px solid ${colors.colorBorder}`,
          marginBottom: "24px",
        }}
      >
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          {accessibilityFeatures.map((feature) => (
            <div key={feature.key}>
              <Space
                align="center"
                style={{ width: "100%", justifyContent: "space-between" }}
              >
                <Space>
                  <span
                    style={{ color: colors.colorPrimary, fontSize: "18px" }}
                  >
                    {feature.icon}
                  </span>
                  <div>
                    <Tooltip title={feature.tooltip}>
                      <Text strong style={{ color: colors.colorTextBase }}>
                        {feature.title}
                      </Text>
                    </Tooltip>
                    <br />
                    <Text type="secondary" style={{ fontSize: "14px" }}>
                      {feature.description}
                    </Text>
                  </div>
                </Space>
                <Switch
                  checked={
                    settings[feature.key as keyof typeof settings] as boolean
                  }
                  onChange={() =>
                    toggleSetting(feature.key as keyof typeof settings)
                  }
                  size="large"
                />
              </Space>
              {feature.key !==
                accessibilityFeatures[accessibilityFeatures.length - 1].key && (
                <Divider style={{ margin: "16px 0" }} />
              )}
            </div>
          ))}
        </Space>
      </Card>

      <Card
        title={
          <Space>
            <KeyboardOutlined style={{ color: colors.colorPrimary }} />
            <Text strong style={{ color: colors.colorTextBase }}>
              Keyboard Shortcuts
            </Text>
          </Space>
        }
        style={{
          backgroundColor: colors.colorBgContainer,
          border: `1px solid ${colors.colorBorder}`,
          marginBottom: "24px",
        }}
      >
        <List
          dataSource={keyboardShortcuts}
          renderItem={(item) => (
            <List.Item style={{ border: "none", padding: "8px 0" }}>
              <Space style={{ width: "100%", justifyContent: "space-between" }}>
                <Text
                  code
                  style={{
                    backgroundColor: colors.colorBgElevated,
                    color: colors.colorTextBase,
                    padding: "4px 8px",
                    borderRadius: "4px",
                  }}
                >
                  {item.key}
                </Text>
                <Text style={{ color: colors.colorTextSecondary }}>
                  {item.description}
                </Text>
              </Space>
            </List.Item>
          )}
        />
      </Card>

      <Card
        title={
          <Space>
            <InfoCircleOutlined style={{ color: colors.colorPrimary }} />
            <Text strong style={{ color: colors.colorTextBase }}>
              Accessibility Information
            </Text>
          </Space>
        }
        style={{
          backgroundColor: colors.colorBgContainer,
          border: `1px solid ${colors.colorBorder}`,
          marginBottom: "24px",
        }}
      >
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          <Paragraph style={{ color: colors.colorTextSecondary, margin: 0 }}>
            This application is designed to be accessible to users with various
            disabilities. The accessibility features include:
          </Paragraph>

          <List
            size="small"
            dataSource={[
              "Screen reader compatibility with ARIA labels and descriptions",
              "Keyboard navigation support for all interactive elements",
              "High contrast mode for users with visual impairments",
              "Large text option for users with low vision",
              "Reduced motion option for users with motion sensitivity",
              "Focus indicators for keyboard users",
              "Semantic HTML structure for better screen reader interpretation",
            ]}
            renderItem={(item) => (
              <List.Item
                style={{
                  border: "none",
                  padding: "4px 0",
                  color: colors.colorTextSecondary,
                }}
              >
                • {item}
              </List.Item>
            )}
          />

          <Alert
            message="WCAG 2.1 AA Compliance"
            description="This application strives to meet WCAG 2.1 AA accessibility standards. If you encounter any accessibility issues, please report them to our support team."
            type="success"
            showIcon
            style={{ marginTop: "16px" }}
          />
        </Space>
      </Card>

      <div style={{ textAlign: "center" }}>
        <Button
          type="default"
          icon={<ResetOutlined />}
          onClick={handleReset}
          size="large"
          style={{
            borderColor: colors.colorBorder,
            color: colors.colorTextBase,
          }}
        >
          Reset to Default Settings
        </Button>
      </div>

      {/* Skip to main content link for screen readers */}
      <a
        href="#main-content"
        style={{
          position: "absolute",
          left: "-10000px",
          width: "1px",
          height: "1px",
          overflow: "hidden",
        }}
        onClick={(e) => {
          e.preventDefault();
          const mainContent =
            document.querySelector("main") ||
            document.querySelector("[role='main']");
          if (mainContent) {
            (mainContent as HTMLElement).focus();
          }
        }}
      >
        Skip to main content
      </a>
    </div>
  );
};

export default AccessibilitySettings;
