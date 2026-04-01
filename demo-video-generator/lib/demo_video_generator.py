#!/usr/bin/env python3
"""
Demo Video Generator - 核心库 v1.1.0
自动生成产品演示视频的工具
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

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️  提示: 安装 tqdm 可以显示进度条 (pip install tqdm)")

try:
    import imageio_ffmpeg
    HAS_IMAGEIO_FFMPEG = True
except ImportError:
    HAS_IMAGEIO_FFMPEG = False

from video_recorder import VideoRecorder
from config_validator import ConfigValidator
from thumbnail_generator import CodeBasedThumbnailGenerator


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
        ffprobe_path = ffmpeg_dir / 'ffprobe.exe'
        if ffprobe_path.exists():
            return str(ffprobe_path)
    
    ffprobe_path = shutil.which('ffprobe')
    if ffprobe_path:
        return ffprobe_path
    
    return None


class DemoVideoGeneratorError(Exception):
    """演示视频生成器错误"""
    pass


class ConfigParser:
    """配置文件解析器"""
    
    def __init__(self, config_file: str, logger: Optional[logging.Logger] = None):
        self.config_file = Path(config_file)
        self.logger = logger or logging.getLogger(__name__)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        self.logger.info(f"加载配置文件: {self.config_file}")
            
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict[str, Any]):
        """验证配置文件"""
        validator = ConfigValidator(self.logger)
        if not validator.validate(config):
            errors = validator.get_errors()
            error_msg = "\n".join(errors)
            raise DemoVideoGeneratorError(f"配置文件验证失败:\n{error_msg}")
                
    def get_project_config(self) -> Dict[str, Any]:
        return self.config['project']
    
    def get_voice_config(self) -> Dict[str, Any]:
        return self.config['voice']
    
    def get_scenes(self) -> List[Dict[str, Any]]:
        return self.config['scenes']
    
    def get_video_config(self) -> Dict[str, Any]:
        return self.config.get('video', {})
    
    def get_subtitle_config(self) -> Dict[str, Any]:
        return self.config.get('subtitle', {})
    
    def get_recording_config(self) -> Dict[str, Any]:
        return self.config.get('recording', {})


class VoiceoverGenerator:
    """语音生成器"""
    
    def __init__(self, voice_config: Dict[str, Any], output_dir: Path, logger: Optional[logging.Logger] = None):
        self.language = voice_config.get('language', 'zh-CN')
        self.voice_name = voice_config.get('voice_name', 'XiaoxiaoNeural')
        self.speed = voice_config.get('speed', 1.0)
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger(__name__)
        self.edge_tts = self._find_edge_tts()
        
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
    
    def generate(self, text: str, output_file: Path) -> float:
        """生成单个语音文件，返回时长（秒）"""
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
            self.logger.debug(f"生成语音: {output_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"生成语音失败: {e.stderr}")
            raise DemoVideoGeneratorError(f"生成语音失败: {e.stderr}")
        
        duration = self._get_duration(output_file)
        return duration
    
    def batch_generate(self, scenes: List[Dict[str, Any]], show_progress: bool = True) -> List[float]:
        """批量生成语音，返回时长列表"""
        durations = []
        
        if show_progress and HAS_TQDM:
            scenes_iter = tqdm(enumerate(scenes, 1), total=len(scenes), desc="生成语音")
        else:
            scenes_iter = enumerate(scenes, 1)
        
        for i, scene in scenes_iter:
            output_file = self.output_dir / f"voice-{i:02d}.mp3"
            
            if not HAS_TQDM or not show_progress:
                print(f"🎙️ 生成场景 {i:02d} 语音...")
            
            try:
                duration = self.generate(scene['text'], output_file)
                durations.append(duration)
                
                if not HAS_TQDM or not show_progress:
                    print(f"  时长: {duration:.3f}s")
            except Exception as e:
                self.logger.error(f"场景 {i} 语音生成失败: {e}")
                raise
        
        return durations
    
    def _get_duration(self, audio_file: Path) -> float:
        """获取音频时长"""
        ffprobe_path = get_ffprobe_path()
        
        if ffprobe_path:
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_file)
            ]
        else:
            ffmpeg_path = get_ffmpeg_path()
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
                import re
                match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3))
                    centiseconds = int(match.group(4))
                    return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                else:
                    raise DemoVideoGeneratorError("无法解析音频时长")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"获取音频时长失败: {e.stderr}")
            raise DemoVideoGeneratorError(f"获取音频时长失败: {e.stderr}")


class SubtitleGenerator:
    """字幕生成器"""
    
    def __init__(self, subtitle_config: Dict[str, Any], output_dir: Path, logger: Optional[logging.Logger] = None):
        self.config = subtitle_config
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger(__name__)
        
    def generate_srt(self, durations: List[float], subtitles: List[str], output_file: Path):
        """生成SRT字幕文件"""
        current_time = 0.0
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, (duration, subtitle) in enumerate(zip(durations, subtitles), 1):
                    start_time = current_time
                    end_time = current_time + duration
                    
                    f.write(f"{i}\n")
                    f.write(f"{self._seconds_to_srt_time(start_time)} --> {self._seconds_to_srt_time(end_time)}\n")
                    f.write(f"{subtitle}\n\n")
                    
                    current_time = end_time
            
            self.logger.info(f"字幕文件已生成: {output_file}")
        except Exception as e:
            self.logger.error(f"生成字幕失败: {e}")
            raise DemoVideoGeneratorError(f"生成字幕失败: {e}")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """将秒数转换为SRT时间格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class VideoComposer:
    """视频合成器"""
    
    def __init__(self, video_config: Dict[str, Any], subtitle_config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.video_config = video_config
        self.subtitle_config = subtitle_config
        self.logger = logger or logging.getLogger(__name__)
        
    def compose(self, video_file: Path, audio_file: Path, subtitle_file: Path, output_file: Path):
        """合成最终视频"""
        self.logger.info(f"合成视频: {output_file}")
        
        ffmpeg_path = get_ffmpeg_path()
        
        cmd = [
            ffmpeg_path,
            '-y',
            '-i', str(video_file),
            '-i', str(audio_file),
        ]
        
        if self.subtitle_config.get('enabled', True):
            subtitle_filter = self._build_subtitle_filter(subtitle_file)
            cmd.extend(['-vf', subtitle_filter])
        
        cmd.extend([
            '-c:v', self.video_config.get('codec', 'libx264'),
            '-c:a', self.video_config.get('audio', {}).get('codec', 'aac'),
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            str(output_file)
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info(f"视频合成完成: {output_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"视频合成失败: {e.stderr}")
            raise DemoVideoGeneratorError(f"视频合成失败: {e.stderr}")
    
    def _build_subtitle_filter(self, subtitle_file: Path) -> str:
        """构建字幕滤镜"""
        font = self.subtitle_config.get('font', 'PingFang SC')
        font_size = self.subtitle_config.get('font_size', 24)
        color = self.subtitle_config.get('color', '&HFFFFFF')
        outline_color = self.subtitle_config.get('outline_color', '&H000000')
        back_color = self.subtitle_config.get('background_color', '&H80000000')
        outline = self.subtitle_config.get('outline', 2)
        shadow = self.subtitle_config.get('shadow', 1)
        
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


class DemoVideoGenerator:
    """演示视频生成器主类 v1.1.0"""
    
    def __init__(self, config_file: str, log_level: str = 'INFO'):
        self.logger = self._setup_logger(log_level)
        
        self.config_parser = ConfigParser(config_file, self.logger)
        
        project_config = self.config_parser.get_project_config()
        self.output_dir = Path(project_config.get('output_dir', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.voiceover_gen = VoiceoverGenerator(
            self.config_parser.get_voice_config(),
            self.output_dir,
            self.logger
        )
        
        self.subtitle_gen = SubtitleGenerator(
            self.config_parser.get_subtitle_config(),
            self.output_dir,
            self.logger
        )
        
        self.video_composer = VideoComposer(
            self.config_parser.get_video_config(),
            self.config_parser.get_subtitle_config(),
            self.logger
        )
        
        self.recording_config = self.config_parser.get_recording_config()
        
        self.thumbnail_config = self.config.get('thumbnail', {})
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('DemoVideoGenerator')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
        
        return logger
    
    def generate(self, auto_record: bool = True) -> Path:
        """生成演示视频"""
        self.logger.info("=" * 50)
        self.logger.info("🎬 Demo Video Generator v1.1.0")
        self.logger.info("=" * 50)
        
        scenes = self.config_parser.get_scenes()
        project_config = self.config_parser.get_project_config()
        
        try:
            # 步骤1: 生成语音 (20%)
            self._print_progress("步骤1: 生成语音", 20)
            durations = self.voiceover_gen.batch_generate(scenes)
            total_duration = sum(durations)
            self.logger.info(f"总语音时长: {total_duration:.3f}s")
            
            # 步骤2: 合并语音 (10%)
            self._print_progress("步骤2: 合并语音", 10)
            audio_file = self._merge_audio(len(scenes))
            self.logger.info(f"语音合并完成: {audio_file}")
            
            # 步骤3: 生成字幕 (10%)
            self._print_progress("步骤3: 生成字幕", 10)
            subtitles = [scene.get('subtitle', '') for scene in scenes]
            subtitle_file = self.output_dir / "subtitles.srt"
            self.subtitle_gen.generate_srt(durations, subtitles, subtitle_file)
            
            # 步骤4: 录制视频 (40%)
            self._print_progress("步骤4: 录制视频", 40)
            video_file = self.output_dir / "recording.webm"
            
            if auto_record and self.recording_config.get('enabled', False):
                self.logger.info("开始自动录制...")
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
                self.logger.warning("需要手动录制视频:")
                self.logger.warning(f"  1. 打开浏览器: agent-browser open '{project_config['url']}'")
                self.logger.warning(f"  2. 开始录制: agent-browser record start '{video_file}'")
                self.logger.warning(f"  3. 执行操作并等待相应时长")
                self.logger.warning(f"  4. 停止录制: agent-browser record stop")
                
                if not video_file.exists():
                    self.logger.error("视频文件不存在，请先录制视频")
                    return None
            
            # 步骤6: 合成视频 (15%)
            self._print_progress("步骤6: 合成视频", 15)
            self.video_composer.compose(
                video_file,
                audio_file,
                subtitle_file,
                self.output_file
            )
            
            # 步骤7: 生成封面 (5%)
            self._print_progress("步骤7: 生成封面", 5)
            thumbnail_path = self._generate_thumbnail()
            
            self.logger.info("=" * 50)
            self.logger.info("✅ 演示视频生成完成！")
            self.logger.info("=" * 50)
            self.logger.info(f"📁 输出目录: {self.output_dir}")
            self.logger.info(f"🎬 视频文件: {self.output_file}")
            if thumbnail_path:
                self.logger.info(f"🖼️  封面文件: {thumbnail_path}")
            self.logger.info(f"📝 字幕文件: {subtitle_file}")
            self.logger.info(f"🎵 音频文件: {audio_file}")
            
            return self.output_file
            
        except Exception as e:
            self.logger.error(f"生成失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _generate_thumbnail(self):
        """
        生成视频封面
        
        Returns:
            生成的封面文件路径，失败返回None
        """
        if not self.thumbnail_config.get('enabled', True):
            self.logger.info("封面生成已禁用")
            return None
        
        try:
            self.logger.info("开始生成封面...")
            
            generator = CodeBasedThumbnailGenerator(
                template_dir=self.thumbnail_config.get('template_dir', 'templates/thumbnails'),
                output_dir=self.output_dir,
                logger=self.logger
            )
            
            project_config = self.config_parser.get_project_config()
            
            thumbnail_data = {
                'title': project_config.get('title', 'Demo Video'),
                'subtitle': project_config.get('description', ''),
                'template': self.thumbnail_config.get('template', 'default.html'),
                'background': self.thumbnail_config.get('background'),
                'font_size': self.thumbnail_config.get('font_size', 80),
                'text_color': self.thumbnail_config.get('text_color', 'white'),
                'badge': self.thumbnail_config.get('badge'),
                'brand': self.thumbnail_config.get('brand'),
                'author': self.thumbnail_config.get('author'),
                'accent_color': self.thumbnail_config.get('accent_color', '#ffd700')
            }
            
            thumbnail_data = {k: v for k, v in thumbnail_data.items() if v is not None}
            
            output_path = generator.generate(thumbnail_data, validate=True)
            
            self.logger.info(f"✅ 封面已生成: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"生成封面失败: {e}")
            self.logger.warning("继续生成视频，跳过封面生成")
            return None
    
    def _print_progress(self, message: str, percentage: int):
        """打印进度"""
        bar_length = 30
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\n[{bar}] {percentage}% - {message}\n")
    
    def _merge_audio(self, scene_count: int) -> Path:
        """合并音频文件"""
        filelist = self.output_dir / "voice-filelist.txt"
        
        try:
            with open(filelist, 'w') as f:
                for i in range(1, scene_count + 1):
                    f.write(f"file 'voice-{i:02d}.mp3'\n")
            
            audio_file = self.output_dir / "voiceover.aac"
            
            ffmpeg_path = get_ffmpeg_path()
            
            cmd = [
                ffmpeg_path,
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(filelist),
                '-c:a', 'aac',
                '-b:a', '128k',
                str(audio_file)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if filelist.exists():
                filelist.unlink()
            
            return audio_file
            
        except Exception as e:
            self.logger.error(f"合并音频失败: {e}")
            raise DemoVideoGeneratorError(f"合并音频失败: {e}")
    
    def _build_recording_actions(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """构建录制操作列表"""
        actions = []
        
        for scene in scenes:
            action = scene.get('action', {})
            
            if action:
                actions.append(action)
            else:
                actions.append({'type': 'wait', 'duration': 1})
        
        return actions


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Demo Video Generator v1.1.0')
    parser.add_argument('config', help='配置文件路径')
    parser.add_argument('--no-auto-record', action='store_true', help='禁用自动录制')
    parser.add_argument('--log-level', default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    try:
        generator = DemoVideoGenerator(args.config, args.log_level)
        output_file = generator.generate(auto_record=not args.no_auto_record)
        
        if output_file:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
