# 项目规则

此文件定义了 AI 员工在处理此项目时必须遵循的规则。

## 代码规范

### TypeScript

- 使用严格模式 (`strict: true`)
- 所有函数必须有返回类型注解
- 避免使用 `any`，使用 `unknown` 或具体类型
- 使用 `interface` 定义对象类型，`type` 定义联合/交叉类型

### 文件命名

- 服务文件: `XxxService.ts`
- 类型文件: `types/xxx.ts`
- 测试文件: `Xxx.test.ts`
- 文档文件: `docs/XXX.md`

## 架构规则

### 服务层

- 服务文件放在 `src-electron/services/`
- 每个服务应该是独立的、可测试的
- 服务之间通过 IPC 通信

### IPC 通信

- IPC 处理程序在 `IPCService.ts` 中注册
- 命名格式: `模块:操作` (如 `browser:snapshot`)

### 测试

- 测试文件放在 `src-electron/tests/`
- 使用 Playwright 进行浏览器测试
- 运行命令: `npx tsx src-electron/tests/Xxx.test.ts`

## 禁止事项

1. ❌ 不要在代码中硬编码 API Key
2. ❌ 不要删除现有的测试用例
3. ❌ 不要修改 `node_modules` 或 `dist` 目录
4. ❌ 不要提交敏感信息到版本控制

## 必须事项

1. ✅ 新功能必须有对应测试
2. ✅ 修改代码后必须运行相关测试
3. ✅ 新增功能必须更新 CLAUDE.md
4. ✅ 保持文档与代码同步

## 运行命令

| 命令 | 说明 |
|------|------|
| `npm run start` | 启动开发模式 |
| `npm run build` | 构建项目 |
| `npx tsx src-electron/tests/Xxx.test.ts` | 运行测试 |

## 技术债务追踪

当前无技术债务记录。

---

**最后更新**: 2026-03-21
