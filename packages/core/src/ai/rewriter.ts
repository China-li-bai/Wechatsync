/**
 * AI 文章改写器
 * 
 * 支持多种 AI 提供商（OpenAI、Anthropic）和改写风格
 */

import type { RewriteStyle, RewriteOptions, RewrittenArticle } from './index'
import { createLogger } from '../lib/logger'

const logger = createLogger('ArticleRewriter')

/**
 * AI 提供商类型
 */
export type AIProvider = 'openai' | 'anthropic'

/**
 * AI 配置
 */
export interface AIConfig {
  provider: AIProvider
  apiKey: string
  baseUrl?: string
  model?: string
}

/**
 * 风格描述映射
 */
const STYLE_DESCRIPTIONS: Record<RewriteStyle, string> = {
  professional: '专业、严谨、客观，使用准确的专业术语，适合技术文章和学术内容',
  casual: '轻松、口语化、易读，贴近读者，适合博客和公众号文章',
  creative: '创意、有趣、吸引人，新颖的视角和表达方式，适合营销文案和创意内容',
  concise: '简洁、精炼、重点突出，去除冗余信息，适合快讯和摘要'
}

/**
 * OpenAI API 响应类型
 */
interface OpenAIResponse {
  choices: Array<{
    message: {
      content: string
    }
  }>
}

/**
 * Anthropic API 响应类型
 */
interface AnthropicResponse {
  content: Array<{
    type: 'text'
    text: string
  }>
}

/**
 * AI 文章改写器
 */
export class ArticleRewriter {
  private provider: AIProvider
  private apiKey: string
  private baseUrl: string
  private model: string

  constructor(config: AIConfig) {
    this.provider = config.provider
    this.apiKey = config.apiKey
    this.baseUrl = config.baseUrl || this.getDefaultBaseUrl()
    this.model = config.model || this.getDefaultModel()

    logger.info(`Initialized ArticleRewriter with provider: ${this.provider}, model: ${this.model}`)
  }

  /**
   * 获取默认 API 基础 URL
   */
  private getDefaultBaseUrl(): string {
    switch (this.provider) {
      case 'openai':
        return 'https://api.openai.com/v1'
      case 'anthropic':
        return 'https://api.anthropic.com/v1'
      default:
        throw new Error(`Unsupported AI provider: ${this.provider}`)
    }
  }

  /**
   * 获取默认模型
   */
  private getDefaultModel(): string {
    switch (this.provider) {
      case 'openai':
        return 'gpt-4-turbo-preview'
      case 'anthropic':
        return 'claude-3-5-sonnet-20241022'
      default:
        throw new Error(`Unsupported AI provider: ${this.provider}`)
    }
  }

  /**
   * 改写文章
   * 
   * @param article 原始文章
   * @param options 改写选项
   * @returns 改写后的文章
   */
  async rewrite(
    article: { title: string; content: string; cover?: string },
    options: RewriteOptions = {}
  ): Promise<RewrittenArticle> {
    const {
      style = 'professional',
      preserveStructure = true,
      targetAudience,
      customPrompt
    } = options

    logger.info(`Rewriting article with style: ${style}`)
    logger.debug('Original article:', { title: article.title, contentLength: article.content.length })

    // 构建提示词
    const prompt = this.buildPrompt(article, {
      style,
      preserveStructure,
      targetAudience,
      customPrompt
    })

    // 调用 AI API
    const response = await this.callAI(prompt)

    // 解析响应
    const rewritten = this.parseResponse(response)

    logger.info('Article rewritten successfully')
    logger.debug('Rewritten article:', { title: rewritten.title, contentLength: rewritten.content.length })

    return {
      ...rewritten,
      cover: article.cover,
      originalTitle: article.title,
      originalContent: article.content,
      style,
      timestamp: Date.now()
    }
  }

  /**
   * 构建提示词
   */
  private buildPrompt(
    article: { title: string; content: string },
    options: Required<Pick<RewriteOptions, 'style' | 'preserveStructure'>> & 
             Pick<RewriteOptions, 'targetAudience' | 'customPrompt'>
  ): string {
    const { style, preserveStructure, targetAudience, customPrompt } = options

    let prompt = customPrompt || `请改写以下文章，要求：

风格：${STYLE_DESCRIPTIONS[style]}
保留结构：${preserveStructure ? '是（保持原有的段落结构、标题层级）' : '否（可以重新组织结构）'}
${targetAudience ? `目标受众：${targetAudience}` : ''}

原始标题：${article.title}

原始内容：
${article.content}

请以 JSON 格式返回改写结果：
{
  "title": "改写后的标题",
  "content": "改写后的内容（HTML 格式）"
}

注意事项：
1. 标题要简洁有力，吸引读者
2. 内容要保持原意，但用更符合${style}风格的方式表达
3. 保留原文中的关键信息和数据
4. 如果原文有代码块、表格等特殊格式，请保留
5. 确保改写后的内容通顺、易读`

    return prompt
  }

  /**
   * 调用 AI API
   */
  private async callAI(prompt: string): Promise<string> {
    switch (this.provider) {
      case 'openai':
        return await this.callOpenAI(prompt)
      case 'anthropic':
        return await this.callAnthropic(prompt)
      default:
        throw new Error(`Unsupported AI provider: ${this.provider}`)
    }
  }

  /**
   * 调用 OpenAI API
   */
  private async callOpenAI(prompt: string): Promise<string> {
    const url = `${this.baseUrl}/chat/completions`

    logger.debug('Calling OpenAI API:', { url, model: this.model })

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: this.model,
        messages: [
          {
            role: 'system',
            content: '你是一个专业的内容改写助手。你擅长根据不同的风格要求改写文章，保持原意的同时让内容更具吸引力。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 4096,
        response_format: { type: 'json_object' }
      })
    })

    if (!response.ok) {
      const error = await response.text()
      logger.error('OpenAI API error:', { status: response.status, error })
      throw new Error(`OpenAI API error: ${response.status} - ${error}`)
    }

    const data = await response.json() as OpenAIResponse
    return data.choices[0].message.content
  }

  /**
   * 调用 Anthropic API
   */
  private async callAnthropic(prompt: string): Promise<string> {
    const url = `${this.baseUrl}/messages`

    logger.debug('Calling Anthropic API:', { url, model: this.model })

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({
        model: this.model,
        max_tokens: 4096,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    })

    if (!response.ok) {
      const error = await response.text()
      logger.error('Anthropic API error:', { status: response.status, error })
      throw new Error(`Anthropic API error: ${response.status} - ${error}`)
    }

    const data = await response.json() as AnthropicResponse
    return data.content[0].text
  }

  /**
   * 解析 AI 响应
   */
  private parseResponse(response: string): { title: string; content: string } {
    try {
      // 尝试提取 JSON
      const jsonMatch = response.match(/\{[\s\S]*\}/)
      if (!jsonMatch) {
        throw new Error('No JSON found in response')
      }

      const parsed = JSON.parse(jsonMatch[0])

      if (!parsed.title || !parsed.content) {
        throw new Error('Invalid response format: missing title or content')
      }

      return {
        title: parsed.title,
        content: parsed.content
      }
    } catch (error) {
      logger.error('Failed to parse AI response:', { error, response })
      throw new Error(`Failed to parse AI response: ${(error as Error).message}`)
    }
  }

  /**
   * 批量改写文章
   * 
   * @param articles 文章列表
   * @param options 改写选项
   * @returns 改写后的文章列表
   */
  async rewriteBatch(
    articles: Array<{ title: string; content: string; cover?: string }>,
    options: RewriteOptions = {}
  ): Promise<RewrittenArticle[]> {
    logger.info(`Batch rewriting ${articles.length} articles`)

    const results: RewrittenArticle[] = []

    for (const article of articles) {
      try {
        const rewritten = await this.rewrite(article, options)
        results.push(rewritten)

        // 添加延迟，避免 API 限流
        await this.delay(1000)
      } catch (error) {
        logger.error(`Failed to rewrite article: ${article.title}`, error)
        // 继续处理下一篇文章
      }
    }

    logger.info(`Batch rewrite completed: ${results.length}/${articles.length} successful`)
    return results
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

/**
 * 创建 AI 改写器实例
 */
export function createArticleRewriter(config: AIConfig): ArticleRewriter {
  return new ArticleRewriter(config)
}

/**
 * 从环境变量创建 AI 改写器
 */
export function createArticleRewriterFromEnv(): ArticleRewriter {
  const provider = (process.env.AI_PROVIDER || 'openai') as AIProvider
  const apiKey = process.env.AI_API_KEY

  if (!apiKey) {
    throw new Error('AI_API_KEY environment variable is required')
  }

  return new ArticleRewriter({
    provider,
    apiKey,
    baseUrl: process.env.AI_BASE_URL,
    model: process.env.AI_MODEL
  })
}
