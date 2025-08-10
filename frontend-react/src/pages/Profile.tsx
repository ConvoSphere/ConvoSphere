import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import {
  Avatar,
  Typography,
  Space,
  Divider,
  Alert,
  Spin,
  Row,
  Col,
  Statistic,
} from "antd";
import {
  UserOutlined,
  MailOutlined,
  CalendarOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  CrownOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernForm, { ModernFormItem } from "../components/ModernForm";
import { Form } from "antd";
import { useQuery } from "@tanstack/react-query";
import { getProfile } from "../services/user";

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const fetchProfileStore = useAuthStore((s) => s.fetchProfile);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const { data: profile, isLoading: isProfileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => getProfile(token || undefined),
    enabled: Boolean(token),
    staleTime: 5 * 60 * 1000,
    initialData: user || undefined,
    onSuccess: (data) => {
      if (!user) fetchProfileStore();
    },
  });

  if (!profile || isProfileLoading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: colors.colorGradientPrimary,
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  const onFinish = async (values: { username: string; email: string }) => {
    setLoading(true);
    setError(null);
    try {
      await updateProfile(values);
      setEditing(false);
    } catch {
      setError(t("profile.update_failed", "Update failed."));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditing(false);
    setError(null);
    form.resetFields();
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "super_admin":
        return <CrownOutlined style={{ color: "#FFD700" }} />;
      case "admin":
        return <CrownOutlined style={{ color: "#FF6B6B" }} />;
      case "moderator":
        return <TeamOutlined style={{ color: "#4ECDC4" }} />;
      default:
        return <UserOutlined style={{ color: colors.colorPrimary }} />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "super_admin":
        return "#FFD700";
      case "admin":
        return "#FF6B6B";
      case "moderator":
        return "#4ECDC4";
      default:
        return colors.colorPrimary;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("de-DE", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
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
            <Avatar
              size={120}
              icon={<UserOutlined />}
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                border: "4px solid rgba(255, 255, 255, 0.3)",
                marginBottom: 24,
              }}
            />
            <Title
              level={1}
              style={{ color: "#FFFFFF", marginBottom: 8, fontSize: "2.5rem" }}
            >
              {t("profile.title", "Profil")}
            </Title>
            <Text
              style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}
            >
              {t(
                "profile.subtitle",
                "Verwalten Sie Ihre persönlichen Informationen",
              )}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Row gutter={[24, 24]}>
            {/* Profile Information */}
            <Col xs={24} lg={16}>
              <ModernCard
                variant="elevated"
                size="lg"
                header={
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <Title level={3} style={{ margin: 0 }}>
                      {t("profile.personal_info", "Persönliche Informationen")}
                    </Title>
                    {!editing && (
                      <ModernButton
                        variant="primary"
                        icon={<EditOutlined />}
                        onClick={() => setEditing(true)}
                      >
                        {t("common.edit", "Bearbeiten")}
                      </ModernButton>
                    )}
                  </div>
                }
              >
                {error && (
                  <Alert
                    type="error"
                    message={error}
                    showIcon
                    style={{
                      marginBottom: 24,
                      borderRadius: "12px",
                      border: "none",
                    }}
                  />
                )}

                {!editing ? (
                  <div className="stagger-children">
                    <Row gutter={[24, 24]}>
                      <Col xs={24} md={12}>
                        <div
                          style={{
                            padding: "20px",
                            backgroundColor: colors.colorBgContainer,
                            borderRadius: "12px",
                            border: `1px solid ${colors.colorBorder}`,
                          }}
                        >
                          <Space
                            direction="vertical"
                            size="small"
                            style={{ width: "100%" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                              }}
                            >
                              <UserOutlined
                                style={{
                                  color: colors.colorPrimary,
                                  fontSize: "18px",
                                }}
                              />
                              <Text strong style={{ fontSize: "16px" }}>
                                {t("profile.username", "Benutzername")}
                              </Text>
                            </div>
                            <Text
                              style={{
                                fontSize: "18px",
                                color: colors.colorTextBase,
                              }}
                            >
                              {profile.username}
                            </Text>
                          </Space>
                        </div>
                      </Col>

                      <Col xs={24} md={12}>
                        <div
                          style={{
                            padding: "20px",
                            backgroundColor: colors.colorBgContainer,
                            borderRadius: "12px",
                            border: `1px solid ${colors.colorBorder}`,
                          }}
                        >
                          <Space
                            direction="vertical"
                            size="small"
                            style={{ width: "100%" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                              }}
                            >
                              <MailOutlined
                                style={{
                                  color: colors.colorSecondary,
                                  fontSize: "18px",
                                }}
                              />
                              <Text strong style={{ fontSize: "16px" }}>
                                {t("profile.email", "E-Mail")}
                              </Text>
                            </div>
                            <Text
                              style={{
                                fontSize: "18px",
                                color: colors.colorTextBase,
                              }}
                            >
                              {profile.email}
                            </Text>
                          </Space>
                        </div>
                      </Col>
                    </Row>

                    <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
                      <Col xs={24} md={12}>
                        <div
                          style={{
                            padding: "20px",
                            backgroundColor: colors.colorBgContainer,
                            borderRadius: "12px",
                            border: `1px solid ${colors.colorBorder}`,
                          }}
                        >
                          <Space
                            direction="vertical"
                            size="small"
                            style={{ width: "100%" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                              }}
                            >
                              {getRoleIcon(profile.role)}
                              <Text strong style={{ fontSize: "16px" }}>
                                {t("profile.role", "Rolle")}
                              </Text>
                            </div>
                            <Text
                              style={{
                                fontSize: "18px",
                                color: getRoleColor(profile.role),
                                fontWeight: 600,
                              }}
                            >
                              {t(`profile.roles.${profile.role}`, profile.role)}
                            </Text>
                          </Space>
                        </div>
                      </Col>

                      <Col xs={24} md={12}>
                        <div
                          style={{
                            padding: "20px",
                            backgroundColor: colors.colorBgContainer,
                            borderRadius: "12px",
                            border: `1px solid ${colors.colorBorder}`,
                          }}
                        >
                          <Space
                            direction="vertical"
                            size="small"
                            style={{ width: "100%" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                              }}
                            >
                              <CalendarOutlined
                                style={{
                                  color: colors.colorAccent,
                                  fontSize: "18px",
                                }}
                              />
                              <Text strong style={{ fontSize: "16px" }}>
                                {t("profile.member_since", "Mitglied seit")}
                              </Text>
                            </div>
                            <Text
                              style={{
                                fontSize: "18px",
                                color: colors.colorTextBase,
                              }}
                            >
                              {profile.createdAt
                                ? formatDate(profile.createdAt)
                                : t("profile.unknown", "Unbekannt")}
                            </Text>
                          </Space>
                        </div>
                      </Col>
                    </Row>
                  </div>
                ) : (
                  <ModernForm
                    form={form}
                    onFinish={onFinish}
                    initialValues={{
                      username: profile.username,
                      email: profile.email,
                    }}
                    layout="vertical"
                  >
                    <Row gutter={[24, 24]}>
                      <Col xs={24} md={12}>
                        <ModernFormItem
                          name="username"
                          label={t("profile.username", "Benutzername")}
                          rules={[
                            {
                              required: true,
                              message: t(
                                "profile.username_required",
                                "Benutzername ist erforderlich",
                              ),
                            },
                          ]}
                        >
                          <ModernInput
                            prefix={
                              <UserOutlined
                                style={{ color: colors.colorPrimary }}
                              />
                            }
                            placeholder={t(
                              "profile.username_placeholder",
                              "Ihr Benutzername",
                            )}
                          />
                        </ModernFormItem>
                      </Col>

                      <Col xs={24} md={12}>
                        <ModernFormItem
                          name="email"
                          label={t("profile.email", "E-Mail")}
                          rules={[
                            {
                              required: true,
                              message: t(
                                "profile.email_required",
                                "E-Mail ist erforderlich",
                              ),
                            },
                            {
                              type: "email",
                              message: t(
                                "profile.email_invalid",
                                "Ungültige E-Mail-Adresse",
                              ),
                            },
                          ]}
                        >
                          <ModernInput
                            prefix={
                              <MailOutlined
                                style={{ color: colors.colorSecondary }}
                              />
                            }
                            placeholder={t(
                              "profile.email_placeholder",
                              "ihre.email@beispiel.de",
                            )}
                          />
                        </ModernFormItem>
                      </Col>
                    </Row>

                    <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
                      <ModernButton
                        variant="primary"
                        size="lg"
                        icon={<SaveOutlined />}
                        htmlType="submit"
                        loading={loading}
                      >
                        {t("profile.save", "Speichern")}
                      </ModernButton>

                      <ModernButton
                        variant="outlined"
                        size="lg"
                        icon={<CloseOutlined />}
                        onClick={handleCancel}
                        disabled={loading}
                      >
                        {t("profile.cancel", "Abbrechen")}
                      </ModernButton>
                    </div>
                  </ModernForm>
                )}
              </ModernCard>
            </Col>

            {/* Statistics Sidebar */}
            <Col xs={24} lg={8}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* User Stats */}
                <ModernCard variant="interactive" size="md">
                  <Title level={4} style={{ marginBottom: 24 }}>
                    {t("profile.statistics", "Statistiken")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <Statistic
                      title={t("profile.total_conversations", "Gespräche")}
                      value={profile.totalConversations || 0}
                      prefix={
                        <UserOutlined style={{ color: colors.colorPrimary }} />
                      }
                      valueStyle={{
                        color: colors.colorPrimary,
                        fontSize: "1.5rem",
                      }}
                    />

                    <Divider style={{ margin: "16px 0" }} />

                    <Statistic
                      title={t("profile.last_login", "Letzter Login")}
                      value={
                        profile.lastLogin
                          ? formatDate(profile.lastLogin)
                          : t("profile.never", "Nie")
                      }
                      prefix={
                        <ClockCircleOutlined
                          style={{ color: colors.colorSecondary }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorSecondary,
                        fontSize: "1rem",
                      }}
                    />
                  </Space>
                </ModernCard>

                {/* Quick Actions */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("profile.quick_actions", "Schnellaktionen")}
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
                      {t("profile.view_activity", "Aktivität anzeigen")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<MailOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("profile.change_password", "Passwort ändern")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<SettingOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("profile.preferences", "Einstellungen")}
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

export default Profile;
