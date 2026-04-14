# 知识更新模板

> 当 AI 员工完成重要工作后，使用此模板更新知识库

## 更新流程

### 1. 更新 CLAUDE.md

在 `CLAUDE.md` 的 **知识更新日志** 部分添加新条目：

```markdown
### YYYY-MM-DD: [功能名称/修复内容]

**类型**: 新功能 / Bug修复 / 重构 / 文档更新

**变更内容**:
- 变更点 1
- 变更点 2

**新增文件**:
- `path/to/new/file.ts`

**修改文件**:
- `path/to/modified/file.ts`

**测试状态**: X/Y 通过

**注意事项**:
- 需要注意的事项
```

### 2. 更新相关文档

| 变更类型 | 需要更新的文档 |
|---------|---------------|
| 新功能 | CLAUDE.md + 详细技术文档 |
| API 变更 | CLAUDE.md + API 文档 |
| 架构变更 | PROJECT_ARCHITECTURE.md |
| Bug 修复 | CLAUDE.md (简要记录) |

### 3. 更新测试

- 新功能 → 新增测试文件
- Bug 修复 → 添加回归测试
- 重构 → 确保现有测试通过

## 知识库文件结构

```
/Users/mac/project/gen-paly/
├── CLAUDE.md                    # 📋 主知识库 (AI 员工必读)
├── TECH_DOCS.md                 # 📚 技术文档索引
├── PROJECT_ARCHITECTURE.md      # 🏗️ 项目架构
├── .trae/
│   └── rules/
│       └── project_rules.md     # 📏 项目规则
└── src-electron/
    └── docs/
        ├── QUICK_START.md       # ⚡ 快速入门
        └── STRUCTURED_SNAPSHOT.md  # 📖 详细文档
```

## 示例：添加新功能

假设你要添加一个"自动登录"功能：

### 步骤 1: 创建代码文件

```typescript
// src-electron/services/AutoLoginService.ts
export class AutoLoginService {
  async login(url: string, credentials: Credentials): Promise<boolean> {
    // 实现
  }
}
```

### 步骤 2: 创建测试文件

```typescript
// src-electron/tests/AutoLoginService.test.ts
// 测试用例
```

### 步骤 3: 更新 CLAUDE.md

```markdown
### 2026-03-22: 自动登录服务

**类型**: 新功能

**变更内容**:
- 新增 AutoLoginService 支持自动登录功能
- 支持多平台登录（小红书、知乎等）
- 添加登录状态检测

**新增文件**:
- `src-electron/services/AutoLoginService.ts`
- `src-electron/tests/AutoLoginService.test.ts`

**测试状态**: 5/5 通过
```

### 步骤 4: 创建详细文档

```markdown
# src-electron/docs/AUTO_LOGIN.md

# 自动登录服务

## 使用方法
...
```

### 步骤 5: 更新 TECH_DOCS.md

在技术文档索引中添加新文档链接。

## 知识更新检查清单

- [ ] CLAUDE.md 知识更新日志已更新
- [ ] 相关技术文档已创建/更新
- [ ] TECH_DOCS.md 索引已更新
- [ ] 测试已添加并通过
- [ ] 代码符合项目规则

---

**最后更新**: 2026-03-21
