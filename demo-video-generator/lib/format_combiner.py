#!/usr/bin/env python3
"""
病毒式格式组合器 - 基于文章中的洞见
支持跨类别、跨年的格式融合
"""

import logging
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from viral_format_library import ViralFormatLibrary, ViralFormat, FormatCombination
from thumbnail_generator import CodeBasedThumbnailGenerator

logger = logging.getLogger(__name__)


@dataclass
class FormatElement:
    """格式元素"""
    name: str
    category: str  # emoji, badge, color, layout, animation
    description: str
    value: Any


class FormatCombiner:
    """格式组合器"""

    def __init__(self, library: ViralFormatLibrary, generator: CodeBasedThumbnailGenerator):
        self.library = library
        self.generator = generator

    def extract_elements(self, viral_format: ViralFormat) -> List[FormatElement]:
        """从格式中提取可复用元素"""
        elements = []

        if viral_format.color_scheme:
            elements.append(FormatElement(
                name="配色方案",
                category="color",
                description=f"{viral_format.color_scheme} 配色",
                value=viral_format.color_scheme
            ))

        if viral_format.template_name:
            elements.append(FormatElement(
                name="模板布局",
                category="layout",
                description=f"{viral_format.template_name} 模板",
                value=viral_format.template_name
            ))

        for key_elem in viral_format.key_elements:
            elements.append(FormatElement(
                name=f"关键元素: {key_elem}",
                category="key_element",
                description=key_elem,
                value=key_elem
            ))

        return elements

    def combine_formats(self, primary_format: ViralFormat,
                       secondary_formats: List[ViralFormat],
                       name: Optional[str] = None) -> Dict[str, Any]:
        """
        组合多个格式（基于文章中的洞见）
        病毒式格式 = 当前病毒格式 + 以往病毒格式的综合
        """
        logger.info("="*70)
        logger.info(f"🔗 开始格式组合")
        logger.info("="*70)

        primary_elements = self.extract_elements(primary_format)
        all_secondary_elements = []

        for fmt in secondary_formats:
            all_secondary_elements.extend(self.extract_elements(fmt))

        logger.info(f"\n📋 主格式: {primary_format.name}")
        logger.info(f"   元素数: {len(primary_elements)}")
        logger.info(f"   成功率: {primary_format.success_rate*100:.0f}%")

        for i, fmt in enumerate(secondary_formats, 1):
            logger.info(f"\n📋 辅助格式{i}: {fmt.name}")
            logger.info(f"   元素数: {len(self.extract_elements(fmt))}")
            logger.info(f"   成功率: {fmt.success_rate*100:.0f}%")

        # 构建组合配置
        combined_config = {
            'template': primary_format.template_name or 'viral-vertical.html',
            'color_scheme': primary_format.color_scheme or 'shock_red',
            'primary_format_id': primary_format.id,
            'secondary_format_ids': [fmt.id for fmt in secondary_formats],
            'combination_name': name or f"{primary_format.name} + 历史格式",
            'key_elements': list(set(
                primary_format.key_elements +
                [elem for fmt in secondary_formats for elem in fmt.key_elements]
            )),
            'description': f"基于{primary_format.name}，融合{len(secondary_formats)}个历史成功格式"
        }

        # 智能选择最佳元素
        # 选择配色方案（优先选成功率最高的）
        all_formats = [primary_format] + secondary_formats
        best_format = max(all_formats, key=lambda x: x.success_rate)

        if best_format.color_scheme:
            combined_config['color_scheme'] = best_format.color_scheme
            logger.info(f"\n🎨 采用配色方案: {best_format.color_scheme} (来自: {best_format.name})")

        # 选择模板（优先选主格式的）
        if primary_format.template_name:
            combined_config['template'] = primary_format.template_name
            logger.info(f"📐 采用模板布局: {primary_format.template_name}")

        logger.info(f"\n✅ 格式组合完成！")
        logger.info(f"   关键元素数: {len(combined_config['key_elements'])}")

        # 记录组合
        combo_id = self.library.create_combination(
            primary_id=primary_format.id,
            secondary_ids=[fmt.id for fmt in secondary_formats],
            name=combined_config['combination_name'],
            description=combined_config['description']
        )

        combined_config['combination_id'] = combo_id

        return combined_config

    def suggest_best_combination(self, target_category: str,
                                num_secondary: int = 2) -> Dict[str, Any]:
        """
        建议最佳格式组合（基于文章中的洞见）
        """
        # 1. 找到目标类别中成功率最高的格式作为主格式
        category_formats = self.library.get_formats_by_category(target_category)
        if not category_formats:
            category_formats = list(self.library.formats.values())

        if not category_formats:
            raise ValueError("没有可用的格式")

        primary = max(category_formats, key=lambda x: x.success_rate)

        # 2. 找到其他类别或其他年份的成功格式作为辅助
        others = [
            f for f in self.library.formats.values()
            if f.id != primary.id and f.success_rate > 0.5
        ]

        # 优先选不同年份的
        historical = sorted(
            others,
            key=lambda x: (abs((x.year or 2025) - (primary.year or 2025)), -x.success_rate)
        )

        secondary = historical[:num_secondary]

        if not secondary:
            secondary = others[:num_secondary]

        # 3. 组合
        return self.combine_formats(primary, secondary)

    def generate_with_combination(self, title: str, subtitle: Optional[str] = None,
                                 target_category: str = "curiosity",
                                 orientation: str = 'vertical') -> str:
        """使用格式组合生成封面"""
        logger.info("\n" + "="*70)
        logger.info(f"🎨 使用格式组合生成封面")
        logger.info("="*70)

        # 获取最佳组合
        combo_config = self.suggest_best_combination(target_category)

        logger.info(f"\n📝 标题: {title}")
        logger.info(f"🎯 目标类别: {target_category}")
        logger.info(f"🔗 组合名称: {combo_config['combination_name']}")

        # 生成基础配置
        base_config = self.generator.generate_viral_optimized_config(
            title=title,
            subtitle=subtitle,
            orientation=orientation
        )

        # 应用组合配置
        final_config = base_config.copy()
        final_config['template'] = combo_config['template']
        final_config['color_scheme'] = combo_config['color_scheme']
        final_config['combination_id'] = combo_config['combination_id']

        # 生成
        output_path = self.generator.generate(
            config=final_config
        )

        logger.info(f"\n✅ 生成成功!")
        logger.info(f"   文件: {output_path.name}")

        return str(output_path)


def example_combination_workflow():
    """格式组合工作流示例（基于文章中的洞见）"""
    print("\n" + "="*70)
    print("  🔗 格式组合工作流示例")
    print("="*70)

    # 初始化
    from viral_format_library import initialize_sample_library
    library = initialize_sample_library()
    generator = CodeBasedThumbnailGenerator()
    combiner = FormatCombiner(library, generator)

    print("\n📊 可用格式:")
    for fmt_id, fmt in library.formats.items():
        print(f"   • {fmt.name}")
        print(f"     成功率: {fmt.success_rate*100:.0f}%, 平均观看: {fmt.views_average:,}")

    # 示例1: 组合2025 Wrapped + 历史格式
    print("\n" + "="*70)
    print("  示例1: 组合2025 Wrapped + 历史格式")
    print("="*70)

    wrapped_2025 = library.get_format("wrapped_2025")
    spotify_2024 = library.get_format("spotify_wrapped_2024")
    cutouts_2022 = library.get_format("cutouts_2022")

    if wrapped_2025 and spotify_2024 and cutouts_2022:
        combo_config = combiner.combine_formats(
            primary_format=wrapped_2025,
            secondary_formats=[spotify_2024, cutouts_2022],
            name="2025 Wrapped + 2024 Spotify + 2022 Cutouts"
        )

        print(f"\n✅ 组合配置:")
        print(f"   名称: {combo_config['combination_name']}")
        print(f"   模板: {combo_config['template']}")
        print(f"   配色: {combo_config['color_scheme']}")
        print(f"   关键元素: {len(combo_config['key_elements'])}个")

    # 示例2: 自动建议最佳组合
    print("\n" + "="*70)
    print("  示例2: 自动建议最佳组合")
    print("="*70)

    try:
        combo_config = combiner.suggest_best_combination("curiosity")
        print(f"\n✅ 建议的组合:")
        print(f"   名称: {combo_config['combination_name']}")
        print(f"   描述: {combo_config['description']}")
    except Exception as e:
        print(f"⚠️ 跳过: {e}")

    # 示例3: 使用组合生成封面
    print("\n" + "="*70)
    print("  示例3: 使用格式组合生成封面")
    print("="*70)

    try:
        output_path = combiner.generate_with_combination(
            title="独家内幕：顶级专家揭秘赚钱的终极秘密方法",
            subtitle="99%的人都不知道的真相",
            target_category="curiosity",
            orientation='vertical'
        )
        print(f"\n✅ 封面已生成: {output_path}")
    except Exception as e:
        print(f"⚠️ 生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("  ✅ 格式组合工作流示例完成!")
    print("="*70)
    print("\n💡 核心思想（基于文章）:")
    print("   病毒式格式 = 当前病毒格式 + 以往病毒格式的综合")
    print("   你的最佳格式不一定来自你的类别，甚至不一定是今年发布的")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    example_combination_workflow()