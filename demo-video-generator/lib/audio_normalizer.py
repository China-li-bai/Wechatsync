#!/usr/bin/env python3
"""
音频标准化器 v1.0.0
使用EBU R128标准进行音频标准化

参考项目:
- ffmpeg-normalize: https://pypi.org/project/ffmpeg-normalize/
- Loudnorm-PRO: https://github.com/urscaviezel/Loudnorm-PRO

技术要点:
- EBU R128响度标准化
- 两遍处理（分析+应用）
- 音量标准化
- 降噪处理
"""

import os
import sys
import subprocess
import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
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


def get_ffprobe_path():
    """获取 ffprobe 可执行文件路径"""
    if HAS_IMAGEIO_FFMPEG:
        ffmpeg_dir = Path(imageio_ffmpeg.get_ffmpeg_exe()).parent
        ffprobe_path = ffmpeg_dir / 'ffprobe'
        if ffprobe_path.exists():
            return str(ffprobe_path)
    
    ffprobe_path = shutil.which('ffprobe')
    if ffprobe_path:
        return ffprobe_path
    
    return None


class AudioNormalizer:
    """音频标准化器 - 基于EBU R128标准"""
    
    def __init__(self, 
                 target_loudness: float = -16.0,
                 true_peak: float = -1.5,
                 lra: float = 11.0,
                 logger: Optional[logging.Logger] = None):
        """
        初始化音频标准化器
        
        Args:
            target_loudness: 目标积分响度，EBU R128标准
            true_peak: 目标真峰值
            lra: 目标响度范围
            logger: 日志记录器
        """
        self.target_loudness = target_loudness
        self.true_peak = true_peak
        self.lra = lra
        self.logger = logger or logging.getLogger(__name__)
        self.ffmpeg_path = get_ffmpeg_path()
        self.ffprobe_path = get_ffprobe_path()
    
    def normalize(self, input_file: Path, output_file: Path, 
                  apply_noise_reduction: bool = True) -> bool:
        """
        标准化音频文件
        
        Args:
            input_file: 输入音频文件
            output_file: 输出音频文件
            apply_noise_reduction: 是否应用降噪
        
        Returns:
            是否成功
        """
        self.logger.info(f"开始音频标准化: {input_file}")
        
        try:
            # 第一遍：分析音频
            loudnorm_stats = self._analyze_audio(input_file)
            
            if loudnorm_stats is None:
                self.logger.error("音频分析失败")
                return False
            
            # 第二遍：应用标准化
            if not self._apply_normalization(input_file, output_file, loudnorm_stats):
                self.logger.error("音频标准化失败")
                return False
            
            # 可选：应用降噪
            if apply_noise_reduction:
                if not self._apply_noise_reduction(output_file):
                    self.logger.warning("降噪处理失败，但标准化已完成")
            
            # 质量检查
            if not self._quality_check(output_file):
                self.logger.warning("音频质量检查未通过")
            
            self.logger.info(f"音频标准化完成: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"音频标准化异常: {e}")
            return False
    
    def _analyze_audio(self, input_file: Path) -> Optional[Dict[str, Any]]:
        """
        第一遍：分析音频特征
        
        Returns:
            loudnorm统计数据
        """
        self.logger.debug("第一遍：分析音频...")
        
        cmd = [
            self.ffmpeg_path,
            '-i', str(input_file),
            '-af', f'loudnorm=I={self.target_loudness}:TP={self.true_peak}:LRA={self.lra}:print_format=json',
            '-f', 'null',
            '-'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 从stderr中提取JSON
            json_match = re.search(r'\{.*\}', result.stderr, re.DOTALL)
            
            if json_match:
                loudnorm_stats = json.loads(json_match.group())
                self.logger.debug(f"音频分析结果: {loudnorm_stats}")
                return loudnorm_stats
            else:
                self.logger.error("无法解析音频分析结果")
                return None
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"音频分析失败: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return None
    
    def _apply_normalization(self, input_file: Path, output_file: Path,
                            loudnorm_stats: Dict[str, Any]) -> bool:
        """
        第二遍：应用标准化
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
            loudnorm_stats: loudnorm统计数据
        
        Returns:
            是否成功
        """
        self.logger.debug("第二遍：应用标准化...")
        
        # 构建loudnorm滤镜参数
        loudnorm_filter = (
            f"loudnorm=I={self.target_loudness}:TP={self.true_peak}:LRA={self.lra}:"
            f"measured_I={loudnorm_stats['input_i']}:"
            f"measured_TP={loudnorm_stats['input_tp']}:"
            f"measured_LRA={loudnorm_stats['input_lra']}:"
            f"measured_thresh={loudnorm_stats['input_thresh']}:"
            f"offset={loudnorm_stats['target_offset']}:"
            f"linear=true:print_format=summary"
        )
        
        # 根据输出文件扩展名选择编码器
        output_ext = output_file.suffix.lower()
        if output_ext in ['.mp3']:
            codec_args = ['-c:a', 'libmp3lame', '-b:a', '128k']
        elif output_ext in ['.aac', '.m4a']:
            codec_args = ['-c:a', 'aac', '-b:a', '128k']
        elif output_ext in ['.wav']:
            codec_args = ['-c:a', 'pcm_s16le']
        elif output_ext in ['.ogg']:
            codec_args = ['-c:a', 'libvorbis', '-b:a', '128k']
        else:
            # 默认使用AAC
            codec_args = ['-c:a', 'aac', '-b:a', '128k']
        
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(input_file),
            '-af', loudnorm_filter,
        ] + codec_args + [str(output_file)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.debug("音频标准化应用成功")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"音频标准化应用失败: {e.stderr}")
            return False
    
    def _apply_noise_reduction(self, audio_file: Path) -> bool:
        """
        应用降噪处理
        
        Args:
            audio_file: 音频文件
        
        Returns:
            是否成功
        """
        self.logger.debug("应用降噪处理...")
        
        temp_file = audio_file.parent / f"{audio_file.stem}_denoised{audio_file.suffix}"
        
        # 使用带通滤波降噪
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(audio_file),
            '-af', 'highpass=f=200,lowpass=f=3000',
            '-c:a', 'aac',
            '-b:a', '128k',
            str(temp_file)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # 替换原文件
            os.replace(str(temp_file), str(audio_file))
            
            self.logger.debug("降噪处理完成")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"降噪处理失败: {e.stderr}")
            if temp_file.exists():
                os.remove(temp_file)
            return False
    
    def _quality_check(self, audio_file: Path) -> bool:
        """
        音频质量检查
        
        Args:
            audio_file: 音频文件
        
        Returns:
            是否通过质量检查
        """
        self.logger.debug("执行音频质量检查...")
        
        # 检查文件是否存在
        if not audio_file.exists():
            self.logger.error("音频文件不存在")
            return False
        
        # 检查文件大小
        file_size = audio_file.stat().st_size
        if file_size < 1000:  # 小于1KB
            self.logger.error(f"音频文件过小: {file_size} bytes")
            return False
        
        # 使用ffprobe检查音频信息
        if self.ffprobe_path:
            cmd = [
                self.ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration,bit_rate',
                '-show_entries', 'stream=sample_rate,channels',
                '-of', 'json',
                str(audio_file)
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                info = json.loads(result.stdout)
                
                duration = float(info['format'].get('duration', 0))
                bit_rate = int(info['format'].get('bit_rate', 0))
                
                if duration < 0.5:
                    self.logger.warning(f"音频时长过短: {duration}秒")
                
                if bit_rate < 64000:
                    self.logger.warning(f"音频比特率过低: {bit_rate}bps")
                
                self.logger.info(f"音频质量检查通过: 时长={duration:.2f}秒, 比特率={bit_rate}bps")
                return True
                
            except Exception as e:
                self.logger.warning(f"音频信息获取失败: {e}")
                return True  # 如果无法获取信息，仍然返回True
        else:
            self.logger.warning("ffprobe不可用，跳过详细质量检查")
            return True
    
    def batch_normalize(self, input_files: list, output_dir: Path,
                       apply_noise_reduction: bool = True) -> Dict[str, bool]:
        """
        批量标准化音频文件
        
        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
            apply_noise_reduction: 是否应用降噪
        
        Returns:
            文件名到成功状态的映射
        """
        self.logger.info(f"开始批量音频标准化: {len(input_files)}个文件")
        
        results = {}
        
        for i, input_file in enumerate(input_files, 1):
            input_path = Path(input_file)
            output_file = output_dir / f"{input_path.stem}_normalized{input_path.suffix}"
            
            self.logger.info(f"处理文件 {i}/{len(input_files)}: {input_path.name}")
            
            success = self.normalize(input_path, output_file, apply_noise_reduction)
            results[input_path.name] = success
        
        # 统计结果
        success_count = sum(1 for v in results.values() if v)
        self.logger.info(f"批量标准化完成: {success_count}/{len(input_files)}成功")
        
        return results


class SimpleAudioNormalizer:
    """简化版音频标准化器 - 单遍处理"""
    
    def __init__(self, 
                 target_loudness: float = -16.0,
                 logger: Optional[logging.Logger] = None):
        """
        初始化简化版音频标准化器
        
        Args:
            target_loudness: 目标响度
            logger: 日志记录器
        """
        self.target_loudness = target_loudness
        self.logger = logger or logging.getLogger(__name__)
        self.ffmpeg_path = get_ffmpeg_path()
    
    def normalize(self, input_file: Path, output_file: Path) -> bool:
        """
        单遍标准化音频
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
        
        Returns:
            是否成功
        """
        self.logger.info(f"单遍音频标准化: {input_file}")
        
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(input_file),
            '-af', f'loudnorm=I={self.target_loudness}:TP=-1.5:LRA=11',
            '-c:a', 'aac',
            '-b:a', '128k',
            str(output_file)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"音频标准化完成: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"音频标准化失败: {e.stderr}")
            return False


if __name__ == "__main__":
    # 测试代码
    import sys
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 3:
        print("用法: python audio_normalizer.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    normalizer = AudioNormalizer()
    success = normalizer.normalize(input_file, output_file)
    
    if success:
        print("✅ 音频标准化成功")
    else:
        print("❌ 音频标准化失败")
        sys.exit(1)
