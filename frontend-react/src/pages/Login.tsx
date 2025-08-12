import React, { useState, useEffect } from "react";
import { Alert, Modal, message, Divider, Typography } from "antd";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useNavigate } from "react-router-dom";
import { getSSOProviders, ssoLogin } from "../services/auth";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernForm, { ModernFormItem } from "../components/ModernForm";

const { Title, Text } = Typography;

interface SSOProvider {
  id: string;
  name: string;
  type: string;
  icon: string;
  login_url: string;
}

const Login: React.FC = () => {
  const { t } = useTranslation();
  const login = useAuthStore((s) => s.login);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [ssoProviders, setSsoProviders] = useState<SSOProvider[]>([]);
  const [ssoLoading, setSsoLoading] = useState(false);

  useEffect(() => {
    // Load SSO providers on component mount only once with caching
    const loadSSOProviders = async () => {
      // Check if we already have providers cached
      const cachedProviders = sessionStorage.getItem("sso_providers");
      if (cachedProviders) {
        try {
          const providers = JSON.parse(cachedProviders);
          setSsoProviders(providers);
          return;
        } catch {
          // Invalid cache, remove it
          sessionStorage.removeItem("sso_providers");
        }
      }

      if (ssoLoading) return; // Prevent multiple simultaneous requests

      setSsoLoading(true);
      try {
        const providers = await getSSOProviders();
        // Only set providers if there are actually configured ones
        if (providers && providers.length > 0) {
          setSsoProviders(providers);
          // Cache the providers for this session
          sessionStorage.setItem("sso_providers", JSON.stringify(providers));
        } else {
          setSsoProviders([]);
          // Cache empty array to prevent future requests
          sessionStorage.setItem("sso_providers", JSON.stringify([]));
          console.log("No SSO providers configured");
        }
      } catch {
        setSsoProviders([]); // auch im Fehlerfall ein Array
        // Cache empty array on error to prevent repeated failed requests
        sessionStorage.setItem("sso_providers", JSON.stringify([]));
        console.log("No SSO providers configured or error loading providers");
      } finally {
        setSsoLoading(false);
      }
    };

    // Only load if not already loaded and not currently loading
    if (ssoProviders.length === 0 && !ssoLoading) {
      loadSSOProviders();
    }
  }, [ssoProviders.length, ssoLoading]);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      await login(values.username, values.password);
      message.success(t("auth.login.success"));
      navigate("/");
    } catch {
      setError(t("auth.login.failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = async (provider: string) => {
    try {
      await ssoLogin(provider);
    } catch {
      setError(t("auth.login.failed"));
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case "google":
        return "🔍"; // Google icon
      case "microsoft":
        return "🪟"; // Microsoft icon
      case "github":
        return "🐙"; // GitHub icon
      case "saml":
        return "🔐"; // SAML icon
      case "oidc":
        return "🔑"; // OIDC icon
      default:
        return "🔗"; // Default SSO icon
    }
  };

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  // Early return if already authenticated to prevent unnecessary rendering
  if (isAuthenticated) {
    return null;
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <ModernCard
        variant="elevated"
        size="xl"
        style={{
          maxWidth: 480,
          width: "100%",
          backdropFilter: "blur(10px)",
          backgroundColor: "rgba(255, 255, 255, 0.95)",
        }}
        className="stagger-children"
      >
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <Title
            level={2}
            style={{
              color: colors.colorTextBase,
              marginBottom: 8,
              fontSize: "2.5rem",
              fontWeight: 700,
            }}
          >
            {t("auth.login.title")}
          </Title>
          <Text type="secondary" style={{ fontSize: "16px" }}>
            {t("auth.login.subtitle2")}
          </Text>
        </div>

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

        {/* SSO Login Buttons */}
        {ssoProviders.length > 0 && (
          <>
            <div style={{ marginBottom: 24 }}>
              {ssoProviders.map((provider, index) => (
                <ModernButton
                  key={provider.id}
                  variant="outlined"
                  size="lg"
                  icon={
                    <span style={{ fontSize: "18px" }}>
                      {getProviderIcon(provider.id)}
                    </span>
                  }
                  onClick={() => handleSSOLogin(provider.id)}
                  style={{
                    width: "100%",
                    marginBottom: 12,
                    justifyContent: "flex-start",
                    padding: "16px 20px",
                    fontSize: "16px",
                  }}
                >
                  {t("auth.login.button")} {provider.name}
                </ModernButton>
              ))}
            </div>
            <Divider style={{ margin: "24px 0" }}>
              <Text type="secondary" style={{ fontSize: "14px" }}>
                {t("common.or")}
              </Text>
            </Divider>
          </>
        )}

        {/* Local Login Form */}
        <ModernForm
          variant="minimal"
          size="lg"
          onFinish={onFinish}
          aria-label={t("auth.login.title")}
          name="login-form"
        >
          <ModernFormItem
            label={t("auth.login.username")}
            required
            name="username"
            rules={[
              { required: true, message: t("auth.login.username_required") },
              { min: 3, message: t("auth.login.username_min_length") },
            ]}
          >
            <ModernInput
              variant="filled"
              size="lg"
              autoFocus
              aria-label={t("auth.login.username")}
              placeholder={t("auth.login.username_placeholder")}
            />
          </ModernFormItem>

          <ModernFormItem
            label={t("auth.login.password")}
            required
            name="password"
            rules={[
              { required: true, message: t("auth.login.password_required") },
              { min: 6, message: t("auth.login.password_min_length") },
            ]}
          >
            <ModernInput
              type="password"
              variant="filled"
              size="lg"
              showPasswordToggle
              aria-label={t("auth.login.password")}
              placeholder={t("auth.login.password_placeholder")}
            />
          </ModernFormItem>

          <ModernFormItem>
            <ModernButton
              variant="gradient"
              size="lg"
              htmlType="submit"
              loading={loading}
              style={{
                width: "100%",
                height: "56px",
                fontSize: "18px",
                fontWeight: 600,
              }}
              aria-label={t("auth.login.button")}
            >
              {t("auth.login.button")}
            </ModernButton>
          </ModernFormItem>
        </ModernForm>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: 24,
            paddingTop: 24,
            borderTop: "1px solid var(--colorBorder)",
          }}
        >
          <ModernButton
            variant="ghost"
            size="sm"
            onClick={() => navigate("/register")}
            aria-label={t("auth.register.title")}
          >
            {t("auth.register.link")}
          </ModernButton>
          <ModernButton
            variant="ghost"
            size="sm"
            onClick={() => navigate("/forgot-password")}
            aria-label={t("auth.forgot_password")}
          >
            {t("auth.forgot_password")}
          </ModernButton>
        </div>
      </ModernCard>
    </div>
  );
};

export default Login;
