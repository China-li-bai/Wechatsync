#!/usr/bin/env python3
"""
提示优化器 v1.0.0
基于RAG和迭代优化的提示增强系统

参考论文:
- 3R: Retrieval, Refinement, and Ranking for Text-to-Video Generation
- RAPO++: Cross-Stage Prompt Optimization for Text-to-Video Generation
- UniAPO: Unified Multimodal Automated Prompt Optimization
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json


class PromptOptimizer:
    """提示优化器 - 自动增强场景描述和解说词"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.modifiers_db = self._load_modifiers()
        self.optimization_history = []
    
    def _load_modifiers(self) -> Dict[str, List[str]]:
        """加载修饰符数据库"""
        return {
            'style': [
                '专业级', '电影质感', '高清', '流畅', '精致',
                '现代化', '简洁', '优雅', '高端', '专业'
            ],
            'action': [
                '精准', '智能', '自动', '实时', '高效',
                '快速', '便捷', '灵活', '强大', '稳定'
            ],
            'quality': [
                '高质量', '专业', '优秀', '出色', '卓越',
                '顶级', '一流', '完美', '极致', '优秀'
            ],
            'emotion': [
                '令人惊叹', '引人入胜', '印象深刻', '令人兴奋',
                '令人信服', '令人满意', '令人愉悦', '令人印象深刻'
            ],
            'technical': [
                'AI驱动', '智能算法', '先进技术', '创新方案',
                '技术领先', '性能卓越', '稳定可靠', '安全高效'
            ],
            'user_benefit': [
                '节省时间', '提高效率', '降低成本', '简化流程',
                '提升体验', '增强功能', '优化性能', '改善质量'
            ]
        }
    
    def enhance_prompt(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        增强提示词
        
        Args:
            text: 原始文本
            context: 上下文信息（可选）
        
        Returns:
            增强后的文本
        """
        self.logger.debug(f"优化提示词: {text[:50]}...")
        
        # 1. 提取关键词
        keywords = self._extract_keywords(text)
        
        # 2. 检索相关修饰符
        modifiers = self._retrieve_modifiers(keywords)
        
        # 3. 分析文本结构
        structure = self._analyze_structure(text)
        
        # 4. 重构文本
        enhanced = self._reconstruct(text, modifiers, structure)
        
        # 5. 记录优化历史
        self._record_optimization(text, enhanced, modifiers)
        
        return enhanced
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 技术关键词
        tech_patterns = [
            r'\b(AI|人工智能|机器学习|深度学习|自动化|智能)\b',
            r'\b(功能|特性|优势|特点)\b',
            r'\b(用户|客户|企业|团队)\b',
            r'\b(效率|性能|质量|体验)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)
        
        # 去重
        keywords = list(set(keywords))
        
        self.logger.debug(f"提取关键词: {keywords}")
        return keywords
    
    def _retrieve_modifiers(self, keywords: List[str]) -> Dict[str, List[str]]:
        """检索相关修饰符"""
        modifiers = {}
        
        # 根据关键词选择修饰符类别
        keyword_str = ' '.join(keywords).lower()
        
        if any(k in keyword_str for k in ['ai', '人工智能', '智能', '自动化']):
            modifiers['technical'] = self.modifiers_db['technical'][:3]
        
        if any(k in keyword_str for k in ['功能', '特性', '优势']):
            modifiers['quality'] = self.modifiers_db['quality'][:3]
        
        if any(k in keyword_str for k in ['用户', '客户', '体验']):
            modifiers['user_benefit'] = self.modifiers_db['user_benefit'][:3]
        
        if any(k in keyword_str for k in ['效率', '性能', '快速']):
            modifiers['action'] = self.modifiers_db['action'][:3]
        
        # 默认添加风格修饰符
        if not modifiers:
            modifiers['style'] = self.modifiers_db['style'][:2]
        
        return modifiers
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """分析文本结构"""
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return {
            'sentence_count': len(sentences),
            'avg_length': len(text) / max(len(sentences), 1),
            'has_question': '？' in text or '?' in text,
            'has_exclamation': '！' in text or '!' in text
        }
    
    def _reconstruct(self, text: str, modifiers: Dict[str, List[str]], 
                     structure: Dict[str, Any]) -> str:
        """重构文本"""
        # 如果文本已经很丰富，直接返回
        if len(text) > 100 and structure['sentence_count'] >= 3:
            return text
        
        # 添加修饰符
        enhanced_parts = []
        
        # 提取句子
        sentences = re.split(r'([。！？\n])', text)
        sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + [''])]
        sentences = [s.strip() for s in sentences if s.strip()]
        
        for i, sentence in enumerate(sentences):
            # 为每个句子选择合适的修饰符
            if i == 0:
                # 第一句：添加技术或质量修饰符
                if 'technical' in modifiers:
                    modifier = modifiers['technical'][0]
                    enhanced = f"{modifier}的{sentence}"
                elif 'quality' in modifiers:
                    modifier = modifiers['quality'][0]
                    enhanced = f"{modifier}{sentence}"
                else:
                    enhanced = sentence
            elif i == len(sentences) - 1:
                # 最后一句：添加情感或用户收益修饰符
                if 'emotion' in modifiers:
                    modifier = modifiers['emotion'][0]
                    enhanced = f"{sentence}，{modifier}"
                elif 'user_benefit' in modifiers:
                    modifier = modifiers['user_benefit'][0]
                    enhanced = f"{sentence}，帮助您{modifier}"
                else:
                    enhanced = sentence
            else:
                # 中间句子：保持原样或添加动作修饰符
                enhanced = sentence
            
            enhanced_parts.append(enhanced)
        
        enhanced_text = ''.join(enhanced_parts)
        
        # 确保文本不会过长
        if len(enhanced_text) > len(text) * 1.5:
            self.logger.warning("增强后文本过长，保持原样")
            return text
        
        return enhanced_text
    
    def _record_optimization(self, original: str, enhanced: str, 
                            modifiers: Dict[str, List[str]]):
        """记录优化历史"""
        self.optimization_history.append({
            'original': original,
            'enhanced': enhanced,
            'modifiers': modifiers,
            'improvement_ratio': len(enhanced) / max(len(original), 1)
        })
    
    def optimize_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化场景配置
        
        Args:
            scene: 场景配置
        
        Returns:
            优化后的场景配置
        """
        optimized = scene.copy()
        
        # 优化解说词
        if 'text' in scene:
            optimized['text'] = self.enhance_prompt(scene['text'])
        
        # 优化字幕（保持简洁）
        if 'subtitle' in scene:
            # 字幕不需要过度优化，保持简洁
            pass
        
        return optimized
    
    def optimize_scenes(self, scenes: List[Dict[str, Any]], 
                       show_progress: bool = False) -> List[Dict[str, Any]]:
        """
        批量优化场景
        
        Args:
            scenes: 场景列表
            show_progress: 是否显示进度
        
        Returns:
            优化后的场景列表
        """
        optimized_scenes = []
        
        iterator = enumerate(scenes, 1)
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(enumerate(scenes, 1), total=len(scenes), 
                              desc="优化场景")
            except ImportError:
                pass
        
        for i, scene in iterator:
            optimized = self.optimize_scene(scene)
            optimized_scenes.append(optimized)
            
            if not show_progress:
                self.logger.info(f"优化场景 {i}/{len(scenes)}")
        
        return optimized_scenes
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        if not self.optimization_history:
            return {'status': 'no_optimizations'}
        
        total_original = sum(len(h['original']) for h in self.optimization_history)
        total_enhanced = sum(len(h['enhanced']) for h in self.optimization_history)
        
        avg_improvement = sum(h['improvement_ratio'] for h in self.optimization_history) / len(self.optimization_history)
        
        return {
            'total_optimizations': len(self.optimization_history),
            'total_original_length': total_original,
            'total_enhanced_length': total_enhanced,
            'average_improvement_ratio': avg_improvement,
            'length_increase': total_enhanced - total_original,
            'percentage_increase': (total_enhanced - total_original) / max(total_original, 1) * 100
        }
    
    def save_optimization_history(self, output_file: Path):
        """保存优化历史"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_history, f, ensure_ascii=False, indent=2)
            self.logger.info(f"优化历史已保存: {output_file}")
        except Exception as e:
            self.logger.error(f"保存优化历史失败: {e}")


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    optimizer = PromptOptimizer()
    
    # 测试用例
    test_prompts = [
        "Claude Code 是一个代理式编码环境。",
        "它可以读取文件、运行命令、自主解决问题。",
        "让 AI 成为你的编程伙伴。"
    ]
    
    print("=" * 60)
    print("提示优化器测试")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n测试 {i}:")
        print(f"原文: {prompt}")
        enhanced = optimizer.enhance_prompt(prompt)
        print(f"优化后: {enhanced}")
    
    # 打印报告
    print("\n" + "=" * 60)
    print("优化报告:")
    print("=" * 60)
    report = optimizer.get_optimization_report()
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    main()
