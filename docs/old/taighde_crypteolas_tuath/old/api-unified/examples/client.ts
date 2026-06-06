/**
 * Example TypeScript client demonstrating how to use the API Unified server
 *
 * This shows:
 * 1. oRPC typed client usage
 * 2. MCP client usage
 * 3. AI chat streaming
 * 4. REST API via fetch
 */

// ============================================================================
// 1. oRPC Client (Type-Safe RPC)
// ============================================================================

/*
import { createClient } from '@orpc/client';
import type { AppRouter } from '../src/rpc/router';

const rpcClient = createClient<AppRouter>({
  baseURL: 'http://localhost:3000/rpc',
  headers: {
    Authorization: 'Bearer token-1'
  }
});

// Fully typed with auto-complete!
async function demoRPC() {
  // Create a todo
  const todo = await rpcClient.todo.create({
    title: 'Learn API Unified',
    description: 'Understand MCP, oRPC, and AI streaming'
  });
  console.log('Created todo:', todo);

  // List todos
  const todos = await rpcClient.todo.list({
    limit: 10,
    completed: false
  });
  console.log('Todos:', todos);

  // Get server health
  const health = await rpcClient.public.health();
  console.log('Health:', health);

  // Get server info
  const info = await rpcClient.public.info();
  console.log('Info:', info);
}
*/

// ============================================================================
// 2. MCP Client (AI Tool Calling)
// ============================================================================

/*
import { McpClient } from '@modelcontextprotocol/sdk/client/mcp.js';

async function demoMCP() {
  const mcpClient = new McpClient({
    endpoint: 'http://localhost:3000/mcp'
  });

  await mcpClient.connect();

  // List available tools
  const tools = await mcpClient.listTools();
  console.log('Available tools:', tools);

  // Call add tool
  const addResult = await mcpClient.callTool('add', {
    a: 10,
    b: 20
  });
  console.log('Add result:', addResult);

  // Call search tool
  const searchResult = await mcpClient.callTool('search', {
    query: 'typescript',
    limit: 5
  });
  console.log('Search result:', searchResult);

  // Call analyzeText tool
  const analysisResult = await mcpClient.callTool('analyzeText', {
    text: 'This is a wonderful example of API design!',
    includeEntities: true,
    includeSentiment: true
  });
  console.log('Analysis result:', analysisResult);

  // List resources
  const resources = await mcpClient.listResources();
  console.log('Available resources:', resources);

  // Read a resource
  const todosResource = await mcpClient.readResource('resource://todos');
  console.log('Todos resource:', todosResource);

  await mcpClient.close();
}
*/

// ============================================================================
// 3. AI Chat Streaming
// ============================================================================

async function demoAIChat() {
  const response = await fetch('http://localhost:3000/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messages: [
        {
          role: 'user',
          content: 'Explain what MCP is in one sentence'
        }
      ],
      model: 'claude-3-5-sonnet-20241022',
      temperature: 0.7
    })
  });

  if (!response.body) {
    throw new Error('No response body');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  console.log('AI Response:');
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    process.stdout.write(chunk);
  }
  console.log('\n');
}

// ============================================================================
// 4. AI Chat with Tools
// ============================================================================

async function demoAIChatWithTools() {
  const response = await fetch('http://localhost:3000/ai/chat-with-tools', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messages: [
        {
          role: 'user',
          content: 'What is 15 + 27? Use the add tool.'
        }
      ]
    })
  });

  if (!response.body) {
    throw new Error('No response body');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  console.log('AI Response with Tools:');
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    process.stdout.write(chunk);
  }
  console.log('\n');
}

// ============================================================================
// 5. REST API via Fetch (OpenAPI endpoints)
// ============================================================================

async function demoREST() {
  // Get health status
  const healthResponse = await fetch('http://localhost:3000/api/public/health');
  const health = await healthResponse.json();
  console.log('Health (REST):', health);

  // Get server info
  const infoResponse = await fetch('http://localhost:3000/api/public/info');
  const info = await infoResponse.json();
  console.log('Info (REST):', info);

  // Create a todo (requires auth)
  const createResponse = await fetch('http://localhost:3000/api/todo/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer token-1'
    },
    body: JSON.stringify({
      title: 'REST API Todo',
      description: 'Created via OpenAPI endpoint'
    })
  });
  const todo = await createResponse.json();
  console.log('Created todo (REST):', todo);

  // List todos
  const listResponse = await fetch('http://localhost:3000/api/todo/list?limit=10', {
    headers: {
      'Authorization': 'Bearer token-1'
    }
  });
  const todos = await listResponse.json();
  console.log('Todos (REST):', todos);
}

// ============================================================================
// 6. Get OpenAPI Spec
// ============================================================================

async function demoOpenAPI() {
  const response = await fetch('http://localhost:3000/api/~openapi.json');
  const spec = await response.json();
  console.log('OpenAPI Spec:');
  console.log(JSON.stringify(spec, null, 2));
}

// ============================================================================
// Run Examples
// ============================================================================

async function main() {
  console.log('='.repeat(80));
  console.log('API Unified Client Examples');
  console.log('='.repeat(80));
  console.log();

  try {
    // Uncomment to run specific examples:

    // await demoRPC();
    // console.log('\n' + '-'.repeat(80) + '\n');

    // await demoMCP();
    // console.log('\n' + '-'.repeat(80) + '\n');

    await demoAIChat();
    console.log('\n' + '-'.repeat(80) + '\n');

    await demoAIChatWithTools();
    console.log('\n' + '-'.repeat(80) + '\n');

    await demoREST();
    console.log('\n' + '-'.repeat(80) + '\n');

    // await demoOpenAPI();

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
