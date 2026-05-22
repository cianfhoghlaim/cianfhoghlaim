/**
 * Comprehensive test script to verify all API endpoints
 * Run this after starting the server to ensure everything works
 */

const BASE_URL = 'http://localhost:3000';
const AUTH_TOKEN = 'token-1';

interface TestResult {
  name: string;
  success: boolean;
  error?: string;
  response?: any;
}

const results: TestResult[] = [];

function logTest(name: string, success: boolean, error?: string, response?: any) {
  results.push({ name, success, error, response });
  const icon = success ? '✅' : '❌';
  console.log(`${icon} ${name}`);
  if (error) {
    console.log(`   Error: ${error}`);
  }
}

// ============================================================================
// Test Helpers
// ============================================================================

async function testEndpoint(
  name: string,
  url: string,
  options?: RequestInit
): Promise<TestResult> {
  try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
    }

    logTest(name, true, undefined, data);
    return { name, success: true, response: data };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logTest(name, false, errorMsg);
    return { name, success: false, error: errorMsg };
  }
}

// ============================================================================
// Root & Info Tests
// ============================================================================

async function testRootEndpoints() {
  console.log('\n📋 Root & Info Endpoints');
  console.log('─'.repeat(50));

  await testEndpoint(
    'Get API Info',
    `${BASE_URL}/`
  );
}

// ============================================================================
// Public Endpoints (No Auth)
// ============================================================================

async function testPublicEndpoints() {
  console.log('\n🌐 Public Endpoints');
  console.log('─'.repeat(50));

  await testEndpoint(
    'Health Check (OpenAPI)',
    `${BASE_URL}/api/public/health`
  );

  await testEndpoint(
    'Server Info (OpenAPI)',
    `${BASE_URL}/api/public/info`
  );

  await testEndpoint(
    'Health Check (oRPC)',
    `${BASE_URL}/rpc/public/health`,
    { method: 'POST' }
  );

  await testEndpoint(
    'Server Info (oRPC)',
    `${BASE_URL}/rpc/public/info`,
    { method: 'POST' }
  );
}

// ============================================================================
// Auth Endpoints
// ============================================================================

async function testAuthEndpoints() {
  console.log('\n🔐 Authentication Endpoints');
  console.log('─'.repeat(50));

  // Test signup
  const randomEmail = `test-${Date.now()}@example.com`;
  await testEndpoint(
    'Sign Up (OpenAPI)',
    `${BASE_URL}/api/auth/signup`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: randomEmail,
        name: 'Test User',
        password: 'password123'
      })
    }
  );

  // Test signin
  await testEndpoint(
    'Sign In (OpenAPI)',
    `${BASE_URL}/api/auth/signin`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'demo@example.com',
        password: 'password123'
      })
    }
  );

  // Test me endpoint
  await testEndpoint(
    'Get Current User (OpenAPI)',
    `${BASE_URL}/api/auth/me`,
    {
      headers: { 'Authorization': `Bearer ${AUTH_TOKEN}` }
    }
  );
}

// ============================================================================
// Todo Endpoints
// ============================================================================

async function testTodoEndpoints() {
  console.log('\n📝 Todo Endpoints');
  console.log('─'.repeat(50));

  // Create todo (OpenAPI)
  const createResult = await testEndpoint(
    'Create Todo (OpenAPI)',
    `${BASE_URL}/api/todo/create`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      },
      body: JSON.stringify({
        title: 'Test Todo from API',
        description: 'Created during endpoint testing'
      })
    }
  );

  // List todos (OpenAPI)
  await testEndpoint(
    'List Todos (OpenAPI)',
    `${BASE_URL}/api/todo/list?limit=10`,
    {
      headers: { 'Authorization': `Bearer ${AUTH_TOKEN}` }
    }
  );

  // Create todo (oRPC)
  await testEndpoint(
    'Create Todo (oRPC)',
    `${BASE_URL}/rpc/todo/create`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      },
      body: JSON.stringify({
        title: 'oRPC Todo',
        description: 'Created via oRPC endpoint'
      })
    }
  );

  // List todos (oRPC)
  await testEndpoint(
    'List Todos (oRPC)',
    `${BASE_URL}/rpc/todo/list`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      },
      body: JSON.stringify({ limit: 5 })
    }
  );

  // Update todo if we have one
  if (createResult.success && createResult.response?.id) {
    await testEndpoint(
      'Update Todo (OpenAPI)',
      `${BASE_URL}/api/todo/update`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${AUTH_TOKEN}`
        },
        body: JSON.stringify({
          id: createResult.response.id,
          completed: true
        })
      }
    );
  }
}

// ============================================================================
// MCP Tool Tests
// ============================================================================

async function testMCPTools() {
  console.log('\n🔧 MCP Tool Endpoints');
  console.log('─'.repeat(50));

  // List tools
  await testEndpoint(
    'List MCP Tools',
    `${BASE_URL}/mcp`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/list'
      })
    }
  );

  // Add tool
  await testEndpoint(
    'Call Add Tool',
    `${BASE_URL}/mcp`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/call',
        params: {
          name: 'add',
          arguments: { a: 10, b: 20 }
        }
      })
    }
  );

  // Search tool
  await testEndpoint(
    'Call Search Tool',
    `${BASE_URL}/mcp`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
          name: 'search',
          arguments: {
            query: 'test query',
            limit: 5
          }
        }
      })
    }
  );

  // Analyze text tool
  await testEndpoint(
    'Call Analyze Text Tool',
    `${BASE_URL}/mcp`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 4,
        method: 'tools/call',
        params: {
          name: 'analyzeText',
          arguments: {
            text: 'This is a test message!',
            includeEntities: true,
            includeSentiment: true
          }
        }
      })
    }
  );

  // Get current time tool
  await testEndpoint(
    'Call Get Current Time Tool',
    `${BASE_URL}/mcp`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 5,
        method: 'tools/call',
        params: {
          name: 'getCurrentTime',
          arguments: {}
        }
      })
    }
  );
}

// ============================================================================
// Documentation Tests
// ============================================================================

async function testDocumentation() {
  console.log('\n📚 Documentation Endpoints');
  console.log('─'.repeat(50));

  // Test OpenAPI spec
  try {
    const response = await fetch(`${BASE_URL}/api/~openapi.json`);
    const spec = await response.json();

    if (spec.openapi && spec.info && spec.paths) {
      logTest('Get OpenAPI Specification', true);
    } else {
      logTest('Get OpenAPI Specification', false, 'Invalid OpenAPI spec structure');
    }
  } catch (error) {
    logTest('Get OpenAPI Specification', false, error instanceof Error ? error.message : String(error));
  }
}

// ============================================================================
// AI Chat Tests (Optional - requires API key)
// ============================================================================

async function testAIChat() {
  console.log('\n💬 AI Chat Endpoints (Optional)');
  console.log('─'.repeat(50));

  // Note: These will fail if ANTHROPIC_API_KEY is not set
  // That's expected, so we don't mark them as critical failures

  try {
    const response = await fetch(`${BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [
          { role: 'user', content: 'Say "test successful" if you receive this' }
        ]
      })
    });

    if (response.ok) {
      logTest('AI Chat (Basic)', true);
    } else {
      const error = await response.text();
      logTest('AI Chat (Basic)', false, `Skipped - ${error}`);
    }
  } catch (error) {
    logTest('AI Chat (Basic)', false, 'Skipped - requires ANTHROPIC_API_KEY');
  }
}

// ============================================================================
// Main Test Runner
// ============================================================================

async function runAllTests() {
  console.log('\n');
  console.log('═'.repeat(50));
  console.log('🧪 API Unified - Endpoint Test Suite');
  console.log('═'.repeat(50));

  try {
    await testRootEndpoints();
    await testPublicEndpoints();
    await testAuthEndpoints();
    await testTodoEndpoints();
    await testMCPTools();
    await testDocumentation();
    await testAIChat();

    // Print summary
    console.log('\n');
    console.log('═'.repeat(50));
    console.log('📊 Test Summary');
    console.log('═'.repeat(50));

    const passed = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    const total = results.length;
    const percentage = ((passed / total) * 100).toFixed(1);

    console.log(`Total:  ${total} tests`);
    console.log(`Passed: ${passed} tests (${percentage}%)`);
    console.log(`Failed: ${failed} tests`);

    if (failed > 0) {
      console.log('\n❌ Failed Tests:');
      results
        .filter(r => !r.success)
        .forEach(r => console.log(`   - ${r.name}: ${r.error}`));
    }

    console.log('\n═'.repeat(50));

    if (failed === 0) {
      console.log('✅ All tests passed!');
    } else {
      console.log(`⚠️  ${failed} test(s) failed`);
    }

    console.log('═'.repeat(50));
    console.log('\n');

    process.exit(failed > 0 ? 1 : 0);

  } catch (error) {
    console.error('\n❌ Test suite error:', error);
    process.exit(1);
  }
}

// Run tests
runAllTests();
