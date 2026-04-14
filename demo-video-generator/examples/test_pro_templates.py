#!/usr/bin/env python3
"""
Pro版本海报测试脚本
基于2025年热门视频封面设计最佳实践
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.thumbnail_generator import CodeBasedThumbnailGenerator
from lib.thumbnail_auditor import ThumbnailAuditor, audit_thumbnail
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pro_templates():
    """测试Pro版本模板"""
    generator = CodeBasedThumbnailGenerator()
    auditor = ThumbnailAuditor()
    
    # 基于真实爆款案例的测试用例
    test_cases = [
        {
            'name': '病毒式震惊 - MrBeast风格',
            'template': 'viral-pro-v3.html',
            'color_scheme': 'shock_red',
            'title': '我花了$1000000做这件事',
            'subtitle': '结果让所有人震惊',
            'emoji': '😱',
            'badge': '🔥 HOT',
            'cta_text': 'CLICK NOW',
            'font_size': 85
        },
        {
            'name': '好奇揭秘 - 神秘风格',
            'template': 'curiosity-pro-v3.html',
            'color_scheme': 'curiosity_blue',
            'title': '99%的人都不知道的秘密',
            'subtitle': '专家隐瞒了20年的真相',
            'emoji': '🤫',
            'badge': '🔍 SECRET',
            'suspense_text': 'REVEALED',
            'font_size': 78
        },
        {
            'name': '清单式 - 数字吸引',
            'template': 'listicle-pro-v3.html',
            'color_scheme': 'listicle_purple',
            'title': '改变人生的5个习惯',
            'subtitle': '成功人士都在用',
            'list_number': '5',
            'item_1': '早起冥想',
            'item_2': '阅读学习',
            'item_3': '运动健身',
            'cta_text': 'Watch Now',
            'font_size': 80
        }
    ]
    
    generated_files = []
    audit_reports = []
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎨 Pro版本海报测试 - 基于2025年爆款设计原则")
    logger.info(f"{'='*70}")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"📝 测试 {i}/{len(test_cases)}: {test_case['name']}")
        logger.info(f"{'='*70}")
        
        try:
            # 生成基础配置
            config = generator.generate_viral_optimized_config(
                title=test_case['title'],
                subtitle=test_case.get('subtitle', ''),
                orientation='vertical'
            )
            
            # 应用测试配置
            config['template'] = test_case['template']
            config['color_scheme'] = test_case['color_scheme']
            config['font_size'] = test_case.get('font_size', 80)
            
            if 'emoji' in test_case:
                config['emoji'] = test_case['emoji']
            if 'badge' in test_case:
                config['badge'] = test_case['badge']
            if 'cta_text' in test_case:
                config['cta_text'] = test_case['cta_text']
            if 'suspense_text' in test_case:
                config['suspense_text'] = test_case['suspense_text']
            if 'list_number' in test_case:
                config['list_number'] = test_case['list_number']
            if 'item_1' in test_case:
                config['item_1'] = test_case['item_1']
                config['item_2'] = test_case['item_2']
                config['item_3'] = test_case['item_3']
            
            # 生成海报
            output_path = generator.generate(config=config)
            logger.info(f"✅ 海报生成成功: {output_path.name}")
            
            # 运行审查
            report = audit_thumbnail(config)
            audit_reports.append(report)
            
            # 打印审查报告
            logger.info(f"\n📊 设计审查结果:")
            logger.info(f"   综合评分: {report.overall_score}/100")
            logger.info(f"   审查状态: {'✅ 通过' if report.passed else '❌ 需改进'}")
            
            if report.recommendations:
                logger.info(f"\n💡 优化建议:")
                for rec in report.recommendations:
                    logger.info(f"   - {rec}")
            
            generated_files.append({
                'name': test_case['name'],
                'path': output_path,
                'config': config.copy(),
                'audit_score': report.overall_score,
                'passed': report.passed
            })
            
        except Exception as e:
            logger.error(f"❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 汇总报告
    logger.info(f"\n{'='*70}")
    logger.info(f"📈 测试汇总报告")
    logger.info(f"{'='*70}")
    
    total_tests = len(test_cases)
    passed_tests = sum(1 for f in generated_files if f['passed'])
    avg_score = sum(f['audit_score'] for f in generated_files) / len(generated_files) if generated_files else 0
    
    logger.info(f"\n✅ 成功生成: {len(generated_files)}/{total_tests} 个海报")
    logger.info(f"✅ 审查通过: {passed_tests}/{len(generated_files)} 个")
    logger.info(f"📊 平均评分: {avg_score:.1f}/100")
    
    logger.info(f"\n📁 生成的文件:")
    for f in generated_files:
        status = "✅" if f['passed'] else "⚠️"
        logger.info(f"   {status} {f['name']}: {f['path'].name} (评分: {f['audit_score']})")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎉 Pro版本测试完成！")
    logger.info(f"{'='*70}")
    
    return generated_files, audit_reports


if __name__ == '__main__':
    test_pro_templates()
