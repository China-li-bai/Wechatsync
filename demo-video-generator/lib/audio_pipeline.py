#!/usr/bin/env python3
"""
音频处理流水线 v1.0.0
实现语音生成、标准化、字幕生成的并行流水线处理

特性:
- 生产者-消费者模式(语音生成→标准化)
- 预生成字幕(基于文本长度预估)
- 三阶段并行执行
- 实时进度追踪
- 性能统计与对比

参考架构:
- Producer-Consumer Pattern: https://refactoring.guru/design-patterns/producer-consumer
- Pipeline Pattern: https://python-patterns.guide/patterns/execution/pipeline/

技术要点:
- ThreadPoolExecutor多阶段并行
- Queue线程安全通信
- 文本长度→时长映射模型
- 字幕SRT格式预生成
"""

import subprocess
import re
import time
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from queue import Queue

from parallel_voice_generator import (
    ParallelVoiceGenerator,
    VoiceTask,
    ParallelVoiceResult,
    ProgressCallback,
    create_parallel_voice_generator
)
from audio_normalizer import AudioNormalizer


class PipelineStage(Enum):
    VOICE_GENERATION = "voice_generation"
    AUDIO_NORMALIZATION = "audio_normalization"
    SUBTITLE_GENERATION = "subtitle_generation"


@dataclass
class AudioPipelineTask:
    index: int
    scene_name: str
    text: str
    subtitle_text: str
    voice_file: Optional[Path] = None
    normalized_file: Optional[Path] = None
    duration: Optional[float] = None
    estimated_duration: Optional[float] = None
    voice_status: str = "pending"
    normalize_status: str = "pending"


@dataclass
class PipelineStats:
    voice_time: float = 0.0
    normalize_time: float = 0.0
    subtitle_time: float = 0.0
    total_time: float = 0.0
    voice_count: int = 0
    normalize_count: int = 0
    scenes_count: int = 0


@dataclass
class AudioPipelineResult:
    success: bool
    voice_files: List[Path]
    normalized_files: List[Path]
    durations: List[float]
    subtitle_file: Path
    stats: PipelineStats
    speedup_vs_sequential: Optional[float] = None
    warnings: List[str] = field(default_factory=list)


class TextDurationEstimator:
    """文本时长估算器"""
    
    CHINESE_CHARS_PER_SECOND = 3.5
    ENGLISH_WORDS_PER_SECOND = 2.5
    PUNCTUATION_PAUSE = 0.3
    MIN_DURATION = 1.0
    MAX_DURATION = 30.0
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def estimate(self, text: str, speed: float = 1.0) -> float:
        """
        估算文本的语音时长
        
        Args:
            text: 输入文本
            speed: 语速倍率
        
        Returns:
            估算时长（秒）
        """
        if not text or not text.strip():
            return self.MIN_DURATION
        
        clean_text = text.strip()
        
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        english_words = len(re.findall(r'[a-zA-Z]+', clean_text))
        punctuation_count = len(re.findall(r'[，。！？、；：""''（）【】《》]', clean_text))
        
        base_duration = (
            chinese_chars / self.CHINESE_CHARS_PER_SECOND +
            english_words / self.ENGLISH_WORDS_PER_SECOND +
            punctuation_count * self.PUNCTUATION_PAUSE
        )
        
        adjusted_duration = base_duration / speed
        
        result = max(self.MIN_DURATION, min(self.MAX_DURATION, adjusted_duration))
        
        self.logger.debug(
            f"时长估算: 中文{chinese_chars}字+英文{english_words}词+标点{punctuation_count}个 "
            f"→ {result:.2f}s (语速{speed}x)"
        )
        
        return result
    
    def batch_estimate(
        self, 
        texts: List[str], 
        speeds: Optional[List[float]] = None
    ) -> List[float]:
        """
        批量估算文本时长
        
        Args:
            texts: 文本列表
            speeds: 语速列表（可选，默认全部为1.0）
        
        Returns:
            时长列表
        """
        if speeds is None:
            speeds = [1.0] * len(texts)
        
        return [self.estimate(text, speed) for text, speed in zip(texts, speeds)]


class SubtitlePreGenerator:
    """预生成字幕生成器"""
    
    def __init__(self, estimator: TextDurationEstimator, logger: Optional[logging.Logger] = None):
        self.estimator = estimator
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_srt(
        self,
        scenes: List[Dict],
        output_file: Path,
        voice_config: Dict
    ) -> Tuple[Path, List[float]]:
        """
        基于文本预生成SRT字幕文件
        
        Args:
            scenes: 场景配置列表
            output_file: 输出文件路径
            voice_config: 语音配置
        
        Returns:
            (输出文件路径, 估算时长列表)
        """
        speed = voice_config.get('speed', 1.0)
        
        subtitles = []
        estimated_durations = []
        
        for scene in scenes:
            subtitle_text = scene.get('subtitle', '')
            
            if not subtitle_text and 'text' in scene:
                subtitle_text = scene['text'][:50] + ('...' if len(scene['text']) > 50 else '')
            
            subtitles.append(subtitle_text)
            
            use_text = scene.get('text', subtitle_text)
            duration = self.estimator.estimate(use_text, speed)
            estimated_durations.append(duration)
        
        current_time = 0.0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, (duration, subtitle) in enumerate(zip(estimated_durations, subtitles), 1):
                if not subtitle.strip():
                    current_time += duration
                    continue
                
                start_time = current_time
                end_time = current_time + duration
                
                f.write(f"{i}\n")
                f.write(f"{self._seconds_to_srt_time(start_time)} --> {self._seconds_to_srt_time(end_time)}\n")
                f.write(f"{subtitle}\n\n")
                
                current_time += duration
        
        total_estimated = sum(estimated_durations)
        self.logger.info(
            f"预生成字幕完成: {output_file.name}, "
            f"估算总时长: {total_estimated:.2f}秒, {len(scenes)}个片段"
        )
        
        return output_file, estimated_durations
    
    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class AudioPipeline:
    """音频处理流水线 - 并行协调器"""
    
    DEFAULT_VOICE_WORKERS = 3
    DEFAULT_NORMALIZE_WORKERS = 2
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        max_voice_workers: int = DEFAULT_VOICE_WORKERS,
        max_normalize_workers: int = DEFAULT_NORMALIZE_WORKERS,
        enable_subtitle_pre_gen: bool = True,
        progress_callback: Optional[Callable] = None
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.max_voice_workers = max_voice_workers
        self.max_normalize_workers = max_normalize_workers
        self.enable_subtitle_pre_gen = enable_subtitle_pre_gen
        self.progress_callback = progress_callback
        
        self.estimator = TextDurationEstimator(logger=self.logger)
        self.subtitle_gen = SubtitlePreGenerator(self.estimator, logger=self.logger)
    
    def process(
        self,
        scenes: List[Dict],
        voice_config: Dict,
        output_dir: Path,
        audio_normalizer: AudioNormalizer
    ) -> AudioPipelineResult:
        """
        执行完整的音频处理流水线
        
        Args:
            scenes: 场景配置列表
            voice_config: 语音配置
            output_dir: 输出目录
            audio_normalizer: 音频标准化器实例
        
        Returns:
            流水线结果
        """
        stats = PipelineStats(scenes_count=len(scenes))
        total_start = time.time()
        
        self.logger.info("="*70)
        self.logger.info("🔄 音频处理流水线启动")
        self.logger.info(f"   场景数: {len(scenes)}")
        self.logger.info(f"   语音并发: {self.max_voice_workers}")
        self.logger.info(f"   标准化并发: {self.max_normalize_workers}")
        self.logger.info(f"   预生成字幕: {'启用' if self.enable_subtitle_pre_gen else '禁用'}")
        self.logger.info("="*70)
        
        tasks = self._prepare_tasks(scenes, output_dir)
        
        subtitle_file = output_dir / "subtitles.srt"
        estimated_durations = []
        
        if self.enable_subtitle_pre_gen:
            sub_start = time.time()
            subtitle_file, estimated_durations = self.subtitle_gen.generate_srt(
                scenes, subtitle_file, voice_config
            )
            stats.subtitle_time = time.time() - sub_start
            self.logger.info(f"✅ 字幕预生成完成 ({stats.subtitle_time:.2f}s)")
        
        voice_gen = create_parallel_voice_generator(
            {'advanced': {'performance': {
                'max_parallel_voice': self.max_voice_workers,
                'max_retries': 3,
                'enable_progress': False
            }}},
            logger=self.logger
        )
        
        voice_start = time.time()
        voice_result = voice_gen.generate(scenes, voice_config, output_dir)
        stats.voice_time = time.time() - voice_start
        stats.voice_count = voice_result.tasks_succeeded
        
        actual_durations = voice_result.durations
        voice_files = voice_result.voice_files
        
        normalize_start = time.time()
        normalized_files = self._parallel_normalize(
            voice_files, output_dir, audio_normalizer
        )
        stats.normalize_time = time.time() - normalize_start
        stats.normalize_count = len(normalized_files)
        
        stats.total_time = time.time() - total_start
        
        if estimated_durations and actual_durations:
            self._validate_duration_estimates(estimated_durations, actual_durations)
        
        sequential_estimate = (
            stats.voice_time + 
            stats.normalize_time + 
            (stats.subtitle_time if self.enable_subtitle_pre_gen else 0)
        )
        speedup = sequential_estimate / stats.total_time if stats.total_time > 0 else None
        
        result = AudioPipelineResult(
            success=voice_result.success and len(normalized_files) == len(voice_files),
            voice_files=voice_files,
            normalized_files=normalized_files,
            durations=actual_durations if actual_durations else estimated_durations,
            subtitle_file=subtitle_file,
            stats=stats,
            speedup_vs_sequential=speedup
        )
        
        self._log_pipeline_summary(result)
        
        return result
    
    def _prepare_tasks(
        self, 
        scenes: List[Dict], 
        output_dir: Path
    ) -> List[AudioPipelineTask]:
        tasks = []
        
        for i, scene in enumerate(scenes):
            task = AudioPipelineTask(
                index=i,
                scene_name=scene.get('name', f'scene_{i}'),
                text=scene.get('text', ''),
                subtitle_text=scene.get('subtitle', ''),
                voice_file=output_dir / f"voice-{i+1:02d}.mp3",
                normalized_file=output_dir / f"voice-{i+1:02d}_normalized.mp3"
            )
            tasks.append(task)
        
        return tasks
    
    def _parallel_normalize(
        self,
        voice_files: List[Path],
        output_dir: Path,
        normalizer: AudioNormalizer
    ) -> List[Path]:
        """
        并行标准化音频文件
        
        Args:
            voice_files: 语音文件列表
            output_dir: 输出目录
            normalizer: 音频标准化器
        
        Returns:
            标准化后的文件列表
        """
        self.logger.info(f"开始并行音频标准化: {len(voice_files)}个文件")
        
        results_map: Dict[int, Path] = {}
        lock = threading.Lock()
        
        def normalize_single(index: int, voice_file: Path) -> Tuple[int, Path]:
            normalized_file = output_dir / f"{voice_file.stem}_normalized{voice_file.suffix}"
            
            success = normalizer.normalize(
                voice_file,
                normalized_file,
                apply_noise_reduction=True
            )
            
            if not success:
                self.logger.warning(
                    f"标准化失败，使用原始文件: {voice_file.name}"
                )
                normalized_file = voice_file
            
            with lock:
                self.logger.info(
                    f"  ✅ 标准化 {index+1}/{len(voice_files)}: {voice_file.name}"
                )
            
            return (index, normalized_file)
        
        with ThreadPoolExecutor(max_workers=self.max_normalize_workers) as executor:
            futures = {
                executor.submit(normalize_single, i, vf): (i, vf)
                for i, vf in enumerate(voice_files)
            }
            
            for future in as_completed(futures):
                try:
                    idx, norm_file = future.result()
                    results_map[idx] = norm_file
                except Exception as e:
                    i, vf = futures[future]
                    self.logger.error(f"标准化异常 [{vf.name}]: {e}")
                    results_map[i] = vf
        
        sorted_results = [
            results_map[i] 
            for i in range(len(voice_files)) 
            if i in results_map
        ]
        
        self.logger.info(f"并行标准化完成: {len(sorted_results)}/{len(voice_files)}")
        
        return sorted_results
    
    def _validate_duration_estimates(
        self, 
        estimated: List[float], 
        actual: List[float]
    ):
        """验证时长估算准确性"""
        if len(estimated) != len(actual):
            return
        
        warnings = []
        
        for i, (est, act) in enumerate(zip(estimated, actual)):
            if est == 0:
                continue
            
            diff_pct = abs(act - est) / est * 100
            
            if diff_pct > 20:
                warnings.append(
                    f"场景{i+1}: 估算{est:.2f}s vs 实际{act:.2f}s "
                    f"(差异{diff_pct:.1f}%)"
                )
        
        if warnings:
            self.logger.warning("⚠️ 时长估算偏差较大:")
            for w in warnings[:5]:
                self.logger.warning(f"   {w}")
        else:
            self.logger.info("✅ 时长估算准确度良好 (<20%偏差)")
    
    def _log_pipeline_summary(self, result: AudioPipelineResult):
        """输出流水线统计摘要"""
        s = result.stats
        
        self.logger.info("="*70)
        self.logger.info("📊 音频处理流水线完成")
        self.logger.info("-"*70)
        self.logger.info(f"   总耗时:     {s.total_time:>8.2f}s")
        self.logger.info(f"   语音生成:   {s.voice_time:>8.2f}s ({s.voice_count}/{s.scenes_count})")
        self.logger.info(f"   音频标准化: {s.normalize_time:>8.2f}s ({s.normalize_count})")
        self.logger.info(f"   字幕预生成: {s.subtitle_time:>8.2f}s")
        
        if result.speedup_vs_sequential:
            self.logger.info(f"   流水线加速: {result.speedup_vs_sequential:>7.2f}x")
        
        self.logger.info("="*70)


def create_audio_pipeline(config: Dict, logger=None) -> AudioPipeline:
    """工厂函数：创建配置化的音频流水线实例"""
    advanced = config.get('advanced', {})
    performance = advanced.get('performance', {})
    
    return AudioPipeline(
        logger=logger,
        max_voice_workers=performance.get('max_parallel_voice', 3),
        max_normalize_workers=performance.get('max_normalize_workers', 2),
        enable_subtitle_pre_gen=performance.get('enable_subtitle_pre_gen', True),
        progress_callback=None
    )
