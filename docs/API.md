# API 文档

本文档介绍 Wechatsync 的核心 API，帮助开发者理解项目架构和扩展功能。

## 📚 文档生成

项目使用 [TypeDoc](https://typedoc.org/) 自动生成 API 文档。

### 生成文档

```bash
# 生成 API 文档
pnpm run docs

# 实时监听文件变化并重新生成
pnpm run docs:watch

# 启动本地服务器查看文档
pnpm run docs:serve
```

生成的文档位于 `docs/api/` 目录，打开 `docs/api/index.html` 即可查看。

## 🏗️ 核心模块

### 1. 适配器系统 (Adapters)

适配器是平台同步的核心，负责与各平台 API 交互。

#### 核心接口

- **[PlatformAdapter](file:///e:/gitlab/idea/Wechatsync/packages/core/src/adapters/types.ts)**: 平台适配器接口
- **[CodeAdapter](file:///e:/gitlab/idea/Wechatsync/packages/core/src/adapters/code-adapter.ts)**: 代码适配器基类（推荐继承）
- **[BaseAdapter](file:///e:/gitlab/idea/Wechatsync/packages/core/src/adapters/base.ts)**: 基础适配器类

#### 平台适配器

所有平台适配器位于 `packages/core/src/adapters/platforms/` 目录：

- `ZhihuAdapter` - 知乎
- `JuejinAdapter` - 掘金
- `CSDNAdapter` - CSDN
- `WeixinAdapter` - 微信公众号
- `WeiboAdapter` - 微博
- ... 等 29+ 平台

#### 添加新平台

```typescript
import { CodeAdapter } from '@wechatsync/core'
import type { Article, AuthResult, SyncResult, PlatformMeta } from '@wechatsync/core'

export class NewPlatformAdapter extends CodeAdapter {
  readonly meta: PlatformMeta = {
    id: 'new-platform',
    name: '新平台',
    icon: 'https://example.com/icon.png',
    homepage: 'https://example.com',
    capabilities: ['article', 'draft', 'image_upload'],
  }

  readonly preprocessConfig = {
    outputFormat: 'markdown' as const,
    // 其他预处理配置...
  }

  async checkAuth(): Promise<AuthResult> {
    // 检查用户登录状态
  }

  async publish(article: Article): Promise<SyncResult> {
    // 发布文章逻辑
  }
}
```

### 2. 运行时抽象 (Runtime)

运行时抽象层使核心逻辑可在不同环境（浏览器扩展、Node.js）中运行。

#### 核心接口

- **[RuntimeInterface](file:///e:/gitlab/idea/Wechatsync/packages/core/src/runtime/interface.ts)**: 运行时接口定义

#### 主要能力

```typescript
interface RuntimeInterface {
  type: 'extension' | 'node'
  
  // HTTP 请求（自动携带 cookies）
  fetch(url: string, options?: RequestInit): Promise<Response>
  
  // Cookie 管理
  cookies: {
    get(domain: string): Promise<Cookie[]>
    set(cookie: Cookie): Promise<void>
    remove(name: string, domain: string): Promise<void>
  }
  
  // 持久化存储
  storage: {
    get<T>(key: string): Promise<T | null>
    set<T>(key: string, value: T): Promise<void>
    remove(key: string): Promise<void>
  }
  
  // Header 规则管理（请求拦截）
  headerRules?: {
    add(rule: HeaderRule): Promise<string>
    remove(ruleId: string): Promise<void>
    clear(): Promise<void>
  }
  
  // Tab 管理（仅扩展环境）
  tabs?: { ... }
  
  // 文件下载（仅扩展环境）
  downloads?: { ... }
}
```

### 3. 类型定义 (Types)

核心类型定义位于 `packages/core/src/types.ts`：

- **Article**: 文章数据结构
- **AuthResult**: 认证结果
- **SyncResult**: 同步结果
- **PlatformMeta**: 平台元信息
- **Cookie**: Cookie 数据结构
- **HeaderRule**: Header 规则

### 4. 工具库 (Lib)

工具库提供常用功能：

- **markdown-images**: Markdown 图片解析
- **turndown**: HTML → Markdown 转换
- **markdown-to-draft**: Markdown → Draft.js 转换
- **logger**: 日志工具
- **aws4**: AWS 签名（用于图片上传）

## 📖 架构说明

### Content Script vs Service Worker

```
Content Script (有 DOM)          Service Worker (无 DOM)
├── HTML 预处理                  ├── 接收已处理的 html/markdown
├── 代码块处理                   ├── 图片上传（URL 替换）
├── 懒加载图片                   └── 调用平台 API
└── HTML → Markdown 转换
```

### 预处理配置系统

每个平台定义自己的预处理配置：

```typescript
readonly preprocessConfig = {
  outputFormat: 'html' | 'markdown',
  removeSpecialTags: true,
  processCodeBlocks: true,
  // ... 更多配置
}
```

## 🔗 相关文档

- [适配器开发规范](./adapter-spec.md) - 详细的适配器开发指南
- [贡献指南](../CONTRIBUTING.md) - 如何参与项目开发
- [更新日志](../CHANGELOG.md) - 版本更新记录

## 💡 开发建议

1. **阅读源码注释**: 核心模块都有详细的 JSDoc 注释
2. **查看测试用例**: `packages/core/src/lib/__tests__/` 目录包含测试示例
3. **参考现有适配器**: 查看已实现的平台适配器作为参考
4. **使用 TypeScript**: 项目全面使用 TypeScript，类型提示有助于理解 API

## 🚀 快速开始

### 安装依赖

```bash
pnpm install
```

### 开发模式

```bash
# 开发扩展
pnpm run dev

# 构建
pnpm run build

# 类型检查
pnpm run typecheck

# 生成文档
pnpm run docs
```

---

**提示**: 完整的 API 文档请运行 `pnpm run docs` 后查看 `docs/api/index.html`。
