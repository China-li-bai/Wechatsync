#!/usr/bin/env python3
"""
测试DiceBear表情模板
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator
from emoji_generator import EmojiGenerator

print("="*60)
print("🎭 测试DiceBear表情模板 - v3.0.0")
print("="*60)

generator = CodeBasedThumbnailGenerator(
    template_dir='templates/thumbnails',
    output_dir='output/test-emoji'
)

emoji_gen = EmojiGenerator(output_dir='output/emojis')

print("\n🎨 测试1: 快乐表情")
print("-"*60)

happy_svg = emoji_gen.generate('happy')
print(f"✅ 表情SVG: {happy_svg}")

config_happy = {
    'title': '超简单教程',
    'subtitle': '3分钟学会',
    'template': 'emoji-dicebear.html',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'badge': 'NEW',
    'emoji_url': 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=happy',
    'emoji_alt': 'happy',
    'accent_color': '#FFD700'
}

try:
    output_path = generator.generate(config_happy)
    print(f"✅ 封面生成成功: {output_path}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n😲 测试2: 震惊表情")
print("-"*60)

shocked_svg = emoji_gen.generate('shocked')
print(f"✅ 表情SVG: {shocked_svg}")

config_shocked = {
    'title': '震惊！这个秘密',
    'subtitle': '你绝对想不到',
    'template': 'emoji-dicebear.html',
    'background': 'linear-gradient(135deg, #FF4757 0%, #FF6B81 100%)',
    'badge': 'HOT',
    'emoji_url': 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=shocked',
    'emoji_alt': 'shocked',
    'accent_color': '#FFD700'
}

try:
    output_path = generator.generate(config_shocked)
    print(f"✅ 封面生成成功: {output_path}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n😎 测试3: 酷表情")
print("-"*60)

cool_svg = emoji_gen.generate('cool')
print(f"✅ 表情SVG: {cool_svg}")

config_cool = {
    'title': '科技新品',
    'subtitle': '抢先体验',
    'template': 'emoji-dicebear.html',
    'background': 'linear-gradient(135deg, #00C6FF 0%, #0072FF 100%)',
    'badge': 'COOL',
    'emoji_url': 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=cool',
    'emoji_alt': 'cool',
    'accent_color': '#FFD700'
}

try:
    output_path = generator.generate(config_cool)
    print(f"✅ 封面生成成功: {output_path}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*60)
print("✅ 所有测试完成！")
print("="*60)

print("\n📊 对比:")
print("  旧方案: SVG静态表情（手工绘制）")
print("  新方案: DiceBear动态表情（API生成）")
print("\n💡 优势:")
print("  ✅ 表情更丰富（15+种预设情感）")
print("  ✅ 生成更快速（API即时生成）")
print("  ✅ 风格更多样（10+种风格）")
print("  ✅ 维护更简单（无需手工绘制）")
print("  ✅ 确定性生成（相同seed相同表情）")
print("="*60)
