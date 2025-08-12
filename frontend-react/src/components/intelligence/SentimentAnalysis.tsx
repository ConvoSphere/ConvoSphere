import React from "react";
import {
  Row,
  Col,
  Card,
  Progress,
  Typography,
  Space,
  Tag,
  List,
  Avatar,
} from "antd";
import {
  SmileOutlined,
  MehOutlined,
  FrownOutlined,
  MessageOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { Pie, Column } from "@ant-design/plots";
import { useTranslation } from "react-i18next";
import type { SentimentAnalysis as SentimentAnalysisType } from "../../services/conversationIntelligence";
import ModernCard from "../ModernCard";

const { Title, Text } = Typography;

interface SentimentAnalysisProps {
  data: SentimentAnalysisType | null;
  loading?: boolean;
}

const SentimentAnalysis: React.FC<SentimentAnalysisProps> = ({
  data,
  loading = false,
}) => {
  const { t } = useTranslation();

  if (!data) {
    return (
      <ModernCard>
        <div style={{ textAlign: "center", padding: "40px" }}>
          <Text type="secondary">{t("intelligence.no_sentiment_data")}</Text>
        </div>
      </ModernCard>
    );
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return <SmileOutlined style={{ color: "#52c41a" }} />;
      case "neutral":
        return <MehOutlined style={{ color: "#faad14" }} />;
      case "negative":
        return <FrownOutlined style={{ color: "#ff4d4f" }} />;
      default:
        return <MehOutlined />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "#52c41a";
      case "neutral":
        return "#faad14";
      case "negative":
        return "#ff4d4f";
      default:
        return "#d9d9d9";
    }
  };

  const getSentimentTag = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return <Tag color="success">{t("intelligence.positive")}</Tag>;
      case "neutral":
        return <Tag color="warning">{t("intelligence.neutral")}</Tag>;
      case "negative":
        return <Tag color="error">{t("intelligence.negative")}</Tag>;
      default:
        return <Tag>{t("intelligence.unknown")}</Tag>;
    }
  };

  // Prepare data for pie chart
  const sentimentDistribution = [
    {
      type: t("intelligence.positive"),
      value: data.messageSentiments.filter((m) => m.sentiment === "positive")
        .length,
    },
    {
      type: t("intelligence.neutral"),
      value: data.messageSentiments.filter((m) => m.sentiment === "neutral")
        .length,
    },
    {
      type: t("intelligence.negative"),
      value: data.messageSentiments.filter((m) => m.sentiment === "negative")
        .length,
    },
  ];

  // Prepare data for column chart
  const sentimentTimeline = data.messageSentiments.map((message, index) => ({
    message: `Message ${index + 1}`,
    score: message.score,
    sentiment: message.sentiment,
  }));

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      {/* Overall Sentiment Summary */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: "center" }}>
              {getSentimentIcon(data.overallSentiment)}
              <Title level={4} style={{ marginTop: 8 }}>
                {t("intelligence.overall_sentiment")}
              </Title>
              <Text strong style={{ fontSize: "18px" }}>
                {t(`intelligence.${data.overallSentiment}`)}
              </Text>
              <Progress
                percent={Math.abs(data.sentimentScore) * 20}
                status={
                  data.sentimentScore > 0
                    ? "success"
                    : data.sentimentScore < 0
                      ? "exception"
                      : "normal"
                }
                style={{ marginTop: 16 }}
              />
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: "center" }}>
              <Title level={4}>{t("intelligence.sentiment_score")}</Title>
              <Text
                strong
                style={{
                  fontSize: "24px",
                  color: getSentimentColor(data.overallSentiment),
                }}
              >
                {data.sentimentScore.toFixed(2)}
              </Text>
              <div style={{ marginTop: 8 }}>
                {getSentimentTag(data.overallSentiment)}
              </div>
            </div>
          </ModernCard>
        </Col>
        <Col xs={24} md={8}>
          <ModernCard>
            <div style={{ textAlign: "center" }}>
              <Title level={4}>{t("intelligence.total_messages")}</Title>
              <Text strong style={{ fontSize: "24px" }}>
                {data.messageSentiments.length}
              </Text>
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">
                  {t("intelligence.analyzed_messages")}
                </Text>
              </div>
            </div>
          </ModernCard>
        </Col>
      </Row>

      {/* Sentiment Distribution Chart */}
      <ModernCard title={t("intelligence.sentiment_distribution")}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Pie
              data={sentimentDistribution}
              angleField="value"
              colorField="type"
              radius={0.8}
              color={["#52c41a", "#faad14", "#ff4d4f"]}
              label={{
                type: "outer",
                content: "{name}: {percentage}",
              }}
              tooltip={{
                formatter: (datum) => {
                  return {
                    name: datum.type,
                    value: `${datum.value} (${((datum.value / data.messageSentiments.length) * 100).toFixed(1)}%)`,
                  };
                },
              }}
            />
          </Col>
          <Col xs={24} md={12}>
            <Column
              data={sentimentTimeline}
              xField="message"
              yField="score"
              seriesField="sentiment"
              isGroup={true}
              columnStyle={{
                radius: [4, 4, 0, 0],
              }}
              color={["#52c41a", "#faad14", "#ff4d4f"]}
              legend={{
                position: "top",
              }}
              xAxis={{
                title: {
                  text: t("intelligence.message_sequence"),
                },
              }}
              yAxis={{
                title: {
                  text: t("intelligence.sentiment_score"),
                },
                min: -1,
                max: 1,
              }}
            />
          </Col>
        </Row>
      </ModernCard>

      {/* Detailed Message Sentiments */}
      <ModernCard title={t("intelligence.detailed_message_sentiments")}>
        <List
          dataSource={data.messageSentiments}
          renderItem={(message, index) => (
            <List.Item>
              <List.Item.Meta
                avatar={<Avatar icon={getSentimentIcon(message.sentiment)} />}
                title={
                  <Space>
                    <Text strong>
                      {t("intelligence.message")} {index + 1}
                    </Text>
                    {getSentimentTag(message.sentiment)}
                    <Text type="secondary">
                      {new Date(message.timestamp).toLocaleString()}
                    </Text>
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    <Text>
                      {t("intelligence.sentiment_score")}:{" "}
                      {message.score.toFixed(3)}
                    </Text>
                    <Progress
                      percent={Math.abs(message.score) * 100}
                      size="small"
                      status={
                        message.score > 0
                          ? "success"
                          : message.score < 0
                            ? "exception"
                            : "normal"
                      }
                      showInfo={false}
                    />
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </ModernCard>
    </Space>
  );
};

export default SentimentAnalysis;
