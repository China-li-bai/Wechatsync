#!/usr/bin/env python3
"""
Unit Tests for Config Validator
配置验证器单元测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from config_validator import ConfigValidator, ConfigValidationError


class TestConfigValidator(unittest.TestCase):
    """配置验证器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = ConfigValidator()
    
    def test_valid_config(self):
        """测试有效配置"""
        config = {
            'project': {
                'name': 'Test Project',
                'url': 'https://example.com',
                'output_dir': './output',
                'output_name': 'test'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural',
                'speed': 1.0
            },
            'scenes': [
                {
                    'text': '这是测试文本',
                    'subtitle': '测试字幕'
                }
            ]
        }
        
        result = self.validator.validate(config)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.get_errors()), 0)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        config = {}
        
        result = self.validator.validate(config)
        self.assertFalse(result)
        self.assertIn("缺少必需字段: project", self.validator.get_errors())
        self.assertIn("缺少必需字段: voice", self.validator.get_errors())
        self.assertIn("缺少必需字段: scenes", self.validator.get_errors())
    
    def test_invalid_url(self):
        """测试无效 URL"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'invalid-url'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural'
            },
            'scenes': [
                {'text': 'Test'}
            ]
        }
        
        result = self.validator.validate(config)
        self.assertFalse(result)
        self.assertTrue(any('url' in error for error in self.validator.get_errors()))
    
    def test_invalid_voice_speed(self):
        """测试无效语音速度"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'https://example.com'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural',
                'speed': 3.0  # 超出范围
            },
            'scenes': [
                {'text': 'Test'}
            ]
        }
        
        result = self.validator.validate(config)
        self.assertTrue(result)  # 验证通过，但有警告
        self.assertTrue(any('speed' in warning for warning in self.validator.get_warnings()))
    
    def test_empty_scenes(self):
        """测试空场景"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'https://example.com'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural'
            },
            'scenes': []
        }
        
        result = self.validator.validate(config)
        self.assertFalse(result)
        self.assertIn("场景配置为空", self.validator.get_errors())
    
    def test_scene_missing_text(self):
        """测试场景缺少文本"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'https://example.com'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural'
            },
            'scenes': [
                {}  # 缺少 text 字段
            ]
        }
        
        result = self.validator.validate(config)
        self.assertFalse(result)
        self.assertTrue(any('缺少 text 字段' in error for error in self.validator.get_errors()))
    
    def test_invalid_video_fps(self):
        """测试无效视频帧率"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'https://example.com'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural'
            },
            'scenes': [
                {'text': 'Test'}
            ],
            'video': {
                'fps': 100  # 超出范围
            }
        }
        
        result = self.validator.validate(config)
        self.assertTrue(result)  # 验证通过，但有警告
        self.assertTrue(any('fps' in warning for warning in self.validator.get_warnings()))
    
    def test_valid_recording_config(self):
        """测试有效录制配置"""
        config = {
            'project': {
                'name': 'Test',
                'url': 'https://example.com'
            },
            'voice': {
                'language': 'zh-CN',
                'voice_name': 'XiaoxiaoNeural'
            },
            'scenes': [
                {'text': 'Test'}
            ],
            'recording': {
                'enabled': True,
                'auto_scroll': True,
                'scroll_distance': 300
            }
        }
        
        result = self.validator.validate(config)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.get_errors()), 0)


class TestConfigValidatorHelpers(unittest.TestCase):
    """配置验证器辅助方法测试"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = ConfigValidator()
    
    def test_is_valid_url(self):
        """测试 URL 验证"""
        self.assertTrue(self.validator._is_valid_url('https://example.com'))
        self.assertTrue(self.validator._is_valid_url('http://localhost:8080'))
        self.assertTrue(self.validator._is_valid_url('https://192.168.1.1'))
        self.assertFalse(self.validator._is_valid_url('invalid-url'))
        self.assertFalse(self.validator._is_valid_url('ftp://example.com'))
    
    def test_is_valid_resolution(self):
        """测试分辨率验证"""
        self.assertTrue(self.validator._is_valid_resolution('1280x720'))
        self.assertTrue(self.validator._is_valid_resolution('1920x1080'))
        self.assertFalse(self.validator._is_valid_resolution('invalid'))
        self.assertFalse(self.validator._is_valid_resolution('1280'))


if __name__ == '__main__':
    unittest.main()
