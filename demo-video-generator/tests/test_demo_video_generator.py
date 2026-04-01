#!/usr/bin/env python3
"""
Demo Video Generator - 测试套件
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from demo_video_generator import (
    ConfigParser,
    SubtitleGenerator,
)


class TestConfigParser(unittest.TestCase):
    """配置解析器测试"""
    
    def setUp(self):
        """创建临时目录和测试配置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / 'test_config.yaml'
        
        self.valid_config = """
project:
  name: "Test Demo"
  url: "https://test.com"
  output_dir: "./output"
  
voice:
  language: "zh-CN"
  voice_name: "XiaoxiaoNeural"
  speed: 1.0
  
scenes:
  - name: "intro"
    type: "hook"
    text: "测试文案"
    subtitle: "测试字幕"
    action: "screenshot"
    
video:
  format: "mp4"
  quality: "high"
"""
        
    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)
        
    def test_load_valid_config(self):
        """测试加载有效配置"""
        self.config_file.write_text(self.valid_config, encoding='utf-8')
        
        parser = ConfigParser(str(self.config_file))
        
        self.assertEqual(parser.get_project_config()['name'], "Test Demo")
        self.assertEqual(parser.get_voice_config()['language'], "zh-CN")
        self.assertEqual(len(parser.get_scenes()), 1)
        
    def test_missing_config_file(self):
        """测试缺失配置文件"""
        with self.assertRaises(FileNotFoundError):
            ConfigParser('nonexistent.yaml')
            
    def test_missing_required_field(self):
        """测试缺少必需字段"""
        invalid_config = """
project:
  name: "Test"
"""
        self.config_file.write_text(invalid_config, encoding='utf-8')
        
        with self.assertRaises(ValueError):
            ConfigParser(str(self.config_file))


class TestSubtitleGenerator(unittest.TestCase):
    """字幕生成器测试"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)
        
    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)
        
    def test_generate_srt(self):
        """测试生成SRT字幕"""
        generator = SubtitleGenerator({}, self.output_dir)
        
        durations = [5.5, 3.2, 4.8]
        subtitles = ["第一句", "第二句", "第三句"]
        output_file = self.output_dir / "test.srt"
        
        generator.generate_srt(durations, subtitles, output_file)
        
        self.assertTrue(output_file.exists())
        
        content = output_file.read_text(encoding='utf-8')
        self.assertIn("第一句", content)
        self.assertIn("第二句", content)
        self.assertIn("第三句", content)
        
    def test_seconds_to_srt_time(self):
        """测试时间格式转换"""
        generator = SubtitleGenerator({}, self.output_dir)
        
        # 测试整数秒
        time_str = generator._seconds_to_srt_time(3661.5)
        self.assertEqual(time_str, "01:01:01,500")
        
        # 测试零秒
        time_str = generator._seconds_to_srt_time(0.0)
        self.assertEqual(time_str, "00:00:00,000")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)
        
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 这里可以添加完整的集成测试
        # 由于涉及外部依赖（edge-tts, ffmpeg等），这里只做基础测试
        pass


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestConfigParser))
    suite.addTests(loader.loadTestsFromTestCase(TestSubtitleGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
