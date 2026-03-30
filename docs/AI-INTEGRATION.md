# AI 改写集成方案

本文档介绍如何将 AI 改写功能集成到 Wechatsync，使用 agent-browser 实现自动化文章改写和同步。

## 🎯 目标

1. **AI 改写文章**：使用 AI 自动改写文章内容
2. **agent-browser 自动化**：通过浏览器自动化实现改写和同步
3. **多平台分发**：改写后自动同步到多个平台

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Wechatsync + AI                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  原始文章     │───▶│  AI 改写     │───▶│  同步分发    │  │
│  │  (提取)      │    │  (改写)      │    │  (发布)      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Content      │    │ AI Provider  │    │ Platform     │  │
│  │ Script       │    │ (OpenAI/     │    │ Adapters     │  │
│  │              │    │  Claude)     │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │         │
│         └────────────────────┴────────────────────┘         │
│                              │                               │
│                              ▼                               │
│                    ┌──────────────┐                         │
│                    │ agent-browser│                         │
│                    │ (自动化)      │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 📦 方案一：OpenClaw + agent-browser 集成

### 1. 安装 OpenClaw 和 agent-browser skill

```bash
# 安装 OpenClaw
pip install openclaw

# 安装 agent-browser skill
openclaw skill install agent-browser
```

### 2. 创建 OpenClaw Skill

创建 `skills/ai-rewrite-sync/skill.yaml`:

```yaml
name: ai-rewrite-sync
version: 1.0.0
description: AI 文章改写并同步到多平台
author: wechatsync

tools:
  - name: rewrite_article
    description: 使用 AI 改写文章内容
    parameters:
      type: object
      properties:
        article:
          type: object
          description: 文章对象
          properties:
            title:
              type: string
              description: 文章标题
            content:
              type: string
              description: 文章内容
        style:
          type: string
          description: 改写风格
          enum: [professional, casual, creative, concise]
          default: professional
      required:
        - article

  - name: sync_to_platforms
    description: 同步文章到多个平台
    parameters:
      type: object
      properties:
        article:
          type: object
          description: 文章对象
        platforms:
          type: array
          items:
            type: string
          description: 目标平台列表
      required:
        - article
        - platforms

  - name: rewrite_and_sync
    description: 改写文章并同步到多个平台（一站式）
    parameters:
      type: object
      properties:
        url:
          type: string
          description: 文章 URL（可选）
        article:
          type: object
          description: 文章对象（可选）
        style:
          type: string
          description: 改写风格
          enum: [professional, casual, creative, concise]
          default: professional
        platforms:
          type: array
          items:
            type: string
          description: 目标平台列表
      required:
        - platforms
```

### 3. 实现工具函数

创建 `skills/ai-rewrite-sync/tools.py`:

```python
import os
from typing import Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic

class AIRewriter:
    """AI 文章改写器"""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4-turbo-preview"
        elif provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"
    
    def rewrite(
        self,
        title: str,
        content: str,
        style: str = "professional",
        preserve_structure: bool = True
    ) -> Dict[str, str]:
        """
        改写文章
        
        Args:
            title: 原始标题
            content: 原始内容
            style: 改写风格
            preserve_structure: 是否保留结构
        
        Returns:
            改写后的文章 {title, content}
        """
        
        style_prompts = {
            "professional": "专业、严谨、客观",
            "casual": "轻松、口语化、易读",
            "creative": "创意、有趣、吸引人",
            "concise": "简洁、精炼、重点突出"
        }
        
        prompt = f"""请改写以下文章，要求：

风格：{style_prompts.get(style, "专业")}
保留结构：{"是" if preserve_structure else "否"}

原始标题：{title}

原始内容：
{content}

请提供：
1. 改写后的标题
2. 改写后的内容

以 JSON 格式返回：
{{
  "title": "改写后的标题",
  "content": "改写后的内容"
}}
"""
        
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容改写助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.content[0].text
        
        import json
        return json.loads(result)


class WechatsyncBridge:
    """Wechatsync 桥接器"""
    
    def __init__(self, extension_id: str):
        self.extension_id = extension_id
    
    async def sync_to_platforms(
        self,
        article: Dict[str, str],
        platforms: List[str]
    ) -> Dict[str, bool]:
        """
        同步文章到多个平台
        
        Args:
            article: 文章对象 {title, content, cover?}
            platforms: 平台列表
        
        Returns:
            同步结果 {platform: success}
        """
        # 通过 Chrome Extension API 调用
        # 或者通过 MCP Server 调用
        pass


# 工具函数
async def rewrite_article(
    article: Dict[str, str],
    style: str = "professional"
) -> Dict[str, str]:
    """改写文章"""
    rewriter = AIRewriter()
    return rewriter.rewrite(
        title=article["title"],
        content=article["content"],
        style=style
    )


async def sync_to_platforms(
    article: Dict[str, str],
    platforms: List[str]
) -> Dict[str, bool]:
    """同步到平台"""
    bridge = WechatsyncBridge()
    return await bridge.sync_to_platforms(article, platforms)


async def rewrite_and_sync(
    url: Optional[str] = None,
    article: Optional[Dict[str, str]] = None,
    style: str = "professional",
    platforms: List[str] = []
) -> Dict[str, any]:
    """改写并同步"""
    
    # 1. 提取文章（如果提供 URL）
    if url:
        # 使用 agent-browser 提取
        article = await extract_article_from_url(url)
    
    if not article:
        raise ValueError("需要提供 url 或 article")
    
    # 2. AI 改写
    rewritten = await rewrite_article(article, style)
    
    # 3. 同步到平台
    results = await sync_to_platforms(rewritten, platforms)
    
    return {
        "original": article,
        "rewritten": rewritten,
        "sync_results": results
    }


async def extract_article_from_url(url: str) -> Dict[str, str]:
    """使用 agent-browser 从 URL 提取文章"""
    # 这将通过 agent-browser 实现
    # 见下文的 agent-browser 配置
    pass
```

### 4. agent-browser 配置

创建 `agent-browser-config.yaml`:

```yaml
# agent-browser 配置

# 浏览器配置
browser:
  headless: false  # 开发时显示浏览器
  timeout: 30000   # 30秒超时

# AI 配置
ai:
  provider: openai  # 或 anthropic
  model: gpt-4-turbo-preview
  
# 任务配置
tasks:
  # 提取文章
  extract_article:
    description: 从网页提取文章内容
    steps:
      - action: navigate
        url: "${article_url}"
      
      - action: wait
        selector: "article, .article-content, .post-content"
        timeout: 5000
      
      - action: extract
        selectors:
          title: "h1, .article-title, .post-title"
          content: "article, .article-content, .post-content"
          cover: "article img:first-of-type, .article-cover img"
      
      - action: return
        data: "${extracted_data}"
  
  # 同步文章（使用浏览器自动化）
  sync_article_browser:
    description: 通过浏览器自动化同步文章
    steps:
      - action: navigate
        url: "https://www.wechatsync.com/md/"
      
      - action: wait
        selector: "#root"
        timeout: 5000
      
      - action: fill
        selector: "[contenteditable='true']"
        value: "${article_content}"
      
      - action: click
        selector: "button:contains('同步')"
      
      - action: wait
        selector: ".sync-dialog"
        timeout: 3000
      
      - action: click
        selector: "input[value='${platform_id}']"
      
      - action: click
        selector: "button:contains('开始同步')"
      
      - action: wait
        selector: ".sync-complete"
        timeout: 60000
      
      - action: return
        data: "success"
```

### 5. 使用示例

#### 在 OpenClaw 中使用

```python
# 安装 skill
openclaw skill install ./skills/ai-rewrite-sync

# 使用
result = await openclaw.run(
    "请改写这篇文章并同步到知乎和掘金",
    context={
        "article_url": "https://mp.weixin.qq.com/s/xxx"
    }
)
```

#### 命令行使用

```bash
# 改写文章
openclaw run "改写这篇文章：https://mp.weixin.qq.com/s/xxx，风格要专业"

# 改写并同步
openclaw run "改写这篇文章并同步到知乎、掘金、CSDN：https://mp.weixin.qq.com/s/xxx"
```

---

## 📦 方案二：集成到 Wechatsync 主仓库

### 1. 创建 AI 改写模块

创建 `packages/core/src/ai/rewriter.ts`:

```typescript
/**
 * AI 文章改写模块
 */

export type RewriteStyle = 'professional' | 'casual' | 'creative' | 'concise'

export interface RewriteOptions {
  style: RewriteStyle
  preserveStructure?: boolean
  provider?: 'openai' | 'anthropic'
}

export interface Article {
  title: string
  content: string
  cover?: string
}

export interface RewrittenArticle extends Article {
  originalTitle: string
  originalContent: string
}

/**
 * AI 改写器
 */
export class ArticleRewriter {
  private provider: 'openai' | 'anthropic'
  private apiKey: string
  
  constructor(provider: 'openai' | 'anthropic' = 'openai', apiKey: string) {
    this.provider = provider
    this.apiKey = apiKey
  }
  
  /**
   * 改写文章
   */
  async rewrite(
    article: Article,
    options: RewriteOptions = { style: 'professional' }
  ): Promise<RewrittenArticle> {
    const prompt = this.buildPrompt(article, options)
    
    if (this.provider === 'openai') {
      return await this.callOpenAI(prompt)
    } else {
      return await this.callAnthropic(prompt)
    }
  }
  
  /**
   * 构建提示词
   */
  private buildPrompt(article: Article, options: RewriteOptions): string {
    const styleDescriptions = {
      professional: '专业、严谨、客观',
      casual: '轻松、口语化、易读',
      creative: '创意、有趣、吸引人',
      concise: '简洁、精炼、重点突出'
    }
    
    return `请改写以下文章，要求：

风格：${styleDescriptions[options.style]}
保留结构：${options.preserveStructure !== false ? '是' : '否'}

原始标题：${article.title}

原始内容：
${article.content}

请以 JSON 格式返回：
{
  "title": "改写后的标题",
  "content": "改写后的内容"
}`
  }
  
  /**
   * 调用 OpenAI API
   */
  private async callOpenAI(prompt: string): Promise<RewrittenArticle> {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4-turbo-preview',
        messages: [
          { role: 'system', content: '你是一个专业的内容改写助手。' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        response_format: { type: 'json_object' }
      })
    })
    
    const data = await response.json()
    const result = JSON.parse(data.choices[0].message.content)
    
    return {
      title: result.title,
      content: result.content,
      originalTitle: '',
      originalContent: ''
    }
  }
  
  /**
   * 调用 Anthropic API
   */
  private async callAnthropic(prompt: string): Promise<RewrittenArticle> {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        messages: [
          { role: 'user', content: prompt }
        ]
      })
    })
    
    const data = await response.json()
    const result = JSON.parse(data.content[0].text)
    
    return {
      title: result.title,
      content: result.content,
      originalTitle: '',
      originalContent: ''
    }
  }
}
```

### 2. 集成到编辑器

修改 `packages/extension/src/editor/EditorApp.tsx`:

```typescript
import { ArticleRewriter, type RewriteStyle } from '@wechatsync/core'

// 添加改写按钮
const handleRewrite = async (style: RewriteStyle) => {
  if (!article) return
  
  setStatus('syncing')
  setError(null)
  
  try {
    // 获取 API Key（从设置中）
    const settings = await chrome.storage.local.get(['aiProvider', 'aiApiKey'])
    
    const rewriter = new ArticleRewriter(
      settings.aiProvider || 'openai',
      settings.aiApiKey
    )
    
    const rewritten = await rewriter.rewrite(article, { style })
    
    // 更新文章
    setArticle({
      ...article,
      title: rewritten.title,
      content: rewritten.content
    })
    
    // 更新编辑器内容
    if (titleRef.current) {
      titleRef.current.innerText = rewritten.title
    }
    if (contentRef.current) {
      contentRef.current.innerHTML = rewritten.content
    }
    
    setStatus('idle')
  } catch (err) {
    setError((err as Error).message)
    setStatus('idle')
  }
}

// UI 部分
<div className="flex items-center gap-2">
  {/* AI 改写按钮 */}
  <select
    onChange={(e) => handleRewrite(e.target.value as RewriteStyle)}
    className="px-3 py-1.5 border rounded-lg text-sm"
    disabled={status === 'syncing'}
  >
    <option value="">AI 改写</option>
    <option value="professional">专业风格</option>
    <option value="casual">轻松风格</option>
    <option value="creative">创意风格</option>
    <option value="concise">简洁风格</option>
  </select>
  
  {/* 同步按钮 */}
  <button onClick={() => setShowSyncDialog(true)}>
    同步
  </button>
</div>
```

### 3. 添加设置页面

创建 `packages/extension/src/popup/pages/AISettings.tsx`:

```typescript
import { useState, useEffect } from 'react'

export function AISettings() {
  const [provider, setProvider] = useState<'openai' | 'anthropic'>('openai')
  const [apiKey, setApiKey] = useState('')
  
  useEffect(() => {
    chrome.storage.local.get(['aiProvider', 'aiApiKey']).then((result) => {
      if (result.aiProvider) setProvider(result.aiProvider)
      if (result.aiApiKey) setApiKey(result.aiApiKey)
    })
  }, [])
  
  const handleSave = async () => {
    await chrome.storage.local.set({
      aiProvider: provider,
      aiApiKey: apiKey
    })
    alert('设置已保存')
  }
  
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">AI 设置</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            AI 提供商
          </label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value as any)}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="openai">OpenAI (GPT-4)</option>
            <option value="anthropic">Anthropic (Claude)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">
            API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          保存设置
        </button>
      </div>
    </div>
  )
}
```

---

## 🚀 方案三：MCP Server 集成（推荐）

### 1. 扩展 MCP Server

修改 `packages/mcp-server/src/server.ts`:

```typescript
import { ArticleRewriter, type RewriteStyle } from '@wechatsync/core'

// 添加 AI 改写工具
this.server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // ... 现有工具
      
      {
        name: 'rewrite_article',
        description: '使用 AI 改写文章内容',
        inputSchema: {
          type: 'object',
          properties: {
            article: {
              type: 'object',
              properties: {
                title: { type: 'string' },
                content: { type: 'string' },
                cover: { type: 'string' }
              },
              required: ['title', 'content']
            },
            style: {
              type: 'string',
              enum: ['professional', 'casual', 'creative', 'concise'],
              default: 'professional'
            }
          },
          required: ['article']
        }
      },
      
      {
        name: 'rewrite_and_sync',
        description: '改写文章并同步到多个平台',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: '文章 URL' },
            article: { type: 'object' },
            style: {
              type: 'string',
              enum: ['professional', 'casual', 'creative', 'concise']
            },
            platforms: {
              type: 'array',
              items: { type: 'string' }
            }
          },
          required: ['platforms']
        }
      }
    ]
  }
})

// 实现工具
this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params
  
  if (name === 'rewrite_article') {
    const rewriter = new ArticleRewriter(
      process.env.AI_PROVIDER || 'openai',
      process.env.AI_API_KEY!
    )
    
    const rewritten = await rewriter.rewrite(args.article, {
      style: args.style || 'professional'
    })
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(rewritten, null, 2)
      }]
    }
  }
  
  if (name === 'rewrite_and_sync') {
    // 1. 提取文章（如果提供 URL）
    let article = args.article
    if (args.url) {
      article = await this.bridge.extractArticle(args.url)
    }
    
    // 2. AI 改写
    const rewriter = new ArticleRewriter(
      process.env.AI_PROVIDER || 'openai',
      process.env.AI_API_KEY!
    )
    const rewritten = await rewriter.rewrite(article, {
      style: args.style || 'professional'
    })
    
    // 3. 同步到平台
    const results = await this.bridge.syncArticle(rewritten, args.platforms)
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          original: article,
          rewritten,
          syncResults: results
        }, null, 2)
      }]
    }
  }
  
  // ... 其他工具
})
```

### 2. 配置环境变量

```bash
# .env
AI_PROVIDER=openai
AI_API_KEY=sk-xxx
```

### 3. 使用示例

在 Claude Code 中：

```
"请改写这篇文章并同步到知乎和掘金：https://mp.weixin.qq.com/s/xxx"
"用轻松的风格改写这篇文章"
"改写这篇文章，风格要专业，然后同步到 CSDN、掘金、知乎"
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **OpenClaw + agent-browser** | 功能强大，自动化程度高 | 需要额外安装 OpenClaw | 重度自动化需求 |
| **集成到主仓库** | 无需额外依赖，用户体验好 | 需要用户配置 API Key | 普通用户 |
| **MCP Server 集成** | 与 AI 原生集成，最自然 | 需要 MCP 环境 | AI 用户（推荐） |

---

## 🎯 推荐方案

**推荐使用方案三：MCP Server 集成**

理由：
1. ✅ 与现有 MCP 架构完美契合
2. ✅ 用户无需额外配置（API Key 在 MCP 配置中）
3. ✅ 支持自然语言交互
4. ✅ 可扩展性强

---

## 🚀 快速开始

### 1. 配置 MCP Server

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

### 2. 使用

```
"请改写这篇文章并同步到知乎和掘金：https://mp.weixin.qq.com/s/xxx"
```

---

## 📝 后续优化

1. **支持更多 AI 提供商**
   - Google Gemini
   - 阿里通义千问
   - 百度文心一言

2. **改写历史记录**
   - 保存改写前后对比
   - 支持版本回退

3. **批量改写**
   - 一次改写多篇文章
   - 批量同步

4. **改写模板**
   - 自定义改写模板
   - 行业特定模板

---

## 🔗 相关资源

- [OpenClaw 官方文档](https://clawhub.ai)
- [agent-browser GitHub](https://github.com/clawhub/agent-browser)
- [Anthropic MCP 协议](https://modelcontextprotocol.io)
- [OpenAI API 文档](https://platform.openai.com/docs)
