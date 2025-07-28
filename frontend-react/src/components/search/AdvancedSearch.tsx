import React, { useState, useEffect } from "react";
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Select,
  DatePicker,
  Slider,
  Checkbox,
  Tag,
  Divider,
  Row,
  Col,
  Collapse,
  Empty,
  Spin,
} from "antd";
import {
  SearchOutlined,
  FilterOutlined,
  ClearOutlined,
  SaveOutlined,
  BookOutlined,
  CalendarOutlined,
  FileTextOutlined,
  TagOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { RangePickerProps } from "antd/es/date-picker";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import ModernInput from "../ModernInput";
import ModernSelect from "../ModernSelect";

const { Title, Text } = Typography;
const { Search } = Input;
const { RangePicker } = DatePicker;
const { Panel } = Collapse;

interface SearchFilters {
  query: string;
  fileTypes: string[];
  tags: string[];
  dateRange: [string, string] | null;
  sizeRange: [number, number];
  author: string;
  status: string[];
  categories: string[];
}

interface SearchResult {
  id: string;
  title: string;
  filename: string;
  description: string;
  fileType: string;
  fileSize: number;
  tags: string[];
  author: string;
  createdAt: string;
  status: string;
  relevance: number;
}

interface AdvancedSearchProps {
  onSearch: (filters: SearchFilters) => void;
  onClear: () => void;
  onSaveSearch?: (name: string, filters: SearchFilters) => void;
  loading?: boolean;
  results?: SearchResult[];
  totalResults?: number;
}

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  onSearch,
  onClear,
  onSaveSearch,
  loading = false,
  results = [],
  totalResults = 0,
}) => {
  const { t } = useTranslation();
  const [filters, setFilters] = useState<SearchFilters>({
    query: "",
    fileTypes: [],
    tags: [],
    dateRange: null,
    sizeRange: [0, 100],
    author: "",
    status: [],
    categories: [],
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [savedSearches, setSavedSearches] = useState<string[]>([]);
  const [searchName, setSearchName] = useState("");

  // Available options for filters
  const fileTypeOptions = [
    { label: "PDF", value: "pdf" },
    { label: "Text", value: "txt" },
    { label: "Markdown", value: "md" },
    { label: "Images", value: "image" },
    { label: "Code", value: "code" },
    { label: "Documents", value: "doc" },
  ];

  const statusOptions = [
    { label: t("documents.status.processed", "Verarbeitet"), value: "processed" },
    { label: t("documents.status.processing", "Wird verarbeitet"), value: "processing" },
    { label: t("documents.status.failed", "Fehlgeschlagen"), value: "failed" },
  ];

  const categoryOptions = [
    { label: t("categories.technical", "Technisch"), value: "technical" },
    { label: t("categories.business", "Geschäftlich"), value: "business" },
    { label: t("categories.personal", "Persönlich"), value: "personal" },
    { label: t("categories.other", "Sonstiges"), value: "other" },
  ];

  const handleSearch = () => {
    onSearch(filters);
  };

  const handleClear = () => {
    setFilters({
      query: "",
      fileTypes: [],
      tags: [],
      dateRange: null,
      sizeRange: [0, 100],
      author: "",
      status: [],
      categories: [],
    });
    onClear();
  };

  const handleSaveSearch = () => {
    if (searchName.trim() && onSaveSearch) {
      onSaveSearch(searchName.trim(), filters);
      setSavedSearches(prev => [...prev, searchName.trim()]);
      setSearchName("");
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleTagRemove = (tag: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag),
    }));
  };

  const handleTagAdd = (tag: string) => {
    if (tag.trim() && !filters.tags.includes(tag.trim())) {
      setFilters(prev => ({
        ...prev,
        tags: [...prev.tags, tag.trim()],
      }));
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getRelevanceColor = (relevance: number): string => {
    if (relevance >= 0.8) return "#52c41a";
    if (relevance >= 0.6) return "#faad14";
    return "#ff4d4f";
  };

  return (
    <div>
      <ModernCard variant="elevated" size="lg">
        {/* Basic Search */}
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ marginBottom: 16 }}>
            <SearchOutlined style={{ marginRight: 8 }} />
            {t("search.title", "Erweiterte Suche")}
          </Title>
          
          <Space.Compact style={{ width: "100%" }}>
            <Search
              placeholder={t("search.placeholder", "Dokumente durchsuchen...")}
              value={filters.query}
              onChange={(e) => handleFilterChange("query", e.target.value)}
              onSearch={handleSearch}
              enterButton={
                <Button type="primary" icon={<SearchOutlined />}>
                  {t("search.search", "Suchen")}
                </Button>
              }
              size="large"
            />
            <ModernButton
              variant="outlined"
              icon={<FilterOutlined />}
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? t("search.hide_filters", "Filter ausblenden") : t("search.show_filters", "Filter anzeigen")}
            </ModernButton>
          </Space.Compact>
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <Collapse defaultActiveKey={["filters"]} style={{ marginBottom: 24 }}>
            <Panel
              header={
                <Space>
                  <FilterOutlined />
                  {t("search.advanced_filters", "Erweiterte Filter")}
                </Space>
              }
              key="filters"
            >
              <Row gutter={[16, 16]}>
                {/* File Types */}
                <Col xs={24} md={12}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.file_types", "Dateitypen")}</Text>
                    <ModernSelect
                      mode="multiple"
                      placeholder={t("search.select_file_types", "Dateitypen auswählen")}
                      value={filters.fileTypes}
                      onChange={(value) => handleFilterChange("fileTypes", value)}
                      options={fileTypeOptions}
                      style={{ width: "100%", marginTop: 8 }}
                    />
                  </div>
                </Col>

                {/* Status */}
                <Col xs={24} md={12}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.status", "Status")}</Text>
                    <ModernSelect
                      mode="multiple"
                      placeholder={t("search.select_status", "Status auswählen")}
                      value={filters.status}
                      onChange={(value) => handleFilterChange("status", value)}
                      options={statusOptions}
                      style={{ width: "100%", marginTop: 8 }}
                    />
                  </div>
                </Col>

                {/* Date Range */}
                <Col xs={24} md={12}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.date_range", "Datum")}</Text>
                    <RangePicker
                      style={{ width: "100%", marginTop: 8 }}
                      placeholder={[t("search.start_date", "Startdatum"), t("search.end_date", "Enddatum")]}
                      onChange={(dates) => {
                        if (dates) {
                          handleFilterChange("dateRange", [
                            dates[0]?.toISOString() || "",
                            dates[1]?.toISOString() || "",
                          ]);
                        } else {
                          handleFilterChange("dateRange", null);
                        }
                      }}
                    />
                  </div>
                </Col>

                {/* Author */}
                <Col xs={24} md={12}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.author", "Autor")}</Text>
                    <ModernInput
                      placeholder={t("search.author_placeholder", "Autor eingeben")}
                      value={filters.author}
                      onChange={(e) => handleFilterChange("author", e.target.value)}
                      style={{ marginTop: 8 }}
                    />
                  </div>
                </Col>

                {/* File Size Range */}
                <Col xs={24}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.file_size", "Dateigröße (MB)")}</Text>
                    <Slider
                      range
                      min={0}
                      max={100}
                      value={filters.sizeRange}
                      onChange={(value) => handleFilterChange("sizeRange", value)}
                      style={{ marginTop: 8 }}
                    />
                    <Text type="secondary">
                      {filters.sizeRange[0]} - {filters.sizeRange[1]} MB
                    </Text>
                  </div>
                </Col>

                {/* Tags */}
                <Col xs={24}>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>{t("search.tags", "Tags")}</Text>
                    <div style={{ marginTop: 8 }}>
                      {filters.tags.map((tag, index) => (
                        <Tag
                          key={index}
                          closable
                          onClose={() => handleTagRemove(tag)}
                          style={{ marginBottom: 4 }}
                        >
                          {tag}
                        </Tag>
                      ))}
                      <ModernInput
                        placeholder={t("search.add_tag", "Tag hinzufügen")}
                        onPressEnter={(e) => {
                          handleTagAdd((e.target as HTMLInputElement).value);
                          (e.target as HTMLInputElement).value = "";
                        }}
                        style={{ width: 200, marginTop: 8 }}
                      />
                    </div>
                  </div>
                </Col>
              </Row>

              {/* Action Buttons */}
              <Divider />
              <Space>
                <ModernButton
                  variant="primary"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                >
                  {t("search.search", "Suchen")}
                </ModernButton>
                <ModernButton
                  variant="outlined"
                  icon={<ClearOutlined />}
                  onClick={handleClear}
                >
                  {t("search.clear", "Zurücksetzen")}
                </ModernButton>
                {onSaveSearch && (
                  <Space>
                    <ModernInput
                      placeholder={t("search.save_name", "Suchname")}
                      value={searchName}
                      onChange={(e) => setSearchName(e.target.value)}
                      style={{ width: 200 }}
                    />
                    <ModernButton
                      variant="outlined"
                      icon={<SaveOutlined />}
                      onClick={handleSaveSearch}
                      disabled={!searchName.trim()}
                    >
                      {t("search.save", "Speichern")}
                    </ModernButton>
                  </Space>
                )}
              </Space>
            </Panel>
          </Collapse>
        )}

        {/* Search Results */}
        {results.length > 0 && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <Text>
                {t("search.results_count", "{{count}} Ergebnisse gefunden", { count: totalResults })}
              </Text>
              <Text type="secondary">
                {t("search.loading", "Lädt...")} {loading && <Spin size="small" />}
              </Text>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {results.map((result) => (
                <Card key={result.id} size="small" hoverable>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                        <FileTextOutlined style={{ color: "#1890ff" }} />
                        <Title level={5} style={{ margin: 0 }}>
                          {result.title}
                        </Title>
                        <Tag color={getRelevanceColor(result.relevance)}>
                          {(result.relevance * 100).toFixed(0)}%
                        </Tag>
                      </div>
                      
                      <Text type="secondary" style={{ display: "block", marginBottom: 8 }}>
                        {result.filename} • {formatFileSize(result.fileSize)} • {result.fileType.toUpperCase()}
                      </Text>
                      
                      <Paragraph style={{ marginBottom: 8 }}>
                        {result.description}
                      </Paragraph>
                      
                      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                        <Space>
                          <TagOutlined />
                          {result.tags.map((tag, index) => (
                            <Tag key={index} size="small">
                              {tag}
                            </Tag>
                          ))}
                        </Space>
                        <Space>
                          <CalendarOutlined />
                          <Text type="secondary" style={{ fontSize: "12px" }}>
                            {new Date(result.createdAt).toLocaleDateString()}
                          </Text>
                        </Space>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && filters.query && (
          <Empty
            description={t("search.no_results", "Keine Ergebnisse gefunden")}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </ModernCard>
    </div>
  );
};

export default AdvancedSearch;