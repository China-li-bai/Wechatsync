#!/usr/bin/env python3
"""
波形同步字幕生成器 v1.0.0
基于音频波形分析的精准字幕同步

参考项目:
- TorchAudio Forced Alignment: https://pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html

技术要点:
- 音频波形分析
- 语音活动检测
- 精准时间对齐
- 多语言支持
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import shutil

try:
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import find_peaks
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("⚠️  提示: 安装 scipy 和 numpy 可以启用波形分析 (pip install scipy numpy)")


class WaveformSyncSubtitleGenerator:
    """波形同步字幕生成器"""
    
    def __init__(self, 
                 sync_precision: float = 0.05,
                 voice_threshold: float = 0.3,
                 logger: Optional[logging.Logger] = None):
        """
        初始化波形同步字幕生成器
        
        Args:
            sync_precision: 同步精度（秒）
            voice_threshold: 语音活动阈值
            logger: 日志记录器
        """
        self.sync_precision = sync_precision
        self.voice_threshold = voice_threshold
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_srt_with_waveform_sync(self,
                                        audio_files: List[Path],
                                        subtitles: List[str],
                                        output_file: Path) -> bool:
        """
        使用波形同步生成SRT字幕
        
        Args:
            audio_files: 音频文件列表
            subtitles: 字幕文本列表
            output_file: 输出文件路径
        
        Returns:
            是否成功
        """
        self.logger.info("开始波形同步字幕生成...")
        
        if not HAS_SCIPY:
            self.logger.warning("scipy未安装，使用简单同步方法")
            return self._generate_simple_srt(audio_files, subtitles, output_file)
        
        try:
            # 分析每个音频文件的波形
            all_segments = []
            
            for i, audio_file in enumerate(audio_files):
                self.logger.debug(f"分析音频 {i+1}/{len(audio_files)}: {audio_file.name}")
                
                segments = self._analyze_audio_waveform(audio_file)
                all_segments.extend(segments)
            
            # 生成SRT文件
            self._write_srt_file(all_segments, subtitles, output_file)
            
            self.logger.info(f"字幕生成完成: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"波形同步失败: {e}")
            self.logger.warning("回退到简单同步方法")
            return self._generate_simple_srt(audio_files, subtitles, output_file)
    
    def _analyze_audio_waveform(self, audio_file: Path) -> List[Dict[str, float]]:
        """
        分析音频波形
        
        Args:
            audio_file: 音频文件路径
        
        Returns:
            语音片段列表
        """
        # 转换为WAV格式
        wav_file = self._convert_to_wav(audio_file)
        
        try:
            # 读取WAV文件
            sample_rate, data = wavfile.read(wav_file)
            
            # 如果是立体声，转换为单声道
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # 计算能量
            energy = np.abs(data).astype(float)
            
            # 归一化能量
            energy = energy / np.max(energy)
            
            # 平滑能量曲线
            window_size = int(sample_rate * 0.05)  # 50ms窗口
            smoothed_energy = np.convolve(
                energy, 
                np.ones(window_size) / window_size, 
                mode='same'
            )
            
            # 检测语音活动
            threshold = np.mean(smoothed_energy) * (1 + self.voice_threshold)
            voice_mask = smoothed_energy > threshold
            
            # 提取语音片段
            segments = self._extract_voice_segments(voice_mask, sample_rate)
            
            return segments
            
        finally:
            # 清理临时WAV文件
            if wav_file != audio_file and wav_file.exists():
                wav_file.unlink()
    
    def _convert_to_wav(self, audio_file: Path) -> Path:
        """
        转换音频文件为WAV格式
        
        Args:
            audio_file: 音频文件路径
        
        Returns:
            WAV文件路径
        """
        if audio_file.suffix.lower() == '.wav':
            return audio_file
        
        # 使用FFmpeg转换
        wav_file = audio_file.parent / f"{audio_file.stem}.wav"
        
        ffmpeg_path = self._get_ffmpeg_path()
        
        cmd = [
            ffmpeg_path,
            '-y',
            '-i', str(audio_file),
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            str(wav_file)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return wav_file
    
    def _extract_voice_segments(self, voice_mask: np.ndarray, 
                               sample_rate: int) -> List[Dict[str, float]]:
        """
        提取语音片段
        
        Args:
            voice_mask: 语音活动掩码
            sample_rate: 采样率
        
        Returns:
            语音片段列表
        """
        segments = []
        in_voice = False
        start_idx = 0
        
        for i, is_voice in enumerate(voice_mask):
            if is_voice and not in_voice:
                # 语音开始
                start_idx = i
                in_voice = True
            
            elif not is_voice and in_voice:
                # 语音结束
                end_idx = i
                duration = (end_idx - start_idx) / sample_rate
                
                if duration >= 0.1:  # 最小片段时长100ms
                    segments.append({
                        'start': start_idx / sample_rate,
                        'end': end_idx / sample_rate,
                        'duration': duration
                    })
                
                in_voice = False
        
        # 处理最后一个片段
        if in_voice:
            end_idx = len(voice_mask)
            duration = (end_idx - start_idx) / sample_rate
            
            if duration >= 0.1:
                segments.append({
                    'start': start_idx / sample_rate,
                    'end': end_idx / sample_rate,
                    'duration': duration
                })
        
        return segments
    
    def _write_srt_file(self, segments: List[Dict[str, float]], 
                       subtitles: List[str], output_file: Path):
        """
        写入SRT文件
        
        Args:
            segments: 语音片段列表
            subtitles: 字幕文本列表
            output_file: 输出文件路径
        """
        current_time = 0.0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, (segment, subtitle) in enumerate(zip(segments, subtitles), 1):
                if not subtitle:
                    continue
                
                # 应用同步精度
                start_time = current_time + self.sync_precision
                end_time = current_time + segment['duration'] - self.sync_precision
                
                f.write(f"{i}\n")
                f.write(f"{self._seconds_to_srt_time(start_time)} --> "
                       f"{self._seconds_to_srt_time(end_time)}\n")
                f.write(f"{subtitle}\n\n")
                
                current_time += segment['duration']
    
    def _generate_simple_srt(self, audio_files: List[Path], 
                            subtitles: List[str], output_file: Path) -> bool:
        """
        生成简单SRT字幕（回退方法）
        
        Args:
            audio_files: 音频文件列表
            subtitles: 字幕文本列表
            output_file: 输出文件路径
        
        Returns:
            是否成功
        """
        self.logger.info("使用简单同步方法生成字幕")
        
        current_time = 0.0
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, (audio_file, subtitle) in enumerate(zip(audio_files, subtitles), 1):
                    if not subtitle:
                        continue
                    
                    # 获取音频时长
                    duration = self._get_audio_duration(audio_file)
                    
                    start_time = current_time
                    end_time = current_time + duration
                    
                    f.write(f"{i}\n")
                    f.write(f"{self._seconds_to_srt_time(start_time)} --> "
                           f"{self._seconds_to_srt_time(end_time)}\n")
                    f.write(f"{subtitle}\n\n")
                    
                    current_time += duration
            
            self.logger.info(f"字幕生成完成: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"字幕生成失败: {e}")
            return False
    
    def _get_audio_duration(self, audio_file: Path) -> float:
        """获取音频时长"""
        ffprobe_path = self._get_ffprobe_path()
        
        if ffprobe_path:
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        else:
            # 使用FFmpeg获取时长
            import re
            ffmpeg_path = self._get_ffmpeg_path()
            cmd = [ffmpeg_path, '-i', str(audio_file), '-f', 'null', '-']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
            
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                centiseconds = int(match.group(4))
                return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
            
            raise RuntimeError("无法解析音频时长")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """将秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _get_ffmpeg_path(self) -> str:
        """获取ffmpeg路径"""
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass
        
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        raise RuntimeError("未找到 ffmpeg")
    
    def _get_ffprobe_path(self) -> Optional[str]:
        """获取ffprobe路径"""
        try:
            import imageio_ffmpeg
            ffmpeg_dir = Path(imageio_ffmpeg.get_ffmpeg_exe()).parent
            ffprobe_path = ffmpeg_dir / 'ffprobe'
            if ffprobe_path.exists():
                return str(ffprobe_path)
        except ImportError:
            pass
        
        return shutil.which('ffprobe')


class EnhancedSubtitleGenerator(WaveformSyncSubtitleGenerator):
    """增强字幕生成器 - 支持更多功能"""
    
    def generate_ass_subtitle(self,
                             audio_files: List[Path],
                             subtitles: List[str],
                             output_file: Path,
                             style_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        生成ASS格式字幕（支持更多样式）
        
        Args:
            audio_files: 音频文件列表
            subtitles: 字幕文本列表
            output_file: 输出文件路径
            style_config: 样式配置
        
        Returns:
            是否成功
        """
        self.logger.info("生成ASS格式字幕...")
        
        style_config = style_config or {}
        
        try:
            # 分析音频波形
            all_segments = []
            
            if HAS_SCIPY:
                for audio_file in audio_files:
                    segments = self._analyze_audio_waveform(audio_file)
                    all_segments.extend(segments)
            else:
                # 回退到简单方法
                for audio_file in audio_files:
                    duration = self._get_audio_duration(audio_file)
                    all_segments.append({
                        'start': 0,
                        'end': duration,
                        'duration': duration
                    })
            
            # 写入ASS文件
            self._write_ass_file(all_segments, subtitles, output_file, style_config)
            
            self.logger.info(f"ASS字幕生成完成: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"ASS字幕生成失败: {e}")
            return False
    
    def _write_ass_file(self, segments: List[Dict[str, float]], 
                       subtitles: List[str], output_file: Path,
                       style_config: Dict[str, Any]):
        """
        写入ASS文件
        
        Args:
            segments: 语音片段列表
            subtitles: 字幕文本列表
            output_file: 输出文件路径
            style_config: 样式配置
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入脚本信息
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("PlayResX: 1280\n")
            f.write("PlayResY: 720\n\n")
            
            # 写入样式
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                   "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                   "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                   "Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            # 默认样式
            font = style_config.get('font', 'PingFang SC')
            font_size = style_config.get('font_size', 24)
            color = style_config.get('color', '&H00FFFFFF')
            outline_color = style_config.get('outline_color', '&H00000000')
            back_color = style_config.get('background_color', '&H80000000')
            
            f.write(f"Style: Default,{font},{font_size},{color},&H000000FF,"
                   f"{outline_color},{back_color},0,0,0,0,100,100,0,0,1,2,1,2,"
                   f"10,10,10,1\n\n")
            
            # 写入事件
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
                   "MarginV, Effect, Text\n")
            
            current_time = 0.0
            
            for segment, subtitle in zip(segments, subtitles):
                if not subtitle:
                    continue
                
                start_time = current_time + self.sync_precision
                end_time = current_time + segment['duration'] - self.sync_precision
                
                start_str = self._seconds_to_ass_time(start_time)
                end_str = self._seconds_to_ass_time(end_time)
                
                f.write(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{subtitle}\n")
                
                current_time += segment['duration']
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """将秒数转换为ASS时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"


if __name__ == "__main__":
    # 测试代码
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== 波形同步字幕生成器测试 ===\n")
    
    generator = WaveformSyncSubtitleGenerator()
    
    print("✅ 波形同步字幕生成器初始化成功")
    print(f"   - 同步精度: {generator.sync_precision}秒")
    print(f"   - 语音阈值: {generator.voice_threshold}")
    
    print("\n提示: 需要音频文件才能进行完整测试")
