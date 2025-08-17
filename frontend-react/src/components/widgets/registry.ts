import type { WidgetProps } from "./WidgetBase";
import StatsWidget from "./StatsWidget";
import ActivityWidget from "./ActivityWidget";
import SystemMetricsWidget from "./SystemMetricsWidget";

export type WidgetType = "stats" | "activity" | "systemMetrics";

export type WidgetSize = "small" | "medium" | "large" | "full";

export type WidgetMeta<TSettings extends Record<string, any> = Record<string, any>> = {
	type: WidgetType;
	component: React.ComponentType<WidgetProps>;
	defaultSize: WidgetSize;
	defaultSettings: TSettings;
	icon: string;
	i18nTitleKey: string;
	i18nDescriptionKey: string;
};

export const WIDGET_REGISTRY: Record<WidgetType, WidgetMeta<any>> = {
	stats: {
		type: "stats",
		component: StatsWidget as unknown as React.ComponentType<WidgetProps>,
		defaultSize: "medium",
		defaultSettings: {
			showConversations: true,
			showMessages: true,
			showDocuments: true,
			showAssistants: true,
			showTools: true,
			showUsers: true,
			showPerformance: true,
			refreshInterval: 30,
		},
		icon: "📊",
		i18nTitleKey: "widgets.system_stats",
		i18nDescriptionKey: "widgets.system_stats_description",
	},
	activity: {
		type: "activity",
		component: ActivityWidget as unknown as React.ComponentType<WidgetProps>,
		defaultSize: "large",
		defaultSettings: {
			maxItems: 10,
			showUserInfo: true,
			showTimestamps: true,
			filterTypes: [],
			refreshInterval: 60,
		},
		icon: "📝",
		i18nTitleKey: "widgets.recent_activity",
		i18nDescriptionKey: "widgets.recent_activity_description",
	},
	systemMetrics: {
		type: "systemMetrics",
		component: SystemMetricsWidget as unknown as React.ComponentType<WidgetProps>,
		defaultSize: "full",
		defaultSettings: {
			refreshInterval: 60,
		},
		icon: "🖥️",
		i18nTitleKey: "monitoring.system_metrics",
		i18nDescriptionKey: "monitoring.system_metrics_description",
	},
};