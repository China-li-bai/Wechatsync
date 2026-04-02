#!/usr/bin/env python3
"""
v3.0 深度优化封面测试 - 标题质量分析 + 病毒传播优化
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


def test_title_analysis():
    """测试标题质量分析"""
    print("\n" + "="*70)
    print("📊 标题质量分析测试")
    print("="*70)
    
    test_titles = [
        "震惊！这个秘密让100万人赚到了第一桶金",
        "教程",
        "如何通过3个简单步骤快速提升工作效率，让你每天多出2小时自由时间",
        "从负债百万到年入千万，这个普通人的故事感动了无数人",
        "Python入门"
    ]
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n--- 标题{i}: {title} ---")
        
        quality = ThumbnailConfigValidator.analyze_title_quality(title)
        
        print(f"   ⭐ 评分: {quality['scores']['total']}/100 ({quality['rating']})")
        print(f"   📏 长度: {quality['title_length']}字")
        print(f"   📝 字数: {quality['word_count']}")
        print(f"   🎯 强力词: {len(quality['power_words'])}个")
        if quality['power_words']:
            for pw in quality['power_words'][:3]:
                print(f"      • {pw['word']} ({pw['category']})")
        print(f"   ❓ 疑问句: {'是' if quality['has_question'] else '否'}")
        print(f"   🔢 数字: {'是' if quality['has_number'] else '否'}")
        
        if quality['suggestions']:
            print(f"   💡 建议:")
            for suggestion in quality['suggestions']:
                print(f"      • {suggestion}")
        
        improvements = ThumbnailConfigValidator.suggest_title_improvements(title)
        if len(improvements) > 1 or (len(improvements) == 1 and "已经很好" not in improvements[0]):
            print(f"   ✨ 改进方案:")
            for imp in improvements[:4]:
                if "已经很好" not in imp:
                    print(f"      • {imp}")


def test_viral_optimization_with_analysis():
    """测试病毒传播优化（带标题分析）"""
    print("\n" + "="*70)
    print("🚀 病毒传播优化测试（带标题分析）")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    
    test_cases = [
        {
            'title': '独家内幕：顶级专家揭秘赚钱的终极秘密方法',
            'subtitle': '99%的人都不知道的真相',
            'orientation': 'vertical',
            'platform_hint': 'tiktok'
        },
        {
            'title': '感动到哭！从负债百万到年入千万的真实故事',
            'subtitle': '"我曾经以为一切都结束了..."',
            'orientation': 'vertical',
            'platform_hint': 'shorts'
        },
        {
            'title': '紧急通知：限时免费分享，错过再等一年！',
            'subtitle': '仅限今天，立即行动！',
            'orientation': 'vertical',
            'platform_hint': 'reels'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例{i} ---")
        print(f"   标题: {test_case['title']}")
        
        quality = ThumbnailConfigValidator.analyze_title_quality(test_case['title'])
        print(f"   标题评分: {quality['scores']['total']}/100 ({quality['rating']})")
        
        try:
            output_path = generator.generate_with_viral_optimization(
                title=test_case['title'],
                subtitle=test_case.get('subtitle'),
                orientation=test_case.get('orientation'),
                platform_hint=test_case.get('platform_hint')
            )
            print(f"   ✅ 生成成功: {output_path.name}")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()


def test_batch_quality_comparison():
    """测试批量标题质量对比"""
    print("\n" + "="*70)
    print("📈 批量标题质量对比")
    print("="*70)
    
    titles = [
        "Python教程",
        "3个Python技巧让你效率翻倍",
        "震惊！这5个Python秘密技巧99%的人都不知道",
        "独家！顶级Python工程师分享的10个终极技巧"
    ]
    
    results = []
    for title in titles:
        quality = ThumbnailConfigValidator.analyze_title_quality(title)
        results.append({
            'title': title,
            'score': quality['scores']['total'],
            'rating': quality['rating'],
            'power_words': len(quality['power_words'])
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n🏆 排名:")
    for i, result in enumerate(results, 1):
        stars = "⭐" * (result['score'] // 20)
        print(f"   {i}. [{result['score']:3d}] {stars} - {result['rating']}")
        print(f"      {result['title']}")
        print(f"      (强力词: {result['power_words']}个)")


def test_stepps_analysis():
    """测试STEPPS病毒传播分析"""
    print("\n" + "="*70)
    print("🧠 STEPPS病毒传播法则分析")
    print("="*70)
    
    test_titles = [
        "独家内幕：顶级专家揭秘赚钱的终极秘密方法",
        "每天5分钟，教你如何快速提升效率",
        "感动到哭！真实故事：从负债百万到年入千万",
        "100万人都在用的方法，你还不知道？",
        "免费教程：3个让你省钱的实用技巧"
    ]
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n--- 标题{i}: {title[:40]}... ---")
        
        stepps_result = CodeBasedThumbnailGenerator.analyze_stepps(title)
        
        print(f"   🔥 病毒评分: {stepps_result['viral_score']}/100")
        print(f"   💡 主要策略: {stepps_result['recommendations']['primary_strategy']}")
        
        if stepps_result['detected']:
            print(f"   📋 检测到的STEPPS原则:")
            for principle_key, data in stepps_result['detected'].items():
                print(f"      • {data['name']}: 匹配{data['count']}个关键词")
                if len(data['matched_keywords']) <= 3:
                    print(f"        关键词: {', '.join(data['matched_keywords'])}")
                else:
                    print(f"        关键词: {', '.join(data['matched_keywords'][:3])}...")
        
        if stepps_result['recommendations']['secondary_strategies']:
            print(f"   🔄 次要策略: {', '.join(stepps_result['recommendations']['secondary_strategies'])}")
        
        print(f"   🚀 病毒潜力: {'高' if stepps_result['has_viral_potential'] else '中'}")


def main():
    """主函数"""
    print("\n" + "🎬"*35)
    print("  v3.0 深度优化封面系统 - 标题质量分析 + STEPPS病毒传播")
    print("🎬"*35)
    
    print("\n📋 测试选项:")
    print("   1. 标题质量分析")
    print("   2. 病毒传播优化（带标题分析）")
    print("   3. 批量标题质量对比")
    print("   4. STEPPS病毒传播分析")
    print("   5. 运行全部测试")
    
    print("\n💡 请选择测试 (1-5, 默认5): ", end='')
    
    try:
        choice = input().strip()
    except:
        choice = '5'
    
    if choice == '':
        choice = '5'
    
    if choice == '1':
        test_title_analysis()
    elif choice == '2':
        test_viral_optimization_with_analysis()
    elif choice == '3':
        test_batch_quality_comparison()
    elif choice == '4':
        test_stepps_analysis()
    elif choice == '5':
        test_title_analysis()
        test_stepps_analysis()
        test_batch_quality_comparison()
        test_viral_optimization_with_analysis()
    else:
        print("⚠️ 无效选择，运行全部测试...")
        test_title_analysis()
        test_stepps_analysis()
        test_batch_quality_comparison()
        test_viral_optimization_with_analysis()
    
    print("\n" + "="*70)
    print("🎉 所有测试完成！")
    print("="*70)
    print("\n📚 详细优化指南请查看: THUMBNAIL-OPTIMIZATION-GUIDE.md")
    print("\n💡 核心功能:")
    print("   • 标题质量评分 (0-100分)")
    print("   • STEPPS病毒传播法则分析")
    print("   • 7大类强力词检测")
    print("   • 自动标题改进建议")
    print("   • 竖屏/横屏自动适配")
    print("   • 基于情绪的模板推荐")


if __name__ == '__main__':
    main()