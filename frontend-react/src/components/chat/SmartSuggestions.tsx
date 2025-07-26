import React from "react";
import { Card, List, Typography } from "antd";
import { BookOutlined, LinkOutlined, BulbOutlined } from "@ant-design/icons";
const { Text } = Typography;

const suggestions = [
  {
    title: "Summarize selected documents",
    description: "Get a concise summary of all selected documents",
    icon: <BookOutlined />,
    action: () => window.alert("Summarize feature coming soon"),
  },
  {
    title: "Find related documents",
    description: "Discover documents similar to your selection",
    icon: <LinkOutlined />,
    action: () => window.alert("Related documents feature coming soon"),
  },
  {
    title: "Generate questions",
    description: "Create questions based on document content",
    icon: <BulbOutlined />,
    action: () => window.alert("Question generation feature coming soon"),
  },
];

const SmartSuggestions: React.FC = () => (
  <Card size="small" title="Smart Suggestions" style={{ marginBottom: "16px" }}>
    <List
      size="small"
      dataSource={suggestions}
      renderItem={(suggestion) => (
        <List.Item
          style={{ padding: "8px 0", cursor: "pointer" }}
          onClick={suggestion.action}
        >
          <List.Item.Meta
            avatar={suggestion.icon}
            title={
              <Text style={{ fontSize: "13px", cursor: "pointer" }}>
                {suggestion.title}
              </Text>
            }
            description={
              <Text type="secondary" style={{ fontSize: "11px" }}>
                {suggestion.description}
              </Text>
            }
          />
        </List.Item>
      )}
    />
  </Card>
);

export default SmartSuggestions;
