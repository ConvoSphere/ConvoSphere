import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Form,
  message,
  Typography,
  Space,
  Alert,
  Spin,
} from "antd";
import { LockOutlined, CheckCircleOutlined } from "@ant-design/icons";

import { resetPassword, validateResetToken } from "../services/auth";
import ModernCard from "../components/ModernCard";
import { ModernFormItem } from "../components/ModernForm";
import ModernInput from "../components/ModernInput";
import ModernButton from "../components/ModernButton";

const { Title, Text } = Typography;

const ResetPassword: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [passwordReset, setPasswordReset] = useState(false);

  const token = searchParams.get("token");

  useEffect(() => {
    validateToken();
  }, [token]);

  const validateToken = async () => {
    if (!token) {
      setTokenValid(false);
      setValidating(false);
      return;
    }

    try {
      const result = await validateResetToken(token);
      setTokenValid(result.valid);
    } catch (error) {
      console.error("Token validation error:", error);
      setTokenValid(false);
    } finally {
      setValidating(false);
    }
  };

  const onFinish = async (values: { password: string; confirmPassword: string }) => {
    if (values.password !== values.confirmPassword) {
      message.error(t("auth.passwordMismatch"));
      return;
    }

    if (!token) {
      message.error(t("auth.invalidToken"));
      return;
    }

    setLoading(true);
    
    try {
      const result = await resetPassword(token, values.password);
      
      if (result.success) {
        setPasswordReset(true);
        message.success(t("auth.passwordResetSuccess"));
      } else {
        message.error(result.message);
      }
    } catch (error) {
      console.error("Reset password error:", error);
      message.error(t("auth.passwordResetError"));
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate("/login");
  };

  const handleRequestNewToken = () => {
    navigate("/forgot-password");
  };

  if (validating) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          padding: "20px",
        }}
      >
        <ModernCard
          style={{
            width: "100%",
            maxWidth: "500px",
            textAlign: "center",
            borderRadius: "16px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
          }}
        >
          <Space direction="vertical" size="large">
            <Spin size="large" />
            <Text style={{ fontSize: "16px", color: "#7A869A" }}>
              {t("auth.validatingToken")}
            </Text>
          </Space>
        </ModernCard>
      </div>
    );
  }

  if (passwordReset) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          padding: "20px",
        }}
      >
        <ModernCard
          style={{
            width: "100%",
            maxWidth: "500px",
            textAlign: "center",
            borderRadius: "16px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
          }}
        >
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <div style={{ fontSize: "64px", color: "#52c41a" }}>
              <CheckCircleOutlined />
            </div>
            
            <Title level={2} style={{ margin: 0, color: "#23224A" }}>
              {t("auth.passwordResetSuccess")}
            </Title>
            
            <Text style={{ fontSize: "16px", color: "#7A869A" }}>
              {t("auth.passwordResetSuccessDescription")}
            </Text>
            
            <ModernButton
              type="primary"
              size="large"
              onClick={handleBackToLogin}
              style={{ width: "100%" }}
            >
              {t("auth.backToLogin")}
            </ModernButton>
          </Space>
        </ModernCard>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          padding: "20px",
        }}
      >
        <ModernCard
          style={{
            width: "100%",
            maxWidth: "500px",
            textAlign: "center",
            borderRadius: "16px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
          }}
        >
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <Title level={2} style={{ margin: 0, color: "#23224A" }}>
              {t("auth.invalidToken")}
            </Title>
            
            <Alert
              message={t("auth.tokenExpiredOrInvalid")}
              description={t("auth.tokenExpiredOrInvalidDescription")}
              type="error"
              showIcon
              style={{ textAlign: "left" }}
            />
            
            <Space direction="vertical" style={{ width: "100%" }}>
              <ModernButton
                type="primary"
                size="large"
                onClick={handleRequestNewToken}
                style={{ width: "100%" }}
              >
                {t("auth.requestNewToken")}
              </ModernButton>
              
              <ModernButton
                type="link"
                onClick={handleBackToLogin}
                style={{ width: "100%" }}
              >
                {t("auth.backToLogin")}
              </ModernButton>
            </Space>
          </Space>
        </ModernCard>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        padding: "20px",
      }}
    >
      <ModernCard
        style={{
          width: "100%",
          maxWidth: "500px",
          borderRadius: "16px",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
        }}
      >
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div style={{ textAlign: "center" }}>
            <Title level={2} style={{ margin: 0, color: "#23224A" }}>
              {t("auth.resetPassword")}
            </Title>
            <Text style={{ fontSize: "16px", color: "#7A869A" }}>
              {t("auth.resetPasswordDescription")}
            </Text>
          </div>

          <Form
            name="resetPassword"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <ModernFormItem
              label={t("auth.newPassword")}
              name="password"
              rules={[
                { required: true, message: t("auth.passwordRequired") },
                { min: 8, message: t("auth.passwordMinLength") },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
                  message: t("auth.passwordRequirements"),
                },
              ]}
            >
              <ModernInput.Password
                prefix={<LockOutlined style={{ color: "#7A869A" }} />}
                placeholder={t("auth.newPasswordPlaceholder")}
                variant="filled"
                size="lg"
                autoFocus
              />
            </ModernFormItem>

            <ModernFormItem
              label={t("auth.confirmPassword")}
              name="confirmPassword"
              rules={[
                { required: true, message: t("auth.confirmPasswordRequired") },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("password") === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error(t("auth.passwordMismatch")));
                  },
                }),
              ]}
            >
              <ModernInput.Password
                prefix={<LockOutlined style={{ color: "#7A869A" }} />}
                placeholder={t("auth.confirmPasswordPlaceholder")}
                variant="filled"
                size="lg"
              />
            </ModernFormItem>

            <ModernFormItem>
              <ModernButton
                type="primary"
                htmlType="submit"
                loading={loading}
                style={{
                  width: "100%",
                  height: "56px",
                  fontSize: "18px",
                  fontWeight: 600,
                }}
              >
                {t("auth.resetPassword")}
              </ModernButton>
            </ModernFormItem>
          </Form>

          <div style={{ textAlign: "center" }}>
            <ModernButton
              type="link"
              onClick={handleBackToLogin}
              style={{ fontSize: "16px" }}
            >
              {t("auth.backToLogin")}
            </ModernButton>
          </div>
        </Space>
      </ModernCard>
    </div>
  );
};

export default ResetPassword;