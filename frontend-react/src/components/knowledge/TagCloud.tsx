import React from "react";
import { Card, Tag } from "antd";
import { Tag as TagType } from "../../services/knowledge";

interface TagCloudProps {
  tags: TagType[];
  onTagSelect?: (tag: TagType) => void;
}

const TagCloud: React.FC<TagCloudProps> = ({ tags, onTagSelect }) => {
  const sortedTags = [...tags].sort((a, b) => b.usage_count - a.usage_count);
  const topTags = sortedTags.slice(0, 20);

  return (
    <Card title="Tag Cloud" style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {topTags.map((tag) => (
          <Tag
            key={tag.id}
            color={tag.color || "#1890ff"}
            style={{
              fontSize: Math.max(12, Math.min(20, 12 + tag.usage_count / 10)),
              cursor: "pointer",
              opacity: tag.usage_count > 0 ? 1 : 0.5,
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

export default TagCloud;
