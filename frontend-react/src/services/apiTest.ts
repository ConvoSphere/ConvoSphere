import api from "./api";
import { message } from "antd";

export interface ApiTestResult {
  endpoint: string;
  method: string;
  success: boolean;
  responseTime: number;
  error?: string;
  data?: any;
}

export interface ApiTestSummary {
  total: number;
  successful: number;
  failed: number;
  averageResponseTime: number;
  results: ApiTestResult[];
}

class ApiTestService {
  private async testEndpoint(
    endpoint: string,
    method: string = "GET",
    data?: any
  ): Promise<ApiTestResult> {
    const startTime = Date.now();
    
    try {
      let response;
      switch (method.toUpperCase()) {
        case "GET":
          response = await api.get(endpoint);
          break;
        case "POST":
          response = await api.post(endpoint, data);
          break;
        case "PUT":
          response = await api.put(endpoint, data);
          break;
        case "DELETE":
          response = await api.delete(endpoint);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }

      const responseTime = Date.now() - startTime;
      
      return {
        endpoint,
        method,
        success: true,
        responseTime,
        data: response.data,
      };
    } catch (error: any) {
      const responseTime = Date.now() - startTime;
      
      return {
        endpoint,
        method,
        success: false,
        responseTime,
        error: error.response?.data?.detail || error.message || "Unknown error",
      };
    }
  }

  async testKnowledgeEndpoints(): Promise<ApiTestResult[]> {
    const endpoints = [
      { endpoint: "/knowledge/documents", method: "GET" },
      { endpoint: "/knowledge/tags", method: "GET" },
      { endpoint: "/knowledge/stats", method: "GET" },
      { endpoint: "/knowledge/search", method: "POST", data: { query: "test" } },
    ];

    const results: ApiTestResult[] = [];
    
    for (const ep of endpoints) {
      const result = await this.testEndpoint(ep.endpoint, ep.method, ep.data);
      results.push(result);
    }

    return results;
  }

  async testToolsEndpoints(): Promise<ApiTestResult[]> {
    const endpoints = [
      { endpoint: "/tools", method: "GET" },
      { endpoint: "/tools/categories/list", method: "GET" },
    ];

    const results: ApiTestResult[] = [];
    
    for (const ep of endpoints) {
      const result = await this.testEndpoint(ep.endpoint, ep.method, ep.data);
      results.push(result);
    }

    return results;
  }

  async testMcpEndpoints(): Promise<ApiTestResult[]> {
    const endpoints = [
      { endpoint: "/mcp/servers", method: "GET" },
      { endpoint: "/mcp/tools", method: "GET" },
    ];

    const results: ApiTestResult[] = [];
    
    for (const ep of endpoints) {
      const result = await this.testEndpoint(ep.endpoint, ep.method, ep.data);
      results.push(result);
    }

    return results;
  }

  async testAuthEndpoints(): Promise<ApiTestResult[]> {
    const endpoints = [
      { endpoint: "/auth/me", method: "GET" },
      { endpoint: "/users/profile", method: "GET" },
    ];

    const results: ApiTestResult[] = [];
    
    for (const ep of endpoints) {
      const result = await this.testEndpoint(ep.endpoint, ep.method, ep.data);
      results.push(result);
    }

    return results;
  }

  async runAllTests(): Promise<ApiTestSummary> {
    const allResults: ApiTestResult[] = [];
    
    // Test all endpoint categories
    const knowledgeResults = await this.testKnowledgeEndpoints();
    const toolsResults = await this.testToolsEndpoints();
    const mcpResults = await this.testMcpEndpoints();
    const authResults = await this.testAuthEndpoints();
    
    allResults.push(...knowledgeResults, ...toolsResults, ...mcpResults, ...authResults);
    
    const successful = allResults.filter(r => r.success).length;
    const failed = allResults.filter(r => !r.success).length;
    const averageResponseTime = allResults.reduce((sum, r) => sum + r.responseTime, 0) / allResults.length;
    
    return {
      total: allResults.length,
      successful,
      failed,
      averageResponseTime,
      results: allResults,
    };
  }

  async testSpecificEndpoint(endpoint: string, method: string = "GET", data?: any): Promise<ApiTestResult> {
    return await this.testEndpoint(endpoint, method, data);
  }
}

export const apiTestService = new ApiTestService();

// Utility function to show test results
export const showApiTestResults = (summary: ApiTestSummary) => {
  const successRate = ((summary.successful / summary.total) * 100).toFixed(1);
  
  if (summary.failed === 0) {
    message.success(`API Tests: ${summary.successful}/${summary.total} successful (${successRate}%)`);
  } else {
    message.warning(`API Tests: ${summary.successful}/${summary.total} successful (${successRate}%) - ${summary.failed} failed`);
  }
  
  // Log detailed results for debugging
  console.group("API Test Results");
  console.log("Summary:", summary);
  summary.results.forEach(result => {
    if (result.success) {
      console.log(`✅ ${result.method} ${result.endpoint} - ${result.responseTime}ms`);
    } else {
      console.error(`❌ ${result.method} ${result.endpoint} - ${result.error}`);
    }
  });
  console.groupEnd();
};