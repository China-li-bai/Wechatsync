#!/usr/bin/env python3
"""
硬件加速编码器 v1.0.0
自动检测和使用硬件加速编码

参考项目:
- NVIDIA NVENC: https://docs.nvidia.com/video-technologies/video-codec-sdk/
- VideoToolbox: macOS硬件加速
- Intel QSV: Intel Quick Sync Video

技术要点:
- 自动检测硬件加速支持
- 多平台支持（macOS、NVIDIA、Intel）
- 参数优化
- 优雅降级
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
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
    VIDEOTOOLBOX = "videotoolbox"  # macOS
    NVENC = "nvenc"                # NVIDIA
    QSV = "qsv"                     # Intel
    AMF = "amf"                     # AMD
    NONE = "none"                   # CPU


class HardwareAcceleratedEncoder:
    """硬件加速编码器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化硬件加速编码器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.ffmpeg_path = get_ffmpeg_path()
        self.hw_accel = self._detect_hardware_acceleration()
        
        self.logger.info(f"检测到硬件加速: {self.hw_accel.value}")
    
    def _detect_hardware_acceleration(self) -> HardwareAccelerator:
        """
        检测硬件加速支持
        
        Returns:
            检测到的硬件加速类型
        """
        # 获取FFmpeg支持的编码器
        encoders = self._get_supported_encoders()
        
        # macOS: VideoToolbox
        if sys.platform == 'darwin':
            if 'h264_videotoolbox' in encoders:
                self.logger.debug("检测到 VideoToolbox 支持")
                return HardwareAccelerator.VIDEOTOOLBOX
        
        # NVIDIA: NVENC
        if self._check_nvenc(encoders):
            self.logger.debug("检测到 NVIDIA NVENC 支持")
            return HardwareAccelerator.NVENC
        
        # Intel: QSV
        if self._check_qsv(encoders):
            self.logger.debug("检测到 Intel QSV 支持")
            return HardwareAccelerator.QSV
        
        # AMD: AMF
        if self._check_amf(encoders):
            self.logger.debug("检测到 AMD AMF 支持")
            return HardwareAccelerator.AMF
        
        # CPU编码
        self.logger.info("未检测到硬件加速，使用CPU编码")
        return HardwareAccelerator.NONE
    
    def _get_supported_encoders(self) -> List[str]:
        """
        获取FFmpeg支持的编码器列表
        
        Returns:
            编码器列表
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-encoders'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析编码器列表
            encoders = []
            for line in result.stdout.split('\n'):
                if line.strip().startswith('V'):
                    parts = line.split()
                    if len(parts) >= 2:
                        encoders.append(parts[1])
            
            return encoders
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"获取编码器列表失败: {e}")
            return []
    
    def _check_nvenc(self, encoders: List[str]) -> bool:
        """
        检查NVIDIA NVENC支持
        
        Args:
            encoders: 编码器列表
        
        Returns:
            是否支持
        """
        nvenc_encoders = [
            'h264_nvenc',
            'hevc_nvenc',
            'av1_nvenc'
        ]
        
        for encoder in nvenc_encoders:
            if encoder in encoders:
                # 额外检查NVIDIA驱动
                if self._check_nvidia_driver():
                    return True
        
        return False
    
    def _check_nvidia_driver(self) -> bool:
        """
        检查NVIDIA驱动是否正常
        
        Returns:
            是否正常
        """
        try:
            # 尝试运行nvidia-smi
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_qsv(self, encoders: List[str]) -> bool:
        """
        检查Intel QSV支持
        
        Args:
            encoders: 编码器列表
        
        Returns:
            是否支持
        """
        qsv_encoders = [
            'h264_qsv',
            'hevc_qsv'
        ]
        
        for encoder in qsv_encoders:
            if encoder in encoders:
                return True
        
        return False
    
    def _check_amf(self, encoders: List[str]) -> bool:
        """
        检查AMD AMF支持
        
        Args:
            encoders: 编码器列表
        
        Returns:
            是否支持
        """
        amf_encoders = [
            'h264_amf',
            'hevc_amf'
        ]
        
        for encoder in amf_encoders:
            if encoder in encoders:
                return True
        
        return False
    
    def get_encoder_params(self, 
                          quality: str = 'high',
                          codec: str = 'h264') -> Dict[str, Any]:
        """
        获取编码器参数
        
        Args:
            quality: 质量等级
            codec: 编码格式
        
        Returns:
            编码器参数字典
        """
        params = {
            'codec': codec,
            'hw_accel': self.hw_accel.value
        }
        
        if self.hw_accel == HardwareAccelerator.VIDEOTOOLBOX:
            params.update(self._get_videotoolbox_params(quality))
        elif self.hw_accel == HardwareAccelerator.NVENC:
            params.update(self._get_nvenc_params(quality))
        elif self.hw_accel == HardwareAccelerator.QSV:
            params.update(self._get_qsv_params(quality))
        elif self.hw_accel == HardwareAccelerator.AMF:
            params.update(self._get_amf_params(quality))
        else:
            params.update(self._get_cpu_params(quality))
        
        return params
    
    def _get_videotoolbox_params(self, quality: str) -> Dict[str, Any]:
        """
        获取VideoToolbox参数
        
        Args:
            quality: 质量等级
        
        Returns:
            参数字典
        """
        quality_map = {
            'low': {'b:v': '2M', 'profile:v': 'baseline'},
            'medium': {'b:v': '5M', 'profile:v': 'main'},
            'high': {'b:v': '8M', 'profile:v': 'high'}
        }
        
        params = {
            'c:v': 'h264_videotoolbox',
            'level': '4.2',
            'allow_sw': '1'  # 允许软件编码作为后备
        }
        
        params.update(quality_map.get(quality, quality_map['medium']))
        
        return params
    
    def _get_nvenc_params(self, quality: str) -> Dict[str, Any]:
        """
        获取NVENC参数
        
        Args:
            quality: 质量等级
        
        Returns:
            参数字典
        """
        quality_map = {
            'low': {
                'preset': 'p1',  # 最快
                'tune': 'll',    # 低延迟
                'cq': '28',
                'b:v': '2M'
            },
            'medium': {
                'preset': 'p4',  # 平衡
                'tune': 'hq',    # 高质量
                'cq': '25',
                'b:v': '5M'
            },
            'high': {
                'preset': 'p7',  # 最慢最佳质量
                'tune': 'hq',    # 高质量
                'cq': '20',
                'b:v': '8M'
            }
        }
        
        params = {
            'c:v': 'h264_nvenc',
            'rc': 'vbr',      # 可变比特率
            'maxrate': '10M',
            'bufsize': '20M',
            'profile:v': 'high',
            'level': '4.2'
        }
        
        params.update(quality_map.get(quality, quality_map['medium']))
        
        return params
    
    def _get_qsv_params(self, quality: str) -> Dict[str, Any]:
        """
        获取QSV参数
        
        Args:
            quality: 质量等级
        
        Returns:
            参数字典
        """
        quality_map = {
            'low': {'global_quality': '28', 'preset': 'veryfast'},
            'medium': {'global_quality': '23', 'preset': 'medium'},
            'high': {'global_quality': '18', 'preset': 'slow'}
        }
        
        params = {
            'c:v': 'h264_qsv',
            'look_ahead': '1',
            'profile:v': 'high',
            'level': '4.2'
        }
        
        params.update(quality_map.get(quality, quality_map['medium']))
        
        return params
    
    def _get_amf_params(self, quality: str) -> Dict[str, Any]:
        """
        获取AMF参数
        
        Args:
            quality: 质量等级
        
        Returns:
            参数字典
        """
        quality_map = {
            'low': {'qp_i': '28', 'qp_p': '28', 'qp_b': '28'},
            'medium': {'qp_i': '23', 'qp_p': '23', 'qp_b': '23'},
            'high': {'qp_i': '18', 'qp_p': '18', 'qp_b': '18'}
        }
        
        params = {
            'c:v': 'h264_amf',
            'profile:v': 'high',
            'level': '4.2'
        }
        
        params.update(quality_map.get(quality, quality_map['medium']))
        
        return params
    
    def _get_cpu_params(self, quality: str) -> Dict[str, Any]:
        """
        获取CPU编码参数
        
        Args:
            quality: 质量等级
        
        Returns:
            参数字典
        """
        quality_map = {
            'low': {'preset': 'veryfast', 'crf': '28'},
            'medium': {'preset': 'medium', 'crf': '23'},
            'high': {'preset': 'slow', 'crf': '18'}
        }
        
        params = {
            'c:v': 'libx264',
            'profile:v': 'high',
            'level': '4.2'
        }
        
        params.update(quality_map.get(quality, quality_map['medium']))
        
        return params
    
    def build_ffmpeg_command(self,
                            input_file: Path,
                            output_file: Path,
                            quality: str = 'high',
                            audio_codec: str = 'aac',
                            audio_bitrate: str = '128k') -> List[str]:
        """
        构建FFmpeg命令
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
            quality: 质量等级
            audio_codec: 音频编码器
            audio_bitrate: 音频比特率
        
        Returns:
            FFmpeg命令列表
        """
        params = self.get_encoder_params(quality)
        
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(input_file)
        ]
        
        # 添加视频编码参数
        for key, value in params.items():
            if key not in ['codec', 'hw_accel']:
                cmd.extend([f'-{key}', str(value)])
        
        # 添加音频编码参数
        cmd.extend([
            '-c:a', audio_codec,
            '-b:a', audio_bitrate
        ])
        
        # 添加输出文件
        cmd.append(str(output_file))
        
        return cmd
    
    def encode(self,
               input_file: Path,
               output_file: Path,
               quality: str = 'high') -> bool:
        """
        编码视频
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
            quality: 质量等级
        
        Returns:
            是否成功
        """
        self.logger.info(f"开始编码: {input_file}")
        self.logger.info(f"使用硬件加速: {self.hw_accel.value}")
        
        cmd = self.build_ffmpeg_command(input_file, output_file, quality)
        
        self.logger.debug(f"FFmpeg命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"编码完成: {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"编码失败: {e.stderr}")
            return False
    
    def benchmark(self, test_duration: int = 10) -> Dict[str, Any]:
        """
        性能基准测试
        
        Args:
            test_duration: 测试时长（秒）
        
        Returns:
            基准测试结果
        """
        self.logger.info(f"开始性能基准测试 (时长: {test_duration}秒)")
        
        import time
        import tempfile
        
        results = {
            'hw_accel': self.hw_accel.value,
            'test_duration': test_duration,
            'encoders': {}
        }
        
        # 创建测试视频（纯色）
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            test_video = Path(tmp.name)
        
        try:
            # 生成测试视频
            cmd = [
                self.ffmpeg_path,
                '-y',
                '-f', 'lavfi',
                '-i', f'color=c=blue:s=1280x720:d={test_duration}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                str(test_video)
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            # 测试当前硬件加速
            start_time = time.time()
            output_file = test_video.parent / f"test_output_{self.hw_accel.value}.mp4"
            
            success = self.encode(test_video, output_file, 'medium')
            
            if success:
                elapsed = time.time() - start_time
                fps = test_duration / elapsed
                
                results['encoders'][self.hw_accel.value] = {
                    'success': True,
                    'elapsed': elapsed,
                    'fps': fps,
                    'speedup': f"{fps:.1f}x realtime"
                }
                
                self.logger.info(f"基准测试结果: {fps:.1f} fps ({fps:.1f}x realtime)")
                
                # 清理输出文件
                if output_file.exists():
                    output_file.unlink()
            
        finally:
            # 清理测试视频
            if test_video.exists():
                test_video.unlink()
        
        return results


if __name__ == "__main__":
    # 测试代码
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    encoder = HardwareAcceleratedEncoder()
    
    print(f"\n检测到的硬件加速: {encoder.hw_accel.value}")
    
    # 显示编码器参数
    params = encoder.get_encoder_params('high')
    print(f"\n编码器参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # 运行基准测试
    print(f"\n运行基准测试...")
    benchmark_results = encoder.benchmark(test_duration=5)
    
    print(f"\n基准测试结果:")
    for encoder_name, result in benchmark_results['encoders'].items():
        if result['success']:
            print(f"  {encoder_name}: {result['fps']:.1f} fps ({result['speedup']})")
