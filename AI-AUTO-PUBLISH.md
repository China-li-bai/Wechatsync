# AI改写 + 自动发布功能

## 功能概述

### 1. AI改写功能

在MD编辑器中集成AI改写功能，支持：
- **全文改写**：保持原意但改变表达方式
- **标题改写**：生成更吸引人的标题
- **生成摘要**：自动生成文章摘要
- **扩展内容**：增加更多细节和例子
- **简化内容**：使文章更易理解
- **专业风格**：改写为技术文章风格
- **轻松风格**：改写为博客风格

### 2. 自动发布功能

在草稿页面注入"一键发布"按钮，支持：
- 掘金
- 知乎
- 简书
- 微信公众号
- 头条号
- 百家号

## 使用方法

### AI改写

1. 打开 [MD编辑器](https://www.wechatsync.com/md/)
2. 编写或导入文章
3. 点击"🤖 AI改写"按钮
4. 选择AI服务商（OpenAI/Claude/DeepSeek）
5. 输入API密钥
6. 选择改写方式
7. 点击"开始改写"

### 自动发布

1. 在MD编辑器中点击"同步发布"
2. 选择目标平台
3. 同步完成后，点击"查看草稿"
4. 草稿页面右上角会出现"🚀 一键发布"按钮
5. 点击按钮自动发布

## 配置说明

### AI服务商配置

#### OpenAI
- API密钥：从 [OpenAI Platform](https://platform.openai.com/) 获取
- 支持模型：gpt-4, gpt-4-turbo, gpt-3.5-turbo
- API地址：https://api.openai.com/v1/chat/completions

#### Claude
- API密钥：从 [Anthropic Console](https://console.anthropic.com/) 获取
- 支持模型：claude-3-opus, claude-3-sonnet, claude-3-haiku
- API地址：https://api.anthropic.com/v1/messages

#### DeepSeek
- API密钥：从 [DeepSeek Platform](https://platform.deepseek.com/) 获取
- 支持模型：deepseek-chat, deepseek-coder
- API地址：https://api.deepseek.com/v1/chat/completions

### agent-browser配置（可选）

如果需要使用agent-browser进行更高级的自动化：

```bash
# 安装agent-browser
npm install -g agent-browser
# 或
brew install agent-browser

# 初始化
agent-browser install

# 使用
node packages/web-extension/src/publishers/auto-publish.js "https://juejin.cn/editor/drafts/12345"
```

## 技术架构

### AI改写流程

```
用户点击"AI改写"
    ↓
显示配置对话框
    ↓
调用AI API
    ↓
返回改写结果
    ↓
填充到编辑器
    ↓
保存到PouchDB（可选）
```

### 自动发布流程

```
同步完成 → 返回draftLink
    ↓
用户点击"查看草稿"
    ↓
content.js检测草稿页面
    ↓
注入inject-publish.js
    ↓
显示"一键发布"按钮
    ↓
用户点击按钮
    ↓
自动点击发布按钮
    ↓
发布成功
```

## 文件结构

```
packages/
├── markdown-editor/
│   └── src/
│       ├── Main.vue              # 增加AI改写按钮和对话框
│       └── ai-config.js          # AI配置文件
└── web-extension/
    └── src/
        ├── content.js            # 增加草稿页面检测
        ├── publishers/
        │   ├── auto-publish.js   # agent-browser自动发布
        │   └── inject-publish.js # 注入"一键发布"按钮
        └── copied/
            └── manifest.json     # 增加权限配置
```

## 开发指南

### 添加新的AI服务商

1. 在 `ai-config.js` 中添加配置
2. 在 `Main.vue` 的 `callAI()` 方法中添加调用逻辑
3. 实现 `call<Provider>()` 方法

### 添加新的发布平台

1. 在 `inject-publish.js` 的 `publishers` 对象中添加配置
2. 在 `content.js` 的 `draftPatterns` 数组中添加URL模式
3. 在 `manifest.json` 的 `content_scripts.matches` 中添加域名

## 注意事项

1. **API密钥安全**：API密钥保存在localStorage，请勿在公共电脑上使用
2. **改写质量**：AI改写结果可能不完全符合预期，建议人工审核
3. **发布频率**：频繁发布可能触发平台风控，建议适度使用
4. **浏览器兼容**：自动发布功能依赖DOM结构，平台更新后可能需要调整选择器

## 故障排查

### AI改写失败

1. 检查API密钥是否正确
2. 检查网络连接
3. 检查API余额是否充足
4. 查看浏览器控制台错误信息

### 自动发布失败

1. 检查是否在草稿页面
2. 检查按钮选择器是否正确
3. 查看浏览器控制台错误信息
4. 尝试手动发布，确认页面结构未变化

## 更新日志

### v1.0.0 (2025-03-27)
- ✨ 新增AI改写功能
- ✨ 新增自动发布功能
- ✨ 支持OpenAI、Claude、DeepSeek
- ✨ 支持掘金、知乎、简书、微信公众号、头条号、百家号
