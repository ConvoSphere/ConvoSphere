import api from "./api";
import { config } from "../config";
import type { WidgetConfig } from "../components/widgets/WidgetBase";

export interface GridPosition {
	id: string;
	x: number;
	y: number;
	width: number;
	height: number;
}

export interface DashboardStateDTO {
	widgets: WidgetConfig[];
	layout: GridPosition[];
}

export const dashboardService = {
	async getMyDashboard(): Promise<DashboardStateDTO> {
		const res = await api.get(`${config.apiUrl}${config.apiEndpoints.config}/me/dashboard`);
		return res.data;
	},

	async saveMyDashboard(state: DashboardStateDTO): Promise<void> {
		await api.put(`${config.apiUrl}${config.apiEndpoints.config}/me/dashboard`, state);
	},
};