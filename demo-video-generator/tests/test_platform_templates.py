#!/usr/bin/env python3
"""
测试平台专属封面生成系统
验证各平台模板配置和生成
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.platform_template_generator import PlatformTemplateGenerator
from lib.thumbnail_generator import CodeBasedThumbnailGenerator


def test_platform_generator():
    """测试平台模板生成器"""
    print("="*70)
    print("📺 测试平台模板生成器")
    print("="*70)
    
    generator = PlatformTemplateGenerator()
    
    print("\n📊 统计信息:")
    stats = generator.get_stats()
    print(f"  总平台数: {stats['total_platforms']}")
    for platform, count in stats['platforms'].items():
        print(f"  {platform}: {count}个模板")
    
    print("\n" + generator.list_platforms())


def test_youtube_templates():
    """测试YouTube模板"""
    print("\n" + "="*70)
    print("📺 测试YouTube模板")
    print("="*70)
    
    platform_gen = PlatformTemplateGenerator()
    thumbnail_gen = CodeBasedThumbnailGenerator()
    
    template_types = ['authentic_expression', 'z_pattern_layout', 'curiosity_gap']
    
    for template_type in template_types:
        print(f"\n生成 '{template_type}' 模板...")
        
        config = platform_gen.generate_template_config(
            platform='youtube',
            template_type=template_type,
            title=f"YouTube {template_type} 测试"
        )
        
        print(f"  尺寸: {config['width']}×{config['height']}")
        print(f"  CTR提升: {config['ctr_boost']}")
        print(f"  设计要素: {', '.join(config['design_elements'][:2])}...")
        
        try:
            output_path = thumbnail_gen.generate(config={
                'template': 'viral.html',
                'title': config['title'],
                'width': config['width'],
                'height': config['height']
            })
            print(f"  ✅ 成功: {output_path}")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")


def test_tiktok_templates():
    """测试TikTok模板"""
    print("\n" + "="*70)
    print("🎵 测试TikTok模板")
    print("="*70)
    
    platform_gen = PlatformTemplateGenerator()
    thumbnail_gen = CodeBasedThumbnailGenerator()
    
    template_types = ['close_up', 'value_direct', 'before_after', 'process_record']
    
    for template_type in template_types:
        print(f"\n生成 '{template_type}' 模板...")
        
        config = platform_gen.generate_template_config(
            platform='tiktok',
            template_type=template_type,
            title=f"TikTok {template_type} 测试"
        )
        
        print(f"  尺寸: {config['width']}×{config['height']}")
        print(f"  CTR提升: {config['ctr_boost']}")
        
        try:
            output_path = thumbnail_gen.generate(config={
                'template': 'viral-vertical.html',
                'title': config['title'],
                'width': config['width'],
                'height': config['height']
            })
            print(f"  ✅ 成功: {output_path}")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")


def test_xiaohongshu_templates():
    """测试小红书模板"""
    print("\n" + "="*70)
    print("📕 测试小红书模板")
    print("="*70)
    
    platform_gen = PlatformTemplateGenerator()
    thumbnail_gen = CodeBasedThumbnailGenerator()
    
    template_types = ['conflict_compare', 'number_cover', 'chat_record', 'memo_style']
    
    for template_type in template_types:
        print(f"\n生成 '{template_type}' 模板...")
        
        config = platform_gen.generate_template_config(
            platform='xiaohongshu',
            template_type=template_type,
            title=f"小红书 {template_type} 测试"
        )
        
        print(f"  尺寸: {config['width']}×{config['height']}")
        print(f"  CTR提升: {config['ctr_boost']}")
        
        try:
            output_path = thumbnail_gen.generate(config={
                'template': 'viral-vertical.html',
                'title': config['title'],
                'width': config['width'],
                'height': config['height']
            })
            print(f"  ✅ 成功: {output_path}")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")


def test_recommendations():
    """测试模板推荐"""
    print("\n" + "="*70)
    print("🎯 测试模板推荐")
    print("="*70)
    
    generator = PlatformTemplateGenerator()
    
    test_cases = [
        ('youtube', 'Vlog'),
        ('tiktok', '美妆'),
        ('xiaohongshu', '护肤'),
        ('tiktok', '美食'),
        ('xiaohongshu', '减肥'),
    ]
    
    for platform, content_type in test_cases:
        print(f"\n平台: {platform}, 内容类型: {content_type}")
        recommendations = generator.recommend_template(platform, content_type)
        
        if recommendations:
            for rec in recommendations:
                template_types = generator.get_platform_template_types(platform)
                if rec in template_types:
                    template = template_types[rec]
                    print(f"  ✅ {template.name} ({template.ctr_boost})")
        else:
            print("  (无推荐)")


def test_best_practices():
    """测试最佳实践"""
    print("\n" + "="*70)
    print("📋 测试最佳实践")
    print("="*70)
    
    generator = PlatformTemplateGenerator()
    
    platforms = ['youtube', 'tiktok', 'xiaohongshu', 'twitter', 'facebook']
    
    for platform in platforms:
        print(f"\n### {platform.upper()}")
        practices = generator.get_best_practices(platform)
        
        for key, value in practices.items():
            print(f"  {key}: {value}")


def test_color_schemes():
    """测试配色方案"""
    print("\n" + "="*70)
    print("🎨 测试配色方案")
    print("="*70)
    
    generator = PlatformTemplateGenerator()
    
    platforms = ['youtube', 'tiktok', 'xiaohongshu', 'twitter', 'facebook']
    
    for platform in platforms:
        print(f"\n### {platform.upper()}")
        color_scheme = generator.get_color_scheme(platform)
        
        primary = color_scheme.get('primary', [])
        print(f"  主色: {', '.join(primary[:3])}")
        
        combinations = color_scheme.get('combinations', [])
        if combinations:
            print(f"  推荐组合: {combinations[0]}")


if __name__ == '__main__':
    test_platform_generator()
    test_youtube_templates()
    test_tiktok_templates()
    test_xiaohongshu_templates()
    test_recommendations()
    test_best_practices()
    test_color_schemes()
    
    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)
