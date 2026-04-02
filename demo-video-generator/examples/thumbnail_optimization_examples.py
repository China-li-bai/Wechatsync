#!/usr/bin/env python3
"""
高CTR封面生成器使用示例

演示如何使用v2.0的新功能生成吸引眼球的封面
"""

import logging
from pathlib import Path
from lib.thumbnail_generator import CodeBasedThumbnailGenerator, ThumbnailConfigValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_smart_optimization():
    """示例1: 智能优化生成 - 自动推荐最佳模板和配色"""
    print("\n" + "="*70)
    print("📱 示例1: 智能CTR优化生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails/examples',
        logger=logger
    )
    
    test_titles = [
        "震惊！这个Python技巧竟然能让你的代码快10倍",
        "揭秘：没人告诉你的AI赚钱秘密武器",
        "紧急！限时24小时，这个机会错过就没了",
        "感动到哭！一个程序员的真实逆袭故事",
        "月入百万！我的终极财富自由之路"
    ]
    
    for title in test_titles:
        print(f"\n🎯 生成封面: {title}")
        print("-" * 60)
        
        try:
            output_path = generator.generate_with_optimization(
                title=title,
                subtitle="点击了解更多",
                output_path=f"output/thumbnails/examples/example1_{len(test_titles) - test_titles.index(title)}.png"
            )
            print(f"✅ 成功生成: {output_path}")
        except Exception as e:
            print(f"❌ 生成失败: {e}")


def example_2_emotion_analysis():
    """示例2: 情绪分析 - 检测标题中的情绪触发词"""
    print("\n" + "="*70)
    print("🔍 示例2: 情绪触发词分析")
    print("="*70)
    
    test_titles = [
        "震惊！这个方法太神奇了",
        "揭秘隐藏的真相",
        "立即行动，最后机会",
        "感动到泪目的故事",
        "突破自我，实现财富自由"
    ]
    
    for title in test_titles:
        print(f"\n📝 分析标题: {title}")
        analysis = ThumbnailConfigValidator.analyze_emotion(title)
        
        print(f"   检测到情绪触发词: {analysis['total_triggers']} 个")
        if analysis['primary']:
            print(f"   主要情绪: {analysis['primary']}")
            print(f"   关键词: {', '.join(analysis['detected'][analysis['primary']]['keywords'])}")


def example_3_template_recommendation():
    """示例3: 模板推荐 - 基于内容推荐最佳模板"""
    print("\n" + "="*70)
    print("🎨 示例3: 智能模板推荐")
    print("="*70)
    
    test_cases = [
        ("震惊！这个发现让人不敢相信", None),
        ("揭秘：隐藏的秘密真相", None),
        ("紧急通知：限时优惠", None),
        ("感人的真实故事", None),
        ("成功之路：财富自由", None),
        ("自定义标题", "viral")
    ]
    
    for title, style in test_cases:
        print(f"\n📋 标题: {title}")
        if style:
            print(f"   指定风格: {style}")
        
        recommendation = ThumbnailConfigValidator.recommend_template(title, style)
        
        print(f"   推荐模板: {recommendation['template']}")
        print(f"   推荐理由: {recommendation['reason']}")
        print(f"   置信度: {recommendation['confidence']}%")


def example_4_color_scheme():
    """示例4: 配色方案推荐 - 基于情绪推荐最佳配色"""
    print("\n" + "="*70)
    print("🌈 示例4: 色彩心理学配色推荐")
    print("="*70)
    
    test_titles = [
        "震惊！爆炸性新闻",
        "神秘未解之谜",
        "紧急行动通知",
        "温暖治愈故事",
        "成功突破记录"
    ]
    
    for title in test_titles:
        print(f"\n🎨 标题: {title}")
        
        color_scheme = ThumbnailConfigValidator.recommend_color_scheme(title)
        
        print(f"   配色方案: {color_scheme['scheme_name']}")
        print(f"   描述: {color_scheme['description']}")
        print(f"   推荐依据: {color_scheme['recommended_by']}")


def example_5_ab_test():
    """示例5: A/B测试 - 生成多个变体进行对比"""
    print("\n" + "="*70)
    print("🧪 示例5: A/B测试变体生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails/examples',
        logger=logger
    )
    
    title = "震惊！这个发现改变一切"
    
    print(f"\n📊 为标题生成A/B测试变体: {title}")
    print("-" * 60)
    
    try:
        variants = generator.generate_ab_test_variants(
            title=title,
            variants_count=3,
            output_dir='output/thumbnails/examples/ab_test'
        )
        
        print(f"\n✅ 成功生成 {len(variants)} 个变体:")
        for variant in variants:
            print(f"   变体{variant['variant_id']}: {variant['style']}")
            print(f"      路径: {variant['output_path']}")
            if variant['meta'].get('optimization_notes'):
                print(f"      优化建议: {variant['meta']['optimization_notes'][0]}")
        
        print("\n💡 使用建议:")
        print("   1. 在实际环境中测试这些变体的点击率")
        print("   2. 收集数据，选择表现最好的变体")
        print("   3. 持续优化，迭代改进")
        
    except Exception as e:
        print(f"❌ A/B测试生成失败: {e}")


def example_6_custom_config():
    """示例6: 自定义配置 - 完全控制每个元素"""
    print("\n" + "="*70)
    print("⚙️ 示例6: 自定义配置生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails/examples',
        logger=logger
    )
    
    config = {
        'title': '终极Python教程',
        'subtitle': '从零到精通的完整指南',
        'template': 'viral.html',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'font_size': 80,
        'text_color': '#FFFFFF',
        'badge': 'HOT',
        'accent_color': '#FFD700',
        'emoji': '🚀',
        'impact_text': '🔥 必看教程 🔥',
        'width': 1280,
        'height': 720
    }
    
    print("\n📋 自定义配置:")
    for key, value in config.items():
        if not key.startswith('_'):
            print(f"   {key}: {value}")
    
    try:
        output_path = generator.generate(
            config=config,
            output_path='output/thumbnails/examples/example6_custom.png'
        )
        print(f"\n✅ 成功生成自定义封面: {output_path}")
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")


def example_7_batch_generation():
    """示例7: 批量生成 - 高效处理多个视频"""
    print("\n" + "="*70)
    print("📦 示例7: 批量生成封面")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails/examples',
        logger=logger
    )
    
    configs = [
        {
            'title': '震惊！AI革命',
            'subtitle': '技术突破',
            'template': 'viral.html',
            'badge': 'HOT'
        },
        {
            'title': '揭秘真相',
            'subtitle': '深度调查',
            'template': 'curiosity.html',
            'badge': '秘密'
        },
        {
            'title': '紧急通知',
            'subtitle': '限时优惠',
            'template': 'urgency.html',
            'badge': '立即'
        }
    ]
    
    print(f"\n📋 批量生成 {len(configs)} 个封面")
    print("-" * 60)
    
    try:
        output_paths = generator.generate_batch(
            configs=configs,
            output_dir='output/thumbnails/examples/batch'
        )
        
        print(f"\n✅ 成功批量生成 {len(output_paths)} 个封面:")
        for i, path in enumerate(output_paths, 1):
            print(f"   {i}. {path}")
            
    except Exception as e:
        print(f"\n❌ 批量生成失败: {e}")


def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print("🎬 高CTR封面生成器 v2.0 - 使用示例")
    print("="*70)
    print("\n本示例演示如何使用新功能生成吸引眼球的封面")
    print("基于CTR优化原则和心理学设计，提升视频点击率")
    
    examples = [
        ("智能优化生成", example_1_smart_optimization),
        ("情绪触发词分析", example_2_emotion_analysis),
        ("智能模板推荐", example_3_template_recommendation),
        ("色彩心理学配色", example_4_color_scheme),
        ("A/B测试变体", example_5_ab_test),
        ("自定义配置", example_6_custom_config),
        ("批量生成", example_7_batch_generation)
    ]
    
    print("\n📚 可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"   {i}. {name}")
    
    print("\n💡 提示:")
    print("   - 运行所有示例: 直接执行此脚本")
    print("   - 运行特定示例: 修改 main() 函数")
    print("   - 查看生成的封面: output/thumbnails/examples/")
    
    print("\n" + "="*70)
    print("🚀 开始执行示例...")
    print("="*70)
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            logger.error(f"示例 '{name}' 执行失败: {e}")
    
    print("\n" + "="*70)
    print("✅ 所有示例执行完成!")
    print("="*70)
    print("\n📂 生成的封面文件位于: output/thumbnails/examples/")
    print("\n💡 下一步:")
    print("   1. 查看生成的封面效果")
    print("   2. 根据实际需求调整配置")
    print("   3. 在实际环境中测试CTR效果")
    print("   4. 持续优化和迭代改进")


if __name__ == '__main__':
    main()