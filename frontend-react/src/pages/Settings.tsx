import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import {
  Typography,
  Space,
  Divider,
  Row,
  Col,
  Statistic,
  Alert,
  message,
} from "antd";
import {
  SettingOutlined,
  GlobalOutlined,
  EyeOutlined,
  BellOutlined,
  SecurityScanOutlined,
  PaletteOutlined,
  UserOutlined,
  LockOutlined,
  NotificationOutlined,
  MonitorOutlined,
  SaveOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernSelect from "../components/ModernSelect";
import ModernForm, { ModernFormItem } from "../components/ModernForm";

const { Title, Text } = Typography;

const Settings: React.FC = () => {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    language: user?.language || "de",
    theme: "light",
    notifications: true,
    emailNotifications: true,
    soundEnabled: true,
    autoSave: true,
    privacyMode: false,
    analytics: true,
  });

  const handleSettingChange = async (key: string, value: any) => {
    setSaving(true);
    try {
      if (key === "language") {
        await updateProfile({ language: value });
        message.success(t("settings.language_updated", "Sprache aktualisiert"));
      } else {
        // Update local settings
        setSettings((prev) => ({ ...prev, [key]: value }));
        message.success(
          t("settings.setting_updated", "Einstellung aktualisiert"),
        );
      }
    } catch {
      message.error(
        t("settings.update_failed", "Aktualisierung fehlgeschlagen"),
      );
    } finally {
      setSaving(false);
    }
  };

  const handleResetSettings = () => {
    setSettings({
      language: "de",
      theme: "light",
      notifications: true,
      emailNotifications: true,
      soundEnabled: true,
      autoSave: true,
      privacyMode: false,
      analytics: true,
    });
    message.success(t("settings.reset_success", "Einstellungen zurückgesetzt"));
  };

  const getThemeIcon = (theme: string) => {
    switch (theme) {
      case "dark":
        return "🌙";
      case "auto":
        return "🔄";
      default:
        return "☀️";
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        {/* Header Section */}
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 24px",
                fontSize: "32px",
              }}
            >
              ⚙️
            </div>
            <Title
              level={1}
              style={{ color: "#FFFFFF", marginBottom: 8, fontSize: "2.5rem" }}
            >
              {t("settings.title", "Einstellungen")}
            </Title>
            <Text
              style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}
            >
              {t(
                "settings.subtitle",
                "Passen Sie die Anwendung an Ihre Bedürfnisse an",
              )}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Row gutter={[24, 24]}>
            {/* Main Settings */}
            <Col xs={24} lg={16}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Language & Regional Settings */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <GlobalOutlined
                        style={{ color: colors.colorPrimary, fontSize: "20px" }}
                      />
                      <Title level={3} style={{ margin: 0 }}>
                        {t("settings.language_regional", "Sprache & Region")}
                      </Title>
                    </div>
                  }
                >
                  <Row gutter={[24, 24]}>
                    <Col xs={24} md={12}>
                      <ModernFormItem
                        label={t("settings.language", "Sprache")}
                        style={{ marginBottom: 0 }}
                      >
                        <ModernSelect
                          value={settings.language}
                          onChange={(value) =>
                            handleSettingChange("language", value)
                          }
                          loading={saving}
                          disabled={saving}
                          style={{ width: "100%" }}
                        >
                          <ModernSelect.Option value="de">
                            🇩🇪 Deutsch
                          </ModernSelect.Option>
                          <ModernSelect.Option value="en">
                            🇺🇸 English
                          </ModernSelect.Option>
                          <ModernSelect.Option value="fr">
                            🇫🇷 Français
                          </ModernSelect.Option>
                          <ModernSelect.Option value="es">
                            🇪🇸 Español
                          </ModernSelect.Option>
                        </ModernSelect>
                      </ModernFormItem>
                    </Col>

                    <Col xs={24} md={12}>
                      <ModernFormItem
                        label={t("settings.timezone", "Zeitzone")}
                        style={{ marginBottom: 0 }}
                      >
                        <ModernSelect
                          defaultValue="Europe/Berlin"
                          style={{ width: "100%" }}
                        >
                          <ModernSelect.Option value="Europe/Berlin">
                            🇩🇪 Berlin (UTC+1)
                          </ModernSelect.Option>
                          <ModernSelect.Option value="Europe/London">
                            🇬🇧 London (UTC+0)
                          </ModernSelect.Option>
                          <ModernSelect.Option value="America/New_York">
                            🇺🇸 New York (UTC-5)
                          </ModernSelect.Option>
                        </ModernSelect>
                      </ModernFormItem>
                    </Col>
                  </Row>
                </ModernCard>

                {/* Appearance Settings */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <PaletteOutlined
                        style={{
                          color: colors.colorSecondary,
                          fontSize: "20px",
                        }}
                      />
                      <Title level={3} style={{ margin: 0 }}>
                        {t("settings.appearance", "Erscheinungsbild")}
                      </Title>
                    </div>
                  }
                >
                  <Row gutter={[24, 24]}>
                    <Col xs={24} md={12}>
                      <ModernFormItem
                        label={t("settings.theme", "Design")}
                        style={{ marginBottom: 0 }}
                      >
                        <ModernSelect
                          value={settings.theme}
                          onChange={(value) =>
                            handleSettingChange("theme", value)
                          }
                          style={{ width: "100%" }}
                        >
                          <ModernSelect.Option value="light">
                            ☀️ {t("settings.theme_light", "Hell")}
                          </ModernSelect.Option>
                          <ModernSelect.Option value="dark">
                            🌙 {t("settings.theme_dark", "Dunkel")}
                          </ModernSelect.Option>
                          <ModernSelect.Option value="auto">
                            🔄 {t("settings.theme_auto", "Automatisch")}
                          </ModernSelect.Option>
                        </ModernSelect>
                      </ModernFormItem>
                    </Col>

                    <Col xs={24} md={12}>
                      <ModernFormItem
                        label={t("settings.font_size", "Schriftgröße")}
                        style={{ marginBottom: 0 }}
                      >
                        <ModernSelect
                          defaultValue="medium"
                          style={{ width: "100%" }}
                        >
                          <ModernSelect.Option value="small">
                            {t("settings.font_small", "Klein")}
                          </ModernSelect.Option>
                          <ModernSelect.Option value="medium">
                            {t("settings.font_medium", "Mittel")}
                          </ModernSelect.Option>
                          <ModernSelect.Option value="large">
                            {t("settings.font_large", "Groß")}
                          </ModernSelect.Option>
                        </ModernSelect>
                      </ModernFormItem>
                    </Col>
                  </Row>
                </ModernCard>

                {/* Notification Settings */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <BellOutlined
                        style={{ color: colors.colorAccent, fontSize: "20px" }}
                      />
                      <Title level={3} style={{ margin: 0 }}>
                        {t("settings.notifications", "Benachrichtigungen")}
                      </Title>
                    </div>
                  }
                >
                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "16px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "12px",
                        border: `1px solid ${colors.colorBorder}`,
                      }}
                    >
                      <div>
                        <Text strong style={{ fontSize: "16px" }}>
                          {t(
                            "settings.push_notifications",
                            "Push-Benachrichtigungen",
                          )}
                        </Text>
                        <br />
                        <Text type="secondary">
                          {t(
                            "settings.push_notifications_desc",
                            "Erhalten Sie Benachrichtigungen über neue Nachrichten",
                          )}
                        </Text>
                      </div>
                      <ModernButton
                        variant={
                          settings.notifications ? "primary" : "outlined"
                        }
                        size="md"
                        onClick={() =>
                          handleSettingChange(
                            "notifications",
                            !settings.notifications,
                          )
                        }
                      >
                        {settings.notifications
                          ? t("settings.enabled", "Aktiviert")
                          : t("settings.disabled", "Deaktiviert")}
                      </ModernButton>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "16px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "12px",
                        border: `1px solid ${colors.colorBorder}`,
                      }}
                    >
                      <div>
                        <Text strong style={{ fontSize: "16px" }}>
                          {t(
                            "settings.email_notifications",
                            "E-Mail-Benachrichtigungen",
                          )}
                        </Text>
                        <br />
                        <Text type="secondary">
                          {t(
                            "settings.email_notifications_desc",
                            "Erhalten Sie wichtige Updates per E-Mail",
                          )}
                        </Text>
                      </div>
                      <ModernButton
                        variant={
                          settings.emailNotifications ? "primary" : "outlined"
                        }
                        size="md"
                        onClick={() =>
                          handleSettingChange(
                            "emailNotifications",
                            !settings.emailNotifications,
                          )
                        }
                      >
                        {settings.emailNotifications
                          ? t("settings.enabled", "Aktiviert")
                          : t("settings.disabled", "Deaktiviert")}
                      </ModernButton>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "16px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "12px",
                        border: `1px solid ${colors.colorBorder}`,
                      }}
                    >
                      <div>
                        <Text strong style={{ fontSize: "16px" }}>
                          {t(
                            "settings.sound_notifications",
                            "Ton-Benachrichtigungen",
                          )}
                        </Text>
                        <br />
                        <Text type="secondary">
                          {t(
                            "settings.sound_notifications_desc",
                            "Spielen Sie Töne bei neuen Nachrichten ab",
                          )}
                        </Text>
                      </div>
                      <ModernButton
                        variant={settings.soundEnabled ? "primary" : "outlined"}
                        size="md"
                        onClick={() =>
                          handleSettingChange(
                            "soundEnabled",
                            !settings.soundEnabled,
                          )
                        }
                      >
                        {settings.soundEnabled
                          ? t("settings.enabled", "Aktiviert")
                          : t("settings.disabled", "Deaktiviert")}
                      </ModernButton>
                    </div>
                  </Space>
                </ModernCard>

                {/* Privacy & Security */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <SecurityScanOutlined
                        style={{ color: "#FF6B6B", fontSize: "20px" }}
                      />
                      <Title level={3} style={{ margin: 0 }}>
                        {t(
                          "settings.privacy_security",
                          "Datenschutz & Sicherheit",
                        )}
                      </Title>
                    </div>
                  }
                >
                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "16px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "12px",
                        border: `1px solid ${colors.colorBorder}`,
                      }}
                    >
                      <div>
                        <Text strong style={{ fontSize: "16px" }}>
                          {t("settings.privacy_mode", "Privatsphäre-Modus")}
                        </Text>
                        <br />
                        <Text type="secondary">
                          {t(
                            "settings.privacy_mode_desc",
                            "Verstecken Sie sensible Informationen",
                          )}
                        </Text>
                      </div>
                      <ModernButton
                        variant={settings.privacyMode ? "primary" : "outlined"}
                        size="md"
                        onClick={() =>
                          handleSettingChange(
                            "privacyMode",
                            !settings.privacyMode,
                          )
                        }
                      >
                        {settings.privacyMode
                          ? t("settings.enabled", "Aktiviert")
                          : t("settings.disabled", "Deaktiviert")}
                      </ModernButton>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "16px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "12px",
                        border: `1px solid ${colors.colorBorder}`,
                      }}
                    >
                      <div>
                        <Text strong style={{ fontSize: "16px" }}>
                          {t("settings.analytics", "Analytics")}
                        </Text>
                        <br />
                        <Text type="secondary">
                          {t(
                            "settings.analytics_desc",
                            "Helfen Sie uns, die Anwendung zu verbessern",
                          )}
                        </Text>
                      </div>
                      <ModernButton
                        variant={settings.analytics ? "primary" : "outlined"}
                        size="md"
                        onClick={() =>
                          handleSettingChange("analytics", !settings.analytics)
                        }
                      >
                        {settings.analytics
                          ? t("settings.enabled", "Aktiviert")
                          : t("settings.disabled", "Deaktiviert")}
                      </ModernButton>
                    </div>
                  </Space>
                </ModernCard>
              </div>
            </Col>

            {/* Sidebar */}
            <Col xs={24} lg={8}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Quick Actions */}
                <ModernCard variant="interactive" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("settings.quick_actions", "Schnellaktionen")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    <ModernButton
                      variant="primary"
                      size="md"
                      icon={<SaveOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("settings.save_all", "Alle speichern")}
                    </ModernButton>

                    <ModernButton
                      variant="outlined"
                      size="md"
                      icon={<ReloadOutlined />}
                      onClick={handleResetSettings}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("settings.reset_defaults", "Zurücksetzen")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<LockOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("settings.change_password", "Passwort ändern")}
                    </ModernButton>
                  </Space>
                </ModernCard>

                {/* Settings Summary */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("settings.summary", "Übersicht")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "12px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "8px",
                      }}
                    >
                      <Text>
                        {t(
                          "settings.active_notifications",
                          "Aktive Benachrichtigungen",
                        )}
                      </Text>
                      <Text strong style={{ color: colors.colorPrimary }}>
                        {settings.notifications ? "2" : "0"}
                      </Text>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "12px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "8px",
                      }}
                    >
                      <Text>
                        {t("settings.current_theme", "Aktuelles Design")}
                      </Text>
                      <Text strong style={{ color: colors.colorSecondary }}>
                        {getThemeIcon(settings.theme)}{" "}
                        {t(`settings.theme_${settings.theme}`, settings.theme)}
                      </Text>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "12px",
                        backgroundColor: colors.colorBgContainer,
                        borderRadius: "8px",
                      }}
                    >
                      <Text>{t("settings.language", "Sprache")}</Text>
                      <Text strong style={{ color: colors.colorAccent }}>
                        {settings.language === "de" ? "🇩🇪" : "🇺🇸"}{" "}
                        {settings.language.toUpperCase()}
                      </Text>
                    </div>
                  </Space>
                </ModernCard>

                {/* Help & Support */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("settings.help_support", "Hilfe & Support")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<UserOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("settings.contact_support", "Support kontaktieren")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<MonitorOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("settings.system_status", "Systemstatus")}
                    </ModernButton>
                  </Space>
                </ModernCard>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

export default Settings;
