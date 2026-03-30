/**
 * AI 改写器单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ArticleRewriter, createArticleRewriter, createArticleRewriterFromEnv } from '../rewriter'
import type { RewriteStyle } from '../index'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('ArticleRewriter', () => {
  let rewriter: ArticleRewriter

  beforeEach(() => {
    vi.clearAllMocks()
    
    rewriter = new ArticleRewriter({
      provider: 'openai',
      apiKey: 'test-api-key',
      model: 'gpt-4-turbo-preview'
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('constructor', () => {
    it('should initialize with OpenAI provider', () => {
      expect(rewriter).toBeDefined()
    })

    it('should use default model if not specified', () => {
      const rewriterWithDefaultModel = new ArticleRewriter({
        provider: 'openai',
        apiKey: 'test-key'
      })
      expect(rewriterWithDefaultModel).toBeDefined()
    })

    it('should use custom base URL if provided', () => {
      const rewriterWithCustomUrl = new ArticleRewriter({
        provider: 'openai',
        apiKey: 'test-key',
        baseUrl: 'https://custom-api.openai.com/v1'
      })
      expect(rewriterWithCustomUrl).toBeDefined()
    })
  })

  describe('rewrite', () => {
    const mockArticle = {
      title: '测试文章标题',
      content: '<p>这是一段测试内容。</p>',
      cover: 'https://example.com/cover.jpg'
    }

    const mockOpenAIResponse = {
      choices: [
        {
          message: {
            content: JSON.stringify({
              title: '改写后的标题',
              content: '<p>改写后的内容。</p>'
            })
          }
        }
      ]
    }

    it('should rewrite article with professional style', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const result = await rewriter.rewrite(mockArticle, { style: 'professional' })

      expect(result.title).toBe('改写后的标题')
      expect(result.content).toBe('<p>改写后的内容。</p>')
      expect(result.originalTitle).toBe(mockArticle.title)
      expect(result.originalContent).toBe(mockArticle.content)
      expect(result.style).toBe('professional')
      expect(result.cover).toBe(mockArticle.cover)
      expect(result.timestamp).toBeDefined()

      expect(mockFetch).toHaveBeenCalledTimes(1)
      const [url, options] = mockFetch.mock.calls[0]
      expect(url).toContain('openai.com')
      expect(options.method).toBe('POST')
      expect(options.headers.Authorization).toBe('Bearer test-api-key')
    })

    it('should rewrite article with casual style', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const result = await rewriter.rewrite(mockArticle, { style: 'casual' })

      expect(result.style).toBe('casual')
      expect(mockFetch).toHaveBeenCalledTimes(1)
    })

    it('should rewrite article with creative style', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const result = await rewriter.rewrite(mockArticle, { style: 'creative' })

      expect(result.style).toBe('creative')
      expect(mockFetch).toHaveBeenCalledTimes(1)
    })

    it('should rewrite article with concise style', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const result = await rewriter.rewrite(mockArticle, { style: 'concise' })

      expect(result.style).toBe('concise')
      expect(mockFetch).toHaveBeenCalledTimes(1)
    })

    it('should preserve structure when specified', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      await rewriter.rewrite(mockArticle, { 
        style: 'professional',
        preserveStructure: true 
      })

      const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body)
      expect(requestBody.messages[1].content).toContain('保留结构：是')
    })

    it('should not preserve structure when specified', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      await rewriter.rewrite(mockArticle, { 
        style: 'professional',
        preserveStructure: false 
      })

      const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body)
      expect(requestBody.messages[1].content).toContain('保留结构：否')
    })

    it('should include target audience in prompt', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      await rewriter.rewrite(mockArticle, { 
        style: 'professional',
        targetAudience: '技术人员'
      })

      const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body)
      expect(requestBody.messages[1].content).toContain('目标受众：技术人员')
    })

    it('should use custom prompt when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const customPrompt = '请用幽默的语气改写这篇文章'
      await rewriter.rewrite(mockArticle, { 
        customPrompt 
      })

      const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body)
      expect(requestBody.messages[1].content).toBe(customPrompt)
    })

    it('should handle API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: async () => 'Unauthorized'
      })

      await expect(rewriter.rewrite(mockArticle)).rejects.toThrow('OpenAI API error: 401')
    })

    it('should handle invalid JSON response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          choices: [
            {
              message: {
                content: 'This is not JSON'
              }
            }
          ]
        })
      })

      await expect(rewriter.rewrite(mockArticle)).rejects.toThrow('Failed to parse AI response')
    })

    it('should handle missing title in response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          choices: [
            {
              message: {
                content: JSON.stringify({ content: 'Only content' })
              }
            }
          ]
        })
      })

      await expect(rewriter.rewrite(mockArticle)).rejects.toThrow('Invalid response format')
    })

    it('should handle missing content in response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          choices: [
            {
              message: {
                content: JSON.stringify({ title: 'Only title' })
              }
            }
          ]
        })
      })

      await expect(rewriter.rewrite(mockArticle)).rejects.toThrow('Invalid response format')
    })
  })

  describe('rewriteBatch', () => {
    const mockArticles = [
      { title: '文章1', content: '<p>内容1</p>' },
      { title: '文章2', content: '<p>内容2</p>' },
      { title: '文章3', content: '<p>内容3</p>' }
    ]

    const mockOpenAIResponse = {
      choices: [
        {
          message: {
            content: JSON.stringify({
              title: '改写标题',
              content: '<p>改写内容</p>'
            })
          }
        }
      ]
    }

    it('should rewrite multiple articles', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockOpenAIResponse
      })

      const results = await rewriter.rewriteBatch(mockArticles, { style: 'professional' })

      expect(results).toHaveLength(3)
      expect(mockFetch).toHaveBeenCalledTimes(3)
      
      results.forEach((result, index) => {
        expect(result.originalTitle).toBe(mockArticles[index].title)
        expect(result.originalContent).toBe(mockArticles[index].content)
      })
    })

    it('should continue on error', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockOpenAIResponse
        })
        .mockRejectedValueOnce(new Error('API error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockOpenAIResponse
        })

      const results = await rewriter.rewriteBatch(mockArticles)

      expect(results).toHaveLength(2)
      expect(mockFetch).toHaveBeenCalledTimes(3)
    })
  })

  describe('Anthropic provider', () => {
    let anthropicRewriter: ArticleRewriter

    beforeEach(() => {
      anthropicRewriter = new ArticleRewriter({
        provider: 'anthropic',
        apiKey: 'test-anthropic-key',
        model: 'claude-3-5-sonnet-20241022'
      })
    })

    it('should call Anthropic API', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                title: '改写标题',
                content: '<p>改写内容</p>'
              })
            }
          ]
        })
      })

      const result = await anthropicRewriter.rewrite({
        title: '测试标题',
        content: '<p>测试内容</p>'
      })

      expect(result.title).toBe('改写标题')
      expect(mockFetch).toHaveBeenCalledTimes(1)
      
      const [url, options] = mockFetch.mock.calls[0]
      expect(url).toContain('anthropic.com')
      expect(options.headers['x-api-key']).toBe('test-anthropic-key')
    })

    it('should handle Anthropic API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        text: async () => 'Bad request'
      })

      await expect(anthropicRewriter.rewrite({
        title: '测试',
        content: '内容'
      })).rejects.toThrow('Anthropic API error: 400')
    })
  })
})

describe('createArticleRewriter', () => {
  it('should create rewriter with config', () => {
    const rewriter = createArticleRewriter({
      provider: 'openai',
      apiKey: 'test-key'
    })
    expect(rewriter).toBeInstanceOf(ArticleRewriter)
  })
})

describe('createArticleRewriterFromEnv', () => {
  const originalEnv = process.env

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should create rewriter from environment variables', () => {
    process.env.AI_API_KEY = 'env-api-key'
    process.env.AI_PROVIDER = 'openai'
    process.env.AI_MODEL = 'gpt-4'

    const rewriter = createArticleRewriterFromEnv()
    expect(rewriter).toBeInstanceOf(ArticleRewriter)
  })

  it('should throw error if AI_API_KEY is not set', () => {
    delete process.env.AI_API_KEY

    expect(() => createArticleRewriterFromEnv()).toThrow('AI_API_KEY environment variable is required')
  })

  it('should use default provider if not set', () => {
    process.env.AI_API_KEY = 'test-key'
    delete process.env.AI_PROVIDER

    const rewriter = createArticleRewriterFromEnv()
    expect(rewriter).toBeInstanceOf(ArticleRewriter)
  })
})
