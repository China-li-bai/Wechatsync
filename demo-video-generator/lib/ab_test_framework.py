#!/usr/bin/env python3
"""
A/B测试框架 - 基于文章中的洞见
支持快速迭代、对比和记录测试结果
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from thumbnail_generator import CodeBasedThumbnailGenerator, ThumbnailConfigValidator
from viral_format_library import ViralFormatLibrary, ViralFormat, ABTestResult

logger = logging.getLogger(__name__)


@dataclass
class TestVariant:
    """A/B测试变体"""
    variant_id: str
    name: str
    config: Dict[str, Any]
    description: str


class ABTestFramework:
    """A/B测试框架"""

    def __init__(self, generator: CodeBasedThumbnailGenerator, library: ViralFormatLibrary):
        self.generator = generator
        self.library = library

    def create_variants_from_tweaks(self, base_config: Dict[str, Any], tweaks: List[Dict[str, Any]]) -> List[TestVariant]:
        """
        通过细微调整创建变体（基于文章中的洞见）
        细微变化：渐变、更亮的笔触、表情符号等 → 1000倍结果差异
        """
        variants = []

        # 基础变体（A）
        variant_a = TestVariant(
            variant_id="variant_a",
            name="基础版本",
            config=base_config.copy(),
            description="原始配置，作为对照组"
        )
        variants.append(variant_a)

        # 应用微调创建变体B、C、D...
        for i, tweak in enumerate(tweaks):
            variant_config = base_config.copy()
            variant_config.update(tweak)

            variant = TestVariant(
                variant_id=f"variant_{chr(98 + i)}",  # b, c, d...
                name=f"变体{chr(65 + i + 1)}",
                config=variant_config,
                description=f"应用微调: {json.dumps(tweak, ensure_ascii=False)}"
            )
            variants.append(variant)

        return variants

    def generate_common_tweaks(self) -> List[Dict[str, Any]]:
        """
        生成常见的微调选项（基于文章中的洞见）
        即使是最细微的变化也能带来1000倍结果
        """
        return [
            # 渐变调整
            {
                'color_scheme': 'shock_red',
                'description': '改为震惊红渐变'
            },
            {
                'color_scheme': 'mystery_dark',
                'description': '改为神秘深蓝渐变'
            },
            {
                'color_scheme': 'urgency_orange',
                'description': '改为紧迫橙红渐变'
            },

            # Emoji变化
            {
                'emoji': '🔥',
                'description': 'Emoji改为火焰'
            },
            {
                'emoji': '💥',
                'description': 'Emoji改为爆炸'
            },
            {
                'emoji': '⚡',
                'description': 'Emoji改为闪电'
            },

            # 徽章变化
            {
                'badge': '🔥 HOT',
                'description': '徽章改为HOT'
            },
            {
                'badge': '⚡ EXCLUSIVE',
                'description': '徽章改为EXCLUSIVE'
            },
            {
                'badge': '💎 TOP',
                'description': '徽章改为TOP'
            },

            # 字体微调
            {
                'font_size': 85,
                'description': '字体调大10px'
            },
            {
                'font_size': 65,
                'description': '字体调小10px'
            }
        ]

    def run_ab_test(self, title: str, subtitle: Optional[str] = None,
                   num_variants: int = 3, custom_tweaks: Optional[List[Dict[str, Any]]] = None,
                   orientation: str = 'vertical') -> Tuple[str, List[Dict[str, Any]]]:
        """
        运行A/B测试（基于文章中的洞见）
        每个界面版本在多个账号发至少10条TikTok，如果不走红就修改
        """
        test_id = f"abtest_{uuid.uuid4().hex[:8]}"

        logger.info("="*70)
        logger.info(f"🚀 开始A/B测试: {test_id}")
        logger.info("="*70)

        # 生成基础配置
        base_config = self.generator.generate_viral_optimized_config(
            title=title,
            subtitle=subtitle,
            orientation=orientation
        )

        # 获取微调选项
        tweaks = custom_tweaks if custom_tweaks else self.generate_common_tweaks()

        # 选择前N个微调
        selected_tweaks = tweaks[:num_variants - 1]

        # 创建变体
        variants = self.create_variants_from_tweaks(base_config, selected_tweaks)

        logger.info(f"   📋 生成 {len(variants)} 个变体")

        results = []

        # 生成每个变体
        for variant in variants:
            logger.info(f"\n--- 生成 {variant.name} ---")
            logger.info(f"   描述: {variant.description}")

            try:
                output_path = self.generator.generate(
                    config=variant.config
                )

                result = {
                    'variant_id': variant.variant_id,
                    'variant_name': variant.name,
                    'config': variant.config,
                    'output_path': str(output_path),
                    'description': variant.description,
                    'generated_at': datetime.now().isoformat()
                }
                results.append(result)

                logger.info(f"   ✅ 生成成功: {output_path.name}")

            except Exception as e:
                logger.error(f"   ❌ 生成失败: {e}")
                result = {
                    'variant_id': variant.variant_id,
                    'variant_name': variant.name,
                    'config': variant.config,
                    'error': str(e),
                    'description': variant.description,
                    'generated_at': datetime.now().isoformat()
                }
                results.append(result)

        # 记录测试（初始状态，等待真实数据）
        ab_result = ABTestResult(
            test_id=test_id,
            title=f"A/B测试: {title[:30]}...",
            variant_a={
                'config': variants[0].config,
                'results': results[0] if results else {}
            },
            variant_b={
                'config': variants[1].config if len(variants) > 1 else {},
                'results': results[1] if len(results) > 1 else {}
            },
            created_at=datetime.now().isoformat()
        )
        self.library.record_ab_test(ab_result)

        logger.info("\n" + "="*70)
        logger.info(f"✅ A/B测试完成！测试ID: {test_id}")
        logger.info("="*70)
        logger.info("\n📊 下一步:")
        logger.info("   1. 在多个账号上发布每个变体至少10条视频")
        logger.info("   2. 收集观看数据和CTR")
        logger.info("   3. 更新测试结果")
        logger.info("   4. 如果都不走红，修改界面重新测试")

        return test_id, results

    def record_test_results(self, test_id: str, views_a: int, views_b: int,
                            ctr_a: float = 0.0, ctr_b: float = 0.0,
                            notes: Optional[str] = None):
        """
        记录测试结果（基于文章中的洞见）
        """
        ab_result = self.library.ab_tests.get(test_id)
        if not ab_result:
            logger.error(f"找不到测试: {test_id}")
            return

        # 更新数据
        ab_result.views_a = views_a
        ab_result.views_b = views_b
        ab_result.ctr_a = ctr_a
        ab_result.ctr_b = ctr_b
        ab_result.notes = notes

        # 确定赢家
        if views_a > views_b and ctr_a > ctr_b:
            ab_result.winner = 'A'
        elif views_b > views_a and ctr_b > ctr_a:
            ab_result.winner = 'B'
        else:
            ab_result.winner = None

        self.library._save()

        logger.info("="*70)
        logger.info(f"📊 测试结果已更新: {test_id}")
        logger.info("="*70)

        if ab_result.winner:
            logger.info(f"🎉 赢家: 变体{ab_result.winner}")
        else:
            logger.warning("⚠️ 没有明显赢家，建议继续测试")

        logger.info(f"\n📈 数据:")
        logger.info(f"   变体A: {views_a:,} 观看, CTR {ctr_a*100:.2f}%")
        logger.info(f"   变体B: {views_b:,} 观看, CTR {ctr_b*100:.2f}%")

        if ab_result.winner:
            diff_views = views_b - views_a if ab_result.winner == 'B' else views_a - views_b
            diff_ctr = ctr_b - ctr_a if ab_result.winner == 'B' else ctr_a - ctr_b
            logger.info(f"\n🚀 提升:")
            logger.info(f"   观看: +{diff_views:,} (+{(diff_views/(min(views_a, views_b) if min(views_a, views_b) > 0 else 1))*100:.1f}%)")
            logger.info(f"   CTR: +{diff_ctr*100:.2f}%")

        if notes:
            logger.info(f"\n📝 备注: {notes}")

    def get_insights_summary(self) -> Dict[str, Any]:
        """获取所有A/B测试的洞察总结"""
        insights = self.library.get_ab_test_insights()

        summary = {
            'total_tests': len(insights),
            'winner_variant_a': sum(1 for i in insights if i['winner'] == 'A'),
            'winner_variant_b': sum(1 for i in insights if i['winner'] == 'B'),
            'avg_views_improvement': 0,
            'avg_ctr_improvement': 0,
            'key_findings': []
        }

        if insights:
            summary['avg_views_improvement'] = sum(i['views_diff'] for i in insights) / len(insights)
            summary['avg_ctr_improvement'] = sum(i['ctr_diff'] for i in insights) / len(insights)

            # 找出最成功的微调
            successful_tweaks = {}
            for insight in insights:
                if insight['notes']:
                    note = insight['notes']
                    if note not in successful_tweaks:
                        successful_tweaks[note] = 0
                    successful_tweaks[note] += 1

            summary['key_findings'] = sorted(
                successful_tweaks.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

        return summary


def example_ab_test_workflow():
    """A/B测试工作流示例（基于文章中的洞见）"""
    print("\n" + "="*70)
    print("  🧪 A/B测试工作流示例")
    print("="*70)

    # 初始化
    generator = CodeBasedThumbnailGenerator()
    library = ViralFormatLibrary()
    framework = ABTestFramework(generator, library)

    # 测试标题
    title = "独家内幕：顶级专家揭秘赚钱的终极秘密方法"
    subtitle = "99%的人都不知道的真相"

    print(f"\n📝 测试标题: {title}")

    # 运行A/B测试
    test_id, results = framework.run_ab_test(
        title=title,
        subtitle=subtitle,
        num_variants=3,
        orientation='vertical'
    )

    print(f"\n✅ 测试已创建: {test_id}")
    print(f"\n📋 生成的变体:")
    for result in results:
        print(f"   • {result['variant_name']}: {result['output_path']}")
        print(f"     {result['description']}")

    print("\n" + "="*70)
    print("  💡 下一步（基于文章中的洞见）:")
    print("="*70)
    print("   1. 在多个TikTok账号上发布每个变体")
    print("   2. 每个变体至少发10条视频")
    print("   3. 收集观看数据和CTR")
    print("   4. 如果都不走红 → 修改界面，重新测试")
    print("   5. 即使细微变化（渐变、Emoji）也可能带来1000倍结果")
    print("="*70)

    return test_id


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    example_ab_test_workflow()