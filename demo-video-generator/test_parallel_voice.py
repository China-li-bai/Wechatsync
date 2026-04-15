#!/usr/bin/env python3
"""
并行语音生成器测试脚本
验证功能正确性和性能提升

用法:
    python test_parallel_voice.py
"""

import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from parallel_voice_generator import ParallelVoiceGenerator, ProgressInfo


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('TestParallelVoice')


def create_test_scenes(count: int = 5) -> list:
    """创建测试场景数据"""
    scenes = []
    
    sample_texts = [
        "你有没有想过，让产品自己介绍自己？我们的产品让这个想法变成现实。",
        "传统方案太复杂！我们的产品只需简单配置，五分钟搞定。",
        "想象一下：用户只需点击按钮，功能自动执行。不需要复杂操作。",
        "提升效率、节省时间、降低成本。让你的工作更轻松，让用户更满意。",
        "现在就试试，体验产品的魅力！开源免费，快速上手。",
        "这是一个关于技术创新的故事，让我们一起探索未来的可能性。",
        "在这个快速变化的时代，我们需要更智能的解决方案来应对挑战。",
        "每一个细节都经过精心设计，只为给你最好的使用体验。",
        "从今天开始，让你的工作效率提升到一个全新的高度。",
        "这不仅仅是一个工具，更是你实现梦想的得力助手。"
    ]
    
    for i in range(min(count, len(sample_texts))):
        scenes.append({
            'name': f'test_scene_{i+1}',
            'text': sample_texts[i],
            'subtitle': f'测试字幕 {i+1}'
        })
    
    return scenes


def test_parallel_generation():
    """测试并行生成功能"""
    logger = setup_logging()
    
    print("\n" + "="*70)
    print("🧪 并行语音生成器 - 功能与性能测试")
    print("="*70 + "\n")
    
    scenes = create_test_scenes(5)
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    
    voice_config = {
        'language': 'zh-CN',
        'voice_name': 'XiaoxiaoNeural',
        'speed': 1.0
    }
    
    progress_info = []
    
    def on_progress(completed, total, task_name, pct):
        progress_info.append({
            'completed': completed,
            'total': total,
            'task': task_name,
            'pct': pct
        })
        print(f"  📊 进度: {completed}/{total} ({pct:.0f}%) - {task_name}")
    
    generator = ParallelVoiceGenerator(
        logger=logger,
        max_workers=3,
        max_retries=2,
        enable_progress=True,
        progress_callback=on_progress
    )
    
    print(f"\n📋 测试配置:")
    print(f"   场景数量: {len(scenes)}")
    print(f"   并发线程: {generator.max_workers}")
    print(f"   最大重试: {generator.max_retries}")
    print(f"   输出目录: {output_dir}")
    print()
    
    start_time = time.time()
    
    try:
        result = generator.generate(
            scenes=scenes,
            voice_config=voice_config,
            output_dir=output_dir
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"✅ 测试完成!")
        print(f"{'='*70}")
        print(f"\n📊 结果统计:")
        print(f"   总耗时: {elapsed:.2f}秒")
        print(f"   成功数: {result.tasks_succeeded}/{result.tasks_total}")
        print(f"   生成文件: {len(result.voice_files)}个")
        
        if result.speedup_ratio:
            print(f"   加速比: {result.speedup_ratio:.2f}x")
        
        if result.durations:
            total_audio = sum(result.durations)
            print(f"   音频总长: {total_audio:.2f}秒")
        
        if result.tasks_failed:
            print(f"\n⚠️  失败任务:")
            for fail in result.tasks_failed:
                print(f"      ❌ [{fail['index']}] {fail['name']}: {fail['error']}")
        
        print(f"\n📁 生成的文件:")
        for i, vf in enumerate(result.voice_files):
            duration = result.durations[i] if i < len(result.durations) else 0
            status = "✅" if vf.exists() else "❌"
            print(f"   {status} {vf.name} ({duration:.2f}s)")
        
        print(f"\n📈 进度回调记录: {len(progress_info)}次")
        
        assert result.success or len(result.tasks_failed) < len(scenes), \
            "不应该全部失败"
        assert len(result.voice_files) == result.tasks_succeeded, \
            "文件数量应该等于成功数"
        
        print(f"\n🎉 所有断言通过! 并行语音生成功能正常工作。\n")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ 测试跳过: {e}")
        print("   提示: 请先安装 edge-tts (pipx install edge-tts)\n")
        return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)


def test_concurrency_comparison():
    """并发数性能对比测试"""
    logger = setup_logging()
    
    print("\n" + "="*70)
    print("🔬 并发数性能对比测试")
    print("="*70 + "\n")
    
    scenes = create_test_scenes(5)
    output_dir = Path('./test_output_bench')
    output_dir.mkdir(exist_ok=True)
    
    voice_config = {
        'language': 'zh-CN',
        'voice_name': 'XiaoxiaoNeural',
        'speed': 1.0
    }
    
    concurrency_levels = [1, 2, 3, 5]
    results = []
    
    for workers in concurrency_levels:
        print(f"\n--- 测试并发数: {workers} ---")
        
        gen = ParallelVoiceGenerator(
            logger=logger,
            max_workers=workers,
            max_retries=1,
            enable_progress=False
        )
        
        try:
            start = time.time()
            result = gen.generate(
                scenes=scenes,
                voice_config=voice_config,
                output_dir=output_dir
            )
            elapsed = time.time() - start
            
            results.append({
                'workers': workers,
                'time': elapsed,
                'speedup': result.speedup_ratio,
                'success': result.success
            })
            
            print(f"   耗时: {elapsed:.2f}s | 加速比: {result.speedup_ratio:.2f}x | 成功: {result.success}")
            
        except Exception as e:
            print(f"   错误: {e}")
            results.append({
                'workers': workers,
                'time': -1,
                'speedup': None,
                'success': False
            })
        
        for f in output_dir.glob('voice-*.mp3'):
            f.unlink(missing_ok=True)
    
    print(f"\n{'='*70}")
    print(f"📊 性能对比总结:")
    print(f"{'='*70}")
    print(f"{'并发数':<8} {'耗时(秒)':<12} {'加速比':<10} {'状态'}")
    print(f"{'-'*40}")
    
    baseline_time = results[0]['time'] if results else 1.0
    for r in results:
        speedup_str = f"{r['speedup']:.2f}x" if r['speedup'] else "N/A"
        status = "✅" if r['success'] else "❌"
        print(f"{r['workers']:<8} {r['time']:<12.2f} {speedup_str:<10} {status}")
    
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
    
    return results


if __name__ == '__main__':
    print("\n" + "🚀"*35)
    print("")
    
    success = test_parallel_generation()
    
    if success:
        test_concurrency_comparison()
    
    print("\n" + "🏁"*35)
    print("")
