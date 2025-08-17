import { statisticsService, type OverviewStats } from "./statistics";
import { monitoringService, type PerformanceData, type SystemMetrics } from "./monitoring";

export type TimeRange = "1h" | "24h" | "7d" | "30d";

export interface SystemSummary {
	totalConversations: number;
	totalMessages: number;
	totalDocuments: number;
	totalAssistants: number;
	totalTools: number;
	activeUsers: number;
	systemHealth: "healthy" | "warning" | "error";
	performance: {
		cpuUsage: number;
		memoryUsage: number;
		responseTime: number;
		uptime: number;
	};
}

export const reportingService = {
	getSystemSummary: async (token: string): Promise<SystemSummary> => {
		const overview: OverviewStats = await statisticsService.getOverviewStats(token);
		return overview.systemStats;
	},

	getUsageTrends: async (timeRange: TimeRange, interval: string = "1m"): Promise<PerformanceData[]> => {
		return monitoringService.getPerformanceData(timeRange, interval);
	},

	getErrorStats: async (timeRange: TimeRange = "24h"): Promise<any> => {
		return monitoringService.getErrorStats(timeRange);
	},

	getSystemMetrics: async (): Promise<SystemMetrics> => {
		return monitoringService.getSystemMetrics();
	},
};