#!/usr/bin/env python3
"""
测试震惊风格封面模板
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator

print("="*60)
print("😱 测试震惊风格封面模板")
print("="*60)

generator = CodeBasedThumbnailGenerator(
    template_dir='templates/thumbnails',
    output_dir='output/test-shocked'
)

# 测试1: 震惊风格
print("\n测试1: 震惊风格封面")
print("-"*60)

config = {
    'title': '震惊！这个秘密',
    'subtitle': '你绝对想不到',
    'template': 'shocked.html',
    'background': 'linear-gradient(135deg, #FF4757 0%, #FF6B81 100%)',
    'badge': 'HOT',
    'font_size': 70,
    'text_color': 'white',
    'accent_color': '#FFD700'
}

try:
    output_path = generator.generate(config)
    print(f"✅ 震惊风格封面已生成: {output_path}")
except Exception as e:
    print(f"❌ 生成失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 对比原模板
print("\n测试2: 对比原模板")
print("-"*60)

config_default = {
    'title': '震惊！这个秘密',
    'subtitle': '你绝对想不到',
    'template': 'default.html',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'badge': 'HOT',
    'font_size': 80,
    'text_color': 'white'
}

try:
    output_path = generator.generate(config_default)
    print(f"✅ 默认模板封面已生成: {output_path}")
except Exception as e:
    print(f"❌ 生成失败: {e}")

print("\n" + "="*60)
print("✅ 测试完成！请对比两个封面效果")
print("="*60)
print("\n📊 对比要点:")
print("  1. 震惊风格: 有人脸+表情+鲜艳颜色+装饰元素")
print("  2. 默认模板: 只有文字+渐变背景")
print("\n💡 预期效果: 震惊风格的CTR应该提升50-100%")
print("="*60)
