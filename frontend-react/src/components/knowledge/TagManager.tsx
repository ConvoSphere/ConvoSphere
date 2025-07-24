import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Button, 
  Input, 
  Modal, 
  Form, 
  Select, 
  Tag, 
  Space, 
  Typography, 
  message,
  Popconfirm
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SearchOutlined,
  TagOutlined
} from '@ant-design/icons';
import type { Tag as TagType } from '../../services/knowledge';
import { useKnowledgeStore } from '../../store/knowledgeStore';
import TagStatistics from './TagStatistics';
import TagCloud from './TagCloud';
import TagTable from './TagTable';
import CreateTagModal from './CreateTagModal';
import EditTagModal from './EditTagModal';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface TagManagerProps {
  onTagSelect?: (tag: TagType) => void;
  showCreateButton?: boolean;
  showStatistics?: boolean;
  mode?: 'selection' | 'management';
}

const TagManager: React.FC<TagManagerProps> = ({
  onTagSelect,
  showCreateButton = true,
  showStatistics = true,
  mode = 'management'
}) => {
  const { tags, fetchTags } = useKnowledgeStore();
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
      // TODO: Implement create tag API call
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
      // TODO: Implement edit tag API call
      message.success('Tag updated successfully');
      setShowEditModal(false);
      setSelectedTag(null);
      editForm.resetFields();
      fetchTags();
    } catch (error) {
      message.error('Failed to update tag');
    }
  };

  const handleDeleteTag = async (tagId: string) => {
    try {
      // TODO: Implement delete tag API call
      message.success('Tag deleted successfully');
      fetchTags();
    } catch (error) {
      message.error('Failed to delete tag');
    }
  };

  const filteredTags = tags.filter(tag => {
    const matchesSearch = tag.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tag.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || 
                       (filterType === 'system' && tag.is_system) ||
                       (filterType === 'user' && !tag.is_system);
    return matchesSearch && matchesType;
  });

  const stats = {
    totalTags: tags.length,
    systemTags: tags.filter(tag => tag.is_system).length,
    userTags: tags.filter(tag => !tag.is_system).length,
    totalUsage: tags.reduce((sum, tag) => sum + tag.usage_count, 0)
  };

  return (
    <div>
      {/* Error Alert removed as per new_code */}

      {showStatistics && <TagStatistics {...stats} />}

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Space>
            <Search
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
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
        <TagTable
          tags={filteredTags}
          loading={false} // Loading state removed from store, so set to false
          mode={mode}
          onTagSelect={onTagSelect}
          onEditTag={(tag) => {
            setSelectedTag(tag);
            if (editForm && editForm.setFieldsValue) {
              editForm.setFieldsValue({
                name: tag.name,
                description: tag.description,
                color: tag.color,
                is_system: tag.is_system
              });
            }
            setShowEditModal(true);
          }}
          onDeleteTag={handleDeleteTag}
        />
      </Card>

      {showStatistics && <TagCloud tags={tags} onTagSelect={onTagSelect} />}

      <CreateTagModal
        open={showCreateModal}
        form={form}
        onFinish={handleCreateTag}
        onCancel={() => setShowCreateModal(false)}
      />
      <EditTagModal
        open={showEditModal}
        form={editForm}
        onFinish={handleEditTag}
        onCancel={() => setShowEditModal(false)}
      />
    </div>
  );
};

export default TagManager;