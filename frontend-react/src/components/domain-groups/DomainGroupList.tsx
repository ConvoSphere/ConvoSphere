import React from "react";
import {
  Table,
  Space,
  Tag,
  Avatar,
  Typography,
  Tooltip,
  Popconfirm,
  Badge,
} from "antd";
import ModernButton from "../ModernButton";
import {
  TeamOutlined,
  EditOutlined,
  DeleteOutlined,
  UserAddOutlined,
  SettingOutlined,
  EyeOutlined,
  ExportOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import type { DomainGroup } from "../../services/domainGroups";
import ModernButton from "../ModernButton";

const { Text } = Typography;

interface DomainGroupListProps {
  groups: DomainGroup[];
  loading?: boolean;
  onEdit: (group: DomainGroup) => void;
  onDelete: (groupId: string) => void;
  onViewUsers: (groupId: string) => void;
  onManagePermissions: (groupId: string) => void;
  onExport: (groupId: string) => void;
  onAssignUsers: (groupId: string) => void;
}

const DomainGroupList: React.FC<DomainGroupListProps> = ({
  groups,
  loading = false,
  onEdit,
  onDelete,
  onViewUsers,
  onManagePermissions,
  onExport,
  onAssignUsers,
}) => {
  const { t } = useTranslation();

  const getLevelIndent = (level: number) => {
    return level * 20;
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "success" : "default";
  };

  const getRoleIcon = (level: number) => {
    if (level === 0) return <TeamOutlined style={{ color: "#1890ff" }} />;
    if (level === 1) return <TeamOutlined style={{ color: "#52c41a" }} />;
    return <TeamOutlined style={{ color: "#faad14" }} />;
  };

  const columns = [
    {
      title: t("domain_groups.name"),
      dataIndex: "name",
      key: "name",
      render: (name: string, record: DomainGroup) => (
        <div style={{ paddingLeft: getLevelIndent(record.level) }}>
          <Space>
            {getRoleIcon(record.level)}
            <Text strong>{name}</Text>
            {record.level === 0 && (
              <Tag color="blue">{t("domain_groups.root")}</Tag>
            )}
          </Space>
        </div>
      ),
      sorter: (a: DomainGroup, b: DomainGroup) => a.name.localeCompare(b.name),
    },
    {
      title: t("domain_groups.description"),
      dataIndex: "description",
      key: "description",
      render: (description: string) => (
        <Text type="secondary" ellipsis={{ tooltip: description }}>
          {description || t("domain_groups.no_description")}
        </Text>
      ),
    },
    {
      title: t("domain_groups.path"),
      dataIndex: "path",
      key: "path",
      render: (path: string) => (
        <Text code style={{ fontSize: "12px" }}>
          {path}
        </Text>
      ),
    },
    {
      title: t("domain_groups.users"),
      dataIndex: "userCount",
      key: "userCount",
      render: (userCount: number) => (
        <Badge
          count={userCount}
          showZero
          style={{ backgroundColor: "#1890ff" }}
        >
          <Avatar size="small" icon={<TeamOutlined />} />
        </Badge>
      ),
      sorter: (a: DomainGroup, b: DomainGroup) => a.userCount - b.userCount,
    },
    {
      title: t("domain_groups.status"),
      dataIndex: "isActive",
      key: "isActive",
      render: (isActive: boolean) => (
        <Tag color={getStatusColor(isActive)}>
          {isActive ? t("domain_groups.active") : t("domain_groups.inactive")}
        </Tag>
      ),
      filters: [
        { text: t("domain_groups.active"), value: true },
        { text: t("domain_groups.inactive"), value: false },
      ],
      onFilter: (value: boolean, record: DomainGroup) =>
        record.isActive === value,
    },
    {
      title: t("domain_groups.created"),
      dataIndex: "createdAt",
      key: "createdAt",
      render: (createdAt: string) => (
        <Text type="secondary">{new Date(createdAt).toLocaleDateString()}</Text>
      ),
      sorter: (a: DomainGroup, b: DomainGroup) =>
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(),
    },
    {
      title: t("domain_groups.actions"),
      key: "actions",
      render: (_, record: DomainGroup) => (
        <Space size="small">
          <Tooltip title={t("domain_groups.view_users")}>
            <ModernButton
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onViewUsers(record.id)}
            />
          </Tooltip>

          <Tooltip title={t("domain_groups.assign_users")}>
            <ModernButton
              type="text"
              size="small"
              icon={<UserAddOutlined />}
              onClick={() => onAssignUsers(record.id)}
            />
          </Tooltip>

          <Tooltip title={t("domain_groups.manage_permissions")}>
            <ModernButton
              type="text"
              size="small"
              icon={<SettingOutlined />}
              onClick={() => onManagePermissions(record.id)}
            />
          </Tooltip>

          <Tooltip title={t("domain_groups.edit")}>
            <ModernButton
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => onEdit(record)}
            />
          </Tooltip>

          <Tooltip title={t("domain_groups.export")}>
            <ModernButton
              type="text"
              size="small"
              icon={<ExportOutlined />}
              onClick={() => onExport(record.id)}
            />
          </Tooltip>

          <Popconfirm
            title={t("domain_groups.delete_confirm_title")}
            description={t("domain_groups.delete_confirm_description")}
            onConfirm={() => onDelete(record.id)}
            okText={t("common.yes")}
            cancelText={t("common.no")}
            placement="left"
          >
            <Tooltip title={t("domain_groups.delete")}>
              <ModernButton
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={groups}
      rowKey="id"
      loading={loading}
      pagination={{
        pageSize: 20,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) =>
          `${t("domain_groups.showing")} ${range[0]}-${range[1]} ${t("domain_groups.of")} ${total} ${t("domain_groups.groups")}`,
      }}
      scroll={{ x: 1200 }}
      expandable={{
        rowExpandable: (record) => record.userCount > 0,
        expandedRowRender: (record) => (
          <div style={{ padding: "16px", backgroundColor: "#fafafa" }}>
            <Text type="secondary">
              {t("domain_groups.user_count_info", { count: record.userCount })}
            </Text>
          </div>
        ),
      }}
    />
  );
};

export default DomainGroupList;
