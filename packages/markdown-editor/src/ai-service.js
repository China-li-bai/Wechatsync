import { generateText } from 'ai'
import { createOpenAI } from '@ai-sdk/openai'
import { createAnthropic } from '@ai-sdk/anthropic'

const REWRITE_PROMPTS = {
  full: '请改写以下文章，保持原意但改变表达方式，使其更加流畅自然：\n\n',
  title: '请改写以下文章标题，使其更加吸引人：\n\n',
  summary: '请为以下文章生成一个简洁的摘要（100字以内）：\n\n',
  expand: '请扩展以下文章内容，增加更多细节和例子：\n\n',
  simplify: '请简化以下文章，使其更易理解：\n\n',
  professional: '请将以下文章改写为更专业的技术文章风格：\n\n',
  casual: '请将以下文章改写为更轻松的博客风格：\n\n'
}

function getModel(provider, apiKey, model) {
  if (provider === 'openai') {
    const openai = createOpenAI({ apiKey })
    return openai(model)
  } else if (provider === 'anthropic') {
    const anthropic = createAnthropic({ apiKey })
    return anthropic(model)
  } else if (provider === 'deepseek') {
    const deepseek = createOpenAI({
      apiKey,
      baseURL: 'https://api.deepseek.com/v1'
    })
    return deepseek(model)
  } else if (provider === 'zhipu') {
    const zhipu = createOpenAI({
      apiKey,
      baseURL: 'https://open.bigmodel.cn/api/paas/v4/'
    })
    return zhipu(model)
  }

  throw new Error(`不支持的AI服务商: ${provider}`)
}

export async function rewriteContent(config) {
  const { provider, apiKey, model, rewriteType, content } = config

  if (!apiKey) {
    throw new Error('请输入API密钥')
  }

  if (!content) {
    throw new Error('请输入要改写的内容')
  }

  const prompt = REWRITE_PROMPTS[rewriteType] + content
  const aiModel = getModel(provider, apiKey, model)

  try {
    const { text } = await generateText({
      model: aiModel,
      prompt: prompt,
      temperature: 0.7,
      maxTokens: 4000
    })

    return text.trim()
  } catch (error) {
    console.error('AI改写失败:', error)
    throw new Error(error.message || 'AI改写失败，请检查API密钥和网络连接')
  }
}

export async function streamRewriteContent(config, onChunk) {
  const { provider, apiKey, model, rewriteType, content } = config

  if (!apiKey) {
    throw new Error('请输入API密钥')
  }

  if (!content) {
    throw new Error('请输入要改写的内容')
  }

  const prompt = REWRITE_PROMPTS[rewriteType] + content
  const aiModel = getModel(provider, apiKey, model)

  try {
    const { textStream } = await generateText({
      model: aiModel,
      prompt: prompt,
      temperature: 0.7,
      maxTokens: 4000
    })

    let fullText = ''
    for await (const textPart of textStream) {
      fullText += textPart
      if (onChunk) {
        onChunk(textPart)
      }
    }

    return fullText.trim()
  } catch (error) {
    console.error('AI改写失败:', error)
    throw new Error(error.message || 'AI改写失败，请检查API密钥和网络连接')
  }
}

export const PROVIDERS = {
  openai: {
    name: 'OpenAI',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    defaultModel: 'gpt-3.5-turbo'
  },
  anthropic: {
    name: 'Claude',
    models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
    defaultModel: 'claude-3-sonnet-20240229'
  },
  deepseek: {
    name: 'DeepSeek',
    models: ['deepseek-chat', 'deepseek-coder'],
    defaultModel: 'deepseek-chat'
  },
  zhipu: {
    name: '智谱AI',
    models: ['glm-4-flash', 'glm-4', 'glm-4-plus', 'glm-3-turbo'],
    defaultModel: 'glm-4-flash'
  }
}

export { REWRITE_PROMPTS }
