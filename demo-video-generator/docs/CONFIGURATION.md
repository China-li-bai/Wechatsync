# Demo Video Generator - 配置文件详解

## 📋 配置文件结构

配置文件采用 YAML 格式，包含以下主要部分：

```yaml
project:      # 项目基础配置
voice:        # 语音配置
scenes:       # 场景配置（核心）
video:        # 视频配置
audio:        # 音频配置
subtitle:     # 字幕配置
advanced:     # 高级配置（可选）
```

---

## 🎯 项目配置（project）

```yaml
project:
  name: "Product Demo"                # 项目名称（用于显示）
  url: "https://product.com"          # 目标网站URL
  output_dir: "./output"              # 输出目录
  output_name: "demo"                 # 输出文件名（不含扩展名）
```

**说明**:
- `name`: 项目名称，用于日志和显示
- `url`: 要录制的产品网站地址
- `output_dir`: 所有输出文件的目录
- `output_name`: 最终视频文件名

---

## 🎙️ 语音配置（voice）

```yaml
voice:
  language: "zh-CN"                   # 语言代码
  voice_name: "XiaoxiaoNeural"        # 语音名称
  speed: 1.0                          # 语速（0.5-2.0）
```

### 语言代码

| 语言 | 代码 | 说明 |
|------|------|------|
| 大陆中文 | `zh-CN` | 普通话 |
| 台湾中文 | `zh-TW` | 繁体中文 |
| 香港中文 | `zh-HK` | 粤语 |
| 美式英语 | `en-US` | 美式英语 |
| 英式英语 | `en-GB` | 英式英语 |

### 推荐语音

**大陆中文**:
- `XiaoxiaoNeural`: 晓晓 - 女声（最自然，推荐）
- `YunxiNeural`: 云希 - 男声
- `YunyangNeural`: 云扬 - 男声

**台湾中文**:
- `HsiaoChenNeural`: 晓臻 - 女声（推荐）
- `HsiaoYuNeural`: 晓雨 - 女声

**香港中文**:
- `HiuGaaiNeural`: 曉佳 - 女声
- `WanLungNeural`: 雲龍 - 男声

**英文**:
- `JennyNeural`: Jenny - 女声（自然）
- `GuyNeural`: Guy - 男声

### 语速调整

```yaml
voice:
  speed: 0.8    # 慢速（适合教程）
  speed: 1.0    # 正常速度（推荐）
  speed: 1.2    # 快速（适合快速演示）
  speed: 1.5    # 很快（适合概览）
```

---

## 🎬 场景配置（scenes）

场景配置是核心部分，定义了视频的完整流程。

### 基础场景

```yaml
scenes:
  - name: "intro"                     # 场景名称
    type: "hook"                      # 场景类型
    text: "完整的解说文案..."          # 语音文本
    subtitle: "简短字幕"               # 字幕文本
    action: "screenshot"              # 动作类型
    wait_after: 3                     # 动作后等待时间（秒）
```

### 场景类型

#### 1. hook（钩子场景）

**用途**: 开场，抓住观众注意力

**建议时长**: 10-15秒

**文案技巧**:
- 使用反问句
- 提出痛点
- 制造悬念

**示例**:
```yaml
- name: "intro"
  type: "hook"
  text: |
    你有没有想过，让产品自己介绍自己？
    我们的产品让这个想法变成现实。
  subtitle: "你有没有想过，让产品自己介绍自己？"
  action: "screenshot"
  wait_after: 5
```

---

#### 2. feature（特性展示）

**用途**: 展示产品核心特性

**建议时长**: 15-20秒

**文案技巧**:
- 使用 FAB 法则
- 场景化表达
- 对比传统方案

**示例**:
```yaml
- name: "features"
  type: "feature"
  text: |
    传统方案太复杂！我们的产品只需简单配置，5分钟搞定。
    简单、高效、易用。
  subtitle: "只需简单配置，5分钟搞定"
  action: "scroll"
  scroll_distance: 300
  wait_after: 3
```

---

#### 3. demo（功能演示）

**用途**: 演示具体功能

**建议时长**: 20-30秒

**文案技巧**:
- 使用"想象一下"
- 描述使用场景
- 强调简单易用

**示例**:
```yaml
- name: "demo"
  type: "demo"
  text: |
    想象一下：用户只需点击按钮，功能自动执行。
    不需要复杂操作，不需要专业知识。
    就像有个助手在帮你工作。
  subtitle: "想象一下：用户只需点击按钮"
  action: "interact"
  selector: "#demo-button"
  wait_after: 5
```

---

#### 4. benefit（用户收益）

**用途**: 展示用户能获得的价值

**建议时长**: 15-20秒

**文案技巧**:
- 列举具体收益
- 使用数据支撑
- 触发情绪共鸣

**示例**:
```yaml
- name: "benefits"
  type: "benefit"
  text: |
    提升效率、节省时间、降低成本。
    让你的工作更轻松，让用户更满意。
  subtitle: "提升效率、节省时间、降低成本"
  action: "scroll"
  scroll_distance: 300
  wait_after: 3
```

---

#### 5. cta（行动号召）

**用途**: 结尾，引导用户行动

**建议时长**: 10-15秒

**文案技巧**:
- 明确的行动指令
- 强调价值主张
- 制造紧迫感

**示例**:
```yaml
- name: "cta"
  type: "cta"
  text: |
    现在就试试，体验产品的魅力！
    开源免费，快速上手。
  subtitle: "现在就试试，体验产品的魅力！"
  action: "scroll_to_top"
  wait_after: 5
```

---

### 动作类型

#### 1. screenshot（截图）

```yaml
action: "screenshot"
wait_after: 3
```

**说明**: 截取当前页面，等待指定时间

---

#### 2. scroll（滚动）

```yaml
action: "scroll"
scroll_distance: 300    # 滚动距离（像素）
wait_after: 3
```

**说明**: 向下滚动页面指定距离

---

#### 3. interact（交互）

```yaml
action: "interact"
selector: "#button"     # CSS选择器
wait_after: 5
```

**说明**: 点击指定元素

---

#### 4. scroll_to_top（回到顶部）

```yaml
action: "scroll_to_top"
wait_after: 5
```

**说明**: 滚动到页面顶部

---

## 📹 视频配置（video）

```yaml
video:
  format: "mp4"                       # 输出格式
  quality: "high"                     # 质量
  resolution: "1280x720"              # 分辨率
  fps: 30                             # 帧率
  codec: "libx264"                    # 编码器
```

### 输出格式

| 格式 | 兼容性 | 文件大小 | 推荐度 |
|------|--------|----------|--------|
| `mp4` | ✅ 最佳 | 中等 | ⭐⭐⭐⭐⭐ |
| `webm` | ⭐⭐⭐⭐ | 小 | ⭐⭐⭐⭐ |
| `mov` | ⭐⭐⭐ | 大 | ⭐⭐⭐ |

### 质量设置

| 质量 | 比特率 | 文件大小 | 适用场景 |
|------|--------|----------|----------|
| `low` | 500kbps | 小 | 快速预览 |
| `medium` | 1Mbps | 中等 | 一般用途 |
| `high` | 2Mbps | 大 | 高质量输出 |

---

## 🎵 音频配置（audio）

```yaml
audio:
  codec: "aac"                        # 编码器
  bitrate: "128k"                     # 比特率
```

### 音频编码器

| 编码器 | 兼容性 | 质量 | 推荐度 |
|--------|--------|------|--------|
| `aac` | ✅ 最佳 | 优秀 | ⭐⭐⭐⭐⭐ |
| `mp3` | ✅ 优秀 | 良好 | ⭐⭐⭐⭐ |
| `opus` | ⭐⭐⭐⭐ | 优秀 | ⭐⭐⭐⭐ |

---

## 📝 字幕配置（subtitle）

```yaml
subtitle:
  enabled: true                       # 是否启用
  format: "srt"                       # 格式
  font: "PingFang SC"                 # 字体
  font_size: 24                       # 字号
  color: "#FFFFFF"                    # 颜色
  outline_color: "#000000"            # 描边颜色
  background_color: "#80000000"       # 背景色
  outline: 2                          # 描边宽度
  shadow: 1                           # 阴影
```

### 字幕格式

| 格式 | 功能 | 兼容性 | 推荐度 |
|------|------|--------|--------|
| `srt` | 基础 | ✅ 最佳 | ⭐⭐⭐⭐⭐ |
| `ass` | 高级样式 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 字体推荐

**中文**:
- `PingFang SC`: macOS 系统字体（推荐）
- `Microsoft YaHei`: Windows 系统字体
- `SimHei`: 黑体

**英文**:
- `Arial`: 通用字体
- `Helvetica`: macOS 字体

---

## ⚙️ 高级配置（advanced）

```yaml
advanced:
  browser:
    headless: false                   # 无头模式
    timeout: 30000                    # 超时时间（毫秒）
    
  validation:
    check_sync: true                  # 检查同步
    check_quality: true               # 检查质量
    max_file_size: 10                 # 最大文件大小（MB）
    
  performance:
    parallel_voice: true              # 并行生成语音
    skip_existing: true               # 跳过已存在文件
```

---

## 📚 完整示例

查看 `templates/examples/` 目录中的完整示例配置。

---

## 💡 配置技巧

### 1. 时长控制

**总时长估算**:
```
总时长 = Σ(场景文案字数 / 语速)
```

**中文语速**: 约 3-4 字/秒

**示例**:
- 文案: 50字
- 语速: 1.0
- 预估时长: 50 / 3.5 ≈ 14秒

---

### 2. 场景数量

**推荐**: 5-8个场景

**总时长**: 60-120秒

**结构**:
- 开场: 1个场景（10-15秒）
- 中段: 3-6个场景（40-90秒）
- 结尾: 1个场景（10-15秒）

---

### 3. 文案长度

**每个场景**:
- 短文案: 20-30字（8-10秒）
- 中等文案: 30-50字（10-15秒）
- 长文案: 50-80字（15-25秒）

**建议**: 每个场景文案不超过 100字

---

**文档版本**: 1.0  
**最后更新**: 2026-03-30
