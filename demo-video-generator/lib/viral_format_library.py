#!/usr/bin/env python3
"""
病毒式格式库 - 基于文章中的洞见
记录成功和失败的封面模板，支持格式组合和快速迭代
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ViralFormat:
    """病毒式传播格式"""
    id: str
    name: str
    description: str
    category: str  # curiosity, urgency, emotional, social, etc.
    year: Optional[int] = None
    source_platform: Optional[str] = None  # tiktok, youtube, etc.
    success_rate: float = 0.0
    views_average: int = 0
    views_max: int = 0
    template_name: Optional[str] = None
    color_scheme: Optional[str] = None
    key_elements: List[str] = None
    variations: List[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.key_elements is None:
            self.key_elements = []
        if self.variations is None:
            self.variations = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


@dataclass
class FormatCombination:
    """格式组合（当前格式 + 历史格式）"""
    id: str
    name: str
    primary_format_id: str
    secondary_format_ids: List[str]
    description: str
    success_rate: float = 0.0
    views_average: int = 0
    views_max: int = 0
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ABTestResult:
    """A/B测试结果"""
    test_id: str
    title: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    winner: Optional[str] = None  # 'A' or 'B' or None
    views_a: int = 0
    views_b: int = 0
    ctr_a: float = 0.0
    ctr_b: float = 0.0
    notes: Optional[str] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class ViralFormatLibrary:
    """病毒式格式库"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path('viral_format_library.json')
        self.formats: Dict[str, ViralFormat] = {}
        self.combinations: Dict[str, FormatCombination] = {}
        self.ab_tests: Dict[str, ABTestResult] = {}
        self._load()

    def _load(self):
        """从文件加载库"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.formats = {k: ViralFormat(**v) for k, v in data.get('formats', {}).items()}
                    self.combinations = {k: FormatCombination(**v) for k, v in data.get('combinations', {}).items()}
                    self.ab_tests = {k: ABTestResult(**v) for k, v in data.get('ab_tests', {}).items()}
                logger.info(f"已加载 {len(self.formats)} 个病毒式格式")
            except Exception as e:
                logger.error(f"加载库失败: {e}")

    def _save(self):
        """保存库到文件"""
        data = {
            'formats': {k: asdict(v) for k, v in self.formats.items()},
            'combinations': {k: asdict(v) for k, v in self.combinations.items()},
            'ab_tests': {k: asdict(v) for k, v in self.ab_tests.items()}
        }
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存库到 {self.storage_path}")

    def add_format(self, viral_format: ViralFormat) -> str:
        """添加病毒式格式"""
        self.formats[viral_format.id] = viral_format
        self._save()
        logger.info(f"已添加格式: {viral_format.name}")
        return viral_format.id

    def get_format(self, format_id: str) -> Optional[ViralFormat]:
        """获取格式"""
        return self.formats.get(format_id)

    def get_formats_by_category(self, category: str) -> List[ViralFormat]:
        """按类别获取格式"""
        return [f for f in self.formats.values() if f.category == category]

    def get_top_formats(self, limit: int = 10) -> List[ViralFormat]:
        """获取成功率最高的格式"""
        return sorted(
            self.formats.values(),
            key=lambda x: x.success_rate,
            reverse=True
        )[:limit]

    def create_combination(self, primary_id: str, secondary_ids: List[str], name: str, description: str) -> str:
        """创建格式组合（当前格式 + 历史格式）"""
        combo_id = f"combo_{int(datetime.now().timestamp())}"
        combo = FormatCombination(
            id=combo_id,
            name=name,
            primary_format_id=primary_id,
            secondary_format_ids=secondary_ids,
            description=description
        )
        self.combinations[combo_id] = combo
        self._save()
        logger.info(f"已创建格式组合: {name}")
        return combo_id

    def suggest_combination(self, target_category: str) -> Optional[FormatCombination]:
        """建议格式组合（基于文章中的洞见）"""
        # 寻找同一类别中成功率最高的格式
        category_formats = self.get_formats_by_category(target_category)
        if not category_formats:
            return None

        primary = max(category_formats, key=lambda x: x.success_rate)

        # 寻找历史成功格式（不同年份或不同类别的）
        historical = [
            f for f in self.formats.values()
            if f.id != primary.id and f.success_rate > 0.5
        ][:2]

        if not historical:
            return None

        combo_id = self.create_combination(
            primary_id=primary.id,
            secondary_ids=[h.id for h in historical],
            name=f"{primary.name} + 历史格式组合",
            description=f"基于{primary.name}的核心设计，融合{len(historical)}个历史成功格式的元素"
        )
        return self.combinations.get(combo_id)

    def record_ab_test(self, test_result: ABTestResult) -> str:
        """记录A/B测试结果"""
        self.ab_tests[test_result.test_id] = test_result
        self._save()
        logger.info(f"已记录A/B测试: {test_result.title}")
        return test_result.test_id

    def get_ab_test_insights(self) -> List[Dict[str, Any]]:
        """获取A/B测试洞察"""
        insights = []
        for test in self.ab_tests.values():
            if test.winner:
                insights.append({
                    'test_title': test.title,
                    'winner': test.winner,
                    'views_diff': test.views_b - test.views_a if test.winner == 'B' else test.views_a - test.views_b,
                    'ctr_diff': test.ctr_b - test.ctr_a if test.winner == 'B' else test.ctr_a - test.ctr_b,
                    'notes': test.notes
                })
        return insights


def initialize_sample_library():
    """初始化示例病毒式格式库（基于文章中的洞见）"""
    library = ViralFormatLibrary()

    # Spotify Wrapped 风格 - 蒙面遮掩数据
    spotify_2024 = ViralFormat(
        id="spotify_wrapped_2024",
        name="Spotify Wrapped 2024 - 蒙面遮掩",
        description="双手被遮盖，遮住数据，暗示即将到来的震惊数据",
        category="curiosity",
        year=2024,
        source_platform="tiktok",
        success_rate=0.85,
        views_average=500000,
        views_max=15000000,
        key_elements=[
            "蒙面遮掩元素",
            "暗示震惊数据",
            "渐变背景",
            "金色强调色"
        ],
        template_name="curiosity-vertical.html",
        color_scheme="mystery_dark"
    )
    library.add_format(spotify_2024)

    # Cutouts应用 - 品牌关联
    cutouts_2022 = ViralFormat(
        id="cutouts_2022",
        name="Cutouts 2022 - 品牌关联",
        description="将产品与值得信赖的品牌联系起来",
        category="social",
        year=2022,
        source_platform="tiktok",
        success_rate=0.78,
        views_average=300000,
        views_max=8000000,
        key_elements=[
            "品牌Logo展示",
            "可信度背书",
            "前后对比"
        ],
        template_name="viral-vertical.html",
        color_scheme="success_green"
    )
    library.add_format(cutouts_2022)

    # 2025 Wrapped - 组合格式
    wrapped_2025 = ViralFormat(
        id="wrapped_2025",
        name="2025 Wrapped - 组合格式",
        description="蒙面遮掩数据 + 品牌关联的组合格式",
        category="curiosity",
        year=2025,
        source_platform="tiktok",
        success_rate=0.92,
        views_average=1200000,
        views_max=36000000,
        key_elements=[
            "蒙面遮掩iMessage截图",
            "暗示iMessage被包裹",
            "渐变背景",
            "动态元素"
        ],
        template_name="viral-vertical.html",
        color_scheme="shock_red",
        variations=["spotify_wrapped_2024", "cutouts_2022"]
    )
    library.add_format(wrapped_2025)

    # 紧急通知风格
    urgency_style = ViralFormat(
        id="urgency_notification",
        name="紧急通知 - FOMO",
        description="限时、倒计时、紧迫感触发",
        category="urgency",
        year=2025,
        source_platform="tiktok",
        success_rate=0.68,
        views_average=200000,
        views_max=5000000,
        key_elements=[
            "倒计时显示",
            "紧急通知徽章",
            "红色/橙色渐变",
            "行动按钮"
        ],
        template_name="urgency-vertical.html",
        color_scheme="urgency_orange"
    )
    library.add_format(urgency_style)

    # 情感故事风格
    emotional_story = ViralFormat(
        id="emotional_story",
        name="情感故事 - 共鸣",
        description="真实故事、情感触发、共鸣",
        category="emotional",
        year=2025,
        source_platform="tiktok",
        success_rate=0.75,
        views_average=400000,
        views_max=16000000,
        key_elements=[
            "真实故事标签",
            "情感Emoji",
            "温馨配色",
            "副标题故事"
        ],
        template_name="emotional-vertical.html",
        color_scheme="emotional_purple"
    )
    library.add_format(emotional_story)

    logger.info("✅ 示例病毒式格式库初始化完成！")
    return library


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("="*70)
    print("  🧬 病毒式格式库初始化")
    print("="*70)

    library = initialize_sample_library()

    print("\n📊 库统计:")
    print(f"   • 病毒式格式: {len(library.formats)}")
    print(f"   • 格式组合: {len(library.combinations)}")
    print(f"   • A/B测试: {len(library.ab_tests)}")

    print("\n🏆 成功率最高的格式:")
    top_formats = library.get_top_formats(3)
    for i, fmt in enumerate(top_formats, 1):
        print(f"   {i}. {fmt.name}")
        print(f"      成功率: {fmt.success_rate*100:.0f}%")
        print(f"      平均观看: {fmt.views_average:,}")
        print(f"      最高观看: {fmt.views_max:,}")

    print("\n🔗 建议格式组合:")
    combo = library.suggest_combination("curiosity")
    if combo:
        print(f"   • {combo.name}")
        print(f"   • {combo.description}")

    print("\n" + "="*70)
    print("  ✅ 初始化完成！")
    print("="*70)