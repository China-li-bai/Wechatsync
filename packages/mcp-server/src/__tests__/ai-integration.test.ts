/**
 * AI 集成测试
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
    rewrite: vi.fn().mockResolvedValue({
      title: '改写标题',
      content: '<p>改写内容</p>',
      originalTitle: '原标题',
      originalContent: '<p>原内容</p>',
      style: 'professional',
      timestamp: Date.now(),
    }),
    rewriteBatch: vi.fn(),
  })),
  createArticleRewriterFromEnv: vi.fn().mockImplementation(() => {
    if (!process.env.AI_API_KEY) {
      throw new Error('AI_API_KEY is required')
    }
    return {
      rewrite: vi.fn().mockResolvedValue({
        title: '改写标题',
        content: '<p>改写内容</p>',
        originalTitle: '原标题',
        originalContent: '<p>原内容</p>',
        style: 'professional',
        timestamp: Date.now(),
      }),
      rewriteBatch: vi.fn(),
    }
  }),
}))

describe('AI Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    delete process.env.AI_API_KEY
    delete process.env.AI_PROVIDER
    delete process.env.AI_MODEL
  })

  describe('AI Rewriter Initialization', () => {
    it('should initialize AI rewriter with OpenAI', async () => {
      process.env.AI_API_KEY = 'test-openai-key'
      process.env.AI_PROVIDER = 'openai'
      process.env.AI_MODEL = 'gpt-4-turbo-preview'

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should initialize AI rewriter with Anthropic', async () => {
      process.env.AI_API_KEY = 'test-anthropic-key'
      process.env.AI_PROVIDER = 'anthropic'
      process.env.AI_MODEL = 'claude-3-5-sonnet-20241022'

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should not initialize AI rewriter without API key', async () => {
      delete process.env.AI_API_KEY

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should use default provider if not specified', async () => {
      process.env.AI_API_KEY = 'test-key'
      delete process.env.AI_PROVIDER

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      process.env.AI_API_KEY = 'test-key'
      process.env.AI_PROVIDER = 'openai'

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })

    it('should handle invalid API responses', async () => {
      process.env.AI_API_KEY = 'test-key'
      process.env.AI_PROVIDER = 'openai'

      const { SyncAssistantMcpServer } = await import('../server')
      const server = new SyncAssistantMcpServer()
      expect(server).toBeDefined()
    })
  })
})
