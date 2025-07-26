import React from "react";
import {
  Table,
  Space,
  Button,
  Tooltip,
  Popconfirm,
  Tag,
  Typography,
  Select,
} from "antd";
import { EditOutlined, DeleteOutlined, TagOutlined } from "@ant-design/icons";
import { Tag as TagType } from "../../services/knowledge";

const { Text } = Typography;
const { Option } = Select;

interface TagTableProps {
  tags: TagType[];
  loading: boolean;
  mode: "management" | "selection" | "view";
  onTagSelect?: (tag: TagType) => void;
  onEditTag?: (tag: TagType) => void;
  onDeleteTag?: (tagId: string) => void;
}

const TagTable: React.FC<TagTableProps> = ({
  tags,
  loading,
  mode,
  onTagSelect,
  onEditTag,
  onDeleteTag,
}) => {
  const columns = [
    {
      title: "Tag",
      key: "tag",
      render: (record: TagType) => (
        <Space>
          <Tag color={record.color || "#1890ff"} icon={<TagOutlined />}>
            {record.name}
          </Tag>
          {record.is_system && <Tag color="red">System</Tag>}
        </Space>
      ),
      sorter: (a: TagType, b: TagType) => a.name.localeCompare(b.name),
    },
    {
      title: "Description",
      dataIndex: "description",
      key: "description",
      render: (description: string) =>
        description || <Text type="secondary">-</Text>,
      ellipsis: true,
    },
    {
      title: "Usage Count",
      dataIndex: "usage_count",
      key: "usage_count",
      render: (count: number) => <Text strong>{count.toLocaleString()}</Text>,
      sorter: (a: TagType, b: TagType) => a.usage_count - b.usage_count,
    },
    {
      title: "Type",
      key: "type",
      render: (record: TagType) => (
        <Tag color={record.is_system ? "red" : "green"}>
          {record.is_system ? "System" : "User"}
        </Tag>
      ),
      filters: [
        { text: "System", value: "system" },
        { text: "User", value: "user" },
      ],
      onFilter: (value: string, record: TagType) =>
        (value === "system" && record.is_system) ||
        (value === "user" && !record.is_system),
    },
    {
      title: "Created",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a: TagType, b: TagType) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: "Actions",
      key: "actions",
      render: (record: TagType) => (
        <Space>
          {mode === "selection" && (
            <Button
              type="text"
              size="small"
              onClick={() => onTagSelect?.(record)}
            >
              Select
            </Button>
          )}
          {mode === "management" && (
            <>
              <Tooltip title="Edit Tag">
                <Button
                  type="text"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => onEditTag?.(record)}
                  disabled={record.is_system}
                />
              </Tooltip>
              <Popconfirm
                title="Are you sure you want to delete this tag?"
                onConfirm={() => onDeleteTag?.(record.id)}
                okText="Yes"
                cancelText="No"
                disabled={record.is_system || record.usage_count > 0}
              >
                <Tooltip
                  title={
                    record.usage_count > 0
                      ? "Cannot delete tag in use"
                      : "Delete Tag"
                  }
                >
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    disabled={record.is_system || record.usage_count > 0}
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={tags}
      loading={loading}
      rowKey="id"
      pagination={{
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} tags`,
        pageSizeOptions: ["10", "20", "50"],
        defaultPageSize: 20,
      }}
    />
  );
};

export default TagTable;
