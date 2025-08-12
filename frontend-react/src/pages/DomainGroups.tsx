import React, { useEffect, useState } from "react";
import {
  Typography,
  Space,
  Row,
  Col,
  Card,
  Button,
  Input,
  Modal,
  Form,
  Select,
  Switch,
  message,
  Spin,
  Alert,
  Tooltip,
  Tabs,
  Statistic,
} from "antd";
import {
  TeamOutlined,
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SettingOutlined,
  UserOutlined,
  LockOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useDomainGroupsStore } from "../store/domainGroupsStore";
import { useAuthStore } from "../store/authStore";
import DomainGroupList from "../components/domain-groups/DomainGroupList";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";
import type {
  DomainGroup,
  DomainGroupCreate,
  DomainGroupUpdate,
} from "../services/domainGroups";

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const DomainGroups: React.FC = () => {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const {
    groups,
    selectedGroup,
    loading,
    error,
    searchQuery,
    fetchGroups,
    createGroup,
    updateGroup,
    deleteGroup,
    searchGroups,
    setSelectedGroup,
    setSearchQuery,
    clearError,
  } = useDomainGroupsStore();

  // Local state
  const [modalVisible, setModalVisible] = useState(false);
  const [editingGroup, setEditingGroup] = useState<DomainGroup | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState("groups");

  // Load initial data
  useEffect(() => {
    fetchGroups();
  }, []);

  // Handle search
  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      searchGroups(value);
    } else {
      fetchGroups();
    }
  };

  // Handle create/edit group
  const handleCreateGroup = () => {
    setEditingGroup(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditGroup = (group: DomainGroup) => {
    setEditingGroup(group);
    form.setFieldsValue({
      name: group.name,
      description: group.description,
      parentId: group.parentId,
      isActive: group.isActive,
    });
    setModalVisible(true);
  };

  const handleSaveGroup = async (values: any) => {
    try {
      if (editingGroup) {
        const updateData: DomainGroupUpdate = {
          name: values.name,
          description: values.description,
          parentId: values.parentId,
          isActive: values.isActive,
        };
        await updateGroup(editingGroup.id, updateData);
        message.success(t("domain_groups.group_updated"));
      } else {
        const createData: DomainGroupCreate = {
          name: values.name,
          description: values.description,
          parentId: values.parentId,
        };
        await createGroup(createData);
        message.success(t("domain_groups.group_created"));
      }
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error(t("domain_groups.save_error"));
    }
  };

  // Handle delete group
  const handleDeleteGroup = async (groupId: string) => {
    try {
      await deleteGroup(groupId);
      message.success(t("domain_groups.group_deleted"));
    } catch (error) {
      message.error(t("domain_groups.delete_error"));
    }
  };

  // Handle view users
  const handleViewUsers = (groupId: string) => {
    setSelectedGroup(groups.find((g) => g.id === groupId) || null);
    setActiveTab("users");
  };

  // Handle manage permissions
  const handleManagePermissions = (groupId: string) => {
    setSelectedGroup(groups.find((g) => g.id === groupId) || null);
    setActiveTab("permissions");
  };

  // Handle export
  const handleExport = async (groupId: string) => {
    try {
      // This would be implemented in the service
      message.success(t("domain_groups.export_success"));
    } catch (error) {
      message.error(t("domain_groups.export_error"));
    }
  };

  // Handle assign users
  const handleAssignUsers = (groupId: string) => {
    setSelectedGroup(groups.find((g) => g.id === groupId) || null);
    setActiveTab("users");
  };

  // Refresh data
  const handleRefresh = () => {
    fetchGroups();
    message.info(t("domain_groups.data_refreshed"));
  };

  // Calculate statistics
  const totalGroups = groups.length;
  const activeGroups = groups.filter((g) => g.isActive).length;
  const totalUsers = groups.reduce((sum, group) => sum + group.userCount, 0);
  const rootGroups = groups.filter((g) => g.level === 0).length;

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <Row
        justify="space-between"
        align="middle"
        style={{ marginBottom: "24px" }}
      >
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <TeamOutlined style={{ marginRight: "8px" }} />
            {t("domain_groups.title")}
          </Title>
          <Text type="secondary">{t("domain_groups.description")}</Text>
        </Col>
        <Col>
          <Space>
            <Tooltip title={t("domain_groups.refresh_data")}>
              <ModernButton
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loading}
              >
                {t("domain_groups.refresh")}
              </ModernButton>
            </Tooltip>
            <Tooltip title={t("domain_groups.create_group")}>
              <ModernButton
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreateGroup}
              >
                {t("domain_groups.create_group")}
              </ModernButton>
            </Tooltip>
          </Space>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Alert
          message={t("domain_groups.error")}
          description={error}
          type="error"
          showIcon
          closable
          onClose={clearError}
          style={{ marginBottom: "16px" }}
        />
      )}

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: "24px" }}>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("domain_groups.total_groups")}
              value={totalGroups}
              prefix={<TeamOutlined />}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("domain_groups.active_groups")}
              value={activeGroups}
              prefix={<TeamOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("domain_groups.total_users")}
              value={totalUsers}
              prefix={<UserOutlined />}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("domain_groups.root_groups")}
              value={rootGroups}
              prefix={<TeamOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </ModernCard>
        </Col>
      </Row>

      {/* Search */}
      <ModernCard style={{ marginBottom: "24px" }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={16}>
            <ModernInput
              placeholder={t("domain_groups.search_placeholder")}
              prefix={<SearchOutlined />}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={24} sm={8}>
            <Space>
              <Text type="secondary">
                {t("domain_groups.showing")} {groups.length}{" "}
                {t("domain_groups.groups")}
              </Text>
            </Space>
          </Col>
        </Row>
      </ModernCard>

      {/* Main Content */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
        <TabPane
          tab={
            <span>
              <TeamOutlined />
              {t("domain_groups.groups")}
            </span>
          }
          key="groups"
        >
          <Spin spinning={loading}>
            <DomainGroupList
              groups={groups}
              loading={loading}
              onEdit={handleEditGroup}
              onDelete={handleDeleteGroup}
              onViewUsers={handleViewUsers}
              onManagePermissions={handleManagePermissions}
              onExport={handleExport}
              onAssignUsers={handleAssignUsers}
            />
          </Spin>
        </TabPane>

        <TabPane
          tab={
            <span>
              <UserOutlined />
              {t("domain_groups.users")}
            </span>
          }
          key="users"
        >
          {selectedGroup ? (
            <div>
              <Title level={4}>
                {t("domain_groups.users_in_group")}: {selectedGroup.name}
              </Title>
              <Text type="secondary">
                {t("domain_groups.user_management_coming_soon")}
              </Text>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "40px" }}>
              <Text type="secondary">
                {t("domain_groups.select_group_to_view_users")}
              </Text>
            </div>
          )}
        </TabPane>

        <TabPane
          tab={
            <span>
              <LockOutlined />
              {t("domain_groups.permissions")}
            </span>
          }
          key="permissions"
        >
          {selectedGroup ? (
            <div>
              <Title level={4}>
                {t("domain_groups.permissions_for_group")}: {selectedGroup.name}
              </Title>
              <Text type="secondary">
                {t("domain_groups.permission_management_coming_soon")}
              </Text>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "40px" }}>
              <Text type="secondary">
                {t("domain_groups.select_group_to_manage_permissions")}
              </Text>
            </div>
          )}
        </TabPane>
      </Tabs>

      {/* Create/Edit Group Modal */}
      <Modal
        title={
          editingGroup
            ? t("domain_groups.edit_group")
            : t("domain_groups.create_group")
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveGroup}
          initialValues={{
            isActive: true,
          }}
        >
          <Form.Item
            name="name"
            label={t("domain_groups.name")}
            rules={[
              { required: true, message: t("domain_groups.name_required") },
              { min: 2, message: t("domain_groups.name_min_length") },
            ]}
          >
            <ModernInput placeholder={t("domain_groups.enter_group_name")} />
          </Form.Item>

          <Form.Item name="description" label={t("domain_groups.description")}>
            <ModernInput.TextArea
              placeholder={t("domain_groups.enter_group_description")}
              rows={3}
            />
          </Form.Item>

          <Form.Item name="parentId" label={t("domain_groups.parent_group")}>
            <ModernSelect
              placeholder={t("domain_groups.select_parent_group")}
              allowClear
            >
              {groups.map((group) => (
                <Option key={group.id} value={group.id}>
                  {group.name}
                </Option>
              ))}
            </ModernSelect>
          </Form.Item>

          <Form.Item
            name="isActive"
            label={t("domain_groups.status")}
            valuePropName="checked"
          >
            <Switch
              checkedChildren={t("domain_groups.active")}
              unCheckedChildren={t("domain_groups.inactive")}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {editingGroup
                  ? t("domain_groups.update")
                  : t("domain_groups.create")}
              </ModernButton>
              <ModernButton onClick={() => setModalVisible(false)}>
                {t("domain_groups.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DomainGroups;
