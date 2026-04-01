# 🚀 快速开始指南

## 📦 安装（5分钟）

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/demo-video-generator.git
cd demo-video-generator
```

### 2. 安装依赖

```bash
# Python 依赖
pip install PyYAML

# 系统依赖
brew install ffmpeg          # macOS
pipx install edge-tts        # 语音生成
npm install -g agent-browser # 视频录制
```

### 3. 安装 CLI 工具

```bash
chmod +x bin/demo-gen
```

---

## 🎬 生成第一个视频（10分钟）

### 步骤1: 初始化项目

```bash
./bin/demo-gen init my-first-demo
cd my-first-demo
```

### 步骤2: 编辑配置文件

打开 `config.yaml`，修改以下内容：

```yaml
project:
  name: "我的第一个演示视频"
  url: "https://your-product.com"  # 改成你的产品网址
  
scenes:
  - name: "intro"
    text: "这是我的第一个演示视频！"  # 改成你的文案
    subtitle: "这是我的第一个演示视频！"
```

### 步骤3: 验证配置

```bash
../bin/demo-gen validate config.yaml
```

### 步骤4: 生成语音和字幕

```bash
../bin/demo-gen generate config.yaml
```

### 步骤5: 录制视频

按照提示手动录制视频：

```bash
# 打开浏览器
agent-browser open "https://your-product.com"

# 开始录制
agent-browser record start output/recording.webm

# 执行操作（浏览页面、点击按钮等）
# 等待相应时长...

# 停止录制
agent-browser record stop
```

### 步骤6: 查看视频

```bash
open output/demo.mp4
```

---

## 📚 下一步

### 学习配置文件

查看完整的配置说明：

```bash
cat docs/CONFIGURATION.md
```

### 使用示例模板

```bash
# 查看 PageAgent 示例
cat templates/examples/pageagent.yaml

# 使用示例配置
cp templates/examples/pageagent.yaml my-demo/config.yaml
```

### 学习最佳实践

查看专业解说技巧：

```bash
cat ../VOICEOVER-BEST-PRACTICES.md
```

---

## 🎯 常用命令

```bash
# 初始化项目
./bin/demo-gen init <project-name>

# 验证配置
./bin/demo-gen validate <config.yaml>

# 生成视频
./bin/demo-gen generate <config.yaml>

# 列出可用语音
./bin/demo-gen list-voices

# 列出可用模板
./bin/demo-gen templates
```

---

## 💡 提示

### 文案编写技巧

1. **使用钩子开头**
   ```yaml
   text: "你有没有想过，让产品自己介绍自己？"
   ```

2. **场景化表达**
   ```yaml
   text: "想象一下：用户只需点击按钮，功能自动执行。"
   ```

3. **简短字幕**
   ```yaml
   subtitle: "只需点击按钮，功能自动执行"  # 不超过30字
   ```

### 场景设计建议

- **总场景数**: 5-8个
- **总时长**: 60-120秒
- **每个场景**: 10-30秒

---

## 🐛 遇到问题？

### 常见问题

**Q: edge-tts 未找到**
```bash
pipx install edge-tts
```

**Q: ffmpeg 未找到**
```bash
brew install ffmpeg  # macOS
```

**Q: 字幕不同步**
- 确保使用最新版本
- 重新生成语音和字幕

### 获取帮助

- 📖 查看 [完整文档](./docs/)
- 💬 提交 [Issue](https://github.com/your-repo/demo-video-generator/issues)
- 📧 发送邮件至 support@example.com

---

**祝你使用愉快！🎉**
