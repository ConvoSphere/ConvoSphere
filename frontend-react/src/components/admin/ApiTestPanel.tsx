import React, { useState } from "react";
import {
  Card,
  Button,
  Space,
  Typography,
  Table,
  Tag,
  Progress,
  Alert,
  Collapse,
  Divider,
} from "antd";
import {
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  StopOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { apiTestService, showApiTestResults, type ApiTestResult, type ApiTestSummary } from "../../services/apiTest";
import { handleError } from "../../utils/errorHandler";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import { LoadingState } from "../LoadingStates";

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const ApiTestPanel: React.FC = () => {
  const { t } = useTranslation();
  const [testResults, setTestResults] = useState<ApiTestSummary | null>(null);
  const [running, setRunning] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const runAllTests = async () => {
    setRunning(true);
    try {
      const results = await apiTestService.runAllTests();
      setTestResults(results);
      showApiTestResults(results);
    } catch (error) {
      handleError(error, "api_test");
    } finally {
      setRunning(false);
    }
  };

  const runCategoryTests = async (category: string) => {
    setRunning(true);
    setSelectedCategory(category);
    try {
      let results: ApiTestResult[] = [];
      
      switch (category) {
        case "knowledge":
          results = await apiTestService.testKnowledgeEndpoints();
          break;
        case "tools":
          results = await apiTestService.testToolsEndpoints();
          break;
        case "mcp":
          results = await apiTestService.testMcpEndpoints();
          break;
        case "auth":
          results = await apiTestService.testAuthEndpoints();
          break;
        default:
          throw new Error(`Unknown category: ${category}`);
      }

      const summary: ApiTestSummary = {
        total: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        averageResponseTime: results.reduce((sum, r) => sum + r.responseTime, 0) / results.length,
        results,
      };

      setTestResults(summary);
      showApiTestResults(summary);
    } catch (error) {
      handleError(error, "api_test_category");
    } finally {
      setRunning(false);
    }
  };

  const getStatusColor = (success: boolean) => {
    return success ? "green" : "red";
  };

  const getStatusIcon = (success: boolean) => {
    return success ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />;
  };

  const getResponseTimeColor = (time: number) => {
    if (time < 500) return "green";
    if (time < 2000) return "orange";
    return "red";
  };

  const columns = [
    {
      title: t("api_test.endpoint", "Endpoint"),
      dataIndex: "endpoint",
      key: "endpoint",
      render: (endpoint: string) => (
        <Text code style={{ fontSize: "12px" }}>
          {endpoint}
        </Text>
      ),
    },
    {
      title: t("api_test.method", "Method"),
      dataIndex: "method",
      key: "method",
      render: (method: string) => (
        <Tag color="blue" size="small">
          {method}
        </Tag>
      ),
    },
    {
      title: t("api_test.status", "Status"),
      dataIndex: "success",
      key: "success",
      render: (success: boolean) => (
        <Tag color={getStatusColor(success)} icon={getStatusIcon(success)}>
          {success ? t("api_test.success", "Success") : t("api_test.failed", "Failed")}
        </Tag>
      ),
    },
    {
      title: t("api_test.response_time", "Response Time"),
      dataIndex: "responseTime",
      key: "responseTime",
      render: (time: number) => (
        <Text style={{ color: getResponseTimeColor(time) }}>
          {time}ms
        </Text>
      ),
    },
    {
      title: t("api_test.error", "Error"),
      dataIndex: "error",
      key: "error",
      render: (error: string) => (
        error ? (
          <Text type="danger" style={{ fontSize: "12px" }}>
            {error}
          </Text>
        ) : (
          <Text type="secondary">-</Text>
        )
      ),
    },
  ];

  const categories = [
    {
      key: "knowledge",
      label: t("api_test.categories.knowledge", "Knowledge Base"),
      description: t("api_test.categories.knowledge_desc", "Test document and search endpoints"),
      endpoints: ["/knowledge/documents", "/knowledge/tags", "/knowledge/stats", "/knowledge/search"],
    },
    {
      key: "tools",
      label: t("api_test.categories.tools", "Tools"),
      description: t("api_test.categories.tools_desc", "Test tool management endpoints"),
      endpoints: ["/tools", "/tools/categories/list"],
    },
    {
      key: "mcp",
      label: t("api_test.categories.mcp", "MCP Tools"),
      description: t("api_test.categories.mcp_desc", "Test MCP server and tool endpoints"),
      endpoints: ["/mcp/servers", "/mcp/tools"],
    },
    {
      key: "auth",
      label: t("api_test.categories.auth", "Authentication"),
      description: t("api_test.categories.auth_desc", "Test authentication endpoints"),
      endpoints: ["/auth/me", "/users/profile"],
    },
  ];

  const renderSummary = () => {
    if (!testResults) return null;

    const successRate = ((testResults.successful / testResults.total) * 100).toFixed(1);
    const isHealthy = testResults.failed === 0;

    return (
      <ModernCard variant="elevated" size="md" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
            <ApiOutlined style={{ marginRight: 8, color: isHealthy ? "#52c41a" : "#ff4d4f" }} />
            {t("api_test.summary", "API Test Summary")}
          </Title>
          <Tag color={isHealthy ? "green" : "red"} size="large">
            {isHealthy ? t("api_test.healthy", "Healthy") : t("api_test.unhealthy", "Unhealthy")}
          </Tag>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
          <div>
            <Text type="secondary">{t("api_test.total_endpoints", "Total Endpoints")}</Text>
            <div>
              <Text strong style={{ fontSize: "24px" }}>
                {testResults.total}
              </Text>
            </div>
          </div>
          
          <div>
            <Text type="secondary">{t("api_test.successful", "Successful")}</Text>
            <div>
              <Text strong style={{ fontSize: "24px", color: "#52c41a" }}>
                {testResults.successful}
              </Text>
            </div>
          </div>
          
          <div>
            <Text type="secondary">{t("api_test.failed", "Failed")}</Text>
            <div>
              <Text strong style={{ fontSize: "24px", color: "#ff4d4f" }}>
                {testResults.failed}
              </Text>
            </div>
          </div>
          
          <div>
            <Text type="secondary">{t("api_test.success_rate", "Success Rate")}</Text>
            <div>
              <Text strong style={{ fontSize: "24px" }}>
                {successRate}%
              </Text>
            </div>
          </div>
          
          <div>
            <Text type="secondary">{t("api_test.avg_response_time", "Avg Response Time")}</Text>
            <div>
              <Text strong style={{ fontSize: "24px" }}>
                {testResults.averageResponseTime.toFixed(0)}ms
              </Text>
            </div>
          </div>
        </div>

        <Divider />

        <div>
          <Text type="secondary">{t("api_test.overall_health", "Overall Health")}</Text>
          <Progress
            percent={parseFloat(successRate)}
            status={isHealthy ? "success" : "exception"}
            strokeColor={isHealthy ? "#52c41a" : "#ff4d4f"}
            style={{ marginTop: 8 }}
          />
        </div>
      </ModernCard>
    );
  };

  return (
    <div>
      <ModernCard
        variant="elevated"
        size="lg"
        header={
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Title level={3} style={{ margin: 0 }}>
              <ApiOutlined style={{ marginRight: 8, color: "#1890ff" }} />
              {t("api_test.title", "API Health Check")}
            </Title>
            <Space>
              <ModernButton
                variant="outlined"
                icon={<ReloadOutlined />}
                onClick={() => setTestResults(null)}
                disabled={running}
              >
                {t("api_test.clear", "Clear Results")}
              </ModernButton>
              <ModernButton
                variant="primary"
                icon={running ? <StopOutlined /> : <PlayCircleOutlined />}
                onClick={runAllTests}
                loading={running}
              >
                {running ? t("api_test.running", "Running...") : t("api_test.run_all", "Run All Tests")}
              </ModernButton>
            </Space>
          </div>
        }
      >
        <Paragraph type="secondary" style={{ marginBottom: 24 }}>
          {t("api_test.description", "Test the health and connectivity of all API endpoints to ensure the system is functioning correctly.")}
        </Paragraph>

        {renderSummary()}

        <Collapse defaultActiveKey={["categories"]} style={{ marginBottom: 24 }}>
          <Panel
            header={
              <Space>
                <ApiOutlined />
                {t("api_test.test_categories", "Test Categories")}
              </Space>
            }
            key="categories"
          >
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
              {categories.map((category) => (
                <Card
                  key={category.key}
                  size="small"
                  title={
                    <Space>
                      <ApiOutlined />
                      {category.label}
                    </Space>
                  }
                  extra={
                    <ModernButton
                      size="small"
                      variant="outlined"
                      onClick={() => runCategoryTests(category.key)}
                      loading={running && selectedCategory === category.key}
                      disabled={running}
                    >
                      {t("api_test.test", "Test")}
                    </ModernButton>
                  }
                >
                  <Paragraph type="secondary" style={{ fontSize: "12px", marginBottom: 12 }}>
                    {category.description}
                  </Paragraph>
                  <div>
                    {category.endpoints.map((endpoint) => (
                      <Tag key={endpoint} size="small" style={{ marginBottom: 4 }}>
                        {endpoint}
                      </Tag>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          </Panel>
        </Collapse>

        {testResults && (
          <div>
            <Title level={4} style={{ marginBottom: 16 }}>
              {t("api_test.detailed_results", "Detailed Results")}
            </Title>
            <Table
              columns={columns}
              dataSource={testResults.results}
              rowKey={(record) => `${record.method}-${record.endpoint}`}
              pagination={false}
              size="small"
              scroll={{ x: true }}
            />
          </div>
        )}

        {testResults && testResults.failed > 0 && (
          <Alert
            message={t("api_test.issues_detected", "Issues Detected")}
            description={t("api_test.issues_description", "Some API endpoints are not responding correctly. Check the detailed results above and contact your system administrator if the issues persist.")}
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </ModernCard>
    </div>
  );
};

export default ApiTestPanel;