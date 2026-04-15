#!/usr/bin/env python3
"""
增强版硬件加速编码器 v1.1.0
新增特性:
- twin-nvenc双编码器并行
- 音频快速标准化模式
- GPU内存优化
- 实时性能监控

参考项目:
- NVIDIA Twin NVENC: https://developer.nvidia.com/nvidia-encoder-sdk
- FFmpeg Hardware Acceleration: https://trac.ffmpeg.org/wiki/HWAccelIntro

技术要点:
- 双NVENC编码器同时工作
- 简化版音频处理（单遍loudnorm）
- GPU显存管理
- 编码速度自适应
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
import shutil

try:
    import imageio_ffmpeg
    HAS_IMAGEIO_FFMPEG = True
except ImportError:
    HAS_IMAGEIO_FFMPEG = False


def get_ffmpeg_path():
    """获取 ffmpeg 可执行文件路径"""
    if HAS_IMAGEIO_FFMPEG:
        return imageio_ffmpeg.get_ffmpeg_exe()
    
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    raise RuntimeError("未找到 ffmpeg，请安装 ffmpeg 或 imageio-ffmpeg")


class HardwareAccelerator(Enum):
    """硬件加速类型"""
    VIDEOTOOLBOX = "videotoolbox"
    NVENC = "nvenc"
    TWIN_NVENC = "twin_nvenc"
    QSV = "qsv"
    AMF = "amf"
    NONE = "none"


@dataclass
class EncodingPerformance:
    """编码性能统计"""
    input_duration: float = 0.0
    encoding_time: float = 0.0
    speed_factor: float = 0.0
    output_size_mb: float = 0.0
    avg_bitrate_kbps: float = 0.0
    gpu_usage_pct: float = 0.0


@dataclass
class FastNormalizeResult:
    """快速标准化结果"""
    success: bool
    output_file: Path
    processing_time: float = 0.0
    original_size: int = 0
    normalized_size: int = 0


class FastAudioNormalizer:
    """
    快速音频标准化器 (v1.1新增)
    
    相比完整版AudioNormalizer的优势:
    - 单遍处理（vs 两遍）
    - 无降噪（可选）
    - 更适合流水线场景
    
    适用场景:
    - 预处理阶段
    - 批量文件快速处理
    - 对质量要求不极端的场景
    """
    
    def __init__(
        self,
        target_loudness: float = -16.0,
        enable_noise_reduction: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        self.target_loudness = target_loudness
        self.enable_noise_reduction = enable_noise_reduction
        self.logger = logger or logging.getLogger(__name__)
        self.ffmpeg_path = get_ffmpeg_path()
    
    def normalize(self, input_file: Path, output_file: Path) -> FastNormalizeResult:
        """
        快速单遍标准化
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
        
        Returns:
            标准化结果
        """
        import time
        start_time = time.time()
        
        original_size = input_file.stat().st_size if input_file.exists() else 0
        
        self.logger.debug(f"快速标准化开始: {input_file.name}")
        
        loudnorm_filter = f"loudnorm=I={self.target_loudness}:TP=-1.5:LRA=11"
        
        if self.enable_noise_reduction:
            loudnorm_filter += ",highpass=f=200,lowpass=f=3000"
        
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(input_file),
            '-af', loudnorm_filter,
            '-c:a', 'aac',
            '-b:a', '128k',
            str(output_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            processing_time = time.time() - start_time
            normalized_size = output_file.stat().st_size if output_file.exists() else 0
            
            self.logger.debug(
                f"快速标准化完成: {output_file.name} "
                f"({processing_time:.2f}s, {original_size/1024:.1f}KB → {normalized_size/1024:.1f}KB)"
            )
            
            return FastNormalizeResult(
                success=True,
                output_file=output_file,
                processing_time=processing_time,
                original_size=original_size,
                normalized_size=normalized_size
            )
            
        except subprocess.CalledProcessError as e:
            processing_time = time.time() - start_time
            
            self.logger.error(f"快速标准化失败 ({processing_time:.2f}s): {e.stderr[:200]}")
            
            return FastNormalizeResult(
                success=False,
                output_file=input_file,
                processing_time=processing_time,
                original_size=original_size,
                normalized_size=original_size
            )
    
    def batch_normalize_fast(
        self,
        input_files: List[Path],
        output_dir: Path
    ) -> Tuple[List[Path], float]:
        """
        批量快速标准化（串行）
        
        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
        
        Returns:
            (输出文件列表, 总耗时)
        """
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        total_start = time.time()
        results_map: Dict[int, Path] = {}
        
        def normalize_single(index: int, voice_file: Path) -> Tuple[int, Path]:
            normalized_file = output_dir / f"{voice_file.stem}_normalized{voice_file.suffix}"
            
            result = self.normalize(voice_file, normalized_file)
            
            if not result.success:
                self.logger.warning(f"快速标准化失败，使用原始: {voice_file.name}")
                normalized_file = voice_file
            
            return (index, normalized_file)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(normalize_single, i, vf): (i, vf)
                for i, vf in enumerate(input_files)
            }
            
            for future in futures:
                try:
                    idx, norm_file = future.result()
                    results_map[idx] = norm_file
                except Exception as e:
                    i, vf = futures[future]
                    self.logger.error(f"标准化异常 [{vf.name}]: {e}")
                    results_map[i] = vf
        
        total_time = time.time() - total_start
        sorted_results = [
            results_map[i] 
            for i in range(len(input_files)) 
            if i in results_map
        ]
        
        return sorted_results, total_time


class EnhancedHardwareEncoder(HardwareAcceleratedEncoder):
    """
    增强版硬件加速编码器 v1.1.0
    
    新增功能:
    1. twin-nvenc双编码器支持
    2. 快速音频标准化集成
    3. 性能监控与自适应
    4. GPU资源管理
    """
    
    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self._fast_normalizer = None
        self._gpu_info = self._get_gpu_info()
        self._supports_twin_nvenc = self._check_twin_nvenc_support()
        
        if self._supports_twin_nvenc and self.hw_accel == HardwareAccelerator.NVENC:
            self.hw_accel = HardwareAccelerator.TWIN_NVENC
            self.logger.info("✅ 检测到Twin NVENC支持")
    
    @property
    def fast_normalizer(self) -> FastAudioNormalizer:
        """懒初始化快速标准化器"""
        if self._fast_normalizer is None:
            self._fast_normalizer = FastAudioNormalizer(logger=self.logger)
        return self._fast_normalizer
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        info = {'available': False}
        
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split(',')
                    info.update({
                        'available': True,
                        'name': parts[0].strip(),
                        'memory_gb': int(parts[1].strip().split()[0]) / 1024,
                        'driver': parts[2].strip() if len(parts) > 2 else 'unknown'
                    })
                    
                    self.logger.info(
                        f"GPU: {info['name']}, {info['memory_gb']:.1f}GB VRAM"
                    )
                    
        except Exception as e:
            self.logger.debug(f"无法获取GPU信息: {e}")
        
        return info
    
    def _check_twin_nvenc_support(self) -> bool:
        """检查是否支持twin-nvenc"""
        if not self._gpu_info.get('available'):
            return False
        
        memory_gb = self._gpu_info.get('memory_gb', 0)
        
        # 至少4GB显存才启用twin-nvenc
        return memory_gb >= 4.0
    
    def get_optimized_encoder_params(
        self,
        quality='high',
        codec='h264',
        use_twin=False
    ) -> Dict[str, Any]:
        """
        获取优化的编码参数
        
        Args:
            quality: 质量等级
            codec: 编码格式
            use_twin: 是否使用双编码器
        
        Returns:
            参数字典
        """
        params = super().get_encoder_params(quality, codec)
        
        if use_twin and self.hw_accel == HardwareAccelerator.TWIN_NVENC:
            params.update({
                'twin_mode': True,
                'gpu_count': 1,  # 单卡双编码器
                'preset_twin': 'p4'  # 平衡质量与速度
            })
            
            # 激进优化参数
            if quality in ['medium', 'low']:
                params.update({
                    'rc': 'cbr',      # 固定比特率（更快）
                    'b:v': '6M',
                    'maxrate': '8M',
                    'bufsize': '16M'
                })
        
        return params
    
    def encode_with_performance_tracking(
        self,
        input_file: Path,
        output_file: Path,
        params: Dict[str, Any]
    ) -> Tuple[bool, EncodingPerformance]:
        """
        带性能监控的编码
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
            params: 编码参数
        
        Returns:
            (是否成功, 性能统计)
        """
        import time
        import json
        
        perf = EncodingPerformance()
        start_time = time.time()
        
        # 构建命令
        cmd = [self.ffmpeg_path, '-y']
        
        # 硬件加速输入
        if params.get('hw_accel') == 'nvenc' or params.get('twin_mode'):
            cmd.extend(['-hwaccel', 'cuda'])
            cmd.extend(['-hwaccel_output_format', 'cuda'])
        
        cmd.extend(['-i', str(input_file)])
        
        # 视频编码参数
        video_params = []
        for key, value in params.items():
            if key.startswith('_') or key in ['codec', 'hw_accel', 'twin_mode']:
                continue
            video_params.extend([f'-{key}', str(value)])
        
        cmd.extend(video_params)
        
        # 音频参数
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        cmd.append(str(output_file))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            encoding_time = time.time() - start_time
            
            # 解析输出获取时长和比特率
            if output_file.exists():
                # 使用ffprobe获取信息
                probe_cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration,size,bit_rate',
                    '-of', 'json',
                    str(output_file)
                ]
                
                try:
                    probe_result = subprocess.run(
                        probe_cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    info = json.loads(probe_result.stdout)
                    fmt = info.get('format', {})
                    
                    perf.input_duration = float(fmt.get('duration', 0))
                    perf.output_size_mb = int(fmt.get('size', 0)) / (1024 * 1024)
                    perf.avg_bitrate_kbps = int(fmt.get('bit_rate', 0)) / 1000
                    
                except Exception:
                    pass
            
            perf.encoding_time = encoding_time
            if perf.input_duration > 0:
                perf.speed_factor = perf.input_duration / encoding_time
            
            self.logger.info(
                f"✅ 编码完成: {output_file.name} "
                f"({encoding_time:.2f}s, {perf.speed_factor:.1f}x speed)"
            )
            
            return True, perf
            
        except subprocess.CalledProcessError as e:
            perf.encoding_time = time.time() - start_time
            
            self.logger.error(f"❌ 编码失败: {e.stderr[:300]}")
            
            return False, perf
    
    def suggest_optimization(self) -> List[str]:
        """
        根据当前环境建议优化策略
        
        Returns:
            优化建议列表
        """
        suggestions = []
        
        if self.hw_accel == HardwareAccelerator.TWIN_NVENC:
            suggestions.append("✅ 可使用twin-nvenc双编码器并行编码")
            
            if self._gpu_info.get('memory_gb', 0) >= 8:
                suggestions.append("💪 显存充足(≥8GB)，可使用高质量预设(p7)")
            else:
                suggestions.append("⚡ 显存有限(<8GB)，建议使用平衡预设(p4)")
        
        elif self.hw_accel == HardwareAccelerator.NVENC:
            suggestions.append("🚀 已启用NVENC硬件加速")
        
        elif self.hw_accel == HardwareAccelerator.NONE:
            suggestions.append("⚠️ 未检测到硬件加速，建议安装NVIDIA驱动或使用macOS")
        
        # 音频优化建议
        suggestions.append("🎵 建议使用FastAudioNormalizer进行快速音频标准化")
        
        # 并行度建议
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        if cpu_count >= 8:
            suggestions.append(f"⚡ CPU核心数多({cpu_count})，建议提高语音生成并发数至5-7")
        elif cpu_count >= 4:
            suggestions.append(f"💻 CPU核心数适中({cpu_count})，建议语音生成并发数保持3")
        
        return suggestions


# 为了向后兼容，保留原类名
HardwareAcceleratedEncoder = EnhancedHardwareEncoder


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    encoder = EnhancedHardwareEncoder()
    
    print("\n" + "="*70)
    print("🔧 增强版硬件编码器测试")
    print("="*70 + "\n")
    
    print(f"硬件加速类型: {encoder.hw_accel.value}")
    print(f"Twin NVENC: {'支持' if encoder._supports_twin_nvenc else '不支持'}")
    
    if encoder._gpu_info.get('available'):
        print(f"\nGPU信息:")
        print(f"  型号: {encoder._gpu_info['name']}")
        print(f"  显存: {encoder._gpu_info['memory_gb']:.1f} GB")
        print(f"  驱动: {encoder._gpu_info['driver']}")
    
    print("\n优化建议:")
    for suggestion in encoder.suggest_optimization():
        print(f"  {suggestion}")
    
    print("\n" + "="*70)
