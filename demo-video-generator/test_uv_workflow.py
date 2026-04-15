#!/usr/bin/env python3
"""
UV测试脚本 - 测试封面生成和视频配置
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))


def test_thumbnail_generation():
    """测试封面生成"""
    print("\n" + "="*70)
    print("🎨 测试封面生成")
    print("="*70)
    
    try:
        from thumbnail_generator import CodeBasedThumbnailGenerator
        
        generator = CodeBasedThumbnailGenerator()
        
        config = {
            "template": "viral-vertical.html",
            "title": "震惊！这个方法太神奇了",
            "subtitle": "99%的人都不知道",
            "width": 1080,
            "height": 1920
        }
        
        print("\n📝 配置:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        print("\n🔄 生成封面...")
        output_path = generator.generate(config=config)
        
        if output_path and output_path.exists():
            print(f"✅ 成功: {output_path}")
            print(f"📊 文件大小: {output_path.stat().st_size / 1024:.2f} KB")
            return True
        else:
            print("❌ 失败: 文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_emotion_system():
    """测试表情系统"""
    print("\n" + "="*70)
    print("🎭 测试表情系统")
    print("="*70)
    
    try:
        from emotion_manager import EmotionManager
        
        manager = EmotionManager()
        
        print("\n📊 统计:")
        stats = manager.get_stats()
        print(f"  总表情数: {stats['total_emotions']}")
        print(f"  总分类数: {stats['total_categories']}")
        
        print("\n🎯 测试生成配置:")
        config = manager.get_template_config('happy', title="测试标题")
        print(f"  模板: {config['template']}")
        print(f"  表情: {config['emotion_name']}")
        print(f"  Emoji: {config['emoji']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_platform_templates():
    """测试平台模板"""
    print("\n" + "="*70)
    print("📺 测试平台模板系统")
    print("="*70)
    
    try:
        from platform_template_generator import PlatformTemplateGenerator
        
        generator = PlatformTemplateGenerator()
        
        print("\n📊 统计:")
        stats = generator.get_stats()
        print(f"  总平台数: {stats['total_platforms']}")
        
        print("\n🎯 测试YouTube模板:")
        config = generator.generate_template_config(
            platform='youtube',
            template_type='authentic_expression',
            title='测试标题'
        )
        print(f"  平台: {config['platform']}")
        print(f"  尺寸: {config['width']}×{config['height']}")
        print(f"  CTR提升: {config['ctr_boost']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_video_config():
    """测试视频配置"""
    print("\n" + "="*70)
    print("🎬 测试视频配置")
    print("="*70)
    
    try:
        import yaml
        
        config_file = Path("templates/basic.yaml")
        
        if not config_file.exists():
            print(f"❌ 配置文件不存在: {config_file}")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("\n📝 项目配置:")
        print(f"  名称: {config['project']['name']}")
        print(f"  URL: {config['project']['url']}")
        print(f"  场景数: {len(config['scenes'])}")
        
        print("\n🎙️ 语音配置:")
        print(f"  语言: {config['voice']['language']}")
        print(f"  语音: {config['voice']['voice_name']}")
        
        print("\n🎬 视频配置:")
        print(f"  格式: {config['video']['format']}")
        print(f"  分辨率: {config['video']['resolution']}")
        print(f"  帧率: {config['video']['fps']}")
        
        print("\n🎨 封面配置:")
        print(f"  启用: {config['thumbnail']['enabled']}")
        print(f"  模板: {config['thumbnail']['template']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 Demo Video Generator - UV测试")
    print("="*70)
    
    results = {
        "封面生成": test_thumbnail_generation(),
        "表情系统": test_emotion_system(),
        "平台模板": test_platform_templates(),
        "视频配置": test_video_config()
    }
    
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
