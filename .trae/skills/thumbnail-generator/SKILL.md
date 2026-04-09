---
name: "thumbnail-generator"
description: "视频封面生成系统 - 基于HTML/CSS+Playwright生成高CTR封面。包含53个模板、24个CSS表情、7种配色。Invoke when user needs to generate video thumbnails, create poster covers, or needs CTR-optimized visual content."
---

# 🎨 视频封面生成系统 Skill

## 📋 系统概述

基于HTML/CSS + Playwright的视频封面生成器，专为**高CTR（点击率）**设计。

**核心数据**:
- 总模板数: **53个**
- CSS表情: **24个**
- 配色方案: **7种**
- 动画效果: **15+种**

---

## 🚀 快速开始

### 1. 基础封面生成

```python
from lib.thumbnail_generator import CodeBasedThumbnailGenerator

generator = CodeBasedThumbnailGenerator()

config = {
    "template": "viral-vertical",
    "title": "震惊！这个方法太神奇了",
    "subtitle": "99%的人都不知道",
    "width": 1080,
    "height": 1920
}

output_path = generator.generate(config=config)
```

### 2. 智能模板推荐

```python
# 自动推荐最佳模板
recommendation = generator.recommend_template("震惊！这个方法让我月入10万")
config = recommendation['config']
output_path = generator.generate(config=config)
```

### 3. 使用表情模板

```python
config = {
    "template": "templates/thumbnails/emotions/emotion-shocked.html",
    "title": "震惊",
    "subtitle": "Unbelievable!"
}
output_path = generator.generate(config=config)
```

---

## 📁 模板分类

### 病毒式传播 (Viral)
- `viral.html` - 横屏 1280x720
- `viral-vertical.html` - 竖屏 1080x1920
- `viral-pro-v3.html` - 专业版
- `viral-expressive-v4.html` - 表情增强版

**适用**: 爆款视频、热点追踪

### 好奇心驱动 (Curiosity)
- `curiosity.html` - 横屏
- `curiosity-vertical.html` - 竖屏
- `curiosity-pro-v3.html` - 专业版

**适用**: 揭秘、教程、知识分享

### 紧迫感 (Urgency)
- `urgency.html` - 横屏
- `urgency-vertical.html` - 竖屏

**适用**: 限时促销、活动通知

### 情感共鸣 (Emotional)
- `emotional.html` - 横屏
- `emotional-vertical.html` - 竖屏

**适用**: 故事类、励志、情感

### MrBeast风格
- `mrbeast-style-v1.html` - 经典版
- `mrbeast-2026-v2.html` - 2026新版（悲伤悖论、数学构图）

**适用**: 挑战视频、YouTube封面

---

## 🎭 表情模板 (24个)

### 基础情绪
- `emotion-happy.html` 😄 - 开心
- `emotion-sad.html` 😢 - 悲伤
- `emotion-angry.html` 😡 - 愤怒
- `emotion-surprised.html` 😱 - 震惊
- `emotion-fear.html` 😨 - 恐惧
- `emotion-disgust.html` 🤢 - 厌恶

### 复杂情绪
- `emotion-anxious.html` 😰 - 焦虑
- `emotion-confused.html` 😕 - 困惑
- `emotion-embarrassed.html` 😅 - 尴尬
- `emotion-disappointed.html` 😞 - 失望
- `emotion-tired.html` 😫 - 疲惫
- `emotion-excited.html` 🤩 - 兴奋
- `emotion-suspicious.html` 🤨 - 怀疑
- `emotion-proud.html` 😏 - 得意
- `emotion-shy.html` 😳 - 害羞
- `emotion-pain.html` 😣 - 痛苦

### 极端情绪
- `emotion-crazy.html` 🤪 - 疯狂
- `emotion-desperate.html` 😩 - 绝望
- `emotion-ecstatic.html` 🥳 - 狂喜
- `emotion-terrified.html` 😱 - 恐怖
- `emotion-furious.html` 🤬 - 暴怒

### 特殊风格
- `emotion-pixel.html` 👾 - 像素风
- `emotion-comic.html` 💥 - 漫画风
- `emotion-minimal.html` ○ - 极简风

---

## 🎨 配色方案

```python
COLOR_SCHEMES = {
    'shock_red': '震惊红 - 紧急、激情',
    'mystery_dark': '神秘深蓝 - 好奇、悬疑',
    'urgency_orange': '紧迫橙红 - 紧急、行动',
    'emotional_purple': '情绪紫 - 情感、故事',
    'impact_black': '冲击黑金 - 极简、力量',
    'success_green': '成功绿 - 成长、财富',
    'energy_yellow': '能量黄 - 活力、创意'
}
```

---

## 🎯 使用场景指南

| 内容类型 | 推荐模板 | 推荐表情 | 配色 |
|---------|---------|---------|------|
| 搞笑视频 | viral-vertical | happy, crazy | energy_yellow |
| 失败经历 | mrbeast-2026-v2 | sad, disappointed | emotional_purple |
| 挑战视频 | viral-pro-v3 | anxious, excited | shock_red |
| 揭秘视频 | curiosity-pro-v3 | surprised, suspicious | mystery_dark |
| 励志视频 | emotional-vertical | proud, excited | success_green |
| 恐怖视频 | urgency-vertical | fear, terrified | impact_black |
| 促销活动 | urgency-vertical | excited, anxious | urgency_orange |
| 情感故事 | emotional-vertical | sad, happy | emotional_purple |

---

## ✨ 高级功能

### A/B测试

```python
variants = generator.generate_ab_variants(
    base_config,
    variations=['color', 'font_size', 'badge']
)
```

### 封面审查

```python
from lib.thumbnail_auditor import audit_thumbnail

report = audit_thumbnail(config)
print(f"评分: {report.overall_score}/100")
print(f"建议: {report.suggestions}")
```

### 批量生成

```python
titles = ["标题1", "标题2", "标题3"]
for title in titles:
    config = {
        "template": "viral-vertical",
        "title": title,
        "width": 1080,
        "height": 1920
    }
    generator.generate(config=config)
```

---

## 📚 相关文档

- `THUMBNAIL-SYSTEM-OVERVIEW.md` - 系统总览
- `EMOTION-TEMPLATE-GUIDE.md` - 表情指南
- `MRBEAST-2026-DESIGN-SYSTEM.md` - MrBeast设计
- `docs/THUMBNAIL-GENERATOR-GUIDE.md` - 详细指南

---

## 🔧 文件位置

```
demo-video-generator/
├── lib/thumbnail_generator.py      # 核心生成器
├── lib/emotion_template_generator.py  # 表情生成器
├── lib/thumbnail_auditor.py        # 审查系统
├── templates/thumbnails/           # 模板目录
│   ├── emotions/                   # 24个表情
│   └── *.html                      # 各类模板
└── examples/                       # 示例脚本
```

---

## 🎬 工作流

1. **分析需求** → 确定内容类型
2. **选择模板** → 使用智能推荐或手动选择
3. **配置参数** → 标题、副标题、配色等
4. **生成封面** → 运行生成脚本
5. **审查优化** → 使用audit_thumbnail检查
6. **A/B测试** → 生成多个变体对比

---

**版本**: v3.0  
**更新日期**: 2026-04-02
