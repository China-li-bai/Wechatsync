#!/usr/bin/env python3
"""
智能视频生成器 v3.0.0
集成页面分析和自动内容生成

新功能:
- 页面智能分析
- 自动生成介绍文案
- 智能场景规划
- 动态字幕生成
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
from thumbnail_generator import CodeBasedThumbnailGenerator
from page_analyzer import PageAnalyzer
from copywriting_engine import CopywritingEngine
from smart_wait_strategy import SmartWaitStrategy


class SmartVideoGenerator:
    """智能视频生成器 v3.1.0 - 集成专业文案引擎"""
    
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
        self.page_analyzer = PageAnalyzer(logger=self.logger)
        self.copywriting_engine = CopywritingEngine(logger=self.logger)
        self.wait_strategy = SmartWaitStrategy(logger=self.logger)
        
        self.logger.info(f"硬件加速: {self.hw_encoder.hw_accel.value}")
        self.logger.info("✨ 已启用专业文案引擎 (AIDA框架)")
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('SmartVideoGenerator')
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
        success, errors = validator.validate_file(config_file)
        
        if not success:
            self.logger.error(f"配置验证失败，发现 {len(errors)} 个错误:")
            for error in errors:
                self.logger.error(f"  - {error.get('path', '')}: {error.get('message', '')}")
            raise ValueError("配置文件验证失败")
    
    def _apply_config_defaults(self):
        """应用配置默认值"""
        defaults = {
            'project': {
                'output_dir': './output',
                'output_name': 'demo-video'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural',
                'speed': 1.0
            },
            'recording': {
                'enabled': True,
                'auto_scroll': True,
                'scroll_distance': 400
            },
            'video': {
                'format': 'mp4',
                'quality': 'high',
                'resolution': '1280x720',
                'fps': 30
            },
            'advanced': {
                'auto_generate_content': True,
                'analyze_page': True
            }
        }
        
        def merge_dict(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                elif key not in base:
                    base[key] = value
        
        merge_dict(self.config, defaults)
    
    def generate(self, auto_record: bool = True) -> Optional[Path]:
        """生成智能视频"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Smart Video Generator v3.0.0")
        self.logger.info("=" * 60)
        
        project_config = self.config['project']
        advanced_config = self.config.get('advanced', {})
        
        try:
            # 步骤0: 页面分析 (新增)
            self._print_progress("步骤0: 智能页面分析", 5)
            page_analysis = self._analyze_page()
            
            # 根据分析结果生成场景
            if advanced_config.get('auto_generate_content', True):
                scenes = self._generate_smart_scenes(page_analysis)
                self.config['scenes'] = scenes
                self.logger.info(f"✅ 自动生成 {len(scenes)} 个场景")
            
            scenes = self.config['scenes']
            
            # 步骤1: 生成语音 (15%)
            self._print_progress("步骤1: 生成语音", 15)
            voice_files, durations = self._generate_voiceovers(scenes)
            
            # 步骤2: 音频标准化 (10%)
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
            
            # 步骤6: 合成视频 (20%)
            self._print_progress("步骤6: 合成视频（硬件加速）", 20)
            output_file = self._compose_video_optimized(video_file, audio_file, subtitle_file)
            
            # 步骤7: 生成封面 (5%)
            self._print_progress("步骤7: 生成封面", 5)
            thumbnail_path = self._generate_thumbnail(page_analysis)
            
            # 完成
            self._print_completion(output_file, thumbnail_path, subtitle_file, audio_file)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"生成失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _analyze_page(self) -> Dict[str, Any]:
        """分析页面内容"""
        self.logger.info("开始智能页面分析...")
        
        project_config = self.config['project']
        url = project_config.get('url')
        
        if not url:
            self.logger.warning("未配置URL，跳过页面分析")
            return {}
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                self.logger.info(f"访问页面: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                # 使用智能等待策略
                self.wait_strategy.wait_for_page_ready(page, timeout=15000)
                
                # 分析页面
                analysis = self.page_analyzer.analyze_page(page)
                
                browser.close()
                
                # 保存分析结果
                analysis_file = self.output_dir / 'page_analysis.json'
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"✅ 页面分析完成，结果已保存: {analysis_file}")
                
                return analysis
                
        except Exception as e:
            self.logger.error(f"页面分析失败: {e}")
            return {}
    
    def _generate_smart_scenes(self, page_analysis: Dict[str, Any]) -> List[Dict]:
        """根据页面分析生成智能场景（使用专业文案引擎）"""
        self.logger.info("使用专业文案引擎生成场景...")
        
        if not page_analysis:
            return self._get_default_scenes()
        
        project_config = self.config.get('project', {})
        product_name = project_config.get('name', '')
        url = project_config.get('url', '')
        
        # 使用CopywritingEngine生成专业文案
        copy_result = self.copywriting_engine.generate_compelling_copy(
            page_analysis=page_analysis,
            product_name=product_name,
            url=url
        )
        
        if not copy_result or 'scenes' not in copy_result:
            self.logger.warning("文案引擎生成失败，使用默认场景")
            return self._get_default_scenes()
        
        # 保存文案分析结果
        self._save_copywriting_result(copy_result)
        
        scenes = copy_result['scenes']
        
        # 添加默认配置
        for scene in scenes:
            if 'action' not in scene:
                scene['action'] = 'scroll' if scene.get('type') != 'hook' else 'screenshot'
            if 'scroll_distance' not in scene:
                scene['scroll_distance'] = 400
            if 'wait_after' not in scene:
                scene['wait_after'] = 3
        
        insight = copy_result.get('insight', {})
        if insight.get('value_proposition'):
            self.logger.info(f"✨ 价值主张: {insight['value_proposition'][:50]}...")
        if insight.get('pain_points'):
            self.logger.info(f"🎯 识别到 {len(insight['pain_points'])} 个用户痛点")
        if insight.get('target_audience'):
            self.logger.info(f"👥 目标用户: {insight['target_audience']}")
        
        return scenes
    
    def _save_copywriting_result(self, copy_result: Dict[str, Any]):
        """保存文案分析结果"""
        try:
            output_file = self.output_dir / 'copywriting_analysis.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(copy_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 文案分析结果已保存: {output_file}")
            
        except Exception as e:
            self.logger.error(f"保存文案分析失败: {e}")
    
    def _get_default_scenes(self) -> List[Dict]:
        """获取默认场景配置"""
        return [
            {
                'name': 'intro',
                'type': 'hook',
                'text': '欢迎观看本视频演示。',
                'subtitle': '视频演示',
                'action': 'screenshot',
                'wait_after': 3
            },
            {
                'name': 'overview',
                'type': 'feature',
                'text': '让我们一起探索这个页面的精彩内容。',
                'subtitle': '页面概述',
                'action': 'scroll',
                'scroll_distance': 400,
                'wait_after': 3
            },
            {
                'name': 'features',
                'type': 'demo',
                'text': '这里有很多有趣的功能等待你去发现。',
                'subtitle': '功能介绍',
                'action': 'scroll',
                'scroll_distance': 400,
                'wait_after': 3
            },
            {
                'name': 'highlights',
                'type': 'benefit',
                'text': '这些特色功能将带给你更好的体验。',
                'subtitle': '亮点展示',
                'action': 'scroll',
                'scroll_distance': 300,
                'wait_after': 3
            },
            {
                'name': 'cta',
                'type': 'cta',
                'text': '希望这个介绍对你有帮助，欢迎继续探索！',
                'subtitle': '总结',
                'action': 'scroll_to_top',
                'wait_after': 3
            }
        ]
    
    def _generate_voiceovers(self, scenes: List[Dict]) -> tuple:
        """生成语音文件"""
        voice_config = self.config['voice']
        
        voice_files = []
        durations = []
        
        for i, scene in enumerate(scenes, 1):
            text = scene.get('text', '')
            if not text:
                continue
            
            output_file = self.output_dir / f"voice-{i:02d}.mp3"
            
            self.logger.info(f"生成语音 {i}/{len(scenes)}: {text[:30]}...")
            
            # 使用edge-tts生成语音
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                voice_config.get('voice_name', 'XiaoxiaoNeural'),
                rate=f"{'+' if voice_config.get('speed', 1.0) > 1 else '-'}{int(abs(voice_config.get('speed', 1.0) - 1) * 100)}%"
            )
            
            import asyncio
            asyncio.run(communicate.save(str(output_file)))
            
            voice_files.append(output_file)
            
            # 获取音频时长
            duration = self._get_audio_duration(output_file)
            durations.append(duration)
        
        return voice_files, durations
    
    def _normalize_audio_files(self, voice_files: List[Path]) -> List[Path]:
        """标准化音频文件"""
        normalized_files = []
        
        for i, voice_file in enumerate(voice_files, 1):
            self.logger.info(f"标准化音频 {i}/{len(voice_files)}")
            
            output_file = self.output_dir / f"{voice_file.stem}_normalized.mp3"
            
            success = self.audio_normalizer.normalize(
                voice_file,
                output_file,
                apply_noise_reduction=False
            )
            
            if success:
                normalized_files.append(output_file)
            else:
                self.logger.warning(f"音频标准化失败，使用原始文件: {voice_file}")
                normalized_files.append(voice_file)
        
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
        
        if not auto_record or not recording_config.get('enabled', True):
            self.logger.warning("跳过自动录制")
            return None
        
        self.logger.info("开始智能录制...")
        
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                
                # 创建带视频录制的context
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    record_video_dir=str(self.output_dir),
                    record_video_size={'width': 1280, 'height': 720}
                )
                
                page = context.new_page()
                
                # 打开页面
                url = project_config.get('url')
                self.logger.info(f"打开浏览器: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                # 等待页面加载
                self.wait_strategy.wait_for_page_ready(page, timeout=15000)
                
                # 执行场景动作
                for i, (scene, duration) in enumerate(zip(scenes, durations), 1):
                    self.logger.info(f"录制场景 {i}/{len(scenes)} ({duration:.1f}秒)")
                    
                    action = scene.get('action', 'screenshot')
                    
                    if action == 'scroll':
                        distance = scene.get('scroll_distance', 400)
                        self.wait_strategy.smart_scroll(page, distance)
                    elif action == 'scroll_to_top':
                        page.evaluate("window.scrollTo(0, 0);")
                        time.sleep(0.5)
                    elif action == 'interact':
                        selector = scene.get('selector')
                        if selector:
                            self.wait_strategy.smart_click(page, selector)
                    
                    # 等待场景时长
                    time.sleep(duration)
                
                # 停止录制并获取视频路径
                self.logger.info("停止录制")
                video_path = page.video.path()
                context.close()
                browser.close()
                
                # 重命名视频文件
                if video_path and Path(video_path).exists():
                    if video_file.exists():
                        video_file.unlink()
                    Path(video_path).rename(video_file)
                    self.logger.info(f"自动录制完成: {video_file}")
                    return video_file
                else:
                    self.logger.error("视频录制失败")
                    return None
                
        except Exception as e:
            self.logger.error(f"录制失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _compose_video_optimized(self, video_file: Path, audio_file: Path, 
                                 subtitle_file: Path) -> Path:
        """使用硬件加速合成视频"""
        project_config = self.config['project']
        video_config = self.config.get('video', {})
        
        output_name = project_config.get('output_name', 'demo-video')
        output_file = self.output_dir / f"{output_name}.mp4"
        
        self.logger.info(f"使用硬件加速: {self.hw_encoder.hw_accel.value}")
        
        # 获取编码器参数
        quality = video_config.get('quality', 'high')
        encoder_params = self.hw_encoder.get_encoder_params(quality)
        
        # 构建FFmpeg命令
        ffmpeg_path = self._get_ffmpeg_path()
        
        cmd = [
            ffmpeg_path,
            '-y',
            '-i', str(video_file),
            '-i', str(audio_file),
        ]
        
        # 添加视频滤镜
        video_filters = []
        
        # 添加字幕
        if subtitle_file.exists():
            video_filters.append(f"subtitles={str(subtitle_file)}:force_style='FontName=PingFang SC,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,Outline=2,Shadow=1'")
        
        if video_filters:
            cmd.extend(['-vf', ','.join(video_filters)])
        
        # 添加编码器参数
        for key, value in encoder_params.items():
            if key not in ['codec', 'hw_accel']:
                if isinstance(value, bool):
                    if value:
                        cmd.append(f'-{key}')
                else:
                    cmd.extend([f'-{key}', str(value)])
        
        # 音频参数
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest'
        ])
        
        cmd.append(str(output_file))
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"视频合成失败: {result.stderr}")
            raise RuntimeError(f"视频合成失败: {result.stderr}")
        
        self.logger.info(f"视频合成完成: {output_file}")
        return output_file
    
    def _print_completion(self, output_file: Path, thumbnail_path: Optional[Path], 
                         subtitle_file: Path, audio_file: Path):
        """打印完成信息"""
        self.logger.info("=" * 60)
        self.logger.info("🎉 智能视频生成完成！")
        self.logger.info("=" * 60)
        self.logger.info(f"📁 视频文件: {output_file}")
        self.logger.info(f"📊 文件大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        if thumbnail_path and thumbnail_path.exists():
            self.logger.info(f"🖼️  封面文件: {thumbnail_path}")
        
        if subtitle_file.exists():
            self.logger.info(f"📝 字幕文件: {subtitle_file}")
        
        if audio_file.exists():
            self.logger.info(f"🎵 音频文件: {audio_file}")
        
        self.logger.info("=" * 60)
    
    def _generate_thumbnail(self, page_analysis: Dict[str, Any] = None) -> Optional[Path]:
        """生成视频封面"""
        thumbnail_config = self.config.get('thumbnail', {})
        
        if not thumbnail_config.get('enabled', True):
            return None
        
        try:
            generator = CodeBasedThumbnailGenerator(logger=self.logger)
            
            # 使用页面分析结果生成封面
            title = "视频演示"
            if page_analysis:
                summary = page_analysis.get('summary', {})
                title = summary.get('title', '视频演示')
            
            # 构建配置字典
            config = {
                'title': title,
                'subtitle': thumbnail_config.get('subtitle', ''),
                'template': thumbnail_config.get('template', 'default.html'),
                'background': thumbnail_config.get('background'),
                'font_size': thumbnail_config.get('font_size', 80),
                'text_color': thumbnail_config.get('text_color', 'white'),
                'badge': thumbnail_config.get('badge'),
                'brand': thumbnail_config.get('brand'),
                'author': thumbnail_config.get('author'),
                'accent_color': thumbnail_config.get('accent_color')
            }
            
            thumbnail_path = generator.generate(
                config=config,
                output_path=str(self.output_dir / 'thumbnail.png'),
                validate=False
            )
            
            self.logger.info(f"封面生成完成: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            self.logger.error(f"封面生成失败: {e}")
            return None
    
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
    
    def _print_progress(self, message: str, percentage: int):
        """打印进度"""
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        self.logger.info(f"\n{message}")
        self.logger.info(f"[{bar}] {percentage}%")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python smart_video_generator.py <config.yaml>")
        sys.exit(1)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    generator = SmartVideoGenerator(sys.argv[1])
    output_file = generator.generate()
    
    if output_file:
        print(f"\n✅ 视频生成成功: {output_file}")
    else:
        print(f"\n❌ 视频生成失败")
        sys.exit(1)
