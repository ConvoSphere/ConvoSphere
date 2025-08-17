import React, { useEffect, useState } from "react";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import SystemMetrics from "../monitoring/SystemMetrics";
import { monitoringService, type SystemMetrics as SystemMetricsType } from "../../services/monitoring";
import { useTranslation } from "react-i18next";

interface SystemMetricsWidgetProps extends Omit<WidgetProps, "children"> {
	config: WidgetConfig & {
		settings: {
			refreshInterval?: number;
		};
	};
}

const SystemMetricsWidget: React.FC<SystemMetricsWidgetProps> = ({
	config,
	onConfigChange,
	onRemove,
	onRefresh,
	loading = false,
	error = null,
}) => {
	const { t } = useTranslation();
	const [metrics, setMetrics] = useState<SystemMetricsType | null>(null);
	const [localLoading, setLocalLoading] = useState(false);
	const [localError, setLocalError] = useState<string | null>(null);

	useEffect(() => {
		loadMetrics();
	}, []);

	useEffect(() => {
		if (config.settings.refreshInterval && config.settings.refreshInterval > 0) {
			const interval = setInterval(loadMetrics, config.settings.refreshInterval * 1000);
			return () => clearInterval(interval);
		}
	}, [config.settings.refreshInterval]);

	const loadMetrics = async () => {
		try {
			setLocalLoading(true);
			setLocalError(null);
			const data = await monitoringService.getSystemMetrics();
			setMetrics(data);
			onConfigChange({
				...config,
				lastRefresh: new Date().toISOString(),
			});
		} catch (e) {
			setLocalError(t("monitoring.failed_to_load_metrics"));
		} finally {
			setLocalLoading(false);
		}
	};

	const handleRefresh = () => {
		loadMetrics();
		if (onRefresh) onRefresh();
	};

	return (
		<WidgetBase
			config={config}
			onConfigChange={onConfigChange}
			onRemove={onRemove}
			onRefresh={handleRefresh}
			loading={loading || localLoading}
			error={error || localError}
		>
			<SystemMetrics data={metrics} loading={loading || localLoading} />
		</WidgetBase>
	);
};

export default SystemMetricsWidget;