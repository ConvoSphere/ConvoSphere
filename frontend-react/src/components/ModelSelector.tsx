import React, { useState, useEffect } from "react";
import {
  Select,
  Card,
  Row,
  Col,
  Typography,
  Tag,
  Space,
  Tooltip,
  Button,
  Modal,
  Table,
  Progress,
  Statistic,
  Divider,
  Alert,
} from "antd";
import {
  InfoCircleOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  BarChartOutlined,
  EyeOutlined,
  StarOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { config } from "../config";
import { colors } from "../styles/colors";

const { Option } = Select;
const { Title, Text } = Typography;

interface AIModel {
  id: string;
  name: string;
  provider: string;
  modelId: string;
  displayName: string;
  description: string;
  maxTokens: number;
  costPer1kTokens: number;
  isActive: boolean;
  isDefault: boolean;
  isFavorite: boolean;
  performance: {
    responseTime: number;
    errorRate: number;
    successRate: number;
    totalRequests: number;
  };
  capabilities: string[];
  lastUsed: string;
  createdAt: string;
  updatedAt: string;
}

interface ModelSelectorProps {
  value?: string;
  onChange?: (value: string) => void;
  showPerformance?: boolean;
  showCosts?: boolean;
  allowCustomParams?: boolean;
  placeholder?: string;
  disabled?: boolean;
  style?: React.CSSProperties;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  value,
  onChange,
  showPerformance = true,
  showCosts = true,
  allowCustomParams = false,
  placeholder,
  disabled = false,
  style,
}) => {
  const { t } = useTranslation();
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparisonModalVisible, setComparisonModalVisible] = useState(false);
  const [selectedModels, setSelectedModels] = useState<AIModel[]>([]);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models`);
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      }
    } catch (error) {
      console.error("Failed to load models:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleComparison = () => {
    const activeModels = models.filter(m => m.isActive);
    setSelectedModels(activeModels.slice(0, 3)); // Compare first 3 active models
    setComparisonModalVisible(true);
  };

  const getPerformanceColor = (rate: number) => {
    if (rate >= 95) return colors.colorSuccess;
    if (rate >= 80) return colors.colorWarning;
    return colors.colorError;
  };

  const getResponseTimeColor = (time: number) => {
    if (time <= 1000) return colors.colorSuccess;
    if (time <= 3000) return colors.colorWarning;
    return colors.colorError;
  };

  const getCostColor = (cost: number) => {
    if (cost <= 0.001) return colors.colorSuccess;
    if (cost <= 0.01) return colors.colorWarning;
    return colors.colorError;
  };

  const renderModelOption = (model: AIModel) => {
    const isSelected = value === model.id;
    
    return (
      <div style={{ 
        padding: "8px 0", 
        borderBottom: "1px solid #f0f0f0",
        backgroundColor: isSelected ? colors.colorPrimaryBg : "transparent"
      }}>
        <Row gutter={16} align="middle">
          <Col span={showPerformance || showCosts ? 8 : 12}>
            <div>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>
                {model.displayName}
                {model.isDefault && (
                  <Tag color="blue" size="small" style={{ marginLeft: 8 }}>
                    {t("model_selector.default")}
                  </Tag>
                )}
                {model.isFavorite && (
                  <StarOutlined style={{ color: colors.colorWarning, marginLeft: 4 }} />
                )}
              </div>
              <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
                {model.provider} • {model.modelId}
              </div>
              {model.description && (
                <div style={{ fontSize: "12px", color: colors.colorTextSecondary, marginTop: 4 }}>
                  {model.description}
                </div>
              )}
            </div>
          </Col>
          
          {showPerformance && (
            <Col span={8}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: "12px" }}>{t("model_selector.response_time")}: </Text>
                <Tag 
                  color={getResponseTimeColor(model.performance.responseTime)}
                  size="small"
                >
                  {model.performance.responseTime}ms
                </Tag>
              </div>
              <div>
                <Text style={{ fontSize: "12px" }}>{t("model_selector.success_rate")}: </Text>
                <Tag 
                  color={getPerformanceColor(model.performance.successRate)}
                  size="small"
                >
                  {model.performance.successRate}%
                </Tag>
              </div>
            </Col>
          )}
          
          {showCosts && (
            <Col span={8}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: "12px" }}>{t("model_selector.cost")}: </Text>
                <Tag 
                  color={getCostColor(model.costPer1kTokens)}
                  size="small"
                >
                  ${model.costPer1kTokens.toFixed(4)}/1k
                </Tag>
              </div>
              <div>
                <Text style={{ fontSize: "12px" }}>{t("model_selector.max_tokens")}: </Text>
                <Text style={{ fontSize: "12px" }}>{model.maxTokens.toLocaleString()}</Text>
              </div>
            </Col>
          )}
        </Row>
      </div>
    );
  };

  const comparisonColumns = [
    {
      title: t("model_selector.comparison.model"),
      dataIndex: "displayName",
      key: "model",
      render: (text: string, record: AIModel) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
            {record.provider} • {record.modelId}
          </div>
        </div>
      ),
    },
    {
      title: t("model_selector.comparison.performance"),
      key: "performance",
      render: (record: AIModel) => (
        <div>
          <div style={{ marginBottom: 8 }}>
            <Text style={{ fontSize: "12px" }}>{t("model_selector.comparison.response_time")}</Text>
            <div>
              <Tag color={getResponseTimeColor(record.performance.responseTime)}>
                {record.performance.responseTime}ms
              </Tag>
            </div>
          </div>
          <div>
            <Text style={{ fontSize: "12px" }}>{t("model_selector.comparison.success_rate")}</Text>
            <div>
              <Progress 
                percent={record.performance.successRate} 
                size="small"
                strokeColor={getPerformanceColor(record.performance.successRate)}
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      title: t("model_selector.comparison.cost"),
      key: "cost",
      render: (record: AIModel) => (
        <div>
          <Statistic
            title={t("model_selector.comparison.cost_per_1k")}
            value={record.costPer1kTokens}
            precision={4}
            prefix="$"
            valueStyle={{ 
              color: getCostColor(record.costPer1kTokens),
              fontSize: "14px"
            }}
          />
          <div style={{ marginTop: 8 }}>
            <Text style={{ fontSize: "12px" }}>{t("model_selector.comparison.max_tokens")}</Text>
            <div>{record.maxTokens.toLocaleString()}</div>
          </div>
        </div>
      ),
    },
    {
      title: t("model_selector.comparison.usage"),
      key: "usage",
      render: (record: AIModel) => (
        <div>
          <Statistic
            title={t("model_selector.comparison.total_requests")}
            value={record.performance.totalRequests}
            valueStyle={{ fontSize: "14px" }}
          />
          <div style={{ marginTop: 8 }}>
            <Text style={{ fontSize: "12px" }}>{t("model_selector.comparison.last_used")}</Text>
            <div>{new Date(record.lastUsed).toLocaleDateString()}</div>
          </div>
        </div>
      ),
    },
    {
      title: t("model_selector.comparison.capabilities"),
      key: "capabilities",
      render: (record: AIModel) => (
        <div>
          {record.capabilities.map((capability) => (
            <Tag key={capability} size="small" style={{ marginBottom: 4 }}>
              {capability}
            </Tag>
          ))}
        </div>
      ),
    },
  ];

  const activeModels = models.filter(m => m.isActive);
  const defaultModel = models.find(m => m.isDefault);
  const favoriteModels = models.filter(m => m.isFavorite);

  return (
    <div>
      <div style={{ marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Text strong>{t("model_selector.title")}</Text>
        <Space>
          {showPerformance && showCosts && (
            <Tooltip title={t("model_selector.compare_models")}>
              <Button 
                size="small" 
                icon={<BarChartOutlined />}
                onClick={handleComparison}
              >
                {t("model_selector.compare")}
              </Button>
            </Tooltip>
          )}
        </Space>
      </div>

      <Select
        value={value}
        onChange={onChange}
        placeholder={placeholder || t("model_selector.placeholder")}
        loading={loading}
        disabled={disabled}
        style={{ width: "100%", ...style }}
        dropdownRender={(menu) => (
          <div>
            {menu}
            <Divider style={{ margin: "8px 0" }} />
            <div style={{ padding: "8px 16px" }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title={t("model_selector.stats.total")}
                    value={models.length}
                    prefix={<BarChartOutlined />}
                    valueStyle={{ fontSize: "14px" }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title={t("model_selector.stats.active")}
                    value={activeModels.length}
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ fontSize: "14px", color: colors.colorSuccess }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title={t("model_selector.stats.favorites")}
                    value={favoriteModels.length}
                    prefix={<StarOutlined />}
                    valueStyle={{ fontSize: "14px", color: colors.colorWarning }}
                  />
                </Col>
              </Row>
            </div>
          </div>
        )}
      >
        {defaultModel && (
          <Option key={defaultModel.id} value={defaultModel.id}>
            {renderModelOption(defaultModel)}
          </Option>
        )}
        
        {favoriteModels.filter(m => m.id !== defaultModel?.id).map((model) => (
          <Option key={model.id} value={model.id}>
            {renderModelOption(model)}
          </Option>
        ))}
        
        {activeModels.filter(m => !m.isDefault && !m.isFavorite).map((model) => (
          <Option key={model.id} value={model.id}>
            {renderModelOption(model)}
          </Option>
        ))}
      </Select>

      {value && (
        <div style={{ marginTop: 8 }}>
          <Alert
            message={t("model_selector.selected_model_info")}
            description={
              <div>
                {(() => {
                  const selectedModel = models.find(m => m.id === value);
                  if (!selectedModel) return null;
                  
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Text style={{ fontSize: "12px" }}>{t("model_selector.info.provider")}: </Text>
                        <Text strong>{selectedModel.provider}</Text>
                      </Col>
                      <Col span={8}>
                        <Text style={{ fontSize: "12px" }}>{t("model_selector.info.max_tokens")}: </Text>
                        <Text strong>{selectedModel.maxTokens.toLocaleString()}</Text>
                      </Col>
                      <Col span={8}>
                        <Text style={{ fontSize: "12px" }}>{t("model_selector.info.cost")}: </Text>
                        <Text strong>${selectedModel.costPer1kTokens.toFixed(4)}/1k</Text>
                      </Col>
                    </Row>
                  );
                })()}
              </div>
            }
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
            style={{ fontSize: "12px" }}
          />
        </div>
      )}

      {/* Model Comparison Modal */}
      <Modal
        title={t("model_selector.comparison.title")}
        open={comparisonModalVisible}
        onCancel={() => setComparisonModalVisible(false)}
        footer={null}
        width={1000}
      >
        <Table
          columns={comparisonColumns}
          dataSource={selectedModels}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Modal>
    </div>
  );
};

export default ModelSelector;