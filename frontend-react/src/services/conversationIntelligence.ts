import api from './api';
import config from '../config';

export interface AnalyticsFilters {
  dateRange?: {
    start: string;
    end: string;
  };
  conversationIds?: string[];
  userIds?: string[];
  assistantIds?: string[];
  tags?: string[];
}

export interface SentimentAnalysis {
  conversationId: string;
  overallSentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number;
  messageSentiments: Array<{
    messageId: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    score: number;
    timestamp: string;
  }>;
}

export interface TopicCluster {
  id: string;
  name: string;
  keywords: string[];
  frequency: number;
  conversations: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
}

export interface UserBehaviorMetrics {
  userId: string;
  username: string;
  totalConversations: number;
  avgMessagesPerConversation: number;
  avgResponseTime: number;
  satisfactionScore: number;
  preferredTopics: string[];
  activeHours: number[];
}

export interface ConversationAnalytics {
  totalConversations: number;
  totalMessages: number;
  avgConversationLength: number;
  avgResponseTime: number;
  satisfactionTrend: Array<{
    date: string;
    score: number;
  }>;
  topTopics: TopicCluster[];
  userEngagement: UserBehaviorMetrics[];
}

export const conversationIntelligenceService = {
  // Get overall analytics
  getAnalytics: async (filters?: AnalyticsFilters): Promise<ConversationAnalytics> => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/analytics`, {
      params: filters,
    });
    return response.data;
  },

  // Get sentiment analysis for specific conversation
  getSentimentAnalysis: async (conversationId: string): Promise<SentimentAnalysis> => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/sentiment/${conversationId}`);
    return response.data;
  },

  // Get topic clustering
  getTopicClustering: async (filters?: AnalyticsFilters): Promise<TopicCluster[]> => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/topics`, {
      params: filters,
    });
    return response.data;
  },

  // Get user behavior analysis
  getUserBehaviorAnalysis: async (filters?: AnalyticsFilters): Promise<UserBehaviorMetrics[]> => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/user-behavior`, {
      params: filters,
    });
    return response.data;
  },

  // Get conversation quality metrics
  getQualityMetrics: async (conversationId: string) => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/quality/${conversationId}`);
    return response.data;
  },

  // Export analytics data
  exportAnalytics: async (filters?: AnalyticsFilters, format: 'csv' | 'json' = 'csv') => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/export`, {
      params: { ...filters, format },
      responseType: 'blob',
    });
    return response.data;
  },

  // Get real-time analytics updates
  getRealTimeMetrics: async () => {
    const response = await api.get(`${config.apiEndpoints.intelligence}/realtime`);
    return response.data;
  },
};