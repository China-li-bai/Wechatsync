#!/usr/bin/env python3
"""
优化版本海报测试脚本
对比原始版本和优化版本的视觉效果
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.thumbnail_generator import CodeBasedThumbnailGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_optimized_templates():
    """测试优化后的模板"""
    generator = CodeBasedThumbnailGenerator()
    
    test_cases = [
        {
            'name': 'V2-病毒式 + 震惊红',
            'template': 'viral-vertical-v2.html',
            'color_scheme': 'shock_red',
            'title': '独家内幕：顶级专家揭秘赚钱的终极秘密方法',
            'subtitle': '99%的人都不知道的真相',
            'emoji': '😱',
            'badge': '🔥 HOT'
        },
        {
            'name': 'V2-好奇式 + 神秘深蓝',
            'template': 'curiosity-vertical-v2.html',
            'color_scheme': 'mystery_dark',
            'title': '隐藏的秘密：为什么99%的人都失败了？',
            'subtitle': '真相即将揭晓...',
            'emoji': '🤫',
            'badge': '🔍 SECRET'
        },
        {
            'name': 'V2-紧急式 + 紧迫橙红',
            'template': 'urgency-vertical-v2.html',
            'color_scheme': 'urgency_orange',
            'title': '紧急通知：今天最后机会，错过不再有！',
            'subtitle': '倒计时开始，立即行动！',
            'emoji': '⚡',
            'badge': '⏰ URGENT'
        },
        {
            'name': 'V2-情感式 + 情绪紫',
            'template': 'emotional-vertical-v2.html',
            'color_scheme': 'emotional_purple',
            'title': '感动千万人的真实故事，看完泪目了',
            'subtitle': '一个普通人的逆袭之路',
            'emoji': '😭',
            'badge': '💎 STORY'
        }
    ]
    
    generated_files = []
    
    logger.info(f"\n{'='*70}")
    logger.info(f"✨ 优化版本海报测试")
    logger.info(f"{'='*70}")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n--- 测试 {i}/{len(test_cases)}: {test_case['name']} ---")
        
        try:
            config = generator.generate_viral_optimized_config(
                title=test_case['title'],
                subtitle=test_case['subtitle'],
                orientation='vertical'
            )
            
            config['template'] = test_case['template']
            config['color_scheme'] = test_case['color_scheme']
            config['emoji'] = test_case['emoji']
            config['badge'] = test_case['badge']
            config['font_size'] = 65
            
            output_path = generator.generate(config=config)
            logger.info(f"✅ 生成成功: {output_path.name}")
            
            generated_files.append({
                'name': test_case['name'],
                'path': output_path,
                'config': config.copy()
            })
            
        except Exception as e:
            logger.error(f"❌ 生成失败: {e}")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"✅ 优化版本测试完成！")
    logger.info(f"{'='*70}")
    logger.info(f"   成功生成: {len(generated_files)} 个优化版海报")
    
    return generated_files


if __name__ == '__main__':
    test_optimized_templates()