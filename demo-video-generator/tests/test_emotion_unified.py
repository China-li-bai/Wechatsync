#!/usr/bin/env python3
"""
测试统一表情模板系统
验证映射方式是否正常工作
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.thumbnail_generator import CodeBasedThumbnailGenerator
from lib.emotion_manager import EmotionManager


def test_emotion_manager():
    """测试表情管理器"""
    print("="*70)
    print("🎭 测试表情管理器")
    print("="*70)
    
    manager = EmotionManager()
    
    print("\n📊 统计信息:")
    stats = manager.get_stats()
    print(f"  总表情数: {stats['total_emotions']}")
    print(f"  总分类数: {stats['total_categories']}")
    
    print("\n📋 表情列表:")
    print(manager.list_emotions())


def test_unified_template():
    """测试统一模板生成"""
    print("\n" + "="*70)
    print("🧪 测试统一模板生成")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    manager = EmotionManager()
    
    test_emotions = ['happy', 'sad', 'angry', 'surprised', 'excited', 'crazy']
    
    output_dir = Path("output/emotion-test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, emotion_id in enumerate(test_emotions):
        print(f"\n[{i+1}/{len(test_emotions)}] 生成 '{emotion_id}' 表情...")
        
        config = manager.get_template_config(
            emotion_id,
            title=f"测试 - {emotion_id}",
            width=1080,
            height=1920
        )
        
        try:
            output_path = generator.generate(config=config)
            
            if output_path and output_path.exists():
                print(f"  ✅ 成功: {output_path}")
            else:
                print(f"  ❌ 失败: 文件不存在")
                
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_all_emotions():
    """测试所有表情"""
    print("\n" + "="*70)
    print("🎯 测试所有24个表情")
    print("="*70)
    
    generator = CodeBasedThumbnailGenerator()
    manager = EmotionManager()
    
    emotions = manager.get_all_emotions()
    total = len(emotions)
    
    success_count = 0
    failed_emotions = []
    
    for i, (emotion_id, emotion) in enumerate(emotions.items()):
        print(f"\n[{i+1}/{total}] {emotion.emoji} {emotion.name} ({emotion_id})...")
        
        config = manager.get_template_config(
            emotion_id,
            title=emotion.name,
            width=1080,
            height=1920
        )
        
        try:
            output_path = generator.generate(config=config)
            
            if output_path and output_path.exists():
                success_count += 1
                print(f"  ✅ 成功")
            else:
                failed_emotions.append(emotion_id)
                print(f"  ❌ 失败")
                
        except Exception as e:
            failed_emotions.append(f"{emotion_id}: {str(e)}")
            print(f"  ❌ 异常: {str(e)}")
    
    print("\n" + "="*70)
    print("📊 测试结果:")
    print(f"  ✅ 成功: {success_count}/{total}")
    print(f"  ❌ 失败: {len(failed_emotions)}/{total}")
    
    if failed_emotions:
        print("\n⚠️  失败的表情:")
        for emotion in failed_emotions:
            print(f"  - {emotion}")


def test_recommendation():
    """测试表情推荐"""
    print("\n" + "="*70)
    print("🎯 测试表情推荐")
    print("="*70)
    
    manager = EmotionManager()
    
    content_types = ['funny', 'failure', 'challenge', 'mystery', 'inspirational']
    
    for content_type in content_types:
        print(f"\n📝 内容类型: {content_type}")
        emotions = manager.recommend_emotions(content_type)
        
        if emotions:
            for emotion in emotions:
                print(f"  {emotion.emoji} {emotion.name}")
        else:
            print("  (无推荐)")


if __name__ == '__main__':
    test_emotion_manager()
    test_unified_template()
    test_all_emotions()
    test_recommendation()
    
    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)
