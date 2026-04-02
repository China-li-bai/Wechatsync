#!/usr/bin/env python3
"""
测试所有生成的表情模板
验证24个表情的效果
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.thumbnail_generator import CodeBasedThumbnailGenerator
from lib.thumbnail_auditor import audit_thumbnail
from lib.emotion_template_generator import EmotionTemplateGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_all_emotions():
    """测试所有表情模板"""
    generator = CodeBasedThumbnailGenerator()
    emotion_gen = EmotionTemplateGenerator()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎭 表情模板全面测试")
    logger.info(f"{'='*70}")
    logger.info(f"\n共 {len(emotion_gen.emotions)} 个表情模板")
    logger.info(f"{'='*70}")
    
    results = []
    
    for emotion_id, config in emotion_gen.emotions.items():
        logger.info(f"\n{'='*70}")
        logger.info(f"🎨 测试表情: {config.emoji} {config.name} ({config.name_en})")
        logger.info(f"{'='*70}")
        logger.info(f"   描述: {config.description}")
        logger.info(f"   特征: 眉毛{config.eyebrow_angle}°, {config.eye_shape}眼, {config.mouth_shape}嘴")
        logger.info(f"   特效: 泪珠={'是' if config.has_tears else '否'}, 腮红={'是' if config.has_blush else '否'}, 汗珠={'是' if config.has_sweat else '否'}, 青筋={'是' if config.has_veins else '否'}")
        
        try:
            # 读取表情模板
            template_path = f"templates/thumbnails/emotions/emotion-{emotion_id}.html"
            
            # 生成海报配置
            test_config = {
                "template": template_path,
                "title": config.name,
                "subtitle": config.name_en,
                "width": 1080,
                "height": 1920
            }
            
            # 生成海报
            output_path = generator.generate(config=test_config)
            logger.info(f"✅ 海报生成成功: {output_path.name}")
            
            # 运行审查
            report = audit_thumbnail(test_config)
            logger.info(f"📊 审查评分: {report.overall_score}/100")
            
            results.append({
                'emotion_id': emotion_id,
                'name': config.name,
                'emoji': config.emoji,
                'score': report.overall_score,
                'passed': report.passed,
                'path': output_path
            })
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            results.append({
                'emotion_id': emotion_id,
                'name': config.name,
                'emoji': config.emoji,
                'score': 0,
                'passed': False,
                'error': str(e)
            })
    
    # 汇总报告
    logger.info(f"\n{'='*70}")
    logger.info(f"📈 表情模板测试汇总报告")
    logger.info(f"{'='*70}")
    
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    avg_score = sum(r['score'] for r in results) / total if total > 0 else 0
    
    logger.info(f"\n✅ 测试完成: {total} 个表情")
    logger.info(f"✅ 通过审查: {passed}/{total}")
    logger.info(f"📊 平均评分: {avg_score:.1f}/100")
    
    # 分类统计
    categories = {
        '基础情绪': ['happy', 'sad', 'angry', 'surprised', 'fear', 'disgust'],
        '复杂情绪': ['anxious', 'confused', 'embarrassed', 'disappointed', 'tired', 'excited', 'suspicious', 'proud', 'shy', 'pain'],
        '极端情绪': ['crazy', 'desperate', 'ecstatic', 'terrified', 'furious'],
        '特殊风格': ['pixel', 'comic', 'minimal']
    }
    
    logger.info(f"\n📊 分类统计:")
    for category, emotion_ids in categories.items():
        category_results = [r for r in results if r['emotion_id'] in emotion_ids]
        category_passed = sum(1 for r in category_results if r.get('passed', False))
        category_avg = sum(r['score'] for r in category_results) / len(category_results) if category_results else 0
        logger.info(f"   {category}: {category_passed}/{len(category_results)} 通过, 平均 {category_avg:.1f}分")
    
    # 高分表情
    top_emotions = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    logger.info(f"\n🏆 评分最高的5个表情:")
    for i, r in enumerate(top_emotions, 1):
        logger.info(f"   {i}. {r['emoji']} {r['name']}: {r['score']}分")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎉 所有表情模板测试完成!")
    logger.info(f"{'='*70}")
    logger.info(f"\n📁 文件位置:")
    logger.info(f"   表情模板: templates/thumbnails/emotions/")
    logger.info(f"   预览页面: templates/thumbnails/emotions/index.html")
    logger.info(f"   生成海报: output/thumbnails/")
    
    return results


if __name__ == '__main__':
    test_all_emotions()
