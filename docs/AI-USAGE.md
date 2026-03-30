# AI 改写功能使用指南

本文档详细介绍如何使用 Wechatsync 的 AI 改写功能，包括配置、使用方法和最佳实践。

## 📋 目录

- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [改写风格](#改写风格)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 🚀 快速开始

### 1. 配置环境变量

```bash
# 必需：AI API 密钥
export AI_API_KEY="sk-xxx"

# 可选：AI 提供商（默认：openai）
export AI_PROVIDER="openai"  # 或 "anthropic"

# 可选：自定义模型
export AI_MODEL="gpt-4-turbo-preview"

# 可选：自定义 API 基础 URL
export AI_BASE_URL="https://api.openai.com/v1"
```

### 2. 配置 MCP Server

编辑 MCP 配置文件：

```json
// ~/.claude/claude_desktop_config.json
{
  "mcpServers": {
    "sync-assistant": {
      "command": "node",
      "args": ["/path/to/Wechatsync/packages/mcp-server/dist/index.js"],
      "env": {
        "MCP_TOKEN": "your-token",
        "AI_PROVIDER": "openai",
        "AI_API_KEY": "sk-xxx"
      }
    }
  }
}
```

### 3. 使用

在 Claude Code 中：

```
"请改写这篇文章：标题是'测试文章'，内容是'<p>这是一段测试内容</p>'"
"用轻松的风格改写这篇文章并同步到知乎和掘金"
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `AI_API_KEY` | ✅ | AI API 密钥 | - |
| `AI_PROVIDER` | ❌ | AI 提供商 | `openai` |
| `AI_MODEL` | ❌ | 使用的模型 | `gpt-4-turbo-preview` (OpenAI)<br>`claude-3-5-sonnet-20241022` (Anthropic) |
| `AI_BASE_URL` | ❌ | API 基础 URL | OpenAI: `https://api.openai.com/v1`<br>Anthropic: `https://api.anthropic.com/v1` |

### 支持的 AI 提供商

#### OpenAI

```bash
export AI_PROVIDER="openai"
export AI_API_KEY="sk-xxx"
export AI_MODEL="gpt-4-turbo-preview"  # 可选
```

**推荐模型**：
- `gpt-4-turbo-preview` - 最新、最强大（推荐）
- `gpt-4` - 稳定版本
- `gpt-3.5-turbo` - 快速、经济

#### Anthropic

```bash
export AI_PROVIDER="anthropic"
export AI_API_KEY="sk-ant-xxx"
export AI_MODEL="claude-3-5-sonnet-20241022"  # 可选
```

**推荐模型**：
- `claude-3-5-sonnet-20241022` - 最新版本（推荐）
- `claude-3-opus-20240229` - 最强大
- `claude-3-haiku-20240307` - 快速、经济

## 📖 使用方法

### 方式一：MCP Server（推荐）

#### 1. 改写文章

```
"请改写这篇文章：
标题：Ractor 下多线程 Ruby 程序指南
内容：<p>Ractor 是 Ruby 3 新引入的特性...</p>
风格：专业"
```

#### 2. 改写并同步

```
"请改写这篇文章并同步到知乎和掘金：
标题：测试文章
内容：<p>这是内容</p>
风格：轻松"
```

#### 3. 从 URL 改写并同步

```
"请从 https://mp.weixin.qq.com/s/xxx 提取文章，改写后同步到知乎、掘金、CSDN"
```

### 方式二：直接调用 API

```typescript
import { createArticleRewriter } from '@wechatsync/core'

// 创建改写器
const rewriter = createArticleRewriter({
  provider: 'openai',
  apiKey: 'sk-xxx',
  model: 'gpt-4-turbo-preview'
})

// 改写文章
const rewritten = await rewriter.rewrite(
  {
    title: '原始标题',
    content: '<p>原始内容</p>',
    cover: 'https://example.com/cover.jpg'
  },
  {
    style: 'professional',
    preserveStructure: true
  }
)

console.log('改写后标题:', rewritten.title)
console.log('改写后内容:', rewritten.content)
```

### 方式三：批量改写

```typescript
const articles = [
  { title: '文章1', content: '<p>内容1</p>' },
  { title: '文章2', content: '<p>内容2</p>' },
  { title: '文章3', content: '<p>内容3</p>' }
]

const results = await rewriter.rewriteBatch(articles, {
  style: 'professional'
})

console.log(`成功改写 ${results.length} 篇文章`)
```

## 🎨 改写风格

### 1. 专业风格（professional）

**特点**：
- 严谨、客观、专业术语准确
- 适合技术文章、学术论文
- 保持专业性和权威性

**示例**：

**原文**：
```
Ractor 是 Ruby 3 的新东西，可以让大家一起跑代码。
```

**改写后**：
```
Ractor 是 Ruby 3 引入的并发编程模型，通过内存隔离机制实现了真正的并行执行能力，
显著提升了多核处理器的利用率。
```

### 2. 轻松风格（casual）

**特点**：
- 口语化、易读、贴近读者
- 适合博客、公众号文章
- 增强亲和力和可读性

**示例**：

**原文**：
```
Ractor 通过内存隔离机制实现了真正的并行执行能力。
```

**改写后**：
```
简单来说，Ractor 就像是给 Ruby 装上了"多核处理器"，
让代码可以真正地同时跑起来，不再被锁住啦！
```

### 3. 创意风格（creative）

**特点**：
- 有趣、吸引人、新颖视角
- 适合营销文案、创意内容
- 增强吸引力和传播性

**示例**：

**原文**：
```
Ractor 是 Ruby 3 引入的并发编程模型。
```

**改写后**：
```
想象一下，你的 Ruby 代码终于可以"分身术"了！
Ractor 就像是给每个任务都配了一个独立的"小助手"，
它们互不干扰，同时工作，效率直接起飞！🚀
```

### 4. 简洁风格（concise）

**特点**：
- 精炼、重点突出、去除冗余
- 适合快讯、摘要
- 提高信息密度

**示例**：

**原文**：
```
Ractor 是 Ruby 3 新引入的特性。Ractor 顾名思义是 Ruby 和 Actor 的组合，
它提供了一种在 Ruby 中实现真正并行执行的方式。在传统的 Ruby 程序中，
由于 GIL (Global Interpreter Lock) 的存在，多线程并不能真正实现并行执行。
而 Ractor 通过隔离内存空间，允许多个 Ractor 同时执行，从而实现真正的并行。
```

**改写后**：
```
Ractor：Ruby 3 并发新特性
- 真正的并行执行（突破 GIL 限制）
- 内存隔离机制
- 多核处理器优化
```

## 🔧 高级功能

### 1. 保留结构

```typescript
await rewriter.rewrite(article, {
  style: 'professional',
  preserveStructure: true  // 保持原有段落结构、标题层级
})
```

### 2. 指定目标受众

```typescript
await rewriter.rewrite(article, {
  style: 'professional',
  targetAudience: '有 3-5 年经验的开发者'
})
```

### 3. 自定义提示词

```typescript
await rewriter.rewrite(article, {
  customPrompt: `
    请用幽默的语气改写这篇文章，要求：
    1. 保持原意
    2. 增加趣味性
    3. 适合在社交媒体传播
  `
})
```

### 4. 批量改写

```typescript
const results = await rewriter.rewriteBatch(articles, {
  style: 'professional'
})

console.log(`成功: ${results.length}/${articles.length}`)
```

## 💡 最佳实践

### 1. 选择合适的风格

| 文章类型 | 推荐风格 | 理由 |
|----------|----------|------|
| 技术教程 | `professional` | 保持专业性和准确性 |
| 博客文章 | `casual` | 增强可读性和亲和力 |
| 营销文案 | `creative` | 提高吸引力和传播性 |
| 新闻快讯 | `concise` | 提高信息密度 |

### 2. 保留关键信息

```typescript
await rewriter.rewrite(article, {
  style: 'professional',
  preserveStructure: true  // 保留代码块、表格等特殊格式
})
```

### 3. 多次迭代优化

```
第一次："用专业风格改写"
第二次："在改写的基础上，让标题更吸引人"
第三次："优化开头，让读者更容易理解"
```

### 4. 结合平台特性

```
"改写这篇文章，风格要适合知乎，加入一些专业分析和数据引用"
"改写这篇文章，风格要适合公众号，增加一些互动性的表达"
```

### 5. 控制成本

- 使用 `gpt-3.5-turbo` 或 `claude-3-haiku` 进行初稿改写
- 使用 `gpt-4-turbo` 或 `claude-3-opus` 进行最终优化
- 批量改写时添加延迟，避免 API 限流

## 🔍 故障排除

### 问题 1：AI 改写功能未启用

**错误信息**：
```
AI 改写功能未启用。请设置环境变量：
- AI_API_KEY: AI API 密钥
- AI_PROVIDER: 提供商（openai 或 anthropic，默认 openai）
```

**解决方案**：
```bash
# 检查环境变量
echo $AI_API_KEY

# 设置环境变量
export AI_API_KEY="sk-xxx"
```

### 问题 2：API 密钥无效

**错误信息**：
```
OpenAI API error: 401 - Unauthorized
```

**解决方案**：
1. 检查 API 密钥是否正确
2. 检查 API 密钥是否有效（未过期）
3. 检查 API 密钥是否有足够的配额

### 问题 3：API 限流

**错误信息**：
```
OpenAI API error: 429 - Too Many Requests
```

**解决方案**：
1. 降低请求频率
2. 使用批量改写功能（内置延迟）
3. 升级 API 套餐

### 问题 4：改写质量不佳

**解决方案**：
1. 尝试不同的风格
2. 使用自定义提示词
3. 指定目标受众
4. 使用更强大的模型（如 `gpt-4-turbo`）

### 问题 5：改写后格式丢失

**解决方案**：
```typescript
await rewriter.rewrite(article, {
  preserveStructure: true  // 保留原有结构
})
```

## 📊 性能优化

### 1. 缓存改写结果

```typescript
const cache = new Map<string, RewrittenArticle>()

async function rewriteWithCache(article: Article, options: RewriteOptions) {
  const key = `${article.title}-${article.content}-${JSON.stringify(options)}`
  
  if (cache.has(key)) {
    return cache.get(key)!
  }
  
  const result = await rewriter.rewrite(article, options)
  cache.set(key, result)
  
  return result
}
```

### 2. 并发控制

```typescript
import pLimit from 'p-limit'

const limit = pLimit(3)  // 最多 3 个并发请求

const results = await Promise.all(
  articles.map(article => 
    limit(() => rewriter.rewrite(article))
  )
)
```

### 3. 错误重试

```typescript
async function rewriteWithRetry(
  article: Article,
  options: RewriteOptions,
  maxRetries = 3
) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await rewriter.rewrite(article, options)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
}
```

## 🔗 相关资源

- [AI 集成完整指南](./AI-INTEGRATION.md)
- [API 文档](./API.md)
- [MCP Server 文档](../packages/mcp-server/README.md)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com)

## 📝 更新日志

### v1.0.0 (2024-01-15)

- ✅ 支持 OpenAI 和 Anthropic 提供商
- ✅ 四种改写风格
- ✅ MCP Server 集成
- ✅ 批量改写功能
- ✅ 自定义提示词

---

**问题反馈**：如有问题或建议，请在 [GitHub Issues](https://github.com/wechatsync/Wechatsync/issues) 中提交。
