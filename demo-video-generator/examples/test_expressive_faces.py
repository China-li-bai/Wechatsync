#!/usr/bin/env python3
"""
CSS夸张表情海报测试脚本
验证CSS绘制的夸张表情效果
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.thumbnail_generator import CodeBasedThumbnailGenerator
from lib.thumbnail_auditor import audit_thumbnail
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_expressive_faces():
    """测试CSS夸张表情海报"""
    generator = CodeBasedThumbnailGenerator()
    
    test_cases = [
        {
            'name': 'CSS夸张表情 - 震惊风格',
            'template': 'viral-expressive-v4.html',
            'color_scheme': 'shock_red',
            'title': '我花了$1000000',
            'subtitle': '结果让所有人震惊',
            'badge': '🔥 VIRAL',
            'cta_text': 'WATCH NOW',
            'font_size': 95
        },
        {
            'name': 'CSS夸张表情 - 极限挑战',
            'template': 'viral-expressive-v4.html',
            'color_scheme': 'shock_red',
            'title': ' impossible Challenge',
            'subtitle': '99%的人无法完成',
            'badge': '⚡ INSANE',
            'cta_text': 'CLICK HERE',
            'font_size': 90
        }
    ]
    
    generated_files = []
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎨 CSS夸张表情海报测试")
    logger.info(f"{'='*70}")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"📝 测试 {i}/{len(test_cases)}: {test_case['name']}")
        logger.info(f"{'='*70}")
        
        try:
            config = {
                "template": test_case['template'],
                "title": test_case['title'],
                "subtitle": test_case['subtitle'],
                "color_scheme": test_case['color_scheme'],
                "font_size": test_case['font_size'],
                "badge": test_case['badge'],
                "cta_text": test_case['cta_text'],
                "width": 1080,
                "height": 1920
            }
            
            # 生成海报
            output_path = generator.generate(config=config)
            logger.info(f"✅ 海报生成成功: {output_path.name}")
            
            # 运行审查
            report = audit_thumbnail(config)
            logger.info(f"\n📊 设计审查结果:")
            logger.info(f"   综合评分: {report.overall_score}/100")
            logger.info(f"   审查状态: {'✅ 通过' if report.passed else '⚠️ 需改进'}")
            
            if report.recommendations:
                logger.info(f"\n💡 优化建议:")
                for rec in report.recommendations:
                    logger.info(f"   - {rec}")
            
            generated_files.append({
                'name': test_case['name'],
                'path': output_path,
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
    
    if generated_files:
        avg_score = sum(f['audit_score'] for f in generated_files) / len(generated_files)
        passed_count = sum(1 for f in generated_files if f['passed'])
        
        logger.info(f"\n✅ 成功生成: {len(generated_files)} 个海报")
        logger.info(f"✅ 审查通过: {passed_count}/{len(generated_files)}")
        logger.info(f"📊 平均评分: {avg_score:.1f}/100")
        
        logger.info(f"\n📁 生成的文件:")
        for f in generated_files:
            status = "✅" if f['passed'] else "⚠️"
            logger.info(f"   {status} {f['name']}: {f['path'].name} (评分: {f['audit_score']})")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎉 CSS夸张表情测试完成！")
    logger.info(f"{'='*70}")
    
    return generated_files


if __name__ == '__main__':
    test_expressive_faces()
