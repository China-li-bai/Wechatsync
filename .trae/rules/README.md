# AI 员工知识管理系统

## 快速开始

### 对于新的 AI 员工

1. **阅读 [CLAUDE.md](../CLAUDE.md)** - 这是项目的主知识库
2. **阅读 [.trae/rules/project_rules.md](.trae/rules/project_rules.md)** - 了解项目规则
3. **查看 [TECH_DOCS.md](../TECH_DOCS.md)** - 获取文档索引

### 对于完成工作的 AI 员工

1. **更新 CLAUDE.md** - 在知识更新日志中记录变更
2. **参考 [knowledge_update_template.md](.trae/rules/knowledge_update_template.md)** - 了解如何更新

## 知识库结构

```
项目根目录/
├── CLAUDE.md                    # 📋 主知识库 (AI 必读)
├── TECH_DOCS.md                 # 📚 文档索引
├── PROJECT_ARCHITECTURE.md      # 🏗️ 架构文档
├── .trae/
│   └── rules/
│       ├── project_rules.md     # 📏 项目规则
│       └── knowledge_update_template.md  # 📝 更新模板
└── src-electron/
    └── docs/                    # 📖 技术文档
```

## 知识持久化机制

### 1. CLAUDE.md (主知识库)

- **作用**: AI 员工的"长期记忆"
- **内容**: 项目概述、核心功能、知识更新日志
- **更新频率**: 每次重要变更后

### 2. 知识更新日志

位于 CLAUDE.md 底部，记录所有重要变更：

```markdown
### YYYY-MM-DD: [变更标题]

**类型**: 新功能 / Bug修复 / 重构 / 文档更新

**变更内容**:
- 具体变更点

**新增/修改文件**:
- 文件列表

**测试状态**: X/Y 通过
```

### 3. 技术文档

每个核心功能都有对应的详细文档：
- 快速入门 (QUICK_START.md)
- 详细文档 (STRUCTURED_SNAPSHOT.md)
- 测试用例 (Xxx.test.ts)

## 知识更新检查清单

完成工作后，确保：

- [ ] CLAUDE.md 知识更新日志已更新
- [ ] 相关技术文档已创建/更新
- [ ] TECH_DOCS.md 索引已更新
- [ ] 测试已添加并通过
- [ ] 代码符合项目规则

## 常见问题

### Q: 如何知道项目当前状态？

A: 阅读 CLAUDE.md 的知识更新日志部分，了解最近的变更。

### Q: 新功能应该放在哪里？

A: 
1. 代码: `src-electron/services/`
2. 测试: `src-electron/tests/`
3. 文档: `src-electron/docs/`
4. 知识记录: 更新 CLAUDE.md

### Q: 如何确保知识不丢失？

A: 
1. 每次工作后更新 CLAUDE.md
2. 创建详细的技术文档
3. 添加测试用例作为"可执行的文档"

---

**创建日期**: 2026-03-21
