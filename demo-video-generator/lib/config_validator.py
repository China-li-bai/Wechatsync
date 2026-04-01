#!/usr/bin/env python3
"""
Config Validator - 配置文件验证器
验证 YAML 配置文件的完整性和正确性
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigValidator:
    """配置文件验证器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.errors = []
        self.warnings = []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        验证配置文件
        
        Args:
            config: 配置字典
        
        Returns:
            是否验证通过
        """
        self.errors = []
        self.warnings = []
        
        self._validate_structure(config)
        self._validate_project(config.get('project', {}))
        self._validate_voice(config.get('voice', {}))
        self._validate_scenes(config.get('scenes', []))
        self._validate_video(config.get('video', {}))
        self._validate_subtitle(config.get('subtitle', {}))
        self._validate_recording(config.get('recording', {}))
        
        if self.errors:
            self.logger.error(f"配置验证失败，发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                self.logger.error(f"  ❌ {error}")
            return False
        
        if self.warnings:
            self.logger.warning(f"配置验证通过，但有 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                self.logger.warning(f"  ⚠️  {warning}")
        else:
            self.logger.info("✅ 配置验证通过")
        
        return True
    
    def _validate_structure(self, config: Dict[str, Any]):
        """验证配置结构"""
        required_fields = ['project', 'voice', 'scenes']
        
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {field}")
    
    def _validate_project(self, project: Dict[str, Any]):
        """验证项目配置"""
        if not project:
            self.errors.append("项目配置为空")
            return
        
        if 'name' not in project:
            self.errors.append("项目配置缺少 name 字段")
        elif not isinstance(project['name'], str):
            self.errors.append("项目 name 必须是字符串")
        
        if 'url' not in project:
            self.errors.append("项目配置缺少 url 字段")
        elif not isinstance(project['url'], str):
            self.errors.append("项目 url 必须是字符串")
        elif not self._is_valid_url(project['url']):
            self.errors.append(f"项目 url 格式无效: {project['url']}")
        
        if 'output_dir' in project:
            if not isinstance(project['output_dir'], str):
                self.errors.append("项目 output_dir 必须是字符串")
        
        if 'output_name' in project:
            if not isinstance(project['output_name'], str):
                self.errors.append("项目 output_name 必须是字符串")
    
    def _validate_voice(self, voice: Dict[str, Any]):
        """验证语音配置"""
        if not voice:
            self.errors.append("语音配置为空")
            return
        
        if 'language' not in voice:
            self.errors.append("语音配置缺少 language 字段")
        elif not isinstance(voice['language'], str):
            self.errors.append("语音 language 必须是字符串")
        elif voice['language'] not in ['zh-CN', 'zh-TW', 'zh-HK', 'en-US', 'en-GB']:
            self.warnings.append(f"语音 language 可能不支持: {voice['language']}")
        
        if 'voice_name' not in voice:
            self.errors.append("语音配置缺少 voice_name 字段")
        elif not isinstance(voice['voice_name'], str):
            self.errors.append("语音 voice_name 必须是字符串")
        
        if 'speed' in voice:
            if not isinstance(voice['speed'], (int, float)):
                self.errors.append("语音 speed 必须是数字")
            elif voice['speed'] < 0.5 or voice['speed'] > 2.0:
                self.warnings.append(f"语音 speed 建议在 0.5-2.0 之间: {voice['speed']}")
    
    def _validate_scenes(self, scenes: List[Dict[str, Any]]):
        """验证场景配置"""
        if not scenes:
            self.errors.append("场景配置为空")
            return
        
        if not isinstance(scenes, list):
            self.errors.append("场景配置必须是列表")
            return
        
        for i, scene in enumerate(scenes, 1):
            if not isinstance(scene, dict):
                self.errors.append(f"场景 {i} 必须是字典")
                continue
            
            if 'text' not in scene:
                self.errors.append(f"场景 {i} 缺少 text 字段")
            elif not isinstance(scene['text'], str):
                self.errors.append(f"场景 {i} text 必须是字符串")
            elif len(scene['text']) == 0:
                self.errors.append(f"场景 {i} text 不能为空")
            elif len(scene['text']) > 500:
                self.warnings.append(f"场景 {i} text 过长 ({len(scene['text'])} 字符)，建议拆分")
            
            if 'subtitle' in scene:
                if not isinstance(scene['subtitle'], str):
                    self.errors.append(f"场景 {i} subtitle 必须是字符串")
            
            if 'action' in scene:
                if not isinstance(scene['action'], dict):
                    self.errors.append(f"场景 {i} action 必须是字典")
                else:
                    self._validate_action(scene['action'], i)
    
    def _validate_action(self, action: Dict[str, Any], scene_num: int):
        """验证动作配置"""
        action_type = action.get('type')
        
        if not action_type:
            self.errors.append(f"场景 {scene_num} action 缺少 type 字段")
            return
        
        valid_types = ['scroll', 'click', 'screenshot', 'wait']
        if action_type not in valid_types:
            self.warnings.append(f"场景 {scene_num} action type 可能不支持: {action_type}")
        
        if action_type == 'scroll':
            if 'distance' in action:
                if not isinstance(action['distance'], int):
                    self.errors.append(f"场景 {scene_num} scroll distance 必须是整数")
        
        if action_type == 'click':
            if 'selector' not in action:
                self.warnings.append(f"场景 {scene_num} click 缺少 selector 字段")
    
    def _validate_video(self, video: Dict[str, Any]):
        """验证视频配置"""
        if not video:
            return
        
        if 'format' in video:
            valid_formats = ['mp4', 'webm', 'mov']
            if video['format'] not in valid_formats:
                self.warnings.append(f"视频 format 可能不支持: {video['format']}")
        
        if 'quality' in video:
            valid_qualities = ['low', 'medium', 'high']
            if video['quality'] not in valid_qualities:
                self.warnings.append(f"视频 quality 必须是: {', '.join(valid_qualities)}")
        
        if 'resolution' in video:
            if not self._is_valid_resolution(video['resolution']):
                self.warnings.append(f"视频 resolution 格式无效: {video['resolution']}")
        
        if 'fps' in video:
            if not isinstance(video['fps'], int):
                self.errors.append("视频 fps 必须是整数")
            elif video['fps'] < 10 or video['fps'] > 60:
                self.warnings.append(f"视频 fps 建议在 10-60 之间: {video['fps']}")
    
    def _validate_subtitle(self, subtitle: Dict[str, Any]):
        """验证字幕配置"""
        if not subtitle:
            return
        
        if 'font_size' in subtitle:
            if not isinstance(subtitle['font_size'], int):
                self.errors.append("字幕 font_size 必须是整数")
            elif subtitle['font_size'] < 10 or subtitle['font_size'] > 72:
                self.warnings.append(f"字幕 font_size 建议在 10-72 之间: {subtitle['font_size']}")
        
        if 'position' in subtitle:
            valid_positions = ['bottom', 'top', 'center']
            if subtitle['position'] not in valid_positions:
                self.warnings.append(f"字幕 position 必须是: {', '.join(valid_positions)}")
    
    def _validate_recording(self, recording: Dict[str, Any]):
        """验证录制配置"""
        if not recording:
            return
        
        if 'enabled' in recording:
            if not isinstance(recording['enabled'], bool):
                self.errors.append("录制 enabled 必须是布尔值")
        
        if 'auto_scroll' in recording:
            if not isinstance(recording['auto_scroll'], bool):
                self.errors.append("录制 auto_scroll 必须是布尔值")
        
        if 'scroll_distance' in recording:
            if not isinstance(recording['scroll_distance'], int):
                self.errors.append("录制 scroll_distance 必须是整数")
            elif recording['scroll_distance'] < 0:
                self.errors.append("录制 scroll_distance 不能为负数")
    
    def _is_valid_url(self, url: str) -> bool:
        """验证 URL 格式"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return pattern.match(url) is not None
    
    def _is_valid_resolution(self, resolution: str) -> bool:
        """验证分辨率格式"""
        pattern = re.compile(r'^\d+x\d+$')
        return pattern.match(resolution) is not None
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings
