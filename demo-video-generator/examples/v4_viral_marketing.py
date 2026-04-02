#!/usr/bin/env python3
"""
v4.0 病毒式营销系统 - 完全基于文章中的洞见
整合：病毒式格式库 + A/B测试 + 格式组合器
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator
from viral_format_library import ViralFormatLibrary, initialize_sample_library
from ab_test_framework import ABTestFramework
from format_combiner import FormatCombiner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_format_library():
    """演示病毒式格式库"""
    print_header("📚 1. 病毒式格式库")

    library = initialize_sample_library()

    print(f"\n📊 库统计:")
    print(f"   • 病毒式格式: {len(library.formats)}")
    print(f"   • 格式组合: {len(library.combinations)}")
    print(f"   • A/B测试: {len(library.ab_tests)}")

    print("\n🏆 成功率最高的格式:")
    top_formats = library.get_top_formats(3)
    for i, fmt in enumerate(top_formats, 1):
        print(f"\n   {i}. {fmt.name}")
        print(f"      类别: {fmt.category}")
        print(f"      年份: {fmt.year or 'N/A'}")
        print(f"      成功率: {fmt.success_rate*100:.0f}%")
        print(f"      平均观看: {fmt.views_average:,}")
        print(f"      最高观看: {fmt.views_max:,}")
        if fmt.key_elements:
            print(f"      关键元素: {', '.join(fmt.key_elements[:3])}")


def demo_ab_testing():
    """演示A/B测试"""
    print_header("🧪 2. A/B测试框架")

    print("""
💡 基于文章中的洞见:
   • 每个界面版本在多个账号发至少10条TikTok
   • 如果不走红，修改界面重新测试
   • 即使细微变化（渐变、更亮的笔触、表情符号）→ 1000倍结果差异
    """)

    # 初始化
    generator = CodeBasedThumbnailGenerator()
    library = ViralFormatLibrary()
    framework = ABTestFramework(generator, library)

    title = "独家内幕：顶级专家揭秘赚钱的终极秘密方法"
    subtitle = "99%的人都不知道的真相"

    print(f"\n📝 测试标题: {title}")

    # 生成常见微调选项
    tweaks = framework.generate_common_tweaks()
    print(f"\n🔧 可用微调选项: {len(tweaks)}个")
    for i, tweak in enumerate(tweaks[:5], 1):
        print(f"   {i}. {tweak.get('description', 'N/A')}")

    # 运行A/B测试
    print("\n🚀 运行A/B测试 (生成3个变体)...")
    test_id, results = framework.run_ab_test(
        title=title,
        subtitle=subtitle,
        num_variants=3,
        orientation='vertical'
    )

    print(f"\n✅ 测试ID: {test_id}")
    print(f"\n📋 生成的变体:")
    for result in results:
        print(f"   • {result['variant_name']}")
        print(f"     {result['description']}")

    # 模拟记录结果（示例数据）
    print("\n📊 模拟记录观看数据 (示例)...")
    framework.record_test_results(
        test_id=test_id,
        views_a=250000,
        views_b=1800000,  # 变体B获胜，7.2倍提升！
        ctr_a=0.035,
        ctr_b=0.128,
        notes="变体B使用了更亮的渐变和火焰Emoji，带来7.2倍观看提升！"
    )

    # 获取洞察
    print("\n📈 A/B测试洞察:")
    insights = framework.get_insights_summary()
    print(f"   总测试数: {insights['total_tests']}")
    print(f"   变体A获胜: {insights['winner_variant_a']}")
    print(f"   变体B获胜: {insights['winner_variant_b']}")


def demo_format_combination():
    """演示格式组合"""
    print_header("🔗 3. 格式组合器")

    print("""
💡 基于文章中的洞见:
   • 病毒式格式 = 当前病毒格式 + 以往病毒格式的综合
   • Spotify Wrapped: 蒙面遮掩数据 + 暗示震惊数据
   • 你的最佳格式不一定来自你的类别，甚至不一定是今年发布的
    """)

    # 初始化
    library = initialize_sample_library()
    generator = CodeBasedThumbnailGenerator()
    combiner = FormatCombiner(library, generator)

    # 示例组合
    print("\n🔄 示例: 组合2025 Wrapped + 2024 Spotify + 2022 Cutouts")

    wrapped_2025 = library.get_format("wrapped_2025")
    spotify_2024 = library.get_format("spotify_wrapped_2024")
    cutouts_2022 = library.get_format("cutouts_2022")

    if wrapped_2025 and spotify_2024 and cutouts_2022:
        combo_config = combiner.combine_formats(
            primary_format=wrapped_2025,
            secondary_formats=[spotify_2024, cutouts_2022],
            name="2025 Wrapped + 2024 Spotify + 2022 Cutouts"
        )

    # 自动建议最佳组合
    print("\n🎯 自动建议最佳组合 (curiosity类别)...")
    try:
        combo_config = combiner.suggest_best_combination("curiosity")
        print(f"   组合名称: {combo_config['combination_name']}")
        print(f"   描述: {combo_config['description']}")
        print(f"   模板: {combo_config['template']}")
        print(f"   配色: {combo_config['color_scheme']}")
        print(f"   关键元素: {len(combo_config['key_elements'])}个")
    except Exception as e:
        print(f"   ⚠️ {e}")

    # 使用组合生成封面
    print("\n🎨 使用组合生成封面...")
    try:
        output_path = combiner.generate_with_combination(
            title="独家内幕：顶级专家揭秘赚钱的终极秘密方法",
            subtitle="99%的人都不知道的真相",
            target_category="curiosity",
            orientation='vertical'
        )
        print(f"   ✅ 生成成功: {output_path}")
    except Exception as e:
        print(f"   ⚠️ 生成失败: {e}")


def demo_full_workflow():
    """演示完整工作流"""
    print_header("🚀 4. 完整病毒式营销工作流")

    print("""
📋 工作流步骤（基于文章中的洞见）:

1️⃣ 产品和营销共同设计（不要产品做完才营销）
2️⃣ 每个界面版本在多个账号发至少10条TikTok
3️⃣ 如果不走红 → 修改界面（即使细微变化！）
4️⃣ 找到病毒式传播格式 → 复制给所有创作者
5️⃣ 格式组合：当前格式 + 历史格式
6️⃣ 持续刷TikTok找趋势（或让AI代理帮你刷）
    """)

    print("\n" + "="*70)
    print("  💡 关键洞见回顾")
    print("="*70)
    print("""
🎯 病毒式传播格式 = 当前病毒格式 + 以往病毒格式的综合

🔬 A/B测试: 即使细微变化（渐变、Emoji）→ 1000倍结果差异

👥 跨团队协作: 市场、工程、设计应该24小时分享一切

🔍 找趋势: 每天刷几小时TikTok，或让AI代理刷10,000个视频

🎭 UGC活动: 找到关键创作者，把成功格式发给所有人

💰 激励: $100/周 + $100/10万观看，创作者会和你一样投入
    """)


def main():
    """主函数"""
    print("\n" + "🎬"*35)
    print("  v4.0 病毒式营销系统 - 基于实战洞见")
    print("🎬"*35)

    print("\n" + "="*70)
    print("  📖 基于文章的核心洞见:")
    print("="*70)
    print("   1. 产品和营销共同设计（不是产品做完才营销）")
    print("   2. 每个界面版本 → 多个账号发至少10条TikTok")
    print("   3. 不走红就改界面 → 即使细微变化也能1000倍结果")
    print("   4. 病毒式格式 = 当前病毒格式 + 以往病毒格式的综合")
    print("   5. 找到病毒式格式 → 复制给所有创作者")
    print("   6. 持续刷TikTok找趋势（或让AI代理刷）")

    print("\n" + "="*70)
    print("  📋 演示选项:")
    print("="*70)
    print("   1. 病毒式格式库")
    print("   2. A/B测试框架")
    print("   3. 格式组合器")
    print("   4. 完整工作流演示")
    print("   5. 运行全部演示")

    print("\n💡 请选择 (1-5, 默认5): ", end='')

    try:
        choice = input().strip()
    except:
        choice = '5'

    if choice == '':
        choice = '5'

    if choice == '1':
        demo_format_library()
    elif choice == '2':
        demo_ab_testing()
    elif choice == '3':
        demo_format_combination()
    elif choice == '4':
        demo_full_workflow()
    elif choice == '5':
        demo_format_library()
        demo_ab_testing()
        demo_format_combination()
        demo_full_workflow()
    else:
        print("⚠️ 无效选择，运行全部演示...")
        demo_format_library()
        demo_ab_testing()
        demo_format_combination()
        demo_full_workflow()

    print("\n" + "="*70)
    print("  📚 新增文件清单:")
    print("="*70)
    print("   • lib/viral_format_library.py    - 病毒式格式库")
    print("   • lib/ab_test_framework.py       - A/B测试框架")
    print("   • lib/format_combiner.py         - 格式组合器")
    print("   • examples/v4_viral_marketing.py - 本演示脚本")
    print("\n" + "="*70)
    print("  ✅ 所有演示完成！")
    print("="*70)


if __name__ == '__main__':
    main()