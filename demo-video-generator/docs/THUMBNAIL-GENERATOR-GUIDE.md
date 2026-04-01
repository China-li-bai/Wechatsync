# 🎨 编码封面生成器 - 使用指南

**版本**: v1.3.0  
**更新日期**: 2026-04-01

---

## 📖 **简介**

编码封面生成器是一个基于HTML/CSS + Playwright的封面生成工具，具有以下特点：

- ✅ **完全可控**: 精确控制每个元素的位置、大小、颜色
- ✅ **可验证**: 配置验证和输出验证
- ✅ **吸引眼球**: 基于CTR优化原则设计
- ✅ **统一风格**: 模板系统保证一致性

---

## 🚀 **快速开始**

### **安装依赖**

```bash
pip install jinja2 playwright
python -m playwright install chromium
```

---

### **基础使用**

```python
from lib.thumbnail_generator import CodeBasedThumbnailGenerator

# 创建生成器
generator = CodeBasedThumbnailGenerator(
    template_dir='templates/thumbnails',
    output_dir='output/thumbnails'
)

# 配置封面
config = {
    'title': '5步吃透CTR',
    'subtitle': 'YouTube封面优化指南',
    'badge': 'HOT',
    'brand': 'Demo Video Generator'
}

# 生成封面
output_path = generator.generate(config)
print(f"封面已生成: {output_path}")
```

---

## 📝 **配置说明**

### **必需字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | str | 主标题（必需） |

---

### **可选字段**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `template` | str | `default.html` | 模板名称 |
| `width` | int | 1280 | 宽度（像素） |
| `height` | int | 720 | 高度（像素） |
| `subtitle` | str | None | 副标题 |
| `background` | str | 渐变色 | 背景色/渐变 |
| `font_size` | int | 80 | 字体大小 |
| `text_color` | str | `white` | 文字颜色 |
| `badge` | str | None | 徽章文字 |
| `brand` | str | None | 品牌名称 |
| `author` | str | None | 作者名称 |
| `accent_color` | str | `#ffd700` | 强调色 |
| `style` | str | `minimal` | 风格类型 |
| `steps` | int | None | 步骤数（教程模板） |
| `rating` | int | None | 评分（评测模板） |

---

### **风格类型**

- `tutorial` - 教程类
- `review` - 评测类
- `news` - 新闻类
- `entertainment` - 娱乐类
- `tech` - 技术类
- `minimal` - 简约类

---

## 🎨 **模板示例**

### **1. 默认模板** (default.html)

**特点**: 简洁大气，适合通用场景

**示例**:
```python
config = {
    'title': 'Python入门教程',
    'subtitle': '从零开始学编程',
    'badge': 'NEW',
    'brand': 'Demo Video Generator',
    'author': 'AI Assistant'
}
```

---

### **2. 教程模板** (tutorial.html)

**特点**: 带步骤指示器，适合教程类视频

**示例**:
```python
config = {
    'template': 'tutorial.html',
    'title': 'Python入门教程',
    'subtitle': '从零开始学编程',
    'badge': 'NEW',
    'brand': 'Demo Video Generator',
    'steps': 5,  # 显示5个步骤
    'author': 'AI Assistant',
    'background': 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)'
}
```

---

### **3. 评测模板** (review.html)

**特点**: 带评分显示，适合评测类视频

**示例**:
```python
config = {
    'template': 'review.html',
    'title': 'iPhone 15 Pro',
    'subtitle': '深度评测',
    'rating': 5,  # 5星评分
    'badge': '推荐',
    'brand': 'Tech Review',
    'background': 'linear-gradient(135deg, #2ec4b6 0%, #e71d36 100%)'
}
```

---

## 🎯 **配色方案**

### **推荐配色**

#### **教程类**
```python
'background': 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)'
'accent_color': '#ffd700'
```

#### **技术类**
```python
'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
'accent_color': '#00d9ff'
```

#### **评测类**
```python
'background': 'linear-gradient(135deg, #2ec4b6 0%, #e71d36 100%)'
'accent_color': '#ffd700'
```

#### **新闻类**
```python
'background': 'linear-gradient(135deg, #e63946 0%, #f1faee 100%)'
'accent_color': '#a8dadc'
```

---

## 💡 **最佳实践**

### **1. 文字设计**

- ✅ **字数**: 主标题建议3-5个词
- ✅ **字体**: 使用粗体，易于阅读
- ✅ **颜色**: 高对比度，确保可读性

---

### **2. 视觉设计**

- ✅ **简洁**: 避免过多元素
- ✅ **焦点**: 突出主要信息
- ✅ **一致性**: 保持品牌风格统一

---

### **3. CTR优化**

- ✅ **吸引眼球**: 使用明亮颜色
- ✅ **情感连接**: 添加人脸特写（可选）
- ✅ **紧迫感**: 使用"NEW"、"HOT"等徽章

---

## 🔧 **高级功能**

### **批量生成**

```python
configs = [
    {'title': f'测试标题 {i}', 'subtitle': f'测试副标题 {i}'}
    for i in range(1, 11)
]

output_paths = generator.generate_batch(configs, output_dir='output/batch')
print(f"生成了 {len(output_paths)} 个封面")
```

---

### **HTML预览**

```python
# 预览HTML（用于调试）
html = generator.preview_html(config)
print(html)
```

---

### **上下文管理器**

```python
# 自动资源管理
with CodeBasedThumbnailGenerator() as generator:
    output_path = generator.generate(config)
    print(f"封面已生成: {output_path}")
# 资源自动清理
```

---

## 📊 **性能指标**

| 操作 | 性能 | 说明 |
|------|------|------|
| **单个生成** | ~1秒 | 包含浏览器启动 |
| **批量生成** | ~0.5秒/个 | 复用浏览器实例 |
| **HTML预览** | <0.1秒 | 仅渲染模板 |

---

## 🐛 **故障排除**

### **问题1: ModuleNotFoundError: No module named 'jinja2'**

**解决方案**:
```bash
pip install jinja2
```

---

### **问题2: ModuleNotFoundError: No module named 'playwright'**

**解决方案**:
```bash
pip install playwright
python -m playwright install chromium
```

---

### **问题3: 浏览器启动失败**

**解决方案**:
- 确保已安装Chromium: `python -m playwright install chromium`
- 检查网络连接
- 尝试使用系统浏览器

---

## 📚 **API参考**

### **CodeBasedThumbnailGenerator**

#### **初始化**

```python
__init__(
    template_dir: str = 'templates/thumbnails',
    output_dir: str = 'output/thumbnails',
    logger: Optional[logging.Logger] = None
)
```

---

#### **generate方法**

```python
generate(
    config: Dict[str, Any],
    output_path: Optional[str] = None,
    validate: bool = True
) -> Path
```

**参数**:
- `config`: 配置字典
- `output_path`: 输出路径（可选）
- `validate`: 是否验证配置

**返回**: 生成的封面文件路径

---

#### **generate_batch方法**

```python
generate_batch(
    configs: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    validate: bool = True
) -> List[Path]
```

**参数**:
- `configs`: 配置列表
- `output_dir`: 输出目录（可选）
- `validate`: 是否验证配置

**返回**: 生成的封面文件路径列表

---

#### **preview_html方法**

```python
preview_html(config: Dict[str, Any]) -> str
```

**参数**:
- `config`: 配置字典

**返回**: 渲染后的HTML字符串

---

## 🎉 **总结**

编码封面生成器提供了：

- ✅ **完全可控**的封面生成
- ✅ **灵活配置**的模板系统
- ✅ **高CTR**的设计原则
- ✅ **统一风格**的品牌一致性

**开始使用**: 按照快速开始指南，立即生成你的第一个封面！

---

**文档版本**: v1.3.0  
**更新日期**: 2026-04-01  
**状态**: ✅ 完成

---

**🎨 编码封面生成器 - 让封面生成更简单！** 🚀
