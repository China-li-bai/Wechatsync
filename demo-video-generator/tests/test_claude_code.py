#!/usr/bin/env python3
"""
测试优化版视频生成器
测试Claude Code文档演示视频生成
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from optimized_demo_video_generator import OptimizedDemoVideoGenerator


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎬 测试优化版视频生成器")
    print("="*70)
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
        print("\n🚀 开始生成视频...")
        print("="*70)
        
        generator = OptimizedDemoVideoGenerator(
            config_file=str(config_file),
            log_level='INFO'
        )
        
        output_file = generator.generate(auto_record=True)
        
        if output_file:
            print("\n" + "="*70)
            print("🎉 视频生成成功！")
            print("="*70)
            print(f"\n📁 输出文件: {output_file}")
            print(f"📊 文件大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
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
