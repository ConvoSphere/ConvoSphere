import React, { useState } from "react";
import { Row, Col, Typography } from "antd";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";

import ModernCard from "../../components/ModernCard";
import CreateToolModal from "../../components/tools/CreateToolModal";

// Import modular components
import ToolList from "./ToolList";
import ToolExecution from "./ToolExecution";
import ToolStats from "./ToolStats";

// Import custom hooks
import { useTools } from "./hooks/useTools";
import { useToolExecution } from "./hooks/useToolExecution";

const { Title, Text } = Typography;

const Tools: React.FC = () => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();

  // Local state for UI
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Custom hooks for data management
  const {
    tools,
    loading,
    error,
    loadTools,
    toggleToolActive,
    addTool,
  } = useTools();

  const {
    executions,
    running,
    selectedTool,
    visible,
    executeTool,
    openExecutionModal,
    closeExecutionModal,
    getExecutionStats,
  } = useToolExecution();

  // Get execution statistics
  const executionStats = getExecutionStats();

  // Event handlers
  const handleToolClick = (tool: any) => {
    openExecutionModal(tool);
  };

  const handleToggleActive = (tool: any) => {
    toggleToolActive(tool);
  };

  const handleAddTool = () => {
    setShowCreateModal(true);
  };

  const handleImportTools = () => {
    // TODO: Implement import functionality
    console.log("Import tools");
  };

  const handleExportTools = () => {
    // TODO: Implement export functionality
    console.log("Export tools");
  };

  const handleCategoryClick = (category: string) => {
    setActiveTab(category);
  };

  const handleCreateToolSuccess = () => {
    setShowCreateModal(false);
    loadTools(); // Reload tools after creation
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        {/* Header Section */}
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 24px",
                fontSize: "32px",
              }}
            >
              ⚡
            </div>
            <Title
              level={1}
              style={{ color: "#FFFFFF", marginBottom: 8, fontSize: "2.5rem" }}
            >
              {t("tools.title", "Tools")}
            </Title>
            <Text
              style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}
            >
              {t("tools.subtitle", "Verwalten und ausführen Sie Ihre Tools")}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Row gutter={[24, 24]}>
            {/* Main Content */}
            <Col xs={24} lg={16}>
              <ToolList
                tools={tools}
                loading={loading}
                searchQuery={searchQuery}
                activeTab={activeTab}
                onSearchChange={setSearchQuery}
                onTabChange={setActiveTab}
                onToolClick={handleToolClick}
                onToggleActive={handleToggleActive}
                onAddTool={handleAddTool}
              />

              <ToolExecution
                executions={executions}
                selectedTool={selectedTool}
                visible={visible}
                running={running}
                onClose={closeExecutionModal}
                onRunTool={executeTool}
                onToolSelect={openExecutionModal}
              />
            </Col>

            {/* Sidebar */}
            <Col xs={24} lg={8}>
              <ToolStats
                tools={tools}
                totalExecutions={executionStats.total}
                successRate={executionStats.successRate}
                onAddTool={handleAddTool}
                onImportTools={handleImportTools}
                onExportTools={handleExportTools}
                onRefresh={loadTools}
                onCategoryClick={handleCategoryClick}
              />
            </Col>
          </Row>
        </div>

        {/* Create Tool Modal */}
        <CreateToolModal
          visible={showCreateModal}
          onCancel={() => setShowCreateModal(false)}
          onSuccess={handleCreateToolSuccess}
        />
      </div>
    </div>
  );
};

export default Tools;