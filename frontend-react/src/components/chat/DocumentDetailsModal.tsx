import React from "react";
import { Modal, Typography, Divider, Space, Tag } from "antd";
import ModernButton from "../ModernButton";
import type { Document } from "../../services/knowledge";
import {
  formatDate,
  formatFileSize,
  formatDocumentType,
} from "../../utils/formatters";

const { Title, Text } = Typography;

interface DocumentDetailsModalProps {
  open: boolean;
  document: Document | null;
  onClose: () => void;
  onUse: (document: Document) => void;
}

const DocumentDetailsModal: React.FC<DocumentDetailsModalProps> = ({
  open,
  document,
  onClose,
  onUse,
}) => (
  <Modal
    title="Document Details"
    open={open}
    onCancel={onClose}
    footer={[
      <ModernButton key="close" variant="secondary" onClick={onClose}>
        Close
      </ModernButton>,
      <ModernButton
        key="use"
        variant="primary"
        onClick={() => document && onUse(document)}
        disabled={!document}
      >
        Use in Chat
      </ModernButton>,
    ]}
    width={600}
  >
    {document && (
      <div>
        <Title level={4}>{document.title}</Title>
        <Text type="secondary">{document.file_name}</Text>
        <Divider />
        <Space direction="vertical" style={{ width: "100%" }}>
          <div>
            <Text strong>Type:</Text>{" "}
            {formatDocumentType(document.document_type || "Unknown")}
          </div>
          {document.author && (
            <div>
              <Text strong>Author:</Text> {document.author}
            </div>
          )}
          {document.language && (
            <div>
              <Text strong>Language:</Text> {document.language}
            </div>
          )}
          {document.year && (
            <div>
              <Text strong>Year:</Text> {document.year}
            </div>
          )}
          {document.page_count && (
            <div>
              <Text strong>Pages:</Text> {document.page_count}
            </div>
          )}
          {document.description && (
            <div>
              <Text strong>Description:</Text>
              <p>{document.description}</p>
            </div>
          )}
          {document.tags && document.tags.length > 0 && (
            <div>
              <Text strong>Tags:</Text>
              <div style={{ marginTop: 8 }}>
                {document.tags.map((tag) => (
                  <Tag key={tag.id} color="blue">
                    {tag.name}
                  </Tag>
                ))}
              </div>
            </div>
          )}
          {document.keywords && document.keywords.length > 0 && (
            <div>
              <Text strong>Keywords:</Text>
              <div style={{ marginTop: 8 }}>
                {document.keywords.map((keyword, index) => (
                  <Tag key={index}>{keyword}</Tag>
                ))}
              </div>
            </div>
          )}
          <div>
            <Text strong>File Size:</Text> {formatFileSize(document.file_size)}
          </div>
          <div>
            <Text strong>Created:</Text> {formatDate(document.created_at)}
          </div>
        </Space>
      </div>
    )}
  </Modal>
);

export default DocumentDetailsModal;
