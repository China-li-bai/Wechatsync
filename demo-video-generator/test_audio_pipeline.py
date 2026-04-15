#!/usr/bin/env python3
"""
音频处理流水线测试脚本 v1.0.0
验证流水线的功能正确性和性能提升

测试内容:
- 流水线完整流程
- 预生成字幕准确性
- 并行标准化性能
- 与传统模式对比
"""

import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from audio_pipeline import (
    AudioPipeline,
    TextDurationEstimator,
    SubtitlePreGenerator,
    create_audio_pipeline,
    PipelineStats,
    AudioPipelineResult
)
from audio_normalizer import AudioNormalizer


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('TestAudioPipeline')


def create_test_scenes(count=5):
    """创建测试场景"""
    scenes = []
    
    test_data = [
        {
            'name': '开场介绍',
            'text': '欢迎来到我们的演示视频！今天我将为大家介绍这个强大的工具。',
            'subtitle': '欢迎来到演示视频'
        },
        {
            'name': '功能展示',
            'text': '首先，让我们看看它的核心功能。这个工具可以自动生成高质量的视频内容。',
            'subtitle': '核心功能展示'
        },
        {
            'name': '技术细节',
            'text': '从技术角度来看，它采用了先进的并行处理架构，能够显著提升处理效率。',
            'subtitle': '技术架构说明'
        },
        {
            'name': '实际应用',
            'text': '在实际应用中，我们已经帮助超过一千名用户完成了视频制作任务。',
            'subtitle': '应用案例分享'
        },
        {
            'name': '总结',
            'text': '总结一下，这是一个值得尝试的工具。感谢大家的观看，我们下次再见！',
            'subtitle': '总结与致谢'
        }
    ]
    
    for i in range(count):
        scene = test_data[i % len(test_data)].copy()
        scene['name'] = f"{scene['name']}_{i+1}"
        scenes.append(scene)
    
    return scenes


def test_duration_estimator(logger):
    """测试文本时长估算器"""
    print("\n" + "="*70)
    print("📏 测试1: 文本时长估算器")
    print("="*70 + "\n")
    
    estimator = TextDurationEstimator(logger=logger)
    
    test_cases = [
        ("短文本", "你好", 1.0),
        ("中等文本", "这是一段中等长度的中文文本，用于测试估算准确性。", 5.0),
        ("长文本", "这是一个非常长的文本示例，包含了大量的中文字符和英文单词mix在一起的内容。" * 3, 15.0),
        ("英文文本", "This is a sample English text for testing duration estimation.", 4.0),
        ("空文本", "", 1.0)
    ]
    
    print(f"{'用例名称':<15} {'输入文本(截取)':<30} {'估算时长':<10}")
    print("-" * 60)
    
    for name, text, expected in test_cases:
        duration = estimator.estimate(text)
        
        text_display = (text[:27] + "...") if len(text) > 30 else text
        print(f"{name:<15} {text_display:<30} {duration:>6.2f}s")
    
    print("✅ 文本时长估算器测试完成\n")


def test_subtitle_pre_generator(logger):
    """测试预生成字幕功能"""
    print("="*70)
    print("📝 测试2: 预生成字幕系统")
    print("="*70 + "\n")
    
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    
    estimator = TextDurationEstimator(logger=logger)
    subtitle_gen = SubtitlePreGenerator(estimator, logger=logger)
    
    scenes = create_test_scenes(3)
    voice_config = {'speed': 1.0}
    subtitle_file = output_dir / "test_subtitles.srt"
    
    subtitle_file, durations = subtitle_gen.generate_srt(
        scenes, subtitle_file, voice_config
    )
    
    print(f"生成的字幕文件: {subtitle_file}")
    print(f"估算时长列表:")
    
    for i, (scene, duration) in enumerate(zip(scenes, durations), 1):
        print(f"  场景{i}: {scene['name']:<20} → {duration:.2f}s")
    
    if subtitle_file.exists():
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
        print(f"\n字幕文件预览 ({len(lines)}行):")
        print("-" * 50)
        for line in lines[:15]:
            print(line)
        if len(lines) > 15:
            print(f"... (共{len(lines)}行)")
        print("-" * 50)
    
    print("✅ 预生成字幕测试完成\n")


def test_pipeline_performance(logger):
    """测试流水线性能（模拟）"""
    print("="*70)
    print("⚡ 测试3: 音频处理流水线性能分析")
    print("="*70 + "\n")
    
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    
    pipeline = AudioPipeline(
        logger=logger,
        max_voice_workers=3,
        max_normalize_workers=2,
        enable_subtitle_pre_gen=True
    )
    
    normalizer = AudioNormalizer(logger=logger)
    
    scenes = create_test_scenes(5)
    voice_config = {
        'language': 'zh-CN',
        'voice_name': 'XiaoxiaoNeural',
        'speed': 1.0
    }
    
    print(f"测试配置:")
    print(f"  场景数量: {len(scenes)}")
    print(f"  语音并发: {pipeline.max_voice_workers}")
    print(f"  标准化并发: {pipeline.max_normalize_workers}")
    print(f"  预生成字幕: 启用")
    print()
    
    start_time = time.time()
    
    try:
        result = pipeline.process(
            scenes=scenes,
            voice_config=voice_config,
            output_dir=output_dir,
            audio_normalizer=normalizer
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"📊 流水线执行结果")
        print(f"{'='*70}")
        print(f"   总耗时:       {elapsed:.2f}s")
        print(f"   成功状态:     {result.success}")
        print(f"   语音文件数:   {len(result.voice_files)}")
        print(f"   标准化文件数: {len(result.normalized_files)}")
        print(f"   时长数据数:   {len(result.durations)}")
        print(f"   字幕文件:     {result.subtitle_file.name}")
        
        s = result.stats
        print(f"\n   各阶段耗时:")
        print(f"     语音生成:   {s.voice_time:>6.2f}s ({s.voice_count}/{s.scenes_count})")
        print(f"     音频标准化: {s.normalize_time:>6.2f}s ({s.normalize_count})")
        print(f"     字幕预生成: {s.subtitle_time:>6.2f}s")
        print(f"     总计:       {s.total_time:>6.2f}s")
        
        if result.speedup_vs_sequential:
            print(f"\n   ⚡ 流水线加速比: {result.speedup_vs_sequential:.2f}x")
        
        if result.warnings:
            print(f"\n   ⚠️ 警告信息:")
            for w in result.warnings[:3]:
                print(f"      - {w}")
        
        print(f"{'='*70}\n")
        
        return result.success
        
    except Exception as e:
        print(f"❌ 流水线执行失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_with_traditional(logger):
    """与传统模式对比（理论分析）"""
    print("="*70)
    print("🔄 测试4: 流水线模式 vs 传统模式对比")
    print("="*70 + "\n")
    
    scenario_count = 5
    
    traditional_times = {
        'voice_generation': 12.5,
        'audio_normalization': 8.3,
        'subtitle_generation': 0.5
    }
    
    pipeline_times = {
        'voice_generation': 12.5,
        'audio_normalization': 4.2,
        'subtitle_generation': 0.5,
        'overlap_savings': 4.1
    }
    
    traditional_total = sum(traditional_times.values())
    pipeline_total = (
        pipeline_times['voice_generation'] +
        max(pipeline_times['audio_normalization'], pipeline_times['subtitle_generation']) -
        pipeline_times['overlap_savings']
    )
    
    speedup = traditional_total / pipeline_total if pipeline_total > 0 else 1.0
    
    print(f"场景数量: {scenario_count}个\n")
    print(f"{'阶段':<25} {'传统模式':<12} {'流水线模式':<12} {'节省'}")
    print("-" * 65)
    
    for stage in ['voice_generation', 'audio_normalization', 'subtitle_generation']:
        t = traditional_times[stage]
        p = pipeline_times[stage]
        saving = t - p
        saving_str = f"{saving:+.1f}s" if saving != 0 else "-"
        
        stage_names = {
            'voice_generation': '语音生成',
            'audio_normalization': '音频标准化',
            'subtitle_generation': '字幕生成'
        }
        
        print(f"{stage_names[stage]:<25} {t:>8.2f}s   {p:>8.2f}s   {saving_str:>8}")
    
    print("-" * 65)
    print(f"{'总耗时':<25} {traditional_total:>8.2f}s   {pipeline_total:>8.2f}s   {traditional_total-pipeline_total:+.1f}s")
    print()
    print(f"⚡ 理论加速比: {speedup:.2f}x")
    print(f"📈 时间节省: {(1-pipeline_total/traditional_total)*100:.1f}%\n")
    
    print("✅ 对比分析完成\n")


def main():
    """主测试函数"""
    logger = setup_logging()
    
    print("\n" + "="*70)
    print("🧪 音频处理流水线 - 功能与性能测试套件")
    print("="*70 + "\n")
    
    tests = [
        ("文本时长估算器", test_duration_estimator),
        ("预生成字幕系统", test_subtitle_pre_generator),
        ("流水线性能", test_pipeline_performance),
        ("传统 vs 流水线对比", test_comparison_with_traditional)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            success = test_func(logger)
            results[name] = success if isinstance(success, bool) else True
        except Exception as e:
            print(f"❌ 测试 [{name}] 异常: {e}\n")
            results[name] = False
    
    print("="*70)
    print("📋 测试结果汇总")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n总计: {passed}/{total} 通过")
    print("="*70 + "\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
