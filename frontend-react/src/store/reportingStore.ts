import { create } from "zustand";
import { reportingService, type TimeRange, type SystemSummary } from "../services/reporting";
import type { PerformanceData } from "../services/monitoring";
import type { SystemMetrics } from "../services/monitoring";

interface ReportingState {
  systemSummary: SystemSummary | null;
  systemMetrics: SystemMetrics | null;
  usageTrends: PerformanceData[];
  errorStats: any;
  timeRange: TimeRange;
  loading: boolean;
  error: string | null;

  setTimeRange: (range: TimeRange) => void;
  fetchSystemSummary: (token: string) => Promise<void>;
  fetchSystemMetrics: () => Promise<void>;
  fetchUsageTrends: (range: TimeRange, interval?: string) => Promise<void>;
  fetchErrorStats: (range?: TimeRange) => Promise<void>;
}

export const useReportingStore = create<ReportingState>((set, get) => ({
  systemSummary: null,
  systemMetrics: null,
  usageTrends: [],
  errorStats: null,
  timeRange: "24h",
  loading: false,
  error: null,

  setTimeRange: (range: TimeRange) => set({ timeRange: range }),

  fetchSystemSummary: async (token: string) => {
    set({ loading: true, error: null });
    try {
      const systemSummary = await reportingService.getSystemSummary(token);
      set({ systemSummary, loading: false });
    } catch (e: any) {
      set({ error: e?.message || "Failed to load system summary", loading: false });
    }
  },

  fetchSystemMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const systemMetrics = await reportingService.getSystemMetrics();
      set({ systemMetrics, loading: false });
    } catch (e: any) {
      set({ error: e?.message || "Failed to load system metrics", loading: false });
    }
  },

  fetchUsageTrends: async (range: TimeRange, interval: string = "1m") => {
    set({ loading: true, error: null, timeRange: range });
    try {
      const usageTrends = await reportingService.getUsageTrends(range, interval);
      set({ usageTrends, loading: false });
    } catch (e: any) {
      set({ error: e?.message || "Failed to load usage trends", loading: false });
    }
  },

  fetchErrorStats: async (range: TimeRange = "24h") => {
    set({ loading: true, error: null, timeRange: range });
    try {
      const errorStats = await reportingService.getErrorStats(range);
      set({ errorStats, loading: false });
    } catch (e: any) {
      set({ error: e?.message || "Failed to load error stats", loading: false });
    }
  },
}));