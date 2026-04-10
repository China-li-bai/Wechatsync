#!/usr/bin/env python3
"""
平台专属封面生成器
基于2024-2025年数据分析，为不同平台生成优化封面
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PlatformSpec:
    """平台规格"""
    name: str
    width: int
    height: int
    aspect_ratio: str
    format: str


@dataclass
class TemplateType:
    """模板类型"""
    name: str
    description: str
    elements: List[str]
    ctr_boost: str
    use_cases: List[str]


class PlatformTemplateGenerator:
    """平台专属模板生成器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "platform_templates.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.platforms = self._parse_platforms()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'platforms': {
                'youtube': {
                    'name': 'YouTube',
                    'specs': {
                        'width': 1280,
                        'height': 720,
                        'aspect_ratio': '16:9',
                        'format': 'PNG'
                    }
                }
            }
        }
    
    def _parse_platforms(self) -> Dict[str, PlatformSpec]:
        """解析平台规格"""
        platforms = {}
        for platform_id, data in self.config.get('platforms', {}).items():
            specs = data.get('specs', {})
            platforms[platform_id] = PlatformSpec(
                name=data.get('name', platform_id),
                width=specs.get('width', 1280),
                height=specs.get('height', 720),
                aspect_ratio=specs.get('aspect_ratio', '16:9'),
                format=specs.get('format', 'PNG')
            )
        return platforms
    
    def get_platform_spec(self, platform: str) -> Optional[PlatformSpec]:
        """获取平台规格"""
        return self.platforms.get(platform)
    
    def get_platform_template_types(self, platform: str) -> Dict[str, TemplateType]:
        """获取平台模板类型"""
        platform_config = self.config.get('platforms', {}).get(platform, {})
        template_types = platform_config.get('template_types', {})
        
        result = {}
        for type_id, data in template_types.items():
            result[type_id] = TemplateType(
                name=data.get('name', type_id),
                description=data.get('description', ''),
                elements=data.get('elements', []),
                ctr_boost=data.get('ctr_boost', '+0%'),
                use_cases=data.get('use_cases', [])
            )
        
        return result
    
    def get_color_scheme(self, platform: str) -> Dict:
        """获取平台配色方案"""
        return self.config.get('color_schemes', {}).get(platform, {})
    
    def get_expression_recommendations(self, platform: str) -> Dict:
        """获取表情推荐"""
        return self.config.get('expression_recommendations', {}).get(platform, {})
    
    def generate_template_config(
        self,
        platform: str,
        template_type: str,
        title: str,
        **kwargs
    ) -> Dict:
        """
        生成模板配置
        
        Args:
            platform: 平台ID (youtube/tiktok/xiaohongshu/twitter/facebook)
            template_type: 模板类型
            title: 标题
            **kwargs: 其他参数
        
        Returns:
            完整的模板配置字典
        """
        platform_spec = self.get_platform_spec(platform)
        template_types = self.get_platform_template_types(platform)
        color_scheme = self.get_color_scheme(platform)
        
        if not platform_spec:
            raise ValueError(f"未知平台: {platform}")
        
        if template_type not in template_types:
            raise ValueError(f"平台 {platform} 不支持模板类型: {template_type}")
        
        template_info = template_types[template_type]
        
        config = {
            'platform': platform,
            'template_type': template_type,
            'template_name': template_info.name,
            'width': platform_spec.width,
            'height': platform_spec.height,
            'aspect_ratio': platform_spec.aspect_ratio,
            'title': title,
            'ctr_boost': template_info.ctr_boost,
            'use_cases': template_info.use_cases,
            'design_elements': template_info.elements,
        }
        
        if color_scheme:
            primary_colors = color_scheme.get('primary', [])
            if primary_colors:
                config['primary_color'] = primary_colors[0]
            
            combinations = color_scheme.get('combinations', [])
            if combinations:
                config['color_combination'] = combinations[0]
        
        config.update(kwargs)
        
        return config
    
    def list_platforms(self) -> str:
        """列出所有平台"""
        lines = ["📺 支持的平台:\n"]
        
        for platform_id, spec in self.platforms.items():
            lines.append(f"\n### {spec.name}")
            lines.append(f"  尺寸: {spec.width}×{spec.height}")
            lines.append(f"  比例: {spec.aspect_ratio}")
            lines.append(f"  格式: {spec.format}")
            
            template_types = self.get_platform_template_types(platform_id)
            lines.append(f"  模板类型: {len(template_types)}个")
            
            for type_id, template in template_types.items():
                lines.append(f"    - {template.name} ({template.ctr_boost})")
        
        return '\n'.join(lines)
    
    def recommend_template(self, platform: str, content_type: str) -> List[str]:
        """
        根据内容类型推荐模板
        
        Args:
            platform: 平台ID
            content_type: 内容类型 (如: 美妆、美食、教程等)
        
        Returns:
            推荐的模板类型列表
        """
        template_types = self.get_platform_template_types(platform)
        recommendations = []
        
        for type_id, template in template_types.items():
            if content_type in template.use_cases:
                recommendations.append(type_id)
        
        return recommendations
    
    def get_best_practices(self, platform: str) -> Dict:
        """获取平台最佳实践"""
        platform_config = self.config.get('platforms', {}).get(platform, {})
        return platform_config.get('best_practices', {})
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_platforms': len(self.platforms),
            'platforms': {
                platform_id: len(self.get_platform_template_types(platform_id))
                for platform_id in self.platforms.keys()
            }
        }


if __name__ == '__main__':
    generator = PlatformTemplateGenerator()
    
    print(generator.list_platforms())
    
    print("\n" + "="*70)
    print("📊 统计:", generator.get_stats())
    
    print("\n" + "="*70)
    print("📝 生成YouTube真实表情型封面配置:")
    config = generator.generate_template_config(
        platform='youtube',
        template_type='authentic_expression',
        title='震惊！这个方法太神奇了'
    )
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70)
    print("🎯 推荐 '美妆' 内容的TikTok模板:")
    recommendations = generator.recommend_template('tiktok', '美妆')
    for rec in recommendations:
        print(f"  - {rec}")
    
    print("\n" + "="*70)
    print("📋 YouTube最佳实践:")
    practices = generator.get_best_practices('youtube')
    for key, value in practices.items():
        print(f"  {key}: {value}")
