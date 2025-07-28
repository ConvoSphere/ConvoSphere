#!/usr/bin/env node

/**
 * Backend Integration Test Script
 * Tests all API endpoints and verifies backend connectivity
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  baseURL: process.env.API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};

// Test results storage
const testResults = {
  total: 0,
  successful: 0,
  failed: 0,
  errors: [],
  responseTimes: [],
  timestamp: new Date().toISOString()
};

// Test endpoints configuration
const endpoints = [
  // Health check
  { method: 'GET', path: '/health', name: 'Health Check' },
  
  // Authentication
  { method: 'GET', path: '/api/v1/auth/me', name: 'Auth Me', requiresAuth: true },
  
  // Knowledge Base
  { method: 'GET', path: '/api/v1/knowledge/documents', name: 'Get Documents' },
  { method: 'GET', path: '/api/v1/knowledge/tags', name: 'Get Tags' },
  { method: 'GET', path: '/api/v1/knowledge/stats', name: 'Get Stats' },
  { method: 'POST', path: '/api/v1/knowledge/search', name: 'Search Documents', data: { query: 'test' } },
  
  // Tools
  { method: 'GET', path: '/api/v1/tools', name: 'Get Tools' },
  { method: 'GET', path: '/api/v1/tools/categories/list', name: 'Get Tool Categories' },
  
  // MCP
  { method: 'GET', path: '/api/v1/mcp/servers', name: 'Get MCP Servers' },
  { method: 'GET', path: '/api/v1/mcp/tools', name: 'Get MCP Tools' },
  
  // Users
  { method: 'GET', path: '/api/v1/users/profile', name: 'Get User Profile', requiresAuth: true },
  
  // Admin
  { method: 'GET', path: '/api/v1/admin/stats', name: 'Get Admin Stats', requiresAuth: true },
  { method: 'GET', path: '/api/v1/admin/audit-logs', name: 'Get Audit Logs', requiresAuth: true },
];

// Utility functions
const log = (message, type = 'info') => {
  const timestamp = new Date().toISOString();
  const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
  console.log(`${prefix} [${timestamp}] ${message}`);
};

const formatResponseTime = (time) => {
  if (time < 1000) return `${time}ms`;
  return `${(time / 1000).toFixed(2)}s`;
};

const getStatusColor = (status) => {
  if (status >= 200 && status < 300) return '\x1b[32m'; // Green
  if (status >= 400 && status < 500) return '\x1b[33m'; // Yellow
  return '\x1b[31m'; // Red
};

// Test individual endpoint
const testEndpoint = async (endpoint) => {
  const startTime = Date.now();
  const url = `${config.baseURL}${endpoint.path}`;
  
  try {
    log(`Testing ${endpoint.name} (${endpoint.method} ${endpoint.path})`);
    
    const response = await axios({
      method: endpoint.method,
      url,
      data: endpoint.data,
      timeout: config.timeout,
      headers: config.headers,
      validateStatus: () => true // Don't throw on HTTP error status
    });
    
    const responseTime = Date.now() - startTime;
    const status = response.status;
    const success = status >= 200 && status < 300;
    
    // Update test results
    testResults.total++;
    if (success) {
      testResults.successful++;
      log(`✅ ${endpoint.name}: ${status} (${formatResponseTime(responseTime)})`, 'success');
    } else {
      testResults.failed++;
      const error = {
        endpoint: endpoint.name,
        path: endpoint.path,
        method: endpoint.method,
        status,
        responseTime,
        error: response.data?.detail || response.statusText
      };
      testResults.errors.push(error);
      
      const color = getStatusColor(status);
      log(`${color}❌ ${endpoint.name}: ${status} - ${error.error}\x1b[0m`, 'error');
    }
    
    testResults.responseTimes.push(responseTime);
    
    return { success, status, responseTime, data: response.data };
    
  } catch (error) {
    const responseTime = Date.now() - startTime;
    testResults.total++;
    testResults.failed++;
    
    const errorInfo = {
      endpoint: endpoint.name,
      path: endpoint.path,
      method: endpoint.method,
      status: 'NETWORK_ERROR',
      responseTime,
      error: error.message
    };
    testResults.errors.push(errorInfo);
    
    log(`❌ ${endpoint.name}: Network Error - ${error.message}`, 'error');
    return { success: false, status: 'NETWORK_ERROR', responseTime, error: error.message };
  }
};

// Run all tests
const runTests = async () => {
  log('🚀 Starting Backend Integration Tests');
  log(`📍 Base URL: ${config.baseURL}`);
  log(`⏱️  Timeout: ${config.timeout}ms`);
  log('─'.repeat(60));
  
  // Test health endpoint first
  const healthTest = await testEndpoint(endpoints[0]);
  if (!healthTest.success) {
    log('❌ Health check failed. Backend might not be running.', 'error');
    log('💡 Make sure the backend server is started and accessible.');
    process.exit(1);
  }
  
  // Test all other endpoints
  for (let i = 1; i < endpoints.length; i++) {
    await testEndpoint(endpoints[i]);
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  // Generate summary
  generateSummary();
  
  // Save results to file
  saveResults();
};

// Generate test summary
const generateSummary = () => {
  const successRate = ((testResults.successful / testResults.total) * 100).toFixed(1);
  const avgResponseTime = testResults.responseTimes.length > 0 
    ? testResults.responseTimes.reduce((a, b) => a + b, 0) / testResults.responseTimes.length 
    : 0;
  
  log('─'.repeat(60));
  log('📊 TEST SUMMARY');
  log('─'.repeat(60));
  log(`Total Tests: ${testResults.total}`);
  log(`Successful: ${testResults.successful}`);
  log(`Failed: ${testResults.failed}`);
  log(`Success Rate: ${successRate}%`);
  log(`Average Response Time: ${formatResponseTime(avgResponseTime)}`);
  
  if (testResults.errors.length > 0) {
    log('\n❌ FAILED TESTS:');
    testResults.errors.forEach(error => {
      log(`  • ${error.endpoint} (${error.method} ${error.path})`);
      log(`    Status: ${error.status}, Error: ${error.error}`);
    });
  }
  
  if (successRate >= 90) {
    log('\n🎉 Backend integration looks good!', 'success');
  } else if (successRate >= 70) {
    log('\n⚠️  Backend integration has some issues. Check failed tests.', 'warning');
  } else {
    log('\n🚨 Backend integration has significant issues. Review failed tests.', 'error');
  }
};

// Save results to file
const saveResults = () => {
  const resultsDir = path.join(__dirname, '..', 'test-results');
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const filename = `backend-test-${new Date().toISOString().split('T')[0]}.json`;
  const filepath = path.join(resultsDir, filename);
  
  fs.writeFileSync(filepath, JSON.stringify(testResults, null, 2));
  log(`📄 Test results saved to: ${filepath}`);
};

// Performance analysis
const analyzePerformance = () => {
  if (testResults.responseTimes.length === 0) return;
  
  const times = testResults.responseTimes.sort((a, b) => a - b);
  const p50 = times[Math.floor(times.length * 0.5)];
  const p95 = times[Math.floor(times.length * 0.95)];
  const p99 = times[Math.floor(times.length * 0.99)];
  
  log('\n📈 PERFORMANCE ANALYSIS:');
  log(`50th percentile: ${formatResponseTime(p50)}`);
  log(`95th percentile: ${formatResponseTime(p95)}`);
  log(`99th percentile: ${formatResponseTime(p99)}`);
  
  // Performance recommendations
  if (p95 > 2000) {
    log('⚠️  Some endpoints are slow (>2s). Consider optimization.', 'warning');
  }
  if (p99 > 5000) {
    log('🚨 Some endpoints are very slow (>5s). Immediate attention needed.', 'error');
  }
};

// Main execution
const main = async () => {
  try {
    await runTests();
    analyzePerformance();
    
    // Exit with appropriate code
    const successRate = (testResults.successful / testResults.total) * 100;
    if (successRate >= 80) {
      process.exit(0); // Success
    } else {
      process.exit(1); // Failure
    }
  } catch (error) {
    log(`❌ Test execution failed: ${error.message}`, 'error');
    process.exit(1);
  }
};

// Handle command line arguments
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
Backend Integration Test Script

Usage: node test-backend-integration.js [options]

Options:
  --base-url <url>    Set the base URL for testing (default: http://localhost:8000)
  --timeout <ms>      Set request timeout in milliseconds (default: 10000)
  --help, -h          Show this help message

Environment Variables:
  API_URL             Set the base URL for testing

Examples:
  node test-backend-integration.js
  node test-backend-integration.js --base-url http://localhost:3000
  API_URL=http://localhost:3000 node test-backend-integration.js
  `);
  process.exit(0);
}

// Parse command line arguments
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--base-url' && args[i + 1]) {
    config.baseURL = args[i + 1];
    i++;
  } else if (args[i] === '--timeout' && args[i + 1]) {
    config.timeout = parseInt(args[i + 1]);
    i++;
  }
}

// Run the tests
main();