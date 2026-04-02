#!/usr/bin/env python3
"""
表情生成器 - 基于DiceBear API
支持多种表情风格，用于YouTube缩略图
"""

import requests
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote
import json


class EmojiGenerator:
    """基于DiceBear的表情生成器"""
    
    STYLES = {
        'fun-emoji': '有趣表情符号风格',
        'avataaars': '卡通头像风格',
        'bottts': '机器人风格',
        'pixel-art': '像素艺术风格',
        'identicon': '抽象图案',
        'initials': '首字母头像',
        'lorelei': '插画风格',
        'notionists': '专业插画',
        'shapes': '几何形状',
        'thumbs': '拇指风格'
    }
    
    EMOTIONS = {
        'happy': '快乐',
        'sad': '悲伤',
        'angry': '愤怒',
        'surprised': '震惊',
        'love': '爱',
        'cool': '酷',
        'cry': '哭泣',
        'laugh': '大笑',
        'wink': '眨眼',
        'sleepy': '困倦',
        'nervous': '紧张',
        'sick': '生病',
        'confused': '困惑',
        'shocked': '震惊',
        'excited': '兴奋'
    }
    
    def __init__(self, output_dir: str = "output/emojis", style: str = "fun-emoji"):
        """
        初始化表情生成器
        
        Args:
            output_dir: 输出目录
            style: 表情风格（默认fun-emoji）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.style = style
        self.base_url = "https://api.dicebear.com/7.x"
        self.cache: Dict[str, str] = {}
    
    def generate_url(self, seed: str, style: Optional[str] = None) -> str:
        """
        生成DiceBear API URL
        
        Args:
            seed: 种子字符串（用于确定性生成）
            style: 风格（可选，默认使用实例风格）
        
        Returns:
            API URL
        """
        style = style or self.style
        encoded_seed = quote(seed)
        return f"{self.base_url}/{style}/svg?seed={encoded_seed}"
    
    def generate_svg(self, seed: str, style: Optional[str] = None) -> str:
        """
        生成SVG内容
        
        Args:
            seed: 种子字符串
            style: 风格（可选）
        
        Returns:
            SVG字符串
        """
        cache_key = f"{style or self.style}:{seed}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = self.generate_url(seed, style)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        svg_content = response.text
        self.cache[cache_key] = svg_content
        return svg_content
    
    def generate(self, emotion: str, filename: Optional[str] = None, 
                 style: Optional[str] = None) -> Path:
        """
        生成表情SVG文件
        
        Args:
            emotion: 情感名称
            filename: 文件名（可选，默认使用情感名称）
            style: 风格（可选）
        
        Returns:
            生成的文件路径
        """
        svg_content = self.generate_svg(emotion, style)
        
        filename = filename or f"{emotion}.svg"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return output_path
    
    def generate_batch(self, emotions: List[str], style: Optional[str] = None) -> Dict[str, Path]:
        """
        批量生成表情
        
        Args:
            emotions: 情感列表
            style: 风格（可选）
        
        Returns:
            情感到文件路径的映射
        """
        results = {}
        for emotion in emotions:
            try:
                path = self.generate(emotion, style=style)
                results[emotion] = path
                print(f"✅ 生成成功: {emotion} -> {path}")
            except Exception as e:
                print(f"❌ 生成失败: {emotion} -> {e}")
        return results
    
    def generate_with_options(self, seed: str, options: Dict) -> str:
        """
        生成带选项的表情
        
        Args:
            seed: 种子字符串
            options: 选项字典（如颜色、大小等）
        
        Returns:
            SVG字符串
        """
        url = self.generate_url(seed)
        
        if options:
            params = []
            for key, value in options.items():
                params.append(f"{key}={quote(str(value))}")
            url += "?" + "&".join(params)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def list_styles(self) -> Dict[str, str]:
        """列出所有可用风格"""
        return self.STYLES
    
    def list_emotions(self) -> Dict[str, str]:
        """列出所有预设情感"""
        return self.EMOTIONS
    
    def get_recommended_emotion(self, content_type: str) -> str:
        """
        根据内容类型推荐表情
        
        Args:
            content_type: 内容类型
        
        Returns:
            推荐的情感
        """
        recommendations = {
            'tutorial': 'happy',
            'news': 'surprised',
            'review': 'angry',
            'story': 'sad',
            'recommendation': 'love',
            'tech': 'cool',
            'funny': 'laugh',
            'shocking': 'shocked',
            'exciting': 'excited'
        }
        return recommendations.get(content_type, 'happy')


class EmojiStyleManager:
    """表情风格管理器"""
    
    def __init__(self, emoji_generator: EmojiGenerator):
        self.generator = emoji_generator
        self.style_variants = {
            'youtube-thumbnail': {
                'style': 'fun-emoji',
                'size': 200,
                'background': 'transparent'
            },
            'avatar': {
                'style': 'avataaars',
                'size': 150,
                'background': 'solid'
            },
            'pixel-art': {
                'style': 'pixel-art',
                'size': 100,
                'background': 'transparent'
            }
        }
    
    def generate_for_youtube(self, emotion: str) -> Path:
        """生成YouTube缩略图专用表情"""
        return self.generator.generate(
            emotion,
            style='fun-emoji'
        )
    
    def generate_for_avatar(self, seed: str) -> Path:
        """生成头像专用表情"""
        return self.generator.generate(
            seed,
            style='avataaars'
        )


if __name__ == "__main__":
    print("="*60)
    print("🎭 表情生成器测试 - DiceBear")
    print("="*60)
    
    generator = EmojiGenerator(output_dir="output/emojis")
    
    print("\n📋 可用风格:")
    for style, desc in generator.list_styles().items():
        print(f"  - {style}: {desc}")
    
    print("\n😊 预设情感:")
    for emotion, desc in generator.list_emotions().items():
        print(f"  - {emotion}: {desc}")
    
    print("\n🧪 测试生成:")
    test_emotions = ['happy', 'surprised', 'angry', 'love', 'cool']
    results = generator.generate_batch(test_emotions)
    
    print("\n📊 测试结果:")
    for emotion, path in results.items():
        print(f"  ✅ {emotion}: {path}")
    
    print("\n🎯 内容推荐测试:")
    content_types = ['tutorial', 'news', 'review', 'shocking']
    for content_type in content_types:
        emotion = generator.get_recommended_emotion(content_type)
        print(f"  - {content_type}: {emotion}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
