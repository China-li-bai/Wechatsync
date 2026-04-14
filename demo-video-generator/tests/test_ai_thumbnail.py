#!/usr/bin/env python3
"""
集成AI图像生成器到封面生成器
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator
from ai_image_generator import AIImageGenerator

print("="*60)
print("🎨 AI封面生成器集成测试")
print("="*60)

API_KEY = 'sk-bslkcslwfoyghkuahkrzzsrvphyrcjgegrjmonnzaxxanvmb'

ai_gen = AIImageGenerator(api_key=API_KEY, output_dir='output/ai-images')
thumb_gen = CodeBasedThumbnailGenerator(
    template_dir='templates/thumbnails',
    output_dir='output/ai-thumbnails'
)

print("\n🧪 测试1: 震惊风格AI封面")
print("-"*60)

print("步骤1: 生成AI背景图像...")
ai_image_path = ai_gen.generate_youtube_thumbnail(
    style='shocking',
    custom_prompt='dramatic explosion in background, person with shocked expression',
    title='Amazing Discovery'
)
print(f"✅ AI图像生成成功: {ai_image_path}")

print("\n步骤2: 生成封面...")
config_shocking = {
    'title': '震惊！这个发现',
    'subtitle': '改变一切',
    'template': 'ai-generated.html',
    'ai_image_url': str(ai_image_path),
    'ai_image_alt': 'Shocking Discovery',
    'badge': 'HOT',
    'accent_color': '#FF4757'
}

output_path = thumb_gen.generate(config_shocking)
print(f"✅ 封面生成成功: {output_path}")

print("\n" + "="*60)
print("🧪 测试2: 科技风格AI封面")
print("-"*60)

print("步骤1: 生成AI背景图像...")
ai_image_path = ai_gen.generate_youtube_thumbnail(
    style='tech',
    custom_prompt='futuristic cityscape with neon lights, cyberpunk atmosphere',
    title='Future Tech'
)
print(f"✅ AI图像生成成功: {ai_image_path}")

print("\n步骤2: 生成封面...")
config_tech = {
    'title': '未来科技',
    'subtitle': '抢先体验',
    'template': 'ai-generated.html',
    'ai_image_url': str(ai_image_path),
    'ai_image_alt': 'Future Technology',
    'badge': 'NEW',
    'accent_color': '#00C6FF'
}

output_path = thumb_gen.generate(config_tech)
print(f"✅ 封面生成成功: {output_path}")

print("\n" + "="*60)
print("🧪 测试3: 自然风格AI封面")
print("-"*60)

print("步骤1: 生成AI背景图像...")
ai_image_path = ai_gen.generate_youtube_thumbnail(
    style='nature',
    custom_prompt='beautiful mountain landscape at sunset, golden hour lighting',
    title='Nature Beauty'
)
print(f"✅ AI图像生成成功: {ai_image_path}")

print("\n步骤2: 生成封面...")
config_nature = {
    'title': '自然之美',
    'subtitle': '震撼心灵',
    'template': 'ai-generated.html',
    'ai_image_url': str(ai_image_path),
    'ai_image_alt': 'Nature Beauty',
    'badge': 'WOW',
    'accent_color': '#FFD700'
}

output_path = thumb_gen.generate(config_nature)
print(f"✅ 封面生成成功: {output_path}")

print("\n" + "="*60)
print("✅ 所有测试完成！")
print("="*60)

print("\n📊 AI封面生成流程:")
print("  1. 使用AI生成高质量背景图像")
print("  2. 应用YouTube风格优化")
print("  3. 叠加文字和徽章")
print("  4. 添加视觉效果和动画")

print("\n💡 优势:")
print("  ✅ 独一无二的背景图像")
print("  ✅ 高质量AI生成")
print("  ✅ 多种风格可选")
print("  ✅ 自动优化提示词")
print("  ✅ 快速生成")
print("="*60)
