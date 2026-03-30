/**
 * AI 处理器接口
 * 后续实现真正的 AI 处理器时需实现此接口
 */
export interface AIProcessor {
  /**
   * 优化文章标题
   * @param title 原标题
   * @param platform 目标平台
   * @returns 优化后的标题选项
   */
  optimizeTitle(title: string, platform: string): Promise<string[]>

  /**
   * 生成文章摘要
   * @param content 文章内容 (HTML)
   * @param maxLength 最大长度
   */
  generateSummary(content: string, maxLength?: number): Promise<string>

  /**
   * 推荐标签
   * @param content 文章内容
   * @param platform 目标平台
   */
  suggestTags(content: string, platform: string): Promise<string[]>

  /**
   * 跨平台内容适配
   * @param content 原内容
   * @param sourcePlatform 来源平台
   * @param targetPlatform 目标平台
   */
  adaptContent(
    content: string,
    sourcePlatform: string,
    targetPlatform: string
  ): Promise<string>

  /**
   * 改写文章
   * @param article 文章对象
   * @param options 改写选项
   */
  rewriteArticle?(
    article: { title: string; content: string; cover?: string },
    options?: RewriteOptions
  ): Promise<RewrittenArticle>
}

/**
 * 改写风格
 */
export type RewriteStyle = 'professional' | 'casual' | 'creative' | 'concise'

/**
 * 改写选项
 */
export interface RewriteOptions {
  style?: RewriteStyle
  preserveStructure?: boolean
  targetAudience?: string
  customPrompt?: string
}

/**
 * 改写后的文章
 */
export interface RewrittenArticle {
  title: string
  content: string
  cover?: string
  originalTitle: string
  originalContent: string
  style: RewriteStyle
  timestamp: number
}

/**
 * 空实现 AI 处理器
 * 直接返回原值，不做任何处理
 */
export class NoopAIProcessor implements AIProcessor {
  async optimizeTitle(title: string): Promise<string[]> {
    return [title]
  }

  async generateSummary(content: string, maxLength = 200): Promise<string> {
    // 简单截取纯文本
    const text = content.replace(/<[^>]+>/g, '').trim()
    if (text.length <= maxLength) {
      return text
    }
    return text.slice(0, maxLength - 3) + '...'
  }

  async suggestTags(): Promise<string[]> {
    return []
  }

  async adaptContent(content: string): Promise<string> {
    return content
  }

  /**
   * 改写文章（空实现，直接返回原文章）
   */
  async rewriteArticle(
    article: { title: string; content: string; cover?: string },
    options?: RewriteOptions
  ): Promise<RewrittenArticle> {
    return {
      title: article.title,
      content: article.content,
      cover: article.cover,
      originalTitle: article.title,
      originalContent: article.content,
      style: options?.style || 'professional',
      timestamp: Date.now()
    }
  }
}

/**
 * AI 处理器工厂
 */
export type AIProcessorFactory = () => AIProcessor

/**
 * 默认 AI 处理器实例
 */
export const defaultAIProcessor = new NoopAIProcessor()

/**
 * AI 处理器配置
 * 后续可扩展支持不同的 AI Provider
 */
export interface AIConfig {
  provider?: 'openai' | 'claude' | 'local' | 'none'
  apiKey?: string
  baseUrl?: string
  model?: string
}

/**
 * 创建 AI 处理器
 * 当前仅返回 NoopAIProcessor，后续可扩展
 */
export function createAIProcessor(_config?: AIConfig): AIProcessor {
  // TODO: 后续根据 config.provider 创建对应的处理器
  // if (config?.provider === 'openai') {
  //   return new OpenAIProcessor(config)
  // }
  // if (config?.provider === 'claude') {
  //   return new ClaudeProcessor(config)
  // }

  return new NoopAIProcessor()
}

// 导出改写器
export {
  ArticleRewriter,
  createArticleRewriter,
  createArticleRewriterFromEnv,
  type AIProvider,
  type AIConfig as RewriterAIConfig
} from './rewriter'
