#!/usr/bin/env python3
"""
测试智能视频生成器
测试页面分析和自动内容生成功能
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from smart_video_generator import SmartVideoGenerator


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎬 测试智能视频生成器 v3.0.0")
    print("="*70)
    print("\n新功能:")
    print("  ✨ 智能页面分析")
    print("  ✨ 自动生成介绍文案")
    print("  ✨ 智能场景规划")
    print("  ✨ 动态字幕生成")
    print("\n测试网站:")
    print("  1. https://code.claude.com/docs/zh-CN/overview")
    print("  2. https://code.claude.com/docs/zh-CN/best-practices")
    print("\n" + "="*70)
    
    config_file = Path(__file__).parent.parent / 'templates' / 'claude-code-test.yaml'
    
    if not config_file.exists():
        print(f"\n❌ 配置文件不存在: {config_file}")
        return 1
    
    print(f"\n✅ 配置文件: {config_file}")
    
    try:
        print("\n🚀 开始生成智能视频...")
        print("="*70)
        
        generator = SmartVideoGenerator(
            config_file=str(config_file),
            log_level='INFO'
        )
        
        output_file = generator.generate(auto_record=True)
        
        if output_file:
            print("\n" + "="*70)
            print("🎉 智能视频生成成功！")
            print("="*70)
            print(f"\n📁 输出文件: {output_file}")
            print(f"📊 文件大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
            
            # 检查页面分析结果
            analysis_file = output_file.parent / 'page_analysis.json'
            if analysis_file.exists():
                print(f"\n📄 页面分析结果: {analysis_file}")
                import json
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                
                print("\n页面分析摘要:")
                summary = analysis.get('summary', {})
                print(f"  - 标题: {summary.get('title', 'N/A')}")
                print(f"  - 主要主题: {', '.join(summary.get('main_topics', []))}")
                print(f"  - 关键功能: {len(summary.get('key_features', []))} 个")
                print(f"  - 亮点: {len(summary.get('highlights', []))} 个")
            
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
