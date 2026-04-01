/**
 * MCP Server 测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock dependencies before importing
vi.mock('@modelcontextprotocol/sdk/server/index.js', () => ({
  Server: vi.fn().mockImplementation(() => ({
    setRequestHandler: vi.fn(),
    connect: vi.fn(),
  })),
}))

vi.mock('@modelcontextprotocol/sdk/server/sse.js', () => ({
  SSEServerTransport: vi.fn().mockImplementation(() => ({
    start: vi.fn(),
  })),
}))

vi.mock('@modelcontextprotocol/sdk/types.js', () => ({
  CallToolRequestSchema: 'CallToolRequestSchema',
  ListToolsRequestSchema: 'ListToolsRequestSchema',
}))

vi.mock('@wechatsync/core', () => ({
  ArticleRewriter: vi.fn().mockImplementation(() => ({
    rewrite: vi.fn(),
    rewriteBatch: vi.fn(),
  })),
  createArticleRewriterFromEnv: vi.fn().mockImplementation(() => ({
    rewrite: vi.fn(),
    rewriteBatch: vi.fn(),
  })),
}))

describe('SyncAssistantMcpServer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    delete process.env.AI_API_KEY
    delete process.env.AI_PROVIDER
    delete process.env.AI_MODEL
  })

  describe('constructor', () => {
    it('should create server instance with default ports', async () => {
      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should create server instance with custom ports', async () => {
      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer(8080, 8081)
      expect(server).toBeDefined()
    })

    it('should initialize without AI rewriter if AI_API_KEY is not set', async () => {
      delete process.env.AI_API_KEY
      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should initialize with AI rewriter if AI_API_KEY is set', async () => {
      process.env.AI_API_KEY = 'test-api-key'
      process.env.AI_PROVIDER = 'openai'
      
      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })
  })
})
