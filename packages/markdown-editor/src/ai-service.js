import { generateText } from 'ai'
import { createOpenAI } from '@ai-sdk/openai'
import { createAnthropic } from '@ai-sdk/anthropic'
import { evaluateRewriteQuality, getRewriteModeDescription } from './rewrite-evaluator'

const REWRITE_PROMPTS = {
  full: '请改写以下文章，保持原意但改变表达方式，使其更加流畅自然：\n\n',
  title: '请改写以下文章标题，使其更加吸引人：\n\n',
  summary: '请为以下文章生成一个简洁的摘要（100字以内）：\n\n',
  expand: '请扩展以下文章内容，增加更多细节和例子：\n\n',
  simplify: '请简化以下文章，使其更易理解：\n\n',
  professional: '请将以下文章改写为更专业的技术文章风格：\n\n',
  casual: '请将以下文章改写为更轻松的博客风格：\n\n',

  academic: `请将以下内容用更高级的学术语言改写，要求：
1. 不改变原意
2. 不要出现AI生成的语言痕迹
3. 句式多样、结构复杂
4. 避免使用"显著提升""在当今背景下"等AI常用表达
5. 使用学术领域的专业术语

原文如下：
`,

  human_rhythm: `请将以下文字以人类语言的写作习惯改写，要求：
1. 适当加入副词、停顿词、断句标点
2. 降低AI识别概率
3. 避免格式统一化
4. 模仿真实的写作节奏
5. 使用口语化表达

原文如下：
`,

  logic_restructure: `请将以下内容进行逻辑重构改写，要求：
1. 改变论证顺序，打破线性逻辑
2. 增加逻辑转折和跳跃
3. 插入个人见解或案例
4. 使用倒装、设问等句式
5. 增加句子的"熵值"

原文如下：
`,

  sentence_restructure: `请将以下段落逐句重写，要求：
1. 每句话采用不同的句式结构（倒装/主被动/插入语等）
2. 降低重复率和AI检测相似度
3. 保持语义连贯
4. 增加句式变化
5. 避免句式过于统一

原文如下：
`,

  keyword_replace: `请帮我将以下学术段落改写，要求：
1. 关键词换成近义词或解释型表达
2. 适当插入简短注释或举例
3. 增强"人写感"
4. 保持专业性
5. 加入具体案例或数据

原文如下：
`,

  anti_detection: `请将以下内容进行深度改写，要求：
1. 改变论证顺序，打破高概率路径
2. 插入低频语义噪声（具体数据、地域特色、时间细节）
3. 频繁交替使用主动/被动语态
4. 将陈述句改为反问、设问
5. 增加句子的复杂度和变化
6. 模仿人类写作的跳跃性思维
7. 避免使用AI常用的高频词汇组合

原文如下：
`
}

const REWRITE_MODES = {
  full: { name: '全文改写', description: '保持原意，改变表达方式' },
  title: { name: '标题优化', description: '让标题更吸引人' },
  summary: { name: '生成摘要', description: '生成简洁摘要（100字内）' },
  expand: { name: '内容扩展', description: '增加细节和例子' },
  simplify: { name: '内容简化', description: '使文章更易理解' },
  professional: { name: '专业风格', description: '改写为技术文章风格' },
  casual: { name: '轻松风格', description: '改写为博客风格' },
  academic: { name: '学术风格', description: '高级学术语言，避免AI痕迹' },
  human_rhythm: { name: '人类节奏', description: '模仿人类写作节奏' },
  logic_restructure: { name: '逻辑重构', description: '打破线性逻辑，增加跳跃' },
  sentence_restructure: { name: '句式重组', description: '逐句改变句式结构' },
  keyword_replace: { name: '关键词替换', description: '换词不换义，加注释' },
  anti_detection: { name: '深度改写', description: '规避AI检测，人类化改写' }
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

    const rewrittenText = text.trim()

    const qualityScore = evaluateRewriteQuality(content, rewrittenText)

    return {
      text: rewrittenText,
      quality: qualityScore,
      mode: rewriteType,
      modeDescription: getRewriteModeDescription(rewriteType)
    }
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

    const rewrittenText = fullText.trim()

    const qualityScore = evaluateRewriteQuality(content, rewrittenText)

    return {
      text: rewrittenText,
      quality: qualityScore,
      mode: rewriteType,
      modeDescription: getRewriteModeDescription(rewriteType)
    }
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

export { REWRITE_PROMPTS, REWRITE_MODES }
