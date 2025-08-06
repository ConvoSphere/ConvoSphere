import React, { useState, useEffect, useMemo } from "react";
import Calendar from "react-calendar";
import { format, isSameDay, isToday, isYesterday, isTomorrow } from "date-fns";
import { de } from "date-fns/locale";
import { List, Tag, Typography, Space, Modal, Form, Input, DatePicker, Select } from "antd";
import ModernButton from "../ModernButton";
import {
  CalendarOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  UserOutlined,
  BellOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import ModernButton from "../ModernButton";

const { Title, Text } = Typography;
const { Option } = Select;

interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  date: Date;
  time?: string;
  type: "meeting" | "reminder" | "deadline" | "event";
  priority: "low" | "medium" | "high";
  attendees?: string[];
  location?: string;
  isCompleted?: boolean;
}

interface CalendarWidgetProps extends Omit<WidgetProps, "children"> {
  config: WidgetConfig & {
    settings: {
      viewMode: "month" | "week" | "day";
      showCompleted: boolean;
      showReminders: boolean;
      defaultView: "calendar" | "list";
      refreshInterval: number;
      timezone: string;
    };
  };
}

const CalendarWidget: React.FC<CalendarWidgetProps> = ({
  config,
  onConfigChange,
  onRemove,
  onRefresh,
  loading = false,
  error = null,
}) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Mock events for demonstration
  const mockEvents: CalendarEvent[] = [
    {
      id: "1",
      title: "Team Meeting",
      description: "Weekly team sync",
      date: new Date(),
      time: "10:00",
      type: "meeting",
      priority: "high",
      attendees: ["Max", "Anna", "Tom"],
    },
    {
      id: "2",
      title: "Project Deadline",
      description: "Submit final report",
      date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
      type: "deadline",
      priority: "high",
    },
    {
      id: "3",
      title: "Client Call",
      description: "Discuss requirements",
      date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
      time: "14:30",
      type: "meeting",
      priority: "medium",
      attendees: ["Client A"],
    },
    {
      id: "4",
      title: "Code Review",
      description: "Review new features",
      date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      time: "16:00",
      type: "reminder",
      priority: "low",
      isCompleted: true,
    },
  ];

  useEffect(() => {
    loadEvents();
  }, [token]);

  useEffect(() => {
    if (config.settings.refreshInterval && config.settings.refreshInterval > 0) {
      const interval = setInterval(loadEvents, config.settings.refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [config.settings.refreshInterval]);

  const loadEvents = async () => {
    try {
      setLocalLoading(true);
      setLocalError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setEvents(mockEvents);
    } catch (error) {
      console.error("Error loading events:", error);
      setLocalError(t("widgets.error_loading_events"));
    } finally {
      setLocalLoading(false);
    }
  };

  const getEventsForDate = (date: Date) => {
    return events.filter(event => isSameDay(event.date, date));
  };

  const getEventsForToday = () => {
    return getEventsForDate(new Date());
  };

  const getUpcomingEvents = () => {
    const today = new Date();
    return events
      .filter(event => event.date >= today && !event.isCompleted)
      .sort((a, b) => a.date.getTime() - b.date.getTime())
      .slice(0, 5);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return colors.colorError;
      case "medium": return colors.colorWarning;
      case "low": return colors.colorSuccess;
      default: return colors.colorTextSecondary;
    }
  };

  const getEventTypeIcon = (type: string) => {
    switch (type) {
      case "meeting": return <UserOutlined />;
      case "reminder": return <BellOutlined />;
      case "deadline": return <ClockCircleOutlined />;
      case "event": return <CalendarOutlined />;
      default: return <CalendarOutlined />;
    }
  };

  const formatEventDate = (date: Date) => {
    if (isToday(date)) return t("widgets.calendar.today");
    if (isYesterday(date)) return t("widgets.calendar.yesterday");
    if (isTomorrow(date)) return t("widgets.calendar.tomorrow");
    return format(date, "MMM dd", { locale: de });
  };

  const tileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view === "month") {
      const dayEvents = getEventsForDate(date);
      if (dayEvents.length > 0) {
        return (
          <div style={{ fontSize: "8px", color: colors.colorPrimary }}>
            {dayEvents.length} {t("widgets.calendar.events")}
          </div>
        );
      }
    }
    return null;
  };

  const tileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === "month") {
      const dayEvents = getEventsForDate(date);
      if (dayEvents.length > 0) {
        return "has-events";
      }
    }
    return null;
  };

  const renderEventList = () => {
    const displayEvents = config.settings.showCompleted 
      ? events 
      : events.filter(event => !event.isCompleted);

    return (
      <List
        dataSource={displayEvents}
        renderItem={(event) => (
          <List.Item
            style={{
              padding: "8px 0",
              opacity: event.isCompleted ? 0.6 : 1,
            }}
          >
            <List.Item.Meta
              avatar={
                <div style={{ color: getPriorityColor(event.priority) }}>
                  {getEventTypeIcon(event.type)}
                </div>
              }
              title={
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Text 
                    strong 
                    style={{ 
                      textDecoration: event.isCompleted ? "line-through" : "none" 
                    }}
                  >
                    {event.title}
                  </Text>
                  <Tag color={getPriorityColor(event.priority)} size="small">
                    {event.priority}
                  </Tag>
                </div>
              }
              description={
                <div>
                  <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
                    {formatEventDate(event.date)}
                    {event.time && ` • ${event.time}`}
                  </div>
                  {event.description && (
                    <div style={{ fontSize: "12px", marginTop: 4 }}>
                      {event.description}
                    </div>
                  )}
                  {event.attendees && event.attendees.length > 0 && (
                    <div style={{ fontSize: "11px", color: colors.colorTextSecondary, marginTop: 4 }}>
                      {event.attendees.join(", ")}
                    </div>
                  )}
                </div>
              }
            />
          </List.Item>
        )}
      />
    );
  };

  const renderCalendar = () => (
    <div>
      <Calendar
        onChange={setSelectedDate}
        value={selectedDate}
        tileContent={tileContent}
        tileClassName={tileClassName}
        locale={de}
        className="custom-calendar"
      />
      
      {/* Events for selected date */}
      <div style={{ marginTop: 16 }}>
        <Title level={5}>
          {format(selectedDate, "EEEE, MMMM dd", { locale: de })}
        </Title>
        {getEventsForDate(selectedDate).length > 0 ? (
          <List
            size="small"
            dataSource={getEventsForDate(selectedDate)}
            renderItem={(event) => (
              <List.Item style={{ padding: "4px 0" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ color: getPriorityColor(event.priority) }}>
                    {getEventTypeIcon(event.type)}
                  </div>
                  <Text style={{ fontSize: "12px" }}>{event.title}</Text>
                  {event.time && (
                    <Text type="secondary" style={{ fontSize: "11px" }}>
                      {event.time}
                    </Text>
                  )}
                </div>
              </List.Item>
            )}
          />
        ) : (
          <Text type="secondary" style={{ fontSize: "12px" }}>
            {t("widgets.calendar.no_events")}
          </Text>
        )}
      </div>
    </div>
  );

  const renderQuickStats = () => (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorPrimary }}>
            {getEventsForToday().length}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.calendar.today")}
          </div>
        </div>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorWarning }}>
            {events.filter(e => e.priority === "high" && !e.isCompleted).length}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.calendar.high_priority")}
          </div>
        </div>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorSuccess }}>
            {events.filter(e => e.isCompleted).length}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.calendar.completed")}
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    if (localError) {
      return (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="danger">{localError}</Text>
        </div>
      );
    }

    return (
      <div>
        {renderQuickStats()}
        
        <div style={{ marginBottom: 16 }}>
          <Space>
            <ModernButton
              variant={config.settings.defaultView === "calendar" ? "primary" : "outlined"}
              size="small"
              onClick={() => onConfigChange({
                ...config,
                settings: { ...config.settings, defaultView: "calendar" }
              })}
            >
              {t("widgets.calendar.calendar_view")}
            </ModernButton>
            <ModernButton
              variant={config.settings.defaultView === "list" ? "primary" : "outlined"}
              size="small"
              onClick={() => onConfigChange({
                ...config,
                settings: { ...config.settings, defaultView: "list" }
              })}
            >
              {t("widgets.calendar.list_view")}
            </ModernButton>
            <ModernButton
              variant="outlined"
              size="small"
              icon={<PlusOutlined />}
              onClick={() => setShowAddEvent(true)}
            >
              {t("widgets.calendar.add_event")}
            </ModernButton>
          </Space>
        </div>

        {config.settings.defaultView === "calendar" ? renderCalendar() : renderEventList()}
      </div>
    );
  };

  return (
    <WidgetBase
      config={config}
      onConfigChange={onConfigChange}
      onRemove={onRemove}
      onRefresh={loadEvents}
      loading={loading || localLoading}
      error={error || localError}
    >
      {renderContent()}
    </WidgetBase>
  );
};

export default CalendarWidget;