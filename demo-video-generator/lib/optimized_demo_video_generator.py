#!/usr/bin/env python3
"""
优化版演示视频生成器 v2.0.0
集成所有优化模块：
- 音频标准化（EBU R128）
- 硬件加速编码
- JSON Schema配置验证
- 智能等待策略
- 字幕同步优化
"""

import os
import sys
import yaml
import subprocess
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil

sys.path.insert(0, str(Path(__file__).parent))

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

from audio_normalizer import AudioNormalizer
from hardware_encoder import HardwareAcceleratedEncoder
from config_schema_validator import ConfigSchemaValidator
from video_recorder import VideoRecorder
from thumbnail_generator import CodeBasedThumbnailGenerator


class OptimizedDemoVideoGenerator:
    """优化版演示视频生成器 v2.0.0"""
    
    def __init__(self, config_file: str, log_level: str = 'INFO'):
        self.logger = self._setup_logger(log_level)
        
        # 使用JSON Schema验证配置
        self._validate_config_with_schema(config_file)
        
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 应用默认值
        self._apply_config_defaults()
        
        # 初始化输出目录
        project_config = self.config['project']
        self.output_dir = Path(project_config.get('output_dir', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化优化模块
        self.audio_normalizer = AudioNormalizer(logger=self.logger)
        self.hw_encoder = HardwareAcceleratedEncoder(logger=self.logger)
        
        self.logger.info(f"硬件加速: {self.hw_encoder.hw_accel.value}")
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('OptimizedDemoVideoGenerator')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _validate_config_with_schema(self, config_file: str):
        """使用JSON Schema验证配置"""
        validator = ConfigSchemaValidator(self.logger)
        success, errors = validator.validate_file(Path(config_file))
        
        if not success:
            error_msg = "配置验证失败:\n"
            for error in errors:
                error_msg += f"  - {error.get('path', 'N/A')}: {error.get('message', 'N/A')}\n"
            raise ValueError(error_msg)
        
        self.logger.info("✅ 配置验证通过")
    
    def _apply_config_defaults(self):
        """应用配置默认值"""
        validator = ConfigSchemaValidator(self.logger)
        self.config = validator.apply_defaults(self.config)
    
    def generate(self, auto_record: bool = True) -> Optional[Path]:
        """生成优化版演示视频"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Optimized Demo Video Generator v2.0.0")
        self.logger.info("=" * 60)
        
        scenes = self.config['scenes']
        project_config = self.config['project']
        
        try:
            # 步骤1: 生成语音 (15%)
            self._print_progress("步骤1: 生成语音", 15)
            voice_files, durations = self._generate_voiceovers(scenes)
            
            # 步骤2: 音频标准化 (10%) - 新增优化
            self._print_progress("步骤2: 音频标准化", 10)
            normalized_files = self._normalize_audio_files(voice_files)
            
            # 步骤3: 合并音频 (5%)
            self._print_progress("步骤3: 合并音频", 5)
            audio_file = self._merge_audio(normalized_files)
            
            # 步骤4: 生成字幕 (10%)
            self._print_progress("步骤4: 生成字幕", 10)
            subtitle_file = self._generate_subtitles(scenes, durations)
            
            # 步骤5: 录制视频 (35%)
            self._print_progress("步骤5: 录制视频", 35)
            video_file = self._record_video(project_config, scenes, durations, auto_record)
            
            if video_file is None:
                return None
            
            # 步骤6: 合成视频 (20%) - 使用硬件加速
            self._print_progress("步骤6: 合成视频（硬件加速）", 20)
            output_file = self._compose_video_optimized(video_file, audio_file, subtitle_file)
            
            # 步骤7: 生成封面 (5%)
            self._print_progress("步骤7: 生成封面", 5)
            thumbnail_path = self._generate_thumbnail()
            
            # 完成
            self._print_completion(output_file, thumbnail_path, subtitle_file, audio_file)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"生成失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _generate_voiceovers(self, scenes: List[Dict]) -> tuple:
        """生成语音文件"""
        voice_config = self.config['voice']
        voice_files = []
        durations = []
        
        edge_tts = self._find_edge_tts()
        
        for i, scene in enumerate(scenes, 1):
            output_file = self.output_dir / f"voice-{i:02d}.mp3"
            voice_files.append(output_file)
            
            self.logger.info(f"生成语音 {i}/{len(scenes)}: {scene['name']}")
            
            voice = f"{voice_config['language']}-{voice_config['voice_name']}"
            
            cmd = [
                edge_tts,
                '--text', scene['text'],
                '--voice', voice,
                '--write-media', str(output_file)
            ]
            
            if voice_config.get('speed', 1.0) != 1.0:
                speed = voice_config['speed']
                rate = f"+{int((speed - 1) * 100)}%" if speed > 1 else f"-{int((1 - speed) * 100)}%"
                cmd.extend(['--rate', rate])
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            duration = self._get_audio_duration(output_file)
            durations.append(duration)
        
        total_duration = sum(durations)
        self.logger.info(f"总语音时长: {total_duration:.2f}秒")
        
        return voice_files, durations
    
    def _normalize_audio_files(self, voice_files: List[Path]) -> List[Path]:
        """标准化音频文件"""
        normalized_files = []
        
        for i, voice_file in enumerate(voice_files, 1):
            normalized_file = self.output_dir / f"voice-{i:02d}_normalized.mp3"
            normalized_files.append(normalized_file)
            
            self.logger.info(f"标准化音频 {i}/{len(voice_files)}")
            
            success = self.audio_normalizer.normalize(
                voice_file,
                normalized_file,
                apply_noise_reduction=True
            )
            
            if not success:
                self.logger.warning(f"音频标准化失败，使用原始文件: {voice_file}")
                normalized_files[-1] = voice_file
        
        return normalized_files
    
    def _merge_audio(self, audio_files: List[Path]) -> Path:
        """合并音频文件"""
        output_file = self.output_dir / "voiceover.aac"
        
        # 创建文件列表（使用绝对路径）
        list_file = self.output_dir / "audio_list.txt"
        with open(list_file, 'w') as f:
            for audio_file in audio_files:
                # 确保使用绝对路径
                abs_path = Path(audio_file).resolve()
                f.write(f"file '{abs_path}'\n")
        
        # 使用FFmpeg合并
        ffmpeg_path = self._get_ffmpeg_path()
        
        cmd = [
            ffmpeg_path,
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c:a', 'aac',
            '-b:a', '128k',
            str(output_file)
        ]
        
        # 不使用capture_output，直接显示输出
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"音频合并失败: {result.stderr}")
            raise RuntimeError(f"音频合并失败: {result.stderr}")
        
        self.logger.info(f"音频合并完成: {output_file}")
        return output_file
    
    def _generate_subtitles(self, scenes: List[Dict], durations: List[float]) -> Path:
        """生成字幕文件"""
        subtitle_file = self.output_dir / "subtitles.srt"
        
        subtitles = [scene.get('subtitle', '') for scene in scenes]
        
        current_time = 0.0
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            for i, (duration, subtitle) in enumerate(zip(durations, subtitles), 1):
                if not subtitle:
                    continue
                
                start_time = current_time
                end_time = current_time + duration
                
                f.write(f"{i}\n")
                f.write(f"{self._seconds_to_srt_time(start_time)} --> {self._seconds_to_srt_time(end_time)}\n")
                f.write(f"{subtitle}\n\n")
                
                current_time += duration
        
        self.logger.info(f"字幕生成完成: {subtitle_file}")
        return subtitle_file
    
    def _record_video(self, project_config: Dict, scenes: List[Dict], 
                     durations: List[float], auto_record: bool) -> Optional[Path]:
        """录制视频"""
        video_file = self.output_dir / "recording.webm"
        
        recording_config = self.config.get('recording', {})
        
        if auto_record and recording_config.get('enabled', False):
            self.logger.info("开始智能录制...")
            
            recorder = VideoRecorder(
                project_config['url'],
                video_file,
                self.logger
            )
            
            actions = self._build_recording_actions(scenes)
            success = recorder.auto_record(durations, actions)
            
            if not success:
                self.logger.error("自动录制失败")
                return None
        else:
            self.logger.warning("需要手动录制视频")
            self.logger.warning(f"视频文件路径: {video_file}")
            
            if not video_file.exists():
                self.logger.error("视频文件不存在")
                return None
        
        return video_file
    
    def _compose_video_optimized(self, video_file: Path, audio_file: Path, 
                                 subtitle_file: Path) -> Path:
        """使用硬件加速合成视频"""
        project_config = self.config['project']
        output_name = project_config.get('output_name', 'demo-video')
        video_config = self.config.get('video', {})
        format_ext = video_config.get('format', 'mp4')
        
        output_file = self.output_dir / f"{output_name}.{format_ext}"
        
        # 使用硬件加速编码器
        cmd = self.hw_encoder.build_ffmpeg_command(
            video_file,
            output_file,
            quality=video_config.get('quality', 'high')
        )
        
        # 添加音频输入
        audio_index = cmd.index('-i') + 2
        cmd.insert(audio_index, '-i')
        cmd.insert(audio_index + 1, str(audio_file))
        
        # 添加字幕
        subtitle_config = self.config.get('subtitle', {})
        if subtitle_config.get('enabled', True):
            subtitle_filter = self._build_subtitle_filter(subtitle_file, subtitle_config)
            cmd.extend(['-vf', subtitle_filter])
        
        # 添加音频编码
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest'
        ])
        
        self.logger.info(f"使用硬件加速: {self.hw_encoder.hw_accel.value}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info(f"视频合成完成: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            self.logger.error(f"视频合成失败: {e.stderr}")
            raise
    
    def _build_subtitle_filter(self, subtitle_file: Path, subtitle_config: Dict) -> str:
        """构建字幕滤镜"""
        font = subtitle_config.get('font', 'PingFang SC')
        font_size = subtitle_config.get('font_size', 24)
        color = subtitle_config.get('color', '&HFFFFFF')
        outline_color = subtitle_config.get('outline_color', '&H000000')
        back_color = subtitle_config.get('background_color', '&H80000000')
        outline = subtitle_config.get('outline', 2)
        shadow = subtitle_config.get('shadow', 1)
        
        force_style = (
            f"FontName={font},"
            f"FontSize={font_size},"
            f"PrimaryColour={color},"
            f"OutlineColour={outline_color},"
            f"BackColour={back_color},"
            f"BorderStyle=3,"
            f"Outline={outline},"
            f"Shadow={shadow}"
        )
        
        return f"subtitles={subtitle_file}:force_style='{force_style}'"
    
    def _generate_thumbnail(self) -> Optional[Path]:
        """生成视频封面"""
        thumbnail_config = self.config.get('thumbnail', {})
        
        if not thumbnail_config.get('enabled', True):
            self.logger.info("封面生成已禁用")
            return None
        
        try:
            generator = CodeBasedThumbnailGenerator(
                template_dir=thumbnail_config.get('template_dir', 'templates/thumbnails'),
                output_dir=self.output_dir,
                logger=self.logger
            )
            
            project_config = self.config['project']
            
            thumbnail_data = {
                'title': project_config.get('title', project_config.get('name', 'Demo Video')),
                'subtitle': project_config.get('description', ''),
                'template': thumbnail_config.get('template', 'default.html'),
                'background': thumbnail_config.get('background'),
                'font_size': thumbnail_config.get('font_size'),
                'text_color': thumbnail_config.get('text_color'),
                'badge': thumbnail_config.get('badge'),
                'brand': thumbnail_config.get('brand'),
                'author': thumbnail_config.get('author'),
                'accent_color': thumbnail_config.get('accent_color')
            }
            
            thumbnail_path = generator.generate(thumbnail_data)
            
            if thumbnail_path:
                self.logger.info(f"封面生成完成: {thumbnail_path}")
            
            return thumbnail_path
            
        except Exception as e:
            self.logger.warning(f"封面生成失败: {e}")
            return None
    
    def _build_recording_actions(self, scenes: List[Dict]) -> List[Dict]:
        """构建录制动作列表"""
        actions = []
        
        for scene in scenes:
            action = {
                'type': scene.get('action', 'screenshot'),
                'selector': scene.get('selector'),
                'scroll_distance': scene.get('scroll_distance', 300)
            }
            actions.append(action)
        
        return actions
    
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
    
    def _find_edge_tts(self) -> str:
        """查找edge-tts可执行文件"""
        possible_paths = [
            shutil.which('edge-tts'),
            Path.home() / '.local' / 'bin' / 'edge-tts',
            '/usr/local/bin/edge-tts',
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return str(path)
        
        raise FileNotFoundError("未找到 edge-tts，请运行: pipx install edge-tts")
    
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
    
    def _print_progress(self, message: str, percentage: int):
        """打印进度"""
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        self.logger.info(f"\n{message}")
        self.logger.info(f"[{bar}] {percentage}%")
    
    def _print_completion(self, output_file: Path, thumbnail_path: Optional[Path],
                         subtitle_file: Path, audio_file: Path):
        """打印完成信息"""
        self.logger.info("=" * 60)
        self.logger.info("✅ 优化版演示视频生成完成！")
        self.logger.info("=" * 60)
        self.logger.info(f"📁 输出目录: {self.output_dir}")
        self.logger.info(f"🎬 视频文件: {output_file}")
        
        if thumbnail_path:
            self.logger.info(f"🖼️  封面文件: {thumbnail_path}")
        
        self.logger.info(f"📝 字幕文件: {subtitle_file}")
        self.logger.info(f"🎵 音频文件: {audio_file}")
        
        # 显示优化效果
        self.logger.info("\n📊 优化效果:")
        self.logger.info(f"   - 音频标准化: EBU R128标准")
        self.logger.info(f"   - 硬件加速: {self.hw_encoder.hw_accel.value}")
        self.logger.info(f"   - 配置验证: JSON Schema")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python optimized_demo_video_generator.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    generator = OptimizedDemoVideoGenerator(config_file)
    output_file = generator.generate()
    
    if output_file:
        print(f"\n✅ 视频生成成功: {output_file}")
        sys.exit(0)
    else:
        print("\n❌ 视频生成失败")
        sys.exit(1)
