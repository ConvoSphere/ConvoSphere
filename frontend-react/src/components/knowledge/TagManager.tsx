import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Input, 
  Modal, 
  Form, 
  Space, 
  Tag, 
  Typography, 
  Popconfirm,
  Tooltip,
  Alert,
  Row,
  Col,
  Statistic,
  Select,
  ColorPicker,
  message
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SearchOutlined,
  TagOutlined,
  EyeOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { useKnowledgeStore, useTags } from '../../store/knowledgeStore';
import { Tag as TagType, Document } from '../../services/knowledge';
import { createTag, deleteTag, searchTags } from '../../services/knowledge';

const { Search } = Input;
const { Title, Text } = Typography;
const { Option } = Select;

interface TagManagerProps {
  onTagSelect?: (tag: TagType) => void;
  showCreateButton?: boolean;
  showStatistics?: boolean;
  mode?: 'management' | 'selection' | 'view';
}

const TagManager: React.FC<TagManagerProps> = ({
  onTagSelect,
  showCreateButton = true,
  showStatistics = true,
  mode = 'management'
}) => {
  const { tags, loading, error, fetchTags } = useTags();
  const { documents } = useKnowledgeStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTag, setSelectedTag] = useState<TagType | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [filterType, setFilterType] = useState<'all' | 'system' | 'user'>('all');

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  const handleCreateTag = async (values: any) => {
    try {
      await createTag({
        name: values.name,
        description: values.description,
        color: values.color?.toHexString?.() || '#1890ff',
        is_system: values.is_system || false
      });
      message.success('Tag created successfully');
      setShowCreateModal(false);
      form.resetFields();
      fetchTags();
    } catch (error) {
      message.error('Failed to create tag');
    }
  };

  const handleEditTag = async (values: any) => {
    if (!selectedTag) return;
    
    try {
      // TODO: Implement updateTag API call
      message.success('Tag updated successfully');
      setShowEditModal(false);
      editForm.resetFields();
      setSelectedTag(null);
      fetchTags();
    } catch (error) {
      message.error('Failed to update tag');
    }
  };

  const handleDeleteTag = async (tagId: string) => {
    try {
      await deleteTag(tagId);
      message.success('Tag deleted successfully');
      fetchTags();
    } catch (error) {
      message.error('Failed to delete tag');
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  const filteredTags = tags.filter(tag => {
    const matchesSearch = tag.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tag.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || 
                       (filterType === 'system' && tag.is_system) ||
                       (filterType === 'user' && !tag.is_system);
    return matchesSearch && matchesType;
  });

  const getTagStatistics = () => {
    const totalTags = tags.length;
    const systemTags = tags.filter(tag => tag.is_system).length;
    const userTags = tags.filter(tag => !tag.is_system).length;
    const totalUsage = tags.reduce((sum, tag) => sum + tag.usage_count, 0);
    const mostUsedTag = tags.reduce((max, tag) => tag.usage_count > max.usage_count ? tag : max, tags[0]);

    return { totalTags, systemTags, userTags, totalUsage, mostUsedTag };
  };

  const columns = [
    {
      title: 'Tag',
      key: 'tag',
      render: (record: TagType) => (
        <Space>
          <Tag color={record.color || '#1890ff'} icon={<TagOutlined />}>
            {record.name}
          </Tag>
          {record.is_system && (
            <Tag color="red" size="small">System</Tag>
          )}
        </Space>
      ),
      sorter: (a: TagType, b: TagType) => a.name.localeCompare(b.name),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (description: string) => description || <Text type="secondary">-</Text>,
      ellipsis: true,
    },
    {
      title: 'Usage Count',
      dataIndex: 'usage_count',
      key: 'usage_count',
      render: (count: number) => (
        <Text strong>{count.toLocaleString()}</Text>
      ),
      sorter: (a: TagType, b: TagType) => a.usage_count - b.usage_count,
    },
    {
      title: 'Type',
      key: 'type',
      render: (record: TagType) => (
        <Tag color={record.is_system ? 'red' : 'green'}>
          {record.is_system ? 'System' : 'User'}
        </Tag>
      ),
      filters: [
        { text: 'System', value: 'system' },
        { text: 'User', value: 'user' },
      ],
      onFilter: (value: string, record: TagType) => 
        (value === 'system' && record.is_system) || (value === 'user' && !record.is_system),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a: TagType, b: TagType) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: TagType) => (
        <Space>
          {mode === 'selection' && (
            <Button 
              type="text" 
              size="small"
              onClick={() => onTagSelect?.(record)}
            >
              Select
            </Button>
          )}
          {mode === 'management' && (
            <>
              <Tooltip title="Edit Tag">
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EditOutlined />}
                  onClick={() => {
                    setSelectedTag(record);
                    editForm.setFieldsValue({
                      name: record.name,
                      description: record.description,
                      color: record.color,
                      is_system: record.is_system
                    });
                    setShowEditModal(true);
                  }}
                  disabled={record.is_system}
                />
              </Tooltip>
              <Popconfirm
                title="Are you sure you want to delete this tag?"
                onConfirm={() => handleDeleteTag(record.id)}
                okText="Yes"
                cancelText="No"
                disabled={record.is_system || record.usage_count > 0}
              >
                <Tooltip title={record.usage_count > 0 ? "Cannot delete tag in use" : "Delete Tag"}>
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

  const renderStatistics = () => {
    const stats = getTagStatistics();
    
    return (
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Tags"
              value={stats.totalTags}
              prefix={<TagOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="System Tags"
              value={stats.systemTags}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="User Tags"
              value={stats.userTags}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Usage"
              value={stats.totalUsage}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  const renderTagCloud = () => {
    const sortedTags = [...tags].sort((a, b) => b.usage_count - a.usage_count);
    const topTags = sortedTags.slice(0, 20);

    return (
      <Card title="Tag Cloud" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {topTags.map(tag => (
            <Tag
              key={tag.id}
              color={tag.color || '#1890ff'}
              style={{
                fontSize: Math.max(12, Math.min(20, 12 + tag.usage_count / 10)),
                cursor: 'pointer',
                opacity: tag.usage_count > 0 ? 1 : 0.5
              }}
              onClick={() => onTagSelect?.(tag)}
            >
              {tag.name} ({tag.usage_count})
            </Tag>
          ))}
        </div>
      </Card>
    );
  };

  return (
    <div>
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      {showStatistics && renderStatistics()}

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Space>
            <Search
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
            />
            <Select
              value={filterType}
              onChange={setFilterType}
              style={{ width: 120 }}
            >
              <Option value="all">All Tags</Option>
              <Option value="system">System</Option>
              <Option value="user">User</Option>
            </Select>
          </Space>
          
          {showCreateButton && mode === 'management' && (
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setShowCreateModal(true)}
            >
              Create Tag
            </Button>
          )}
        </div>

        <Table
          columns={columns}
          dataSource={filteredTags}
          loading={loading}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} tags`,
            pageSizeOptions: ['10', '20', '50'],
            defaultPageSize: 20,
          }}
        />
      </Card>

      {showStatistics && renderTagCloud()}

      {/* Create Tag Modal */}
      <Modal
        title="Create New Tag"
        open={showCreateModal}
        onCancel={() => setShowCreateModal(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTag}
        >
          <Form.Item
            name="name"
            label="Tag Name"
            rules={[
              { required: true, message: 'Please enter a tag name' },
              { min: 2, message: 'Tag name must be at least 2 characters' },
              { max: 50, message: 'Tag name must be less than 50 characters' }
            ]}
          >
            <Input placeholder="Enter tag name" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Description"
            rules={[
              { max: 200, message: 'Description must be less than 200 characters' }
            ]}
          >
            <Input.TextArea 
              placeholder="Enter tag description (optional)"
              rows={3}
            />
          </Form.Item>
          
          <Form.Item
            name="color"
            label="Color"
            initialValue="#1890ff"
          >
            <ColorPicker />
          </Form.Item>
          
          <Form.Item
            name="is_system"
            valuePropName="checked"
            initialValue={false}
          >
            <Select placeholder="Tag Type">
              <Option value={false}>User Tag</Option>
              <Option value={true}>System Tag</Option>
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Tag
              </Button>
              <Button onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Tag Modal */}
      <Modal
        title="Edit Tag"
        open={showEditModal}
        onCancel={() => setShowEditModal(false)}
        footer={null}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleEditTag}
        >
          <Form.Item
            name="name"
            label="Tag Name"
            rules={[
              { required: true, message: 'Please enter a tag name' },
              { min: 2, message: 'Tag name must be at least 2 characters' },
              { max: 50, message: 'Tag name must be less than 50 characters' }
            ]}
          >
            <Input placeholder="Enter tag name" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Description"
            rules={[
              { max: 200, message: 'Description must be less than 200 characters' }
            ]}
          >
            <Input.TextArea 
              placeholder="Enter tag description (optional)"
              rows={3}
            />
          </Form.Item>
          
          <Form.Item
            name="color"
            label="Color"
          >
            <ColorPicker />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Update Tag
              </Button>
              <Button onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TagManager;