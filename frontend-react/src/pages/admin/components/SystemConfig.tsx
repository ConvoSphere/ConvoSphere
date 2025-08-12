import React from "react";
import {
  Card,
  Switch,
  InputNumber,
  Select,
  Space,
  Button,
  Form,
  Row,
  Col,
  Divider,
  message,
} from "antd";
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useSystemConfig } from "../hooks/useSystemConfig";
import { SystemConfigFormData } from "../types/admin.types";
import ModernCard from "../../../components/ModernCard";
import ModernButton from "../../../components/ModernButton";

const { Option } = Select;

const SystemConfig: React.FC = () => {
  const { t } = useTranslation();
  const {
    systemConfig,
    loading,
    configModalVisible,
    handleConfigChange,
    handleConfigSave,
    openConfigModal,
    closeConfigModal,
  } = useSystemConfig();

  const [form] = Form.useForm();

  const handleFormSubmit = async (values: SystemConfigFormData) => {
    await handleConfigSave(values);
  };

  const handleSwitchChange = (key: keyof SystemConfig, checked: boolean) => {
    handleConfigChange(key, checked);
  };

  const handleNumberChange = (key: keyof SystemConfig, value: number) => {
    handleConfigChange(key, value);
  };

  const handleSelectChange = (key: keyof SystemConfig, value: string) => {
    handleConfigChange(key, value);
  };

  if (!systemConfig) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <ModernCard
        title={t("admin.config.title")}
        extra={
          <Space>
            <ModernButton
              icon={<ReloadOutlined />}
              onClick={() => window.location.reload()}
            >
              {t("common.refresh")}
            </ModernButton>
            <ModernButton
              type="primary"
              icon={<SaveOutlined />}
              onClick={openConfigModal}
            >
              {t("common.save")}
            </ModernButton>
          </Space>
        }
      >
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={12}>
            <Card title={t("admin.config.general")} size="small">
              <Space direction="vertical" style={{ width: "100%" }}>
                <div>
                  <label>{t("admin.config.default_language")}</label>
                  <Select
                    value={systemConfig.defaultLanguage}
                    style={{ width: "100%", marginTop: 8 }}
                    onChange={(value) =>
                      handleSelectChange("defaultLanguage", value)
                    }
                  >
                    <Option value="en">English</Option>
                    <Option value="de">Deutsch</Option>
                    <Option value="fr">Français</Option>
                    <Option value="es">Español</Option>
                  </Select>
                </div>

                <div>
                  <label>{t("admin.config.max_file_size")} (MB)</label>
                  <InputNumber
                    value={systemConfig.maxFileSize / (1024 * 1024)}
                    style={{ width: "100%", marginTop: 8 }}
                    min={1}
                    max={100}
                    onChange={(value) =>
                      handleNumberChange(
                        "maxFileSize",
                        (value || 10) * 1024 * 1024,
                      )
                    }
                  />
                </div>

                <div>
                  <label>{t("admin.config.max_users")}</label>
                  <InputNumber
                    value={systemConfig.maxUsers}
                    style={{ width: "100%", marginTop: 8 }}
                    min={1}
                    max={10000}
                    onChange={(value) =>
                      handleNumberChange("maxUsers", value || 1000)
                    }
                  />
                </div>
              </Space>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title={t("admin.config.features")} size="small">
              <Space direction="vertical" style={{ width: "100%" }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>{t("admin.config.enable_registration")}</span>
                  <Switch
                    checked={systemConfig.enableRegistration}
                    onChange={(checked) =>
                      handleSwitchChange("enableRegistration", checked)
                    }
                  />
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>{t("admin.config.enable_email_verification")}</span>
                  <Switch
                    checked={systemConfig.enableEmailVerification}
                    onChange={(checked) =>
                      handleSwitchChange("enableEmailVerification", checked)
                    }
                  />
                </div>

                <Divider />

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>{t("admin.config.maintenance_mode")}</span>
                  <Switch
                    checked={systemConfig.maintenanceMode}
                    onChange={(checked) =>
                      handleSwitchChange("maintenanceMode", checked)
                    }
                  />
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>{t("admin.config.debug_mode")}</span>
                  <Switch
                    checked={systemConfig.debugMode}
                    onChange={(checked) =>
                      handleSwitchChange("debugMode", checked)
                    }
                  />
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </ModernCard>

      <Modal
        title={t("admin.config.save_configuration")}
        open={configModalVisible}
        onCancel={closeConfigModal}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFormSubmit}
          initialValues={systemConfig}
        >
          <Form.Item
            name="defaultLanguage"
            label={t("admin.config.default_language")}
            rules={[
              { required: true, message: t("admin.config.language_required") },
            ]}
          >
            <Select>
              <Option value="en">English</Option>
              <Option value="de">Deutsch</Option>
              <Option value="fr">Français</Option>
              <Option value="es">Español</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="maxFileSize"
            label={t("admin.config.max_file_size")}
            rules={[
              { required: true, message: t("admin.config.file_size_required") },
            ]}
          >
            <InputNumber
              min={1}
              max={100}
              addonAfter="MB"
              style={{ width: "100%" }}
            />
          </Form.Item>

          <Form.Item
            name="maxUsers"
            label={t("admin.config.max_users")}
            rules={[
              { required: true, message: t("admin.config.max_users_required") },
            ]}
          >
            <InputNumber min={1} max={10000} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="enableRegistration"
            valuePropName="checked"
            label={t("admin.config.enable_registration")}
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="enableEmailVerification"
            valuePropName="checked"
            label={t("admin.config.enable_email_verification")}
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="maintenanceMode"
            valuePropName="checked"
            label={t("admin.config.maintenance_mode")}
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="debugMode"
            valuePropName="checked"
            label={t("admin.config.debug_mode")}
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <ModernButton type="primary" htmlType="submit">
                {t("common.save")}
              </ModernButton>
              <Button onClick={closeConfigModal}>{t("common.cancel")}</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SystemConfig;
