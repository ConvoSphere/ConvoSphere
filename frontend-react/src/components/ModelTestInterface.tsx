import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Form,
  Input,
  Button,
  Select,
  Switch,
  Table,
  Typography,
  Space,
  Tag,
  Progress,
  Alert,
  Tabs,
  Divider,
  List,
  Badge,
  Modal,
  message,
  Spin,
  Tooltip,
  Collapse,
  Checkbox,
  Radio,
  Slider,
  InputNumber,
} from "antd";
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ReloadOutlined,
  SaveOutlined,
  FileTextOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  EyeOutlined,
  DownloadOutlined,
  SettingOutlined,
  RobotOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
// // import { colors } from "../styles/colors";
import {
  useAIModelsStore,
  type AIModel,
  type ModelTest,
} from "../store/aiModelsStore";
import { aiModelsService } from "../services/aiModels";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Panel } = Collapse;

interface TestScenario {
  id: string;
  name: string;
  description: string;
  prompt: string;
  expectedResponse?: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  tags: string[];
}

interface ABTestResult {
  modelA: string;
  modelB: string;
  scenario: string;
  results: {
    modelA: ModelTest;
    modelB: ModelTest;
  };
  comparison: {
    responseTime: { winner: string; difference: number };
    cost: { winner: string; difference: number };
    quality: { winner: string; score: number };
  };
}

interface TestSuite {
  id: string;
  name: string;
  description: string;
  scenarios: TestScenario[];
  models: string[];
  autoRun: boolean;
  schedule?: string;
  lastRun?: string;
  status: "idle" | "running" | "completed" | "failed";
}

const ModelTestInterface: React.FC = () => {
  const { t } = useTranslation();
  const { models, testModel } = useAIModelsStore();

  const [activeTab, setActiveTab] = useState("single");
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [testResults, setTestResults] = useState<ModelTest[]>([]);
  const [abTestResults, setAbTestResults] = useState<ABTestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [runningSuite, setRunningSuite] = useState<string | null>(null);

  // Form states
  const [singleTestForm] = Form.useForm();
  const [abTestForm] = Form.useForm();
  const [suiteForm] = Form.useForm();

  // Test scenarios
  const [scenarios, setScenarios] = useState<TestScenario[]>([
    {
      id: "1",
      name: "Basic Question",
      description: "Simple factual question",
      prompt: "What is the capital of France?",
      category: "factual",
      difficulty: "easy",
      tags: ["geography", "basic"],
    },
    {
      id: "2",
      name: "Creative Writing",
      description: "Creative story generation",
      prompt: "Write a short story about a robot learning to paint.",
      category: "creative",
      difficulty: "medium",
      tags: ["creative", "writing"],
    },
    {
      id: "3",
      name: "Code Generation",
      description: "Programming task",
      prompt: "Write a Python function to calculate fibonacci numbers.",
      category: "programming",
      difficulty: "medium",
      tags: ["code", "python"],
    },
    {
      id: "4",
      name: "Complex Reasoning",
      description: "Multi-step reasoning problem",
      prompt:
        "If a train leaves station A at 2 PM traveling 60 mph and another train leaves station B at 3 PM traveling 80 mph, when will they meet if the stations are 200 miles apart?",
      category: "reasoning",
      difficulty: "hard",
      tags: ["math", "reasoning"],
    },
  ]);

  const [selectedScenario, setSelectedScenario] = useState<string>("");
  const [customPrompt, setCustomPrompt] = useState("");
  const [testSettings, setTestSettings] = useState({
    temperature: 0.7,
    maxTokens: 1000,
    includeMetrics: true,
    saveResults: true,
  });

  useEffect(() => {
    loadTestSuites();
  }, []);

  const loadTestSuites = async () => {
    // TODO: Load from API
    const mockSuites: TestSuite[] = [
      {
        id: "1",
        name: "Basic Functionality Test",
        description: "Tests basic model capabilities",
        scenarios: scenarios.slice(0, 2),
        models: models.slice(0, 2).map((m) => m.id),
        autoRun: false,
        status: "idle",
      },
      {
        id: "2",
        name: "Performance Benchmark",
        description: "Comprehensive performance testing",
        scenarios: scenarios,
        models: models.map((m) => m.id),
        autoRun: true,
        schedule: "daily",
        status: "completed",
        lastRun: new Date().toISOString(),
      },
    ];
    setTestSuites(mockSuites);
  };

  const runSingleTest = async () => {
    try {
      const values = await singleTestForm.validateFields();
      setLoading(true);

      const prompt =
        values.customPrompt ||
        scenarios.find((s) => s.id === values.scenario)?.prompt ||
        "";
      const result = await testModel(values.model, prompt);

      setTestResults((prev) => [result, ...prev]);
      message.success(t("test.single_test_success"));
    } catch (error) {
      message.error(t("test.single_test_failed"));
    } finally {
      setLoading(false);
    }
  };

  const runABTest = async () => {
    try {
      const values = await abTestForm.validateFields();
      setLoading(true);

      const prompt =
        values.customPrompt ||
        scenarios.find((s) => s.id === values.scenario)?.prompt ||
        "";

      // Run tests for both models
      const [resultA, resultB] = await Promise.all([
        testModel(values.modelA, prompt),
        testModel(values.modelB, prompt),
      ]);

      // Calculate comparison
      const comparison = {
        responseTime: {
          winner:
            resultA.responseTime < resultB.responseTime
              ? values.modelA
              : values.modelB,
          difference: Math.abs(resultA.responseTime - resultB.responseTime),
        },
        cost: {
          winner: resultA.cost < resultB.cost ? values.modelA : values.modelB,
          difference: Math.abs(resultA.cost - resultB.cost),
        },
        quality: {
          winner:
            resultA.response.length > resultB.response.length
              ? values.modelA
              : values.modelB,
          score: Math.abs(resultA.response.length - resultB.response.length),
        },
      };

      const abResult: ABTestResult = {
        modelA: values.modelA,
        modelB: values.modelB,
        scenario: values.scenario || "custom",
        results: { modelA: resultA, modelB: resultB },
        comparison,
      };

      setAbTestResults((prev) => [abResult, ...prev]);
      message.success(t("test.ab_test_success"));
    } catch (error) {
      message.error(t("test.ab_test_failed"));
    } finally {
      setLoading(false);
    }
  };

  const runTestSuite = async (suiteId: string) => {
    const suite = testSuites.find((s) => s.id === suiteId);
    if (!suite) return;

    setRunningSuite(suiteId);
    setTestSuites((prev) =>
      prev.map((s) => (s.id === suiteId ? { ...s, status: "running" } : s)),
    );

    try {
      const results: ModelTest[] = [];

      for (const modelId of suite.models) {
        for (const scenario of suite.scenarios) {
          const result = await testModel(modelId, scenario.prompt);
          results.push(result);
        }
      }

      setTestResults((prev) => [...results, ...prev]);

      setTestSuites((prev) =>
        prev.map((s) =>
          s.id === suiteId
            ? {
                ...s,
                status: "completed",
                lastRun: new Date().toISOString(),
              }
            : s,
        ),
      );

      message.success(t("test.suite_completed"));
    } catch (error) {
      setTestSuites((prev) =>
        prev.map((s) => (s.id === suiteId ? { ...s, status: "failed" } : s)),
      );
      message.error(t("test.suite_failed"));
    } finally {
      setRunningSuite(null);
    }
  };

  const saveTestSuite = async () => {
    try {
      const values = await suiteForm.validateFields();

      const newSuite: TestSuite = {
        id: Date.now().toString(),
        name: values.name,
        description: values.description,
        scenarios: values.scenarios.map(
          (id: string) => scenarios.find((s) => s.id === id)!,
        ),
        models: values.models,
        autoRun: values.autoRun,
        schedule: values.schedule,
        status: "idle",
      };

      setTestSuites((prev) => [...prev, newSuite]);
      suiteForm.resetFields();
      message.success(t("test.suite_saved"));
    } catch (error) {
      message.error(t("test.suite_save_failed"));
    }
  };

  const exportResults = () => {
    const data = {
      singleTests: testResults,
      abTests: abTestResults,
      timestamp: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `model-test-results-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getModelName = (modelId: string) => {
    return models.find((m) => m.id === modelId)?.displayName || modelId;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return colors.colorSuccess;
      case "medium":
        return colors.colorWarning;
      case "hard":
        return colors.colorError;
      default:
        return colors.colorTextSecondary;
    }
  };

  const testResultColumns = [
    {
      title: t("test.results.model"),
      dataIndex: "modelId",
      key: "model",
      render: (modelId: string) => getModelName(modelId),
    },
    {
      title: t("test.results.response_time"),
      dataIndex: "responseTime",
      key: "responseTime",
      render: (time: number) => (
        <Space>
          <ClockCircleOutlined />
          {time}ms
        </Space>
      ),
    },
    {
      title: t("test.results.tokens"),
      dataIndex: "tokensUsed",
      key: "tokens",
    },
    {
      title: t("test.results.cost"),
      dataIndex: "cost",
      key: "cost",
      render: (cost: number) => (
        <Space>
          <DollarOutlined />${cost.toFixed(4)}
        </Space>
      ),
    },
    {
      title: t("test.results.response"),
      dataIndex: "response",
      key: "response",
      render: (response: string) => (
        <Tooltip title={response}>
          <Text ellipsis style={{ maxWidth: 200 }}>
            {response.substring(0, 100)}...
          </Text>
        </Tooltip>
      ),
    },
    {
      title: t("test.results.timestamp"),
      dataIndex: "timestamp",
      key: "timestamp",
      render: (timestamp: string) => new Date(timestamp).toLocaleString(),
    },
  ];

  const abTestColumns = [
    {
      title: t("test.ab_test.models"),
      key: "models",
      render: (record: ABTestResult) => (
        <Space direction="vertical">
          <Text strong>
            {getModelName(record.modelA)} vs {getModelName(record.modelB)}
          </Text>
          <Text type="secondary">{record.scenario}</Text>
        </Space>
      ),
    },
    {
      title: t("test.ab_test.response_time"),
      key: "responseTime",
      render: (record: ABTestResult) => (
        <Space direction="vertical">
          <Text>
            {getModelName(record.comparison.responseTime.winner)} wins
          </Text>
          <Text type="secondary">
            {record.comparison.responseTime.difference}ms difference
          </Text>
        </Space>
      ),
    },
    {
      title: t("test.ab_test.cost"),
      key: "cost",
      render: (record: ABTestResult) => (
        <Space direction="vertical">
          <Text>{getModelName(record.comparison.cost.winner)} wins</Text>
          <Text type="secondary">
            ${record.comparison.cost.difference.toFixed(4)} difference
          </Text>
        </Space>
      ),
    },
    {
      title: t("test.ab_test.quality"),
      key: "quality",
      render: (record: ABTestResult) => (
        <Space direction="vertical">
          <Text>{getModelName(record.comparison.quality.winner)} wins</Text>
          <Text type="secondary">
            {record.comparison.quality.score} chars difference
          </Text>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        <ExperimentOutlined style={{ marginRight: 8 }} />
        {t("test.title")}
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        {/* Single Model Test */}
        <TabPane tab={t("test.tabs.single")} key="single">
          <Card>
            <Form form={singleTestForm} layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="model"
                    label={t("test.form.model")}
                    rules={[{ required: true }]}
                  >
                    <Select placeholder={t("test.form.select_model")}>
                      {models.map((model) => (
                        <Option key={model.id} value={model.id}>
                          {model.displayName}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="scenario" label={t("test.form.scenario")}>
                    <Select
                      placeholder={t("test.form.select_scenario")}
                      onChange={setSelectedScenario}
                    >
                      {scenarios.map((scenario) => (
                        <Option key={scenario.id} value={scenario.id}>
                          <Space>
                            <Text>{scenario.name}</Text>
                            <Tag
                              color={getDifficultyColor(scenario.difficulty)}
                              size="small"
                            >
                              {scenario.difficulty}
                            </Tag>
                          </Space>
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="customPrompt"
                label={t("test.form.custom_prompt")}
              >
                <TextArea
                  rows={4}
                  placeholder={t("test.form.prompt_placeholder")}
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="temperature"
                    label={t("test.form.temperature")}
                  >
                    <Slider
                      min={0}
                      max={2}
                      step={0.1}
                      defaultValue={0.7}
                      marks={{
                        0: "Focused",
                        1: "Balanced",
                        2: "Creative",
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="maxTokens" label={t("test.form.max_tokens")}>
                    <InputNumber
                      min={1}
                      max={4000}
                      defaultValue={1000}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="includeMetrics"
                    label={t("test.form.include_metrics")}
                    valuePropName="checked"
                  >
                    <Switch defaultChecked />
                  </Form.Item>
                </Col>
              </Row>

              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={runSingleTest}
                loading={loading}
                size="large"
              >
                {t("test.run_single_test")}
              </Button>
            </Form>
          </Card>
        </TabPane>

        {/* A/B Testing */}
        <TabPane tab={t("test.tabs.ab_test")} key="ab_test">
          <Card>
            <Form form={abTestForm} layout="vertical">
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="modelA"
                    label={t("test.form.model_a")}
                    rules={[{ required: true }]}
                  >
                    <Select placeholder={t("test.form.select_model_a")}>
                      {models.map((model) => (
                        <Option key={model.id} value={model.id}>
                          {model.displayName}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="modelB"
                    label={t("test.form.model_b")}
                    rules={[{ required: true }]}
                  >
                    <Select placeholder={t("test.form.select_model_b")}>
                      {models.map((model) => (
                        <Option key={model.id} value={model.id}>
                          {model.displayName}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="scenario" label={t("test.form.scenario")}>
                    <Select placeholder={t("test.form.select_scenario")}>
                      {scenarios.map((scenario) => (
                        <Option key={scenario.id} value={scenario.id}>
                          {scenario.name}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="customPrompt"
                label={t("test.form.custom_prompt")}
              >
                <TextArea
                  rows={4}
                  placeholder={t("test.form.prompt_placeholder")}
                />
              </Form.Item>

              <Button
                type="primary"
                icon={<BarChartOutlined />}
                onClick={runABTest}
                loading={loading}
                size="large"
              >
                {t("test.run_ab_test")}
              </Button>
            </Form>
          </Card>
        </TabPane>

        {/* Test Suites */}
        <TabPane tab={t("test.tabs.suites")} key="suites">
          <Card>
            <div style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => {
                  /* TODO: Open suite creation modal */
                }}
              >
                {t("test.create_suite")}
              </Button>
            </div>

            <List
              dataSource={testSuites}
              renderItem={(suite) => (
                <List.Item
                  actions={[
                    <Button
                      key="run"
                      type="primary"
                      icon={<PlayCircleOutlined />}
                      onClick={() => runTestSuite(suite.id)}
                      loading={runningSuite === suite.id}
                      disabled={suite.status === "running"}
                    >
                      {t("test.run_suite")}
                    </Button>,
                    <Button key="edit" icon={<SettingOutlined />}>
                      {t("test.edit_suite")}
                    </Button>,
                    <Button key="delete" danger>
                      {t("test.delete_suite")}
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Text strong>{suite.name}</Text>
                        <Badge
                          status={
                            suite.status === "completed"
                              ? "success"
                              : suite.status === "running"
                                ? "processing"
                                : suite.status === "failed"
                                  ? "error"
                                  : "default"
                          }
                          text={t(`test.status.${suite.status}`)}
                        />
                      </Space>
                    }
                    description={
                      <div>
                        <Text type="secondary">{suite.description}</Text>
                        <br />
                        <Space>
                          <Text type="secondary">
                            {suite.scenarios.length} {t("test.scenarios")}
                          </Text>
                          <Text type="secondary">
                            {suite.models.length} {t("test.models")}
                          </Text>
                          {suite.lastRun && (
                            <Text type="secondary">
                              {t("test.last_run")}:{" "}
                              {new Date(suite.lastRun).toLocaleString()}
                            </Text>
                          )}
                        </Space>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* Results Section */}
      {(testResults.length > 0 || abTestResults.length > 0) && (
        <Card
          title={t("test.results.title")}
          extra={
            <Space>
              <Button icon={<DownloadOutlined />} onClick={exportResults}>
                {t("test.export_results")}
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setTestResults([]);
                  setAbTestResults([]);
                }}
              >
                {t("test.clear_results")}
              </Button>
            </Space>
          }
          style={{ marginTop: 16 }}
        >
          <Tabs defaultActiveKey="single">
            <TabPane tab={t("test.results.single_tests")} key="single">
              <Table
                columns={testResultColumns}
                dataSource={testResults}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </TabPane>
            <TabPane tab={t("test.results.ab_tests")} key="ab">
              <Table
                columns={abTestColumns}
                dataSource={abTestResults}
                rowKey={(record) =>
                  `${record.modelA}-${record.modelB}-${record.scenario}`
                }
                pagination={{ pageSize: 10 }}
              />
            </TabPane>
          </Tabs>
        </Card>
      )}
    </div>
  );
};

export default ModelTestInterface;
