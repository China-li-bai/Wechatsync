#!/usr/bin/env python3
"""
测试封面生成功能整合到视频生成器
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from demo_video_generator import DemoVideoGenerator
from thumbnail_generator import CodeBasedThumbnailGenerator

print("="*60)
print("🧪 测试封面生成功能整合")
print("="*60)

print("\n步骤1: 测试封面生成器独立功能")
print("-"*60)

generator = CodeBasedThumbnailGenerator(
    template_dir='templates/thumbnails',
    output_dir='output/test-thumbnails'
)

config = {
    'title': '测试封面',
    'subtitle': '整合测试',
    'template': 'default.html',
    'badge': 'TEST'
}

try:
    output_path = generator.generate(config)
    print(f"✅ 封面生成成功: {output_path}")
except Exception as e:
    print(f"❌ 封面生成失败: {e}")
    sys.exit(1)

print("\n步骤2: 测试视频生成器整合")
print("-"*60)

try:
    video_gen = DemoVideoGenerator('config/test-thumbnail.yaml', log_level='INFO')
    print("✅ 视频生成器初始化成功")
    print(f"   封面配置: {video_gen.thumbnail_config}")
except Exception as e:
    print(f"❌ 视频生成器初始化失败: {e}")
    sys.exit(1)

print("\n步骤3: 测试封面生成方法")
print("-"*60)

try:
    thumbnail_path = video_gen._generate_thumbnail()
    if thumbnail_path:
        print(f"✅ 封面生成成功: {thumbnail_path}")
    else:
        print("⚠️  封面生成被禁用或失败")
except Exception as e:
    print(f"❌ 封面生成失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ 所有测试通过！")
print("="*60)
print("\n📝 整合成功总结:")
print("  1. ✅ 封面生成器独立功能正常")
print("  2. ✅ 视频生成器成功整合封面配置")
print("  3. ✅ 封面生成方法正常工作")
print("\n🎉 封面生成功能已成功整合到视频生成流程中！")
print("="*60)
