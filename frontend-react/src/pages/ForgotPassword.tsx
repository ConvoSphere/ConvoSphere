import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Typography,
  Space,
  Alert,
} from "antd";
import { ArrowLeftOutlined, MailOutlined } from "@ant-design/icons";

import { forgotPassword } from "../services/auth";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import { ModernFormItem } from "../components/ModernForm";
import ModernInput from "../components/ModernInput";
import ModernButton from "../components/ModernButton";

const { Title, Text } = Typography;

const ForgotPassword: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const onFinish = async (values: { email: string }) => {
    setLoading(true);
    
    try {
      const result = await forgotPassword(values.email);
      
      if (result.success) {
        setEmailSent(true);
        message.success(t("auth.passwordResetSent"));
      } else {
        message.error(result.message);
      }
    } catch (error) {
      console.error("Forgot password error:", error);
      message.error(t("auth.passwordResetError"));
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate("/login");
  };

  if (emailSent) {
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
              <MailOutlined />
            </div>
            
            <Title level={2} style={{ margin: 0, color: colors.colorTextBase }}>
              {t("auth.checkYourEmail")}
            </Title>
            
            <Text style={{ fontSize: "16px", color: colors.colorTextSecondary }}>
              {t("auth.passwordResetEmailSent")}
            </Text>
            
            <Alert
              message={t("auth.emailInstructions")}
              description={t("auth.emailInstructionsDetail")}
              type="info"
              showIcon
              style={{ textAlign: "left" }}
            />
            
            <Space direction="vertical" style={{ width: "100%" }}>
              <ModernButton
                type="primary"
                size="large"
                onClick={handleBackToLogin}
                style={{ width: "100%" }}
              >
                {t("auth.backToLogin")}
              </ModernButton>
              
              <ModernButton
                type="link"
                onClick={() => setEmailSent(false)}
                style={{ width: "100%" }}
              >
                {t("auth.tryDifferentEmail")}
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
            <Title level={2} style={{ margin: 0, color: colors.colorTextBase }}>
              {t("auth.forgotPassword")}
            </Title>
            <Text style={{ fontSize: "16px", color: colors.colorTextSecondary }}>
              {t("auth.forgotPasswordDescription")}
            </Text>
          </div>

          <Form
            name="forgotPassword"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <ModernFormItem
              label={t("auth.email")}
              name="email"
              rules={[
                { required: true, message: t("auth.emailRequired") },
                { type: "email", message: t("auth.emailInvalid") },
              ]}
            >
              <ModernInput
                prefix={<MailOutlined style={{ color: colors.colorTextSecondary }} />}
                placeholder={t("auth.emailPlaceholder")}
                variant="filled"
                size="lg"
                autoFocus
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
                {t("auth.sendResetEmail")}
              </ModernButton>
            </ModernFormItem>
          </Form>

          <div style={{ textAlign: "center" }}>
            <ModernButton
              type="link"
              icon={<ArrowLeftOutlined />}
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

export default ForgotPassword;