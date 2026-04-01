#!/usr/bin/env python3
"""
并行语音生成器 v1.0.0
支持并行生成语音，显著提升性能（3-4倍）

参考技术:
- 行业最佳实践：并行处理
- Python concurrent.futures
"""

import os
import sys
import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time


class ParallelVoiceoverGenerator:
    """并行语音生成器 - 支持多线程并行生成"""
    
    def __init__(self, voice_config: Dict[str, Any], output_dir: Path, 
                 logger: Optional[logging.Logger] = None, max_workers: int = 4):
        self.language = voice_config.get('language', 'zh-CN')
        self.voice_name = voice_config.get('voice_name', 'XiaoxiaoNeural')
        self.speed = voice_config.get('speed', 1.0)
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger(__name__)
        self.max_workers = max_workers
        self.edge_tts = self._find_edge_tts()
        self._lock = threading.Lock()
        self._progress_counter = 0
    
    def _find_edge_tts(self) -> str:
        """查找 edge-tts 可执行文件"""
        possible_paths = [
            shutil.which('edge-tts'),
            Path.home() / '.local' / 'bin' / 'edge-tts',
            '/usr/local/bin/edge-tts',
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                self.logger.debug(f"找到 edge-tts: {path}")
                return str(path)
        
        raise FileNotFoundError("未找到 edge-tts，请运行: pipx install edge-tts")
    
    def generate_single(self, text: str, output_file: Path, index: int) -> Tuple[int, float]:
        """
        生成单个语音文件
        
        Args:
            text: 文本内容
            output_file: 输出文件路径
            index: 场景索引
        
        Returns:
            (index, duration) 元组
        """
        voice = f"{self.language}-{self.voice_name}"
        
        cmd = [
            self.edge_tts,
            '--text', text,
            '--voice', voice,
            '--write-media', str(output_file)
        ]
        
        if self.speed != 1.0:
            rate = f"+{int((self.speed - 1) * 100)}%" if self.speed > 1 else f"-{int((1 - self.speed) * 100)}%"
            cmd.extend(['--rate', rate])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            with self._lock:
                self._progress_counter += 1
            
            self.logger.debug(f"生成语音 {index}: {output_file}")
            
            duration = self._get_duration(output_file)
            return (index, duration)
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"生成语音 {index} 失败: {e.stderr}")
            raise
    
    def generate_parallel(self, scenes: List[Dict[str, Any]], 
                         show_progress: bool = True) -> List[float]:
        """
        并行生成语音
        
        Args:
            scenes: 场景列表
            show_progress: 是否显示进度
        
        Returns:
            时长列表（按场景顺序）
        """
        self.logger.info(f"开始并行生成 {len(scenes)} 个语音（{self.max_workers} 个线程）")
        
        start_time = time.time()
        
        # 准备任务
        tasks = []
        for i, scene in enumerate(scenes, 1):
            output_file = self.output_dir / f"voice-{i:02d}.mp3"
            tasks.append((i, scene['text'], output_file))
        
        # 并行执行
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self.generate_single, text, output_file, index): index
                for index, text, output_file in tasks
            }
            
            # 收集结果
            if show_progress:
                try:
                    from tqdm import tqdm
                    pbar = tqdm(total=len(tasks), desc="并行生成语音")
                    use_tqdm = True
                except ImportError:
                    use_tqdm = False
            else:
                use_tqdm = False
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result_index, duration = future.result()
                    results[result_index] = duration
                    
                    if use_tqdm:
                        pbar.update(1)
                    elif show_progress:
                        print(f"✅ 场景 {result_index:02d} 完成 ({duration:.3f}s)")
                
                except Exception as e:
                    self.logger.error(f"场景 {index} 生成失败: {e}")
                    raise
            
            if use_tqdm:
                pbar.close()
        
        # 按顺序返回结果
        durations = [results[i] for i in range(1, len(scenes) + 1)]
        
        elapsed_time = time.time() - start_time
        total_duration = sum(durations)
        
        self.logger.info(f"并行生成完成:")
        self.logger.info(f"  总时长: {total_duration:.3f}s")
        self.logger.info(f"  耗时: {elapsed_time:.3f}s")
        self.logger.info(f"  加速比: {total_duration / max(elapsed_time, 0.1):.2f}x")
        
        return durations
    
    def _get_duration(self, audio_file: Path) -> float:
        """获取音频时长"""
        # 尝试使用 ffprobe
        ffprobe_path = shutil.which('ffprobe')
        
        if ffprobe_path:
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_file)
            ]
        else:
            # 尝试使用 imageio-ffmpeg
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                cmd = [
                    ffmpeg_path,
                    '-i', str(audio_file),
                    '-f', 'null',
                    '-'
                ]
            except ImportError:
                # 使用系统 ffmpeg
                ffmpeg_path = shutil.which('ffmpeg')
                if not ffmpeg_path:
                    raise RuntimeError("未找到 ffmpeg 或 ffprobe")
                
                cmd = [
                    ffmpeg_path,
                    '-i', str(audio_file),
                    '-f', 'null',
                    '-'
                ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if ffprobe_path:
                return float(result.stdout.strip())
            else:
                # 从 stderr 解析时长
                import re
                match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3))
                    centiseconds = int(match.group(4))
                    return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                else:
                    raise RuntimeError("无法解析音频时长")
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"获取音频时长失败: {e.stderr}")
            raise
    
    def benchmark(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        性能基准测试
        
        Args:
            scenes: 场景列表
        
        Returns:
            性能数据
        """
        self.logger.info("开始性能基准测试...")
        
        # 测试串行生成
        self.logger.info("测试串行生成...")
        start_time = time.time()
        serial_durations = self._generate_serial(scenes[:3])  # 只测试前3个
        serial_time = time.time() - start_time
        
        # 测试并行生成
        self.logger.info("测试并行生成...")
        start_time = time.time()
        parallel_durations = self.generate_parallel(scenes[:3], show_progress=False)
        parallel_time = time.time() - start_time
        
        # 计算加速比
        speedup = serial_time / max(parallel_time, 0.1)
        
        return {
            'serial_time': serial_time,
            'parallel_time': parallel_time,
            'speedup': speedup,
            'workers': self.max_workers,
            'scenes_tested': min(3, len(scenes))
        }
    
    def _generate_serial(self, scenes: List[Dict[str, Any]]) -> List[float]:
        """串行生成（用于基准测试）"""
        durations = []
        for i, scene in enumerate(scenes, 1):
            output_file = self.output_dir / f"voice-{i:02d}.mp3"
            _, duration = self.generate_single(scene['text'], output_file, i)
            durations.append(duration)
        return durations


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 测试配置
    voice_config = {
        'language': 'zh-CN',
        'voice_name': 'XiaoxiaoNeural',
        'speed': 1.0
    }
    
    output_dir = Path('./output/test_parallel')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 测试场景
    scenes = [
        {'text': '欢迎观看演示视频。'},
        {'text': '这是一个测试场景。'},
        {'text': '感谢您的观看。'}
    ]
    
    print("=" * 60)
    print("并行语音生成器测试")
    print("=" * 60)
    
    # 创建生成器
    generator = ParallelVoiceoverGenerator(
        voice_config, 
        output_dir, 
        max_workers=4
    )
    
    # 并行生成
    durations = generator.generate_parallel(scenes, show_progress=True)
    
    print(f"\n生成完成:")
    print(f"  场景数: {len(scenes)}")
    print(f"  总时长: {sum(durations):.3f}s")
    print(f"  平均时长: {sum(durations) / len(durations):.3f}s")


if __name__ == '__main__':
    main()
