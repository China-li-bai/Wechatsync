#!/usr/bin/env python3
"""
完整海报生成和设计规范检查脚本
生成所有风格、所有配色的海报，并检查是否符合设计规范
"""

import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_design_specs(output_path, config):
    """检查设计规范"""
    logger.info(f"\n{'='*70}")
    logger.info(f"📋 设计规范检查: {output_path.name}")
    logger.info(f"{'='*70}")
    
    checks = []
    
    # 1. 检查尺寸（竖屏）
    if config.get('height', 1920) == 1920 and config.get('width', 1080) == 1080:
        checks.append(("✅ 尺寸正确", "1080x1920 (竖屏 9:16)"))
    else:
        checks.append(("⚠️ 尺寸检查", f"{config.get('width', 1080)}x{config.get('height', 1920)}"))
    
    # 2. 检查配色方案
    color_scheme = config.get('color_scheme', 'shock_red')
    color_descriptions = {
        'shock_red': '震惊红 - 紧急、激情、高能量',
        'mystery_dark': '神秘深蓝 - 好奇、悬疑、高端',
        'urgency_orange': '紧迫橙红 - 紧急、行动、FOMO',
        'emotional_purple': '情绪紫 - 情感、故事、共鸣',
        'impact_black': '冲击黑金 - 极简、力量、权威',
        'success_green': '成功绿 - 成长、财富、积极',
        'energy_yellow': '能量黄 - 注意、警示、活力'
    }
    checks.append(("✅ 配色方案", color_descriptions.get(color_scheme, color_scheme)))
    
    # 3. 检查模板
    template = config.get('template', 'viral-vertical.html')
    template_descriptions = {
        'viral-vertical.html': '病毒式竖屏 - 高冲击感',
        'curiosity-vertical.html': '好奇式竖屏 - 悬疑感',
        'urgency-vertical.html': '紧急式竖屏 - 紧迫感',
        'emotional-vertical.html': '情感式竖屏 - 共鸣感'
    }
    checks.append(("✅ 模板类型", template_descriptions.get(template, template)))
    
    # 4. 检查字体大小
    base_font_size = config.get('font_size', 75)
    actual_font_size = base_font_size * 1.2
    ideal_min = 60
    ideal_max = 90
    if actual_font_size >= ideal_min and actual_font_size <= ideal_max:
        checks.append(("✅ 字体大小", f"{actual_font_size:.0f}px (理想范围)"))
    else:
        checks.append(("⚠️ 字体大小", f"{actual_font_size:.0f}px"))
    
    # 5. 检查是否有徽章
    if config.get('badge'):
        checks.append(("✅ 有徽章", config['badge']))
    else:
        checks.append(("ℹ️ 无徽章", "可选"))
    
    # 6. 检查是否有Emoji
    if config.get('emoji'):
        checks.append(("✅ 有Emoji", config['emoji']))
    else:
        checks.append(("ℹ️ 无Emoji", "可选"))
    
    # 7. 检查是否有副标题
    if config.get('subtitle'):
        checks.append(("✅ 有副标题", config['subtitle'][:30] + '...'))
    else:
        checks.append(("ℹ️ 无副标题", "可选"))
    
    # 打印检查结果
    for check_name, check_value in checks:
        logger.info(f"   {check_name}: {check_value}")
    
    logger.info(f"\n✅ 设计规范检查完成！")
    return checks


def generate_all_variants():
    """生成所有变体的海报"""
    generator = CodeBasedThumbnailGenerator()
    
    # 测试标题
    test_titles = [
        {
            'title': '独家内幕：顶级专家揭秘赚钱的终极秘密方法',
            'subtitle': '99%的人都不知道的真相',
            'emoji': '😱',
            'badge': '🔥 HOT'
        },
        {
            'title': '紧急通知：今天最后机会，错过不再有！',
            'subtitle': '倒计时开始，立即行动！',
            'emoji': '⚡',
            'badge': '⏰ URGENT'
        },
        {
            'title': '感动千万人的真实故事，看完泪目了',
            'subtitle': '一个普通人的逆袭之路',
            'emoji': '😭',
            'badge': '💎 STORY'
        },
        {
            'title': '从0到100万：他是如何做到的？',
            'subtitle': '揭秘成功背后的秘密',
            'emoji': '💰',
            'badge': '🏆 SUCCESS'
        }
    ]
    
    # 所有模板
    templates = [
        'viral-vertical.html',
        'curiosity-vertical.html',
        'urgency-vertical.html',
        'emotional-vertical.html'
    ]
    
    # 所有配色方案
    color_schemes = [
        'shock_red',
        'mystery_dark',
        'urgency_orange',
        'emotional_purple',
        'impact_black',
        'success_green',
        'energy_yellow'
    ]
    
    generated_files = []
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 开始生成所有海报变体")
    logger.info(f"{'='*70}")
    logger.info(f"   标题数: {len(test_titles)}")
    logger.info(f"   模板数: {len(templates)}")
    logger.info(f"   配色数: {len(color_schemes)}")
    logger.info(f"   预计生成: {len(test_titles) * len(templates) * len(color_schemes)} 个海报")
    
    count = 0
    
    for title_data in test_titles:
        for template in templates:
            for color_scheme in color_schemes:
                count += 1
                logger.info(f"\n--- [{count}] 生成中 ---")
                
                config = generator.generate_viral_optimized_config(
                    title=title_data['title'],
                    subtitle=title_data['subtitle'],
                    orientation='vertical'
                )
                
                config['template'] = template
                config['color_scheme'] = color_scheme
                config['emoji'] = title_data['emoji']
                config['badge'] = title_data['badge']
                
                try:
                    output_path = generator.generate(config=config)
                    logger.info(f"✅ 生成成功: {output_path.name}")
                    
                    # 检查设计规范
                    check_design_specs(output_path, config)
                    
                    generated_files.append({
                        'path': output_path,
                        'config': config.copy()
                    })
                    
                except Exception as e:
                    logger.error(f"❌ 生成失败: {e}")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"✅ 所有海报生成完成！")
    logger.info(f"{'='*70}")
    logger.info(f"   成功生成: {len(generated_files)} 个海报")
    
    return generated_files


def generate_quick_test():
    """快速测试：生成关键变体"""
    generator = CodeBasedThumbnailGenerator()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"⚡ 快速测试 - 生成关键变体")
    logger.info(f"{'='*70}")
    
    # 关键测试案例
    test_cases = [
        {
            'name': '病毒式 + 震惊红',
            'template': 'viral-vertical.html',
            'color_scheme': 'shock_red',
            'title': '独家内幕：顶级专家揭秘赚钱的终极秘密方法',
            'subtitle': '99%的人都不知道的真相',
            'emoji': '😱',
            'badge': '🔥 HOT'
        },
        {
            'name': '好奇式 + 神秘深蓝',
            'template': 'curiosity-vertical.html',
            'color_scheme': 'mystery_dark',
            'title': '隐藏的秘密：为什么99%的人都失败了？',
            'subtitle': '真相即将揭晓...',
            'emoji': '🤫',
            'badge': '🔍 SECRET'
        },
        {
            'name': '紧急式 + 紧迫橙红',
            'template': 'urgency-vertical.html',
            'color_scheme': 'urgency_orange',
            'title': '紧急通知：今天最后机会，错过不再有！',
            'subtitle': '倒计时开始，立即行动！',
            'emoji': '⚡',
            'badge': '⏰ URGENT'
        },
        {
            'name': '情感式 + 情绪紫',
            'template': 'emotional-vertical.html',
            'color_scheme': 'emotional_purple',
            'title': '感动千万人的真实故事，看完泪目了',
            'subtitle': '一个普通人的逆袭之路',
            'emoji': '😭',
            'badge': '💎 STORY'
        },
        {
            'name': '病毒式 + 成功绿',
            'template': 'viral-vertical.html',
            'color_scheme': 'success_green',
            'title': '从0到100万：他是如何做到的？',
            'subtitle': '揭秘成功背后的秘密',
            'emoji': '💰',
            'badge': '🏆 SUCCESS'
        },
        {
            'name': '好奇式 + 能量黄',
            'template': 'curiosity-vertical.html',
            'color_scheme': 'energy_yellow',
            'title': '注意！这个改变会影响你的一生',
            'subtitle': '现在知道还不算晚',
            'emoji': '⚠️',
            'badge': '⚡ ALERT'
        }
    ]
    
    generated_files = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n--- 测试 {i}/{len(test_cases)}: {test_case['name']} ---")
        
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
        
        try:
            output_path = generator.generate(config=config)
            logger.info(f"✅ 生成成功: {output_path.name}")
            
            # 检查设计规范
            check_design_specs(output_path, config)
            
            generated_files.append({
                'name': test_case['name'],
                'path': output_path,
                'config': config.copy()
            })
            
        except Exception as e:
            logger.error(f"❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"✅ 快速测试完成！")
    logger.info(f"{'='*70}")
    logger.info(f"   成功生成: {len(generated_files)} 个关键变体")
    
    return generated_files


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  🎨 完整海报生成和设计规范检查")
    print("="*70)
    
    print("\n请选择模式:")
    print("  1. 快速测试 - 生成6个关键变体（推荐）")
    print("  2. 完整测试 - 生成所有变体（可能需要较长时间）")
    
    try:
        choice = input("\n请输入选项 (1/2，默认1): ").strip()
        
        if choice == '2':
            generate_all_variants()
        else:
            generate_quick_test()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()