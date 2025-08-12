import { create } from "zustand";
import {
  conversationIntelligenceService,
  type AnalyticsFilters,
  type ConversationAnalytics,
  type SentimentAnalysis,
  type TopicCluster,
  type UserBehaviorMetrics,
} from "../services/conversationIntelligence";

interface ConversationIntelligenceState {
  // State
  analytics: ConversationAnalytics | null;
  sentimentAnalysis: SentimentAnalysis | null;
  topicClusters: TopicCluster[];
  userBehavior: UserBehaviorMetrics[];
  loading: boolean;
  error: string | null;
  filters: AnalyticsFilters | null;
  realTimeMetrics: any | null;

  // Actions
  fetchAnalytics: (filters?: AnalyticsFilters) => Promise<void>;
  fetchSentimentAnalysis: (conversationId: string) => Promise<void>;
  fetchTopicClustering: (filters?: AnalyticsFilters) => Promise<void>;
  fetchUserBehaviorAnalysis: (filters?: AnalyticsFilters) => Promise<void>;
  fetchRealTimeMetrics: () => Promise<void>;
  exportAnalytics: (
    filters?: AnalyticsFilters,
    format?: "csv" | "json",
  ) => Promise<void>;
  setFilters: (filters: AnalyticsFilters) => void;
  clearError: () => void;
  reset: () => void;
}

export const useConversationIntelligenceStore =
  create<ConversationIntelligenceState>((set, get) => ({
    // Initial state
    analytics: null,
    sentimentAnalysis: null,
    topicClusters: [],
    userBehavior: [],
    loading: false,
    error: null,
    filters: null,
    realTimeMetrics: null,

    // Actions
    fetchAnalytics: async (filters?: AnalyticsFilters) => {
      set({ loading: true, error: null });
      try {
        const analytics =
          await conversationIntelligenceService.getAnalytics(filters);
        set({ analytics, loading: false, filters: filters || null });
      } catch (error: any) {
        set({
          error: error.message || "Failed to fetch analytics",
          loading: false,
        });
      }
    },

    fetchSentimentAnalysis: async (conversationId: string) => {
      set({ loading: true, error: null });
      try {
        const sentimentAnalysis =
          await conversationIntelligenceService.getSentimentAnalysis(
            conversationId,
          );
        set({ sentimentAnalysis, loading: false });
      } catch (error: any) {
        set({
          error: error.message || "Failed to fetch sentiment analysis",
          loading: false,
        });
      }
    },

    fetchTopicClustering: async (filters?: AnalyticsFilters) => {
      set({ loading: true, error: null });
      try {
        const topicClusters =
          await conversationIntelligenceService.getTopicClustering(filters);
        set({ topicClusters, loading: false });
      } catch (error: any) {
        set({
          error: error.message || "Failed to fetch topic clustering",
          loading: false,
        });
      }
    },

    fetchUserBehaviorAnalysis: async (filters?: AnalyticsFilters) => {
      set({ loading: true, error: null });
      try {
        const userBehavior =
          await conversationIntelligenceService.getUserBehaviorAnalysis(
            filters,
          );
        set({ userBehavior, loading: false });
      } catch (error: any) {
        set({
          error: error.message || "Failed to fetch user behavior analysis",
          loading: false,
        });
      }
    },

    fetchRealTimeMetrics: async () => {
      try {
        const realTimeMetrics =
          await conversationIntelligenceService.getRealTimeMetrics();
        set({ realTimeMetrics });
      } catch (error: any) {
        console.error("Failed to fetch real-time metrics:", error);
      }
    },

    exportAnalytics: async (
      filters?: AnalyticsFilters,
      format: "csv" | "json" = "csv",
    ) => {
      try {
        const blob = await conversationIntelligenceService.exportAnalytics(
          filters,
          format,
        );
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `conversation-analytics-${new Date().toISOString().split("T")[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error: any) {
        set({ error: error.message || "Failed to export analytics" });
      }
    },

    setFilters: (filters: AnalyticsFilters) => {
      set({ filters });
    },

    clearError: () => {
      set({ error: null });
    },

    reset: () => {
      set({
        analytics: null,
        sentimentAnalysis: null,
        topicClusters: [],
        userBehavior: [],
        loading: false,
        error: null,
        filters: null,
        realTimeMetrics: null,
      });
    },
  }));
