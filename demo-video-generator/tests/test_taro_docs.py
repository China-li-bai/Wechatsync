#!/usr/bin/env python3
"""
生成 Taro 文档 智能视频 - 使用专业文案引擎 v3.1.0
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from smart_video_generator import SmartVideoGenerator


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎬 Taro 文档 智能视频生成")
    print("="*70)
    
    print("\n📌 目标网站: https://docs.taro.zone/docs/")
    print("\n✨ 使用专业文案引擎:")
    print("  • AIDA营销框架 (Attention-Interest-Desire-Action)")
    print("  • 5种专业钩子类型")
    print("  • 深度页面语义分析")
    print("  • 痛点识别与价值主张提取")
    
    config_file = Path(__file__).parent.parent / 'templates' / 'taro-docs.yaml'
    
    if not config_file.exists():
        print(f"\n❌ 配置文件不存在: {config_file}")
        return 1
    
    print(f"\n✅ 配置文件: {config_file}")
    print("\n" + "="*70)
    
    try:
        print("\n🚀 开始生成专业文案视频...")
        print("="*70)
        
        generator = SmartVideoGenerator(
            config_file=str(config_file),
            log_level='INFO'
        )
        
        output_file = generator.generate(auto_record=True)
        
        if output_file:
            print("\n" + "="*70)
            print("🎉 Taro 文档视频生成成功！")
            print("="*70)
            print(f"\n📁 输出文件: {output_file}")
            print(f"📊 文件大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
            
            # 显示文案分析结果
            copywriting_file = output_file.parent / 'copywriting_analysis.json'
            if copywriting_file.exists():
                print(f"\n{'='*70}")
                print("📝 专业文案分析结果 (AIDA框架)")
                print("="*70)
                
                import json
                with open(copywriting_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                
                insight = analysis.get('insight', {})
                copy = analysis.get('copy', {})
                
                print("\n【🔍 页面深度洞察】")
                if insight.get('value_proposition'):
                    print(f"  💡 价值主张: {insight['value_proposition']}")
                
                if insight.get('pain_points'):
                    print(f"\n  🎯 识别到的用户痛点 ({len(insight['pain_points'])}个):")
                    for i, pain in enumerate(insight['pain_points'], 1):
                        print(f"     {i}. {pain}")
                
                if insight.get('target_audience'):
                    print(f"\n  👥 目标用户画像: {insight['target_audience']}")
                
                if insight.get('key_benefits'):
                    print(f"\n  ✨ 核心用户利益 ({len(insight['key_benefits'])}个):")
                    for benefit in insight['key_benefits'][:5]:
                        print(f"     • {benefit}")
                
                if insight.get('social_proof'):
                    print(f"\n  📊 社会证明: {insight['social_proof'][0]}")
                
                print("\n【🎬 AIDA文案结构】")
                print(f"\n  🔥 Attention (开场钩子):")
                print(f"     >>> {copy.get('hook', 'N/A')}")
                
                print(f"\n  💭 Interest (引发兴趣):")
                interest = copy.get('interest', 'N/A')
                if len(interest) > 150:
                    print(f"     >>> {interest[:150]}...")
                else:
                    print(f"     >>> {interest}")
                
                print(f"\n  ❤️  Desire (刺激欲望):")
                desire = copy.get('solution', 'N/A')
                if len(desire) > 200:
                    print(f"     >>> {desire[:200]}...")
                else:
                    print(f"     >>> {desire}")
                
                print(f"\n  🚀 Action (行动号召):")
                print(f"     >>> {copy.get('cta', 'N/A')}")
            
            # 显示字幕
            subtitle_file = output_file.parent / 'subtitles.srt'
            if subtitle_file.exists():
                print(f"\n{'='*70}")
                print("📝 生成的字幕内容")
                print("="*70)
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            
            return 0
        else:
            print("\n" + "="*70)
            print("❌ 视频生成失败")
            print("="*70)
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        return 1
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
