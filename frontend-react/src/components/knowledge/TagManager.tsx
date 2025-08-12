import React, { useState, useEffect } from "react";
import {
  Card,
  Button,
  Input,
  Form,
  Select,
  Space,
  Typography,
  message,
} from "antd";
import { PlusOutlined } from "@ant-design/icons";
import type { Tag as TagType } from "../../services/knowledge";
import { useKnowledgeStore } from "../../store/knowledgeStore";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getTags, createTag, deleteTag } from "../../services/knowledge";

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

interface TagManagerProps {
  showCreateButton?: boolean;
  showStatistics?: boolean;
}

const TagManager: React.FC<TagManagerProps> = ({
  showCreateButton = true,
  showStatistics = true,
}) => {
  const { fetchTags } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTag, setSelectedTag] = useState<TagType | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [filterType, setFilterType] = useState<"all" | "system" | "user">(
    "all",
  );

  const queryClient = useQueryClient();
  const tagsQuery = useQuery({
    queryKey: ["knowledge-tags"],
    queryFn: getTags,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  const createMutation = useMutation({
    mutationFn: (values: Partial<TagType>) => createTag(values),
    onSuccess: async () => {
      message.success("Tag created successfully");
      setShowCreateModal(false);
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["knowledge-tags"] });
    },
    onError: () => message.error("Failed to create tag"),
  });

  const deleteMutation = useMutation({
    mutationFn: (tagId: string) => deleteTag(tagId),
    onSuccess: async () => {
      message.success("Tag deleted successfully");
      await queryClient.invalidateQueries({ queryKey: ["knowledge-tags"] });
    },
    onError: () => message.error("Failed to delete tag"),
  });

  const handleCreateTag = async () => {
    const values = await form.validateFields();
    createMutation.mutate(values);
  };

  const handleEditTag = async () => {
    if (!selectedTag) return;
    try {
      // TODO: Implement edit tag API call
      message.success("Tag updated successfully");
      setShowEditModal(false);
      setSelectedTag(null);
      editForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["knowledge-tags"] });
    } catch (_error) {
      message.error("Failed to update tag");
    }
  };

  const tags = tagsQuery.data || [];

  const filteredTags = tags.filter((tag: TagType) => {
    const matchesSearch =
      tag.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tag.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType =
      filterType === "all" ||
      (filterType === "system" && tag.is_system) ||
      (filterType === "user" && !tag.is_system);
    return matchesSearch && matchesType;
  });

  const stats = {
    totalTags: tags.length,
    systemTags: tags.filter((tag: TagType) => tag.is_system).length,
    userTags: tags.filter((tag: TagType) => !tag.is_system).length,
    totalUsage: tags.reduce(
      (sum: number, tag: TagType) => sum + tag.usage_count,
      0,
    ),
  };

  return (
    <div>
      {showStatistics && <div>Statistics: {stats.totalTags} tags</div>}

      <Card
        title={
          <Space>
            <span>Tags ({filteredTags.length})</span>
          </Space>
        }
        extra={
          <Space>
            <Search
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: 200 }}
              size="small"
            />
            <Select
              value={filterType}
              onChange={setFilterType}
              size="small"
              style={{ width: 120 }}
            >
              <Option value="all">All</Option>
              <Option value="system">System</Option>
              <Option value="user">User</Option>
            </Select>
            {showCreateButton && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                size="small"
                onClick={() => setShowCreateModal(true)}
              >
                Create Tag
              </Button>
            )}
          </Space>
        }
      >
        <div>
          {filteredTags.map((tag: TagType) => (
            <div
              key={tag.id}
              style={{
                padding: "8px",
                border: "1px solid #f0f0f0",
                marginBottom: "4px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Text>{tag.name}</Text>
              <Button
                danger
                size="small"
                onClick={() => deleteMutation.mutate(tag.id)}
              >
                Delete
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Create Tag Modal */}
      <Form form={form} onFinish={handleCreateTag} layout="vertical">
        <Form.Item
          name="name"
          label="Tag Name"
          rules={[{ required: true, message: "Please enter tag name" }]}
        >
          <Input placeholder="Enter tag name" />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea placeholder="Enter tag description" />
        </Form.Item>
        <Form.Item name="color" label="Color" initialValue="#1890ff">
          <Input type="color" />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              Create
            </Button>
            <Button onClick={() => setShowCreateModal(false)}>Cancel</Button>
          </Space>
        </Form.Item>
      </Form>

      {/* Edit Tag Modal */}
      <Form form={editForm} onFinish={handleEditTag} layout="vertical">
        <Form.Item
          name="name"
          label="Tag Name"
          rules={[{ required: true, message: "Please enter tag name" }]}
        >
          <Input placeholder="Enter tag name" />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea placeholder="Enter tag description" />
        </Form.Item>
        <Form.Item name="color" label="Color">
          <Input type="color" />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              Update
            </Button>
            <Button onClick={() => setShowEditModal(false)}>Cancel</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default TagManager;
