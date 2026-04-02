#!/usr/bin/env python3
"""
v3.0 竖屏封面生成示例 - 基于STEPPS病毒传播法则

本脚本展示如何使用新的竖屏适配功能生成移动端优化的封面
"""

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator, ThumbnailConfigValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_basic_vertical():
    """示例1: 基础竖屏封面生成"""
    print("\n" + "="*70)
    print("📱 示例1: 基础竖屏封面生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    config = {
        'title': '震惊！这个秘密竟然隐藏了十年',
        'template': 'viral-vertical.html',
        'width': 1080,
        'height': 1920,
        'badge': 'HOT',
        'emoji': '😱',
        'impact_text': 'MUST WATCH',
        'background': 'linear-gradient(180deg, #FF0844 0%, #FFB199 100%)',
        'accent_color': '#FFD700'
    }
    
    output_path = generator.generate(config)
    
    print(f"\n✅ 竖屏封面已生成: {output_path}")
    print(f"   尺寸: {config['width']}x{config['height']}")
    print(f"   模板: {config['template']}")
    
    return output_path


def example_2_viral_optimization():
    """示例2: 使用病毒传播优化（自动检测方向）"""
    print("\n" + "="*70)
    print("🚀 示例2: 使用病毒传播优化（自动检测方向）")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    title = "独家内幕：顶级专家揭秘赚钱的终极秘密方法"
    
    output_path = generator.generate_with_viral_optimization(
        title=title,
        subtitle="99%的人都不知道的真相",
        orientation='vertical',
        platform_hint='tiktok'
    )
    
    print(f"\n✅ 病毒优化封面已生成: {output_path}")
    print("   (查看上方日志了解优化详情)")


def example_3_stepps_analysis():
    """示例3: STEPPS病毒传播分析"""
    print("\n" + "="*70)
    print("📊 示例3: STEPPS病毒传播分析")
    print("="*70)
    
    test_titles = [
        "震惊！这个秘密竟然让100万人赚到了第一桶金",
        "感动到哭！真实故事：从负债百万到年入千万的逆袭之路",
        "紧急通知：限时免费分享，错过再等一年！",
        "独家教程：每天5分钟，教你如何快速提升效率300%"
    ]
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n--- 标题{i}: {title[:40]}... ---")
        
        stepps_result = CodeBasedThumbnailGenerator.analyze_stepps(title)
        
        print(f"   🎯 主要策略: {stepps_result['recommendations']['primary_strategy']}")
        print(f"   🔥 病毒评分: {stepps_result['viral_score']}/100")
        print(f"   💡 推荐模板: {stepps_result['recommendations']['best_template']}")
        print(f"   🏷️ 推荐徽章: {stepps_result['recommendations']['best_badge']}")
        
        if stepps_result['detected']:
            print(f"   📋 检测到的策略:")
            for principle_key, data in list(stepps_result['detected'].items())[:3]:
                print(f"      • {data['name']}: 匹配{data['count']}个关键词")


def example_4_multi_platform():
    """示例4: 多平台适配生成"""
    print("\n" + "="*70)
    print("🌐 示例4: 多平台适配生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    title = "震惊！这个方法让我月入十万"
    
    platforms = [
        {'name': 'YouTube 横版', 'orientation': 'horizontal', 'platform_hint': 'youtube'},
        {'name': 'TikTok 竖版', 'orientation': 'vertical', 'platform_hint': 'tiktok'},
        {'name': 'Instagram Reels', 'orientation': 'vertical', 'platform_hint': 'instagram_reels'},
        {'name': 'YouTube Shorts', 'orientation': 'vertical', 'platform_hint': 'youtube_shorts'}
    ]
    
    for platform in platforms:
        print(f"\n   生成 {platform['name']} 封面...")
        
        try:
            output_path = generator.generate_with_viral_optimization(
                title=title,
                subtitle="99%的人不知道的秘密",
                orientation=platform['orientation'],
                platform_hint=platform['platform_hint']
            )
            print(f"   ✅ 已生成: {output_path.name}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")


def example_5_curiosity_vertical():
    """示例5: 好奇心驱动型竖屏模板"""
    print("\n" + "="*70)
    print("❓ 示例5: 好奇心驱动型竖屏模板")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    config = {
        'title': '为什么聪明人都在用这个方法？',
        'template': 'curiosity-vertical.html',
        'width': 1080,
        'height': 1920,
        'badge': '秘密',
        'subtitle': '答案会让你大吃一惊...',
        'background': 'linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        'accent_color': '#FFD700'
    }
    
    output_path = generator.generate(config)
    
    print(f"\n✅ 好奇心封面已生成: {output_path}")


def example_6_emotional_story():
    """示例6: 情感故事型竖屏模板"""
    print("\n" + "="*70)
    print("💖 示例6: 情感故事型竖屏模板")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    config = {
        'title': '从绝望到希望：一个普通人的真实故事',
        'template': 'emotional-vertical.html',
        'width': 1080,
        'height': 1920,
        'badge': '感人',
        'subtitle': '"我曾经以为一切都结束了，直到那天..."',
        'emoji': '😢',
        'tagline': 'EMOTIONAL STORY',
        'background': 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
        'accent_color': '#FFD700'
    }
    
    output_path = generator.generate(config)
    
    print(f"\n✅ 情感封面已生成: {output_path}")


def example_7_urgency_action():
    """示例7: 紧急行动型竖屏模板"""
    print("\n" + "="*70)
    print("⚡ 示例7: 紧急行动型竖屏模板")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    config = {
        'title': '最后机会！错过就再也没有了',
        'template': 'urgency-vertical.html',
        'width': 1080,
        'height': 1920,
        'badge': '限时',
        'subtitle': '仅限今天，立即行动！',
        'timer_text': '⚡ ACT NOW ⚡',
        'cta_text': 'WATCH NOW!',
        'background': 'linear-gradient(180deg, #FF416C 0%, #FF4B2B 100%)',
        'accent_color': '#FFD700'
    }
    
    output_path = generator.generate(config)
    
    print(f"\n✅ 紧急行动封面已生成: {output_path}")


def main():
    """主函数"""
    print("\n" + "🎬"*35)
    print("  v3.0 竖屏封面生成器 - 基于STEPPS病毒传播法则")
    print("  支持移动端优化 (1080x1920) | YouTube Shorts | TikTok | Instagram Reels")
    print("🎬"*35)
    
    examples = [
        ("基础竖屏封面", example_1_basic_vertical),
        ("病毒传播优化", example_2_viral_optimization),
        ("STEPPS分析", example_3_stepps_analysis),
        ("多平台适配", example_4_multi_platform),
        ("好奇心模板", example_5_curiosity_vertical),
        ("情感故事模板", example_6_emotional_story),
        ("紧急行动模板", example_7_urgency_action)
    ]
    
    print("\n📋 可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"   {i}. {name}")
    
    print("\n💡 提示: 运行所有示例或选择特定示例")
    print("   按 Enter 运行全部，或输入编号选择示例: ", end='')
    
    choice = input().strip()
    
    if choice == '':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                logger.error(f"❌ {name} 失败: {e}")
                import traceback
                traceback.print_exc()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            logger.error(f"❌ {name} 失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ 无效选择，运行基础示例...")
        example_1_basic_vertical()
    
    print("\n" + "="*70)
    print("🎉 所有示例完成！")
    print("="*70)
    print("\n📁 输出目录: output/thumbnails/")
    print("\n💡 使用提示:")
    print("   • 竖屏尺寸: 1080x1920 (9:16比例)")
    print("   • 适用平台: TikTok, YouTube Shorts, Instagram Reels, 小红书")
    print("   • 优化法则: STEPPS (社交货币、诱因、情绪、公开性、实用价值、故事)")
    print("   • 自动检测: 根据标题和平台提示自动推荐最佳配置")
    print()


if __name__ == '__main__':
    main()