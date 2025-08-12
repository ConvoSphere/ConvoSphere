import React, { useEffect, useState } from "react";
import {
  Typography,
  Space,
  Row,
  Col,
  Tabs,
  Modal,
  Form,
  Select,
  DatePicker,
  Switch,
  Input,
  message,
  Alert,
  Card,
  Statistic,
  Progress,
  List,
  Avatar,
  Tag,
  Tooltip,
  Popconfirm,
} from "antd";
import {
  DownloadOutlined,
  UploadOutlined,
  SettingOutlined,
  HistoryOutlined,
  ScheduleOutlined,
  CloudUploadOutlined,
  CloudDownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  PlusOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  SettingOutlined as SettingIcon,
  UserOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useExportStore } from "../store/exportStore";
import { RangePickerProps } from "antd/es/date-picker";
import dayjs from "dayjs";

import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";
import ExportJobList from "../components/export/ExportJobList";
import type { ExportOptions, BackupConfig } from "../services/export";

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const ExportBackup: React.FC = () => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();
  const user = useAuthStore((s) => s.user);
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");

  const {
    exportJobs,
    backupJobs,
    exportTemplates,
    scheduledExports,
    backupConfig,
    loading,
    error,
    createExportJob,
    getExportJobStatus,
    listExportJobs,
    cancelExportJob,
    downloadExport,
    bulkExport,
    getExportTemplates,
    saveExportTemplate,
    scheduleExport,
    listScheduledExports,
    updateScheduledExport,
    deleteScheduledExport,
    createBackup,
    getBackupStatus,
    listBackups,
    restoreBackup,
    deleteBackup,
    downloadBackup,
    getBackupConfig,
    updateBackupConfig,
    testBackupConfig,
    getExportStats,
    getBackupStats,
    clearError,
  } = useExportStore();

  // Local state
  const [activeTab, setActiveTab] = useState("export");
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [backupModalVisible, setBackupModalVisible] = useState(false);
  const [templateModalVisible, setTemplateModalVisible] = useState(false);
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [selectedExportType, setSelectedExportType] =
    useState<string>("conversations");
  const [exportForm] = Form.useForm();
  const [backupForm] = Form.useForm();
  const [templateForm] = Form.useForm();
  const [scheduleForm] = Form.useForm();
  const [configForm] = Form.useForm();

  // Load data on component mount
  useEffect(() => {
    if (!isAdmin) return;

    const loadData = async () => {
      await Promise.all([
        listExportJobs(),
        listBackups(),
        getExportTemplates(),
        listScheduledExports(),
        getBackupConfig(),
      ]);
    };

    loadData();
  }, [isAdmin]);

  // Handle export creation
  const handleCreateExport = async (values: any) => {
    try {
      const exportOptions: ExportOptions = {
        format: values.format,
        dateRange: values.dateRange
          ? {
              start: values.dateRange[0].toISOString(),
              end: values.dateRange[1].toISOString(),
            }
          : undefined,
        includeMetadata: values.includeMetadata,
        compression: values.compression,
        customFields: values.customFields,
      };

      await createExportJob(selectedExportType, exportOptions);
      message.success(t("export.job_created"));
      setExportModalVisible(false);
      exportForm.resetFields();
    } catch (error) {
      message.error(t("export.job_creation_failed"));
    }
  };

  // Handle backup creation
  const handleCreateBackup = async (values: any) => {
    try {
      const backupConfig: Partial<BackupConfig> = {
        includeFiles: values.includeFiles,
        includeDatabase: values.includeDatabase,
        includeConfig: values.includeConfig,
        backupLocation: values.backupLocation,
        credentials: values.credentials,
      };

      await createBackup(backupConfig);
      message.success(t("backup.job_created"));
      setBackupModalVisible(false);
      backupForm.resetFields();
    } catch (error) {
      message.error(t("backup.job_creation_failed"));
    }
  };

  // Handle template save
  const handleSaveTemplate = async (values: any) => {
    try {
      await saveExportTemplate({
        name: values.name,
        description: values.description,
        type: selectedExportType,
        options: exportForm.getFieldsValue(),
      });
      message.success(t("export.template_saved"));
      setTemplateModalVisible(false);
      templateForm.resetFields();
    } catch (error) {
      message.error(t("export.template_save_failed"));
    }
  };

  // Handle schedule creation
  const handleCreateSchedule = async (values: any) => {
    try {
      await scheduleExport({
        type: selectedExportType,
        options: exportForm.getFieldsValue(),
        cronExpression: values.cronExpression,
        enabled: values.enabled,
      });
      message.success(t("export.schedule_created"));
      setScheduleModalVisible(false);
      scheduleForm.resetFields();
    } catch (error) {
      message.error(t("export.schedule_creation_failed"));
    }
  };

  // Handle backup restore
  const handleRestoreBackup = async (backupId: string) => {
    try {
      await restoreBackup(backupId, {
        restoreFiles: true,
        restoreDatabase: true,
        restoreConfig: true,
      });
      message.success(t("backup.restore_started"));
    } catch (error) {
      message.error(t("backup.restore_failed"));
    }
  };

  // Handle config update
  const handleUpdateConfig = async (values: any) => {
    try {
      await updateBackupConfig({
        autoBackup: values.autoBackup,
        backupInterval: values.backupInterval,
        retentionDays: values.retentionDays,
        includeFiles: values.includeFiles,
        includeDatabase: values.includeDatabase,
        includeConfig: values.includeConfig,
        backupLocation: values.backupLocation,
        credentials: values.credentials,
      });
      message.success(t("backup.config_updated"));
      setConfigModalVisible(false);
      configForm.resetFields();
    } catch (error) {
      message.error(t("backup.config_update_failed"));
    }
  };

  // Handle download
  const handleDownload = async (jobId: string) => {
    try {
      await downloadExport(jobId);
      message.success(t("export.download_started"));
    } catch (error) {
      message.error(t("export.download_failed"));
    }
  };

  // Handle cancel
  const handleCancel = async (jobId: string) => {
    try {
      await cancelExportJob(jobId);
      message.success(t("export.job_cancelled"));
    } catch (error) {
      message.error(t("export.job_cancel_failed"));
    }
  };

  // Handle refresh
  const handleRefresh = async (jobId: string) => {
    try {
      await getExportJobStatus(jobId);
    } catch (error) {
      message.error(t("export.refresh_failed"));
    }
  };

  if (!isAdmin) {
    return (
      <div style={{ padding: "24px", textAlign: "center" }}>
        <Alert type="error" message={t("errors.forbidden")} showIcon />
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <Row
        justify="space-between"
        align="middle"
        style={{ marginBottom: "24px" }}
      >
        <Col>
          <Title level={2} style={{ margin: 0, color: colors.colorTextBase }}>
            <DownloadOutlined style={{ marginRight: "8px" }} />
            {t("export_backup.title")}
          </Title>
          <Text type="secondary" style={{ color: colors.colorTextSecondary }}>
            {t("export_backup.subtitle")}
          </Text>
        </Col>
        <Col>
          <Space>
            <ModernButton
              icon={<ReloadOutlined />}
              onClick={() => {
                listExportJobs();
                listBackups();
              }}
              loading={loading}
            >
              {t("common.refresh")}
            </ModernButton>
          </Space>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Alert
          message={t("export_backup.error")}
          description={error}
          type="error"
          showIcon
          closable
          onClose={clearError}
          style={{ marginBottom: "16px" }}
        />
      )}

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: "24px" }}>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("export_backup.total_exports")}
              value={exportJobs.length}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: colors.colorPrimary }}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("export_backup.completed_exports")}
              value={exportJobs.filter((j) => j.status === "completed").length}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: colors.colorSuccess }}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("export_backup.total_backups")}
              value={backupJobs.length}
              prefix={<CloudUploadOutlined />}
              valueStyle={{ color: colors.colorWarning }}
            />
          </ModernCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <ModernCard>
            <Statistic
              title={t("export_backup.scheduled_exports")}
              value={scheduledExports.length}
              prefix={<ScheduleOutlined />}
              valueStyle={{ color: colors.colorInfo }}
            />
          </ModernCard>
        </Col>
      </Row>

      {/* Main Content Tabs */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
        {/* Export Tab */}
        <Tabs.TabPane
          tab={
            <span>
              <DownloadOutlined />
              {t("export_backup.export")}
            </span>
          }
          key="export"
        >
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            {/* Export Actions */}
            <ModernCard>
              <Row gutter={[16, 16]} align="middle">
                <Col xs={24} sm={12} md={6}>
                  <ModernSelect
                    value={selectedExportType}
                    onChange={setSelectedExportType}
                    style={{ width: "100%" }}
                  >
                    <Option value="conversations">
                      <FileTextOutlined /> {t("export.types.conversations")}
                    </Option>
                    <Option value="knowledge">
                      <DatabaseOutlined /> {t("export.types.knowledge")}
                    </Option>
                    <Option value="analytics">
                      <BarChartOutlined /> {t("export.types.analytics")}
                    </Option>
                    <Option value="system">
                      <SettingIcon /> {t("export.types.system")}
                    </Option>
                    <Option value="users">
                      <UserOutlined /> {t("export.types.users")}
                    </Option>
                    <Option value="assistants">
                      <RobotOutlined /> {t("export.types.assistants")}
                    </Option>
                  </ModernSelect>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <ModernButton
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setExportModalVisible(true)}
                  >
                    {t("export.create_job")}
                  </ModernButton>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <ModernButton
                    icon={<HistoryOutlined />}
                    onClick={() => setTemplateModalVisible(true)}
                  >
                    {t("export.save_template")}
                  </ModernButton>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <ModernButton
                    icon={<ScheduleOutlined />}
                    onClick={() => setScheduleModalVisible(true)}
                  >
                    {t("export.schedule")}
                  </ModernButton>
                </Col>
              </Row>
            </ModernCard>

            {/* Export Jobs List */}
            <ExportJobList
              jobs={exportJobs}
              loading={loading}
              onDownload={handleDownload}
              onCancel={handleCancel}
              onRefresh={handleRefresh}
            />
          </Space>
        </Tabs.TabPane>

        {/* Backup Tab */}
        <Tabs.TabPane
          tab={
            <span>
              <CloudUploadOutlined />
              {t("export_backup.backup")}
            </span>
          }
          key="backup"
        >
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            {/* Backup Actions */}
            <ModernCard>
              <Row gutter={[16, 16]} align="middle">
                <Col xs={24} sm={12} md={8}>
                  <ModernButton
                    type="primary"
                    icon={<CloudUploadOutlined />}
                    onClick={() => setBackupModalVisible(true)}
                  >
                    {t("backup.create")}
                  </ModernButton>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <ModernButton
                    icon={<SettingOutlined />}
                    onClick={() => setConfigModalVisible(true)}
                  >
                    {t("backup.configuration")}
                  </ModernButton>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    {t("backup.auto_backup")}:{" "}
                    {backupConfig?.autoBackup
                      ? t("common.enabled")
                      : t("common.disabled")}
                  </Text>
                </Col>
              </Row>
            </ModernCard>

            {/* Backup Jobs List */}
            <ModernCard title={t("backup.jobs")}>
              <List
                dataSource={backupJobs}
                loading={loading}
                renderItem={(backup) => (
                  <List.Item
                    actions={[
                      backup.status === "completed" && (
                        <Tooltip title={t("backup.download")}>
                          <ModernButton
                            variant="primary"
                            icon={<CloudDownloadOutlined />}
                            size="sm"
                            onClick={() => downloadBackup(backup.id)}
                          >
                            {t("backup.download")}
                          </ModernButton>
                        </Tooltip>
                      ),
                      backup.status === "completed" && (
                        <Tooltip title={t("backup.restore")}>
                          <Popconfirm
                            title={t("backup.restore_confirm")}
                            onConfirm={() => handleRestoreBackup(backup.id)}
                            okText={t("common.yes")}
                            cancelText={t("common.no")}
                          >
                            <ModernButton icon={<UploadOutlined />} size="sm">
                              {t("backup.restore")}
                            </ModernButton>
                          </Popconfirm>
                        </Tooltip>
                      ),
                      <Tooltip title={t("backup.delete")}>
                        <Popconfirm
                          title={t("backup.delete_confirm")}
                          onConfirm={() => deleteBackup(backup.id)}
                          okText={t("common.yes")}
                          cancelText={t("common.no")}
                        >
                          <ModernButton
                            variant="error"
                            icon={<DeleteOutlined />}
                            size="sm"
                          >
                            {t("backup.delete")}
                          </ModernButton>
                        </Popconfirm>
                      </Tooltip>,
                    ].filter(Boolean)}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          icon={
                            backup.status === "completed" ? (
                              <CheckCircleOutlined />
                            ) : backup.status === "processing" ? (
                              <ClockCircleOutlined />
                            ) : (
                              <ExclamationCircleOutlined />
                            )
                          }
                          style={{
                            backgroundColor:
                              backup.status === "completed"
                                ? "#52c41a"
                                : backup.status === "processing"
                                  ? "#1890ff"
                                  : "#ff4d4f",
                          }}
                        />
                      }
                      title={
                        <Space>
                          <Text strong>
                            {t("backup.job")} #{backup.id}
                          </Text>
                          <Tag
                            color={
                              backup.status === "completed"
                                ? "success"
                                : backup.status === "processing"
                                  ? "processing"
                                  : "error"
                            }
                          >
                            {t(`backup.status.${backup.status}`)}
                          </Tag>
                          <Tag color="blue">{backup.type}</Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small">
                          <Text type="secondary">
                            {t("backup.created")}:{" "}
                            {new Date(backup.createdAt).toLocaleString()}
                          </Text>
                          {backup.completedAt && (
                            <Text type="secondary">
                              {t("backup.completed")}:{" "}
                              {new Date(backup.completedAt).toLocaleString()}
                            </Text>
                          )}
                          {backup.fileSize && (
                            <Text type="secondary">
                              {t("backup.file_size")}:{" "}
                              {(backup.fileSize / 1024 / 1024).toFixed(2)} MB
                            </Text>
                          )}
                          {backup.status === "processing" && (
                            <Progress percent={backup.progress} size="small" />
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </ModernCard>
          </Space>
        </Tabs.TabPane>
      </Tabs>

      {/* Export Modal */}
      <Modal
        title={t("export.create_job")}
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={exportForm} layout="vertical" onFinish={handleCreateExport}>
          <Form.Item
            name="format"
            label={t("export.format")}
            rules={[{ required: true, message: t("export.format_required") }]}
          >
            <ModernSelect>
              <Option value="csv">CSV</Option>
              <Option value="json">JSON</Option>
              <Option value="xlsx">Excel (XLSX)</Option>
              <Option value="pdf">PDF</Option>
            </ModernSelect>
          </Form.Item>

          <Form.Item name="dateRange" label={t("export.date_range")}>
            <RangePicker style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="includeMetadata"
            label={t("export.include_metadata")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="compression"
            label={t("export.compression")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {t("export.create")}
              </ModernButton>
              <ModernButton onClick={() => setExportModalVisible(false)}>
                {t("common.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Backup Modal */}
      <Modal
        title={t("backup.create")}
        open={backupModalVisible}
        onCancel={() => setBackupModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={backupForm} layout="vertical" onFinish={handleCreateBackup}>
          <Form.Item
            name="includeFiles"
            label={t("backup.include_files")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="includeDatabase"
            label={t("backup.include_database")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="includeConfig"
            label={t("backup.include_config")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="backupLocation"
            label={t("backup.location")}
            rules={[{ required: true, message: t("backup.location_required") }]}
          >
            <ModernSelect>
              <Option value="local">{t("backup.location_local")}</Option>
              <Option value="s3">Amazon S3</Option>
              <Option value="gcs">Google Cloud Storage</Option>
            </ModernSelect>
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {t("backup.create")}
              </ModernButton>
              <ModernButton onClick={() => setBackupModalVisible(false)}>
                {t("common.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Template Modal */}
      <Modal
        title={t("export.save_template")}
        open={templateModalVisible}
        onCancel={() => setTemplateModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={templateForm}
          layout="vertical"
          onFinish={handleSaveTemplate}
        >
          <Form.Item
            name="name"
            label={t("export.template_name")}
            rules={[
              { required: true, message: t("export.template_name_required") },
            ]}
          >
            <ModernInput />
          </Form.Item>

          <Form.Item
            name="description"
            label={t("export.template_description")}
          >
            <ModernInput.TextArea rows={3} />
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {t("export.save")}
              </ModernButton>
              <ModernButton onClick={() => setTemplateModalVisible(false)}>
                {t("common.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Schedule Modal */}
      <Modal
        title={t("export.schedule")}
        open={scheduleModalVisible}
        onCancel={() => setScheduleModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={scheduleForm}
          layout="vertical"
          onFinish={handleCreateSchedule}
        >
          <Form.Item
            name="cronExpression"
            label={t("export.cron_expression")}
            rules={[
              { required: true, message: t("export.cron_expression_required") },
            ]}
          >
            <ModernInput placeholder="0 0 * * *" />
          </Form.Item>

          <Form.Item
            name="enabled"
            label={t("export.enabled")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {t("export.schedule")}
              </ModernButton>
              <ModernButton onClick={() => setScheduleModalVisible(false)}>
                {t("common.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Config Modal */}
      <Modal
        title={t("backup.configuration")}
        open={configModalVisible}
        onCancel={() => setConfigModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={configForm}
          layout="vertical"
          onFinish={handleUpdateConfig}
          initialValues={backupConfig}
        >
          <Form.Item
            name="autoBackup"
            label={t("backup.auto_backup")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item name="backupInterval" label={t("backup.interval")}>
            <ModernSelect>
              <Option value="daily">{t("backup.interval_daily")}</Option>
              <Option value="weekly">{t("backup.interval_weekly")}</Option>
              <Option value="monthly">{t("backup.interval_monthly")}</Option>
            </ModernSelect>
          </Form.Item>

          <Form.Item name="retentionDays" label={t("backup.retention_days")}>
            <ModernInput type="number" min={1} />
          </Form.Item>

          <Form.Item
            name="includeFiles"
            label={t("backup.include_files")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="includeDatabase"
            label={t("backup.include_database")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="includeConfig"
            label={t("backup.include_config")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item name="backupLocation" label={t("backup.location")}>
            <ModernSelect>
              <Option value="local">{t("backup.location_local")}</Option>
              <Option value="s3">Amazon S3</Option>
              <Option value="gcs">Google Cloud Storage</Option>
            </ModernSelect>
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit" loading={loading}>
                {t("backup.save_config")}
              </ModernButton>
              <ModernButton onClick={() => setConfigModalVisible(false)}>
                {t("common.cancel")}
              </ModernButton>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ExportBackup;
