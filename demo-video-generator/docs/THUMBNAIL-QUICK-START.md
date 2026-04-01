# 🚀 封面生成功能 - 快速开始指南

**版本**: v1.3.0  
**更新日期**: 2026-04-01

---

## ⚡ **快速开始（3步）**

### **步骤1: 添加配置**

在你的配置文件中添加`thumbnail`配置：

```yaml
project:
  name: "My Product Demo"
  title: "5步吃透CTR优化"        # 封面标题
  description: "YouTube封面设计指南"  # 封面副标题

# 添加封面配置
thumbnail:
  enabled: true
  template: "default.html"
  badge: "HOT"
  brand: "My Brand"
```

### **步骤2: 运行视频生成**

```bash
python3 lib/demo_video_generator.py config/my-config.yaml
```

### **步骤3: 查看结果**

视频生成完成后，封面自动生成在输出目录：

```
output/
├── demo-video.mp4          # 视频文件
├── thumbnail_xxxxx.png     # 封面文件 ✨
├── subtitles.srt           # 字幕文件
└── voiceover.aac           # 音频文件
```

---

## 🎨 **模板选择**

### **1. 默认模板 (default.html)**

**适合**: 产品演示、功能介绍

```yaml
thumbnail:
  template: "default.html"
```

### **2. 教程模板 (tutorial.html)**

**适合**: 教程视频、操作指南

```yaml
thumbnail:
  template: "tutorial.html"
```

### **3. 评测模板 (review.html)**

**适合**: 产品评测、功能对比

```yaml
thumbnail:
  template: "review.html"
```

---

## 🎯 **配置示例**

### **示例1: 简洁风格**

```yaml
thumbnail:
  enabled: true
  template: "default.html"
  badge: "NEW"
```

### **示例2: 品牌风格**

```yaml
thumbnail:
  enabled: true
  template: "default.html"
  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  text_color: "white"
  badge: "HOT"
  brand: "My Brand"
  accent_color: "#ffd700"
```

### **示例3: 技术风格**

```yaml
thumbnail:
  enabled: true
  template: "default.html"
  background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
  text_color: "#00d9ff"
  accent_color: "#ff6b6b"
  badge: "2024"
```

---

## 📋 **完整配置说明**

```yaml
thumbnail:
  # 基础配置
  enabled: true                    # 是否启用封面生成
  template: "default.html"         # 模板文件
  template_dir: "templates/thumbnails"  # 模板目录
  
  # 样式配置
  background: "linear-gradient(...)"  # 背景颜色或渐变
  font_size: 80                    # 标题字号
  text_color: "white"              # 文字颜色
  accent_color: "#ffd700"          # 强调色
  
  # 内容配置
  badge: "HOT"                     # 徽章文字
  brand: "My Brand"                # 品牌名称
  author: "AI Assistant"           # 作者名称
```

---

## 💡 **最佳实践**

### **标题设计**

✅ **好的标题**:
- "5步吃透CTR"
- "3分钟学会"
- "2024必备"

❌ **不好的标题**:
- "如何通过5个步骤优化YouTube封面点击率" (太长)
- "教程视频" (太普通)

### **配色建议**

**高对比度** (推荐):
```yaml
background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
text_color: "white"
```

**技术风格**:
```yaml
background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
text_color: "#00d9ff"
```

**温暖风格**:
```yaml
background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
text_color: "white"
```

### **徽章使用**

- `NEW` - 新品发布
- `HOT` - 热门内容
- `FREE` - 免费资源
- `2024` - 年份标记
- `PRO` - 专业版

---

## 🔧 **常见问题**

### **Q1: 如何禁用封面生成？**

```yaml
thumbnail:
  enabled: false
```

### **Q2: 封面生成失败会影响视频生成吗？**

不会。封面生成失败时，系统会记录错误并继续生成视频。

### **Q3: 如何自定义封面样式？**

创建自定义模板文件，放在`templates/thumbnails/`目录下，然后在配置中指定：

```yaml
thumbnail:
  template: "my-custom.html"
```

### **Q4: 封面标题从哪里来？**

封面标题来自`project.title`配置：

```yaml
project:
  title: "这是封面标题"
```

---

## 📚 **更多资源**

- **完整文档**: [THUMBNAIL-GENERATOR-GUIDE.md](file:///Users/mac/project/Wechatsync/demo-video-generator/docs/THUMBNAIL-GENERATOR-GUIDE.md)
- **整合报告**: [THUMBNAIL-INTEGRATION-REPORT-v1.3.0.md](file:///Users/mac/project/Wechatsync/demo-video-generator/THUMBNAIL-INTEGRATION-REPORT-v1.3.0.md)
- **示例代码**: [examples/thumbnail_examples.py](file:///Users/mac/project/Wechatsync/demo-video-generator/examples/thumbnail_examples.py)

---

## 🎉 **开始使用**

现在就在你的配置文件中添加`thumbnail`配置，享受自动封面生成的便利吧！

```yaml
thumbnail:
  enabled: true
  template: "default.html"
  badge: "HOT"
  brand: "My Brand"
```

运行视频生成，封面自动生成！🚀
