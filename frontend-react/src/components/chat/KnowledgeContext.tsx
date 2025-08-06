import React, { useState } from "react";
import { List, Typography, Tag, Input, message } from "antd";
import ModernButton from "../ModernButton";
import { useTranslation } from "react-i18next";
import { BookOutlined, SearchOutlined } from "@ant-design/icons";
import { useKnowledgeStore } from "../../store/knowledgeStore";
import type { Document } from "../../services/knowledge";
import { formatDocumentType } from "../../utils/formatters";

const { Title, Text } = Typography;

interface KnowledgeContextProps {
  onDocumentSelect?: (document: Document) => void;
  selectedDocuments?: Document[];
}

const KnowledgeContext: React.FC<KnowledgeContextProps> = ({
  onDocumentSelect,
  selectedDocuments = [],
}) => {
  const { t } = useTranslation();
  const { documents } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredDocuments = Array.isArray(documents)
    ? documents.filter((doc) => {
        const matchesSearch =
          !searchQuery ||
          doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          doc.description?.toLowerCase().includes(searchQuery.toLowerCase());

        return matchesSearch;
      })
    : [];

  const renderDocumentItem = (document: Document) => (
    <List.Item
      key={document.id}
      onClick={() => onDocumentSelect?.(document)}
      style={{ cursor: "pointer" }}
    >
      <List.Item.Meta
        avatar={<BookOutlined />}
        title={
          <div>
            <Text strong>{document.title}</Text>
            <div style={{ marginTop: "4px" }}>
              <Tag color="blue">
                {formatDocumentType(document.document_type || "Unknown")}
              </Tag>
              {document.language && (
                <Tag color="green">{document.language.toUpperCase()}</Tag>
              )}
              {document.page_count && (
                <Tag color="orange">{document.page_count} pages</Tag>
              )}
            </div>
          </div>
        }
        description={
          <div>
            <Text type="secondary">
              {document.description || "No description"}
            </Text>
            {document.tags && document.tags.length > 0 && (
              <div style={{ marginTop: "4px" }}>
                {document.tags.map((tag) => (
                  <Tag key={tag.id} color="purple">
                    {tag.name}
                  </Tag>
                ))}
              </div>
            )}
          </div>
        }
      />
    </List.Item>
  );

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "8px",
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            <BookOutlined /> {t("knowledge.context_title")}
          </Title>
        </div>
      </div>

      {/* Search */}
      <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
        <Input
          placeholder={t("knowledge.search_documents")}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          prefix={<SearchOutlined />}
          style={{ width: "100%" }}
        />
      </div>

      {/* Selected Documents */}
      {selectedDocuments.length > 0 && (
        <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "8px",
            }}
          >
            <Text strong style={{ fontSize: "12px" }}>
              {t("knowledge.selected_documents")} ({selectedDocuments.length})
            </Text>
            <ModernButton
              variant="ghost"
              size="sm"
              onClick={() => {
                // TODO: Implement clear all
                message.info("Clear all coming soon");
              }}
            >
              {t("common.clear_all")}
            </ModernButton>
          </div>
          <List
            size="small"
            dataSource={selectedDocuments}
            renderItem={(doc) => (
              <List.Item
                key={doc.id}
                style={{ padding: "4px 0" }}
                actions={[
                  <ModernButton
                    key="remove"
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: Implement remove
                      message.info("Remove coming soon");
                    }}
                  >
                    {t("common.remove")}
                  </ModernButton>,
                ]}
              >
                <List.Item.Meta
                  title={<Text style={{ fontSize: "12px" }}>{doc.title}</Text>}
                  description={
                    <Text type="secondary" style={{ fontSize: "10px" }}>
                      {doc.document_type}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      )}

      {/* Search Results */}
      <div style={{ flex: 1, overflow: "hidden" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "8px",
            padding: "16px 16px 0",
          }}
        >
          <Text strong style={{ fontSize: "12px" }}>
            {t("knowledge.available_documents")} ({filteredDocuments.length})
          </Text>
        </div>

        <div
          style={{
            height: "calc(100% - 30px)",
            overflowY: "auto",
            padding: "0 16px 16px",
          }}
        >
          {filteredDocuments.length === 0 ? (
            <div style={{ padding: "20px 0" }}>
              <Text type="secondary">{t("common.no_results")}</Text>
            </div>
          ) : (
            <List
              dataSource={filteredDocuments}
              renderItem={renderDocumentItem}
              size="small"
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeContext;
