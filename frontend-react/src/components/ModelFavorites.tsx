import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  List,
  Button,
  Typography,
  Space,
  Tag,
  Badge,
  Tooltip,
  Modal,
  Form,
  Input,
  Select,
  message,
  Empty,
  Alert,
  Divider,
  Popconfirm,
  Switch,
  InputNumber,
  Slider,
} from "antd";
import {
  StarOutlined,
  StarFilled,
  HeartOutlined,
  HeartFilled,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SettingOutlined,
  RocketOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  DragOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
// // import { colors } from "../styles/colors";
import { useAIModelsStore, type AIModel } from "../store/aiModelsStore";
import { aiModelsService } from "../services/aiModels";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface ModelFavorite {
  id: string;
  modelId: string;
  userId: string;
  name: string;
  description?: string;
  category: string;
  priority: number;
  customSettings?: {
    temperature: number;
    maxTokens: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
  };
  tags: string[];
  usageCount: number;
  lastUsed: string;
  createdAt: string;
  updatedAt: string;
}

interface FavoriteCategory {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
}

const ModelFavorites: React.FC = () => {
  const { t } = useTranslation();
  const { models, selectedModel, setSelectedModel } = useAIModelsStore();

  const [favorites, setFavorites] = useState<ModelFavorite[]>([]);
  const [categories, setCategories] = useState<FavoriteCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingFavorite, setEditingFavorite] = useState<ModelFavorite | null>(
    null,
  );
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [sortBy, setSortBy] = useState<
    "name" | "priority" | "usage" | "lastUsed"
  >("priority");

  const [form] = Form.useForm();

  useEffect(() => {
    loadFavorites();
    loadCategories();
  }, []);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      // TODO: Load from API
      const mockFavorites: ModelFavorite[] = [
        {
          id: "1",
          modelId: "gpt-4",
          userId: "user1",
          name: "My GPT-4",
          description: "Primary model for complex tasks",
          category: "productivity",
          priority: 1,
          customSettings: {
            temperature: 0.7,
            maxTokens: 2000,
            topP: 1,
            frequencyPenalty: 0,
            presencePenalty: 0,
          },
          tags: ["primary", "complex", "analysis"],
          usageCount: 150,
          lastUsed: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: "2",
          modelId: "claude-3-sonnet",
          userId: "user1",
          name: "Claude Creative",
          description: "Creative writing and brainstorming",
          category: "creative",
          priority: 2,
          customSettings: {
            temperature: 0.9,
            maxTokens: 1500,
            topP: 0.9,
            frequencyPenalty: 0.1,
            presencePenalty: 0.1,
          },
          tags: ["creative", "writing", "brainstorming"],
          usageCount: 89,
          lastUsed: new Date(Date.now() - 86400000).toISOString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: "3",
          modelId: "gpt-3.5-turbo",
          userId: "user1",
          name: "Quick Assistant",
          description: "Fast responses for simple tasks",
          category: "efficiency",
          priority: 3,
          customSettings: {
            temperature: 0.3,
            maxTokens: 500,
            topP: 1,
            frequencyPenalty: 0,
            presencePenalty: 0,
          },
          tags: ["fast", "simple", "efficient"],
          usageCount: 234,
          lastUsed: new Date(Date.now() - 3600000).toISOString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];
      setFavorites(mockFavorites);
    } catch (error) {
      message.error(t("favorites.load_failed"));
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    const mockCategories: FavoriteCategory[] = [
      {
        id: "productivity",
        name: t("favorites.categories.productivity"),
        description: t("favorites.categories.productivity_desc"),
        color: colors.colorPrimary,
        icon: "⚡",
      },
      {
        id: "creative",
        name: t("favorites.categories.creative"),
        description: t("favorites.categories.creative_desc"),
        color: colors.colorWarning,
        icon: "🎨",
      },
      {
        id: "efficiency",
        name: t("favorites.categories.efficiency"),
        description: t("favorites.categories.efficiency_desc"),
        color: colors.colorSuccess,
        icon: "🚀",
      },
      {
        id: "analysis",
        name: t("favorites.categories.analysis"),
        description: t("favorites.categories.analysis_desc"),
        color: colors.colorInfo,
        icon: "📊",
      },
    ];
    setCategories(mockCategories);
  };

  const addToFavorites = async (modelId: string) => {
    try {
      const model = models.find((m) => m.id === modelId);
      if (!model) return;

      const newFavorite: ModelFavorite = {
        id: Date.now().toString(),
        modelId,
        userId: "user1", // TODO: Get from auth
        name: model.displayName,
        description: `Favorite ${model.displayName}`,
        category: "general",
        priority: favorites.length + 1,
        customSettings: {
          temperature: 0.7,
          maxTokens: model.maxTokens,
          topP: 1,
          frequencyPenalty: 0,
          presencePenalty: 0,
        },
        tags: ["favorite"],
        usageCount: 0,
        lastUsed: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setFavorites((prev) => [...prev, newFavorite]);
      message.success(t("favorites.added_success"));
    } catch (error) {
      message.error(t("favorites.add_failed"));
    }
  };

  const removeFromFavorites = async (favoriteId: string) => {
    try {
      setFavorites((prev) => prev.filter((f) => f.id !== favoriteId));
      message.success(t("favorites.removed_success"));
    } catch (error) {
      message.error(t("favorites.remove_failed"));
    }
  };

  const updateFavorite = async (values: any) => {
    try {
      if (editingFavorite) {
        const updatedFavorite = { ...editingFavorite, ...values };
        setFavorites((prev) =>
          prev.map((f) => (f.id === editingFavorite.id ? updatedFavorite : f)),
        );
        message.success(t("favorites.updated_success"));
      } else {
        const newFavorite: ModelFavorite = {
          id: Date.now().toString(),
          ...values,
          userId: "user1",
          usageCount: 0,
          lastUsed: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        setFavorites((prev) => [...prev, newFavorite]);
        message.success(t("favorites.created_success"));
      }

      setModalVisible(false);
      form.resetFields();
      setEditingFavorite(null);
    } catch (error) {
      message.error(t("favorites.save_failed"));
    }
  };

  const selectFavorite = (favorite: ModelFavorite) => {
    setSelectedModel(models.find((m) => m.id === favorite.modelId) || null);

    // Update usage count
    setFavorites((prev) =>
      prev.map((f) =>
        f.id === favorite.id
          ? {
              ...f,
              usageCount: f.usageCount + 1,
              lastUsed: new Date().toISOString(),
            }
          : f,
      ),
    );

    message.success(t("favorites.model_selected"));
  };

  const getModelName = (modelId: string) => {
    return models.find((m) => m.id === modelId)?.displayName || modelId;
  };

  const getCategoryInfo = (categoryId: string) => {
    return categories.find((c) => c.id === categoryId) || categories[0];
  };

  const filteredFavorites = favorites
    .filter(
      (f) => selectedCategory === "all" || f.category === selectedCategory,
    )
    .sort((a, b) => {
      switch (sortBy) {
        case "name":
          return a.name.localeCompare(b.name);
        case "priority":
          return a.priority - b.priority;
        case "usage":
          return b.usageCount - a.usageCount;
        case "lastUsed":
          return (
            new Date(b.lastUsed).getTime() - new Date(a.lastUsed).getTime()
          );
        default:
          return 0;
      }
    });

  const renderFavoriteCard = (favorite: ModelFavorite) => {
    const model = models.find((m) => m.id === favorite.modelId);
    const category = getCategoryInfo(favorite.category);

    return (
      <Card
        key={favorite.id}
        hoverable
        style={{ marginBottom: 16 }}
        actions={[
          <Tooltip title={t("favorites.use_model")}>
            <Button
              type="text"
              icon={<RocketOutlined />}
              onClick={() => selectFavorite(favorite)}
             />
          </Tooltip>,
          <Tooltip title={t("favorites.edit")}>
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => {
                setEditingFavorite(favorite);
                form.setFieldsValue(favorite);
                setModalVisible(true);
              }}
            />
          </Tooltip>,
          <Tooltip title={t("favorites.remove")}>
            <Popconfirm
              title={t("favorites.remove_confirm")}
              onConfirm={() => removeFromFavorites(favorite.id)}
            >
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>,
        ]}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
          }}
        >
          <div style={{ flex: 1 }}>
            <div
              style={{ display: "flex", alignItems: "center", marginBottom: 8 }}
            >
              <Text strong style={{ fontSize: 16, marginRight: 8 }}>
                {favorite.name}
              </Text>
              <Badge
                count={favorite.priority}
                style={{ backgroundColor: category.color }}
              />
            </div>

            <Text
              type="secondary"
              style={{ display: "block", marginBottom: 8 }}
            >
              {favorite.description}
            </Text>

            <div style={{ marginBottom: 8 }}>
              <Tag color={category.color} icon={<span>{category.icon}</span>}>
                {category.name}
              </Tag>
              {favorite.tags.map((tag) => (
                <Tag key={tag} size="small">
                  {tag}
                </Tag>
              ))}
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Space>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <ClockCircleOutlined /> {favorite.usageCount}{" "}
                  {t("favorites.uses")}
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <DollarOutlined /> {model?.costPer1kTokens?.toFixed(4)}/1k
                </Text>
              </Space>

              <Text type="secondary" style={{ fontSize: 12 }}>
                {new Date(favorite.lastUsed).toLocaleDateString()}
              </Text>
            </div>
          </div>
        </div>
      </Card>
    );
  };

  const renderFavoriteList = (favorite: ModelFavorite) => {
    const model = models.find((m) => m.id === favorite.modelId);
    const category = getCategoryInfo(favorite.category);

    return (
      <List.Item
        key={favorite.id}
        actions={[
          <Button
            type="primary"
            size="small"
            icon={<RocketOutlined />}
            onClick={() => selectFavorite(favorite)}
          >
            {t("favorites.use")}
          </Button>,
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingFavorite(favorite);
              form.setFieldsValue(favorite);
              setModalVisible(true);
            }}
          >
            {t("favorites.edit")}
          </Button>,
          <Popconfirm
            title={t("favorites.remove_confirm")}
            onConfirm={() => removeFromFavorites(favorite.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              {t("favorites.remove")}
            </Button>
          </Popconfirm>,
        ]}
      >
        <List.Item.Meta
          avatar={
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: "50%",
                backgroundColor: category.color,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 16,
              }}
            >
              {category.icon}
            </div>
          }
          title={
            <Space>
              <Text strong>{favorite.name}</Text>
              <Badge
                count={favorite.priority}
                style={{ backgroundColor: category.color }}
              />
              <Tag color={category.color}>{category.name}</Tag>
            </Space>
          }
          description={
            <div>
              <Text type="secondary">{favorite.description}</Text>
              <br />
              <Space>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <ClockCircleOutlined /> {favorite.usageCount}{" "}
                  {t("favorites.uses")}
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <DollarOutlined /> {model?.costPer1kTokens?.toFixed(4)}/1k
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {new Date(favorite.lastUsed).toLocaleDateString()}
                </Text>
              </Space>
              <br />
              <Space>
                {favorite.tags.map((tag) => (
                  <Tag key={tag} size="small">
                    {tag}
                  </Tag>
                ))}
              </Space>
            </div>
          }
        />
      </List.Item>
    );
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        <HeartFilled style={{ marginRight: 8, color: colors.colorError }} />
        {t("favorites.title")}
      </Title>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              value={selectedCategory}
              onChange={setSelectedCategory}
              style={{ width: "100%" }}
            >
              <Option value="all">{t("favorites.all_categories")}</Option>
              {categories.map((category) => (
                <Option key={category.id} value={category.id}>
                  <Space>
                    <span>{category.icon}</span>
                    {category.name}
                  </Space>
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              value={sortBy}
              onChange={setSortBy}
              style={{ width: "100%" }}
            >
              <Option value="priority">{t("favorites.sort.priority")}</Option>
              <Option value="name">{t("favorites.sort.name")}</Option>
              <Option value="usage">{t("favorites.sort.usage")}</Option>
              <Option value="lastUsed">{t("favorites.sort.last_used")}</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              value={viewMode}
              onChange={setViewMode}
              style={{ width: "100%" }}
            >
              <Option value="grid">{t("favorites.view.grid")}</Option>
              <Option value="list">{t("favorites.view.list")}</Option>
            </Select>
          </Col>
          <Col span={6}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEditingFavorite(null);
                form.resetFields();
                setModalVisible(true);
              }}
            >
              {t("favorites.add_favorite")}
            </Button>
          </Col>
          <Col span={4}>
            <Text type="secondary">
              {filteredFavorites.length} {t("favorites.total")}
            </Text>
          </Col>
        </Row>
      </Card>

      {/* Favorites Display */}
      {filteredFavorites.length === 0 ? (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={t("favorites.no_favorites")}
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEditingFavorite(null);
                form.resetFields();
                setModalVisible(true);
              }}
            >
              {t("favorites.add_first")}
            </Button>
          </Empty>
        </Card>
      ) : viewMode === "grid" ? (
        <Row gutter={[16, 16]}>
          {filteredFavorites.map((favorite) => (
            <Col xs={24} sm={12} md={8} lg={6} key={favorite.id}>
              {renderFavoriteCard(favorite)}
            </Col>
          ))}
        </Row>
      ) : (
        <List
          dataSource={filteredFavorites}
          renderItem={renderFavoriteList}
          pagination={{ pageSize: 10 }}
        />
      )}

      {/* Add/Edit Favorite Modal */}
      <Modal
        title={
          editingFavorite
            ? t("favorites.edit_favorite")
            : t("favorites.add_favorite")
        }
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false);
          setEditingFavorite(null);
          form.resetFields();
        }}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={updateFavorite}>
          <Form.Item
            name="modelId"
            label={t("favorites.form.model")}
            rules={[{ required: true }]}
          >
            <Select placeholder={t("favorites.form.select_model")}>
              {models.map((model) => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="name"
            label={t("favorites.form.name")}
            rules={[{ required: true }]}
          >
            <Input placeholder={t("favorites.form.name_placeholder")} />
          </Form.Item>

          <Form.Item name="description" label={t("favorites.form.description")}>
            <Input placeholder={t("favorites.form.description_placeholder")} />
          </Form.Item>

          <Form.Item
            name="category"
            label={t("favorites.form.category")}
            rules={[{ required: true }]}
          >
            <Select placeholder={t("favorites.form.select_category")}>
              {categories.map((category) => (
                <Option key={category.id} value={category.id}>
                  <Space>
                    <span>{category.icon}</span>
                    {category.name}
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="priority"
            label={t("favorites.form.priority")}
            rules={[{ required: true }]}
          >
            <InputNumber min={1} max={100} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item name="tags" label={t("favorites.form.tags")}>
            <Select
              mode="tags"
              placeholder={t("favorites.form.tags_placeholder")}
            />
          </Form.Item>

          <Divider>{t("favorites.form.custom_settings")}</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={["customSettings", "temperature"]}
                label={t("favorites.form.temperature")}
              >
                <Slider min={0} max={2} step={0.1} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={["customSettings", "maxTokens"]}
                label={t("favorites.form.max_tokens")}
              >
                <InputNumber min={1} max={4000} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default ModelFavorites;
