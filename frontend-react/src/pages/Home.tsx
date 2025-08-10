import React from "react";
import {
  Typography,
  Space,
  Row,
  Col,
} from "antd";
import {
  MessageOutlined,
  RobotOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ChatInitializer from "../components/chat/ChatInitializer";
import { config } from "../config";
import { useQuery } from "@tanstack/react-query";

const { Title, Text } = Typography;

interface Assistant {
  id: string;
  name: string;
  description: string;
  personality: string;
  isActive: boolean;
}

const fetchAssistants = async (token: string) => {
  const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error("Failed to load assistants");
  }
  const data = await response.json();
  return (data as Assistant[]).filter((assistant) => assistant.isActive);
};

const Home: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const { data: assistants = [], isLoading } = useQuery({
    queryKey: ["assistants", { userId: user?.id }],
    queryFn: () => fetchAssistants(token!),
    enabled: Boolean(token),
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div style={{ padding: "24px 0", maxWidth: "800px", margin: "0 auto" }}>
      {/* Welcome Section */}
      <ModernCard variant="gradient" size="lg" className="stagger-children">
        <div style={{ textAlign: "center", padding: "32px 0" }}>
          <Title
            level={1}
            style={{ color: "#FFFFFF", marginBottom: 16, fontSize: "2.5rem" }}
          >
            {t("home.welcome", {
              username: user?.username || t("common.user"),
            })}
          </Title>
          <Text style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}>
            {t("home.subtitle")}
          </Text>
        </div>
      </ModernCard>

      {/* Chat Initialization Form */}
      <ChatInitializer variant="card" />

      {/* Quick Start Options */}
      {!isLoading && assistants.length > 1 && (
        <ModernCard
          variant="outlined"
          size="lg"
          header={
            <Title level={4} style={{ margin: 0 }}>
              {t("home.quick_start")}
            </Title>
          }
        >
          <Row gutter={[16, 16]}>
            {assistants.slice(0, 4).map((assistant) => (
              <Col xs={24} sm={12} key={assistant.id}>
                <ModernButton
                  variant="secondary"
                  size="md"
                  icon={<RobotOutlined />}
                  onClick={() => navigate(`/chat?assistant=${assistant.id}`)}
                  style={{ width: "100%", height: "60px" }}
                >
                  <div style={{ textAlign: "left" }}>
                    <div style={{ fontWeight: 500 }}>{assistant.name}</div>
                    <div style={{ fontSize: "12px", opacity: 0.7 }}>
                      {assistant.description.substring(0, 40)}...
                    </div>
                  </div>
                </ModernButton>
              </Col>
            ))}
          </Row>
        </ModernCard>
      )}

      {/* Recent Conversations Link */}
      <ModernCard
        variant="interactive"
        size="md"
        onClick={() => navigate("/conversations")}
        style={{ cursor: "pointer" }}
      >
        <div style={{ textAlign: "center" }}>
          <Text style={{ fontSize: "16px" }}>
            <MessageOutlined style={{ marginRight: 8 }} />
            {t("home.view_recent_conversations")}
          </Text>
        </div>
      </ModernCard>
    </div>
  );
};

export default Home;