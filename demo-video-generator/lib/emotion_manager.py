#!/usr/bin/env python3
"""
表情管理器 - 统一管理所有表情配置
使用映射方式，只需一个模板文件
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class EmotionData:
    """表情数据"""
    id: str
    name: str
    emoji: str
    face_color: str
    description: str


class EmotionManager:
    """表情管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "emotion_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.emotions = self._parse_emotions()
        self.categories = self.config.get('categories', {})
        self.recommendations = self.config.get('recommendations', {})
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'emotions': {
                'happy': {
                    'name': '开心',
                    'emoji': '😄',
                    'face_color': '#FFD700',
                    'description': '大笑，眼睛弯成月牙，腮红'
                }
            },
            'categories': {
                'basic': {
                    'name': '基础情绪',
                    'emotions': ['happy']
                }
            },
            'recommendations': {},
            'default_emotion': 'happy'
        }
    
    def _parse_emotions(self) -> Dict[str, EmotionData]:
        """解析表情数据"""
        emotions = {}
        for emotion_id, data in self.config.get('emotions', {}).items():
            emotions[emotion_id] = EmotionData(
                id=emotion_id,
                name=data.get('name', emotion_id),
                emoji=data.get('emoji', '😊'),
                face_color=data.get('face_color', '#FFD700'),
                description=data.get('description', '')
            )
        return emotions
    
    def get_emotion(self, emotion_id: str) -> Optional[EmotionData]:
        """获取表情数据"""
        return self.emotions.get(emotion_id)
    
    def get_all_emotions(self) -> Dict[str, EmotionData]:
        """获取所有表情"""
        return self.emotions
    
    def get_emotions_by_category(self, category: str) -> List[EmotionData]:
        """根据分类获取表情"""
        if category not in self.categories:
            return []
        
        emotion_ids = self.categories[category].get('emotions', [])
        return [self.emotions[eid] for eid in emotion_ids if eid in self.emotions]
    
    def get_categories(self) -> Dict[str, Dict]:
        """获取所有分类"""
        return self.categories
    
    def recommend_emotions(self, content_type: str) -> List[EmotionData]:
        """根据内容类型推荐表情"""
        emotion_ids = self.recommendations.get(content_type, [])
        return [self.emotions[eid] for eid in emotion_ids if eid in self.emotions]
    
    def get_template_config(self, emotion_id: str, **kwargs) -> Dict:
        """
        获取模板配置
        返回可直接用于生成器的配置字典
        """
        emotion = self.get_emotion(emotion_id)
        
        if not emotion:
            emotion = self.emotions.get(self.config.get('default_emotion', 'happy'))
        
        config = {
            'template': 'emotion-unified.html',
            'emotion': emotion_id,
            'emotion_name': emotion.name,
            'emoji': emotion.emoji,
            'face_color': emotion.face_color,
        }
        
        config.update(kwargs)
        
        return config
    
    def list_emotions(self) -> str:
        """列出所有表情"""
        lines = ["🎭 可用表情列表:\n"]
        
        for category_id, category_data in self.categories.items():
            lines.append(f"\n### {category_data['name']}")
            
            for emotion_id in category_data.get('emotions', []):
                if emotion_id in self.emotions:
                    emotion = self.emotions[emotion_id]
                    lines.append(f"  {emotion.emoji} {emotion_id:15s} - {emotion.name}: {emotion.description}")
        
        return '\n'.join(lines)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_emotions': len(self.emotions),
            'total_categories': len(self.categories),
            'categories': {
                cat_id: len(cat_data.get('emotions', []))
                for cat_id, cat_data in self.categories.items()
            }
        }


if __name__ == '__main__':
    manager = EmotionManager()
    
    print(manager.list_emotions())
    print("\n" + "="*70)
    print(f"📊 统计: {manager.get_stats()}")
    
    print("\n" + "="*70)
    print("📝 获取 'happy' 表情配置:")
    config = manager.get_template_config('happy', title="测试标题", width=1080, height=1920)
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70)
    print("🎯 推荐 'funny' 内容的表情:")
    for emotion in manager.recommend_emotions('funny'):
        print(f"  {emotion.emoji} {emotion.name}")
