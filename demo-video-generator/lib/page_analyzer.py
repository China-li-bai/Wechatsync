#!/usr/bin/env python3
"""
页面分析器 v1.0.0
智能分析网页内容，提取关键信息和亮点

功能:
- 页面结构分析
- 关键内容提取
- 功能亮点识别
- 自动生成介绍文案
"""

import logging
import re
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page


class PageAnalyzer:
    """页面分析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化页面分析器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_page(self, page: Page) -> Dict[str, Any]:
        """
        分析页面内容
        
        Args:
            page: Playwright页面对象
        
        Returns:
            页面分析结果
        """
        self.logger.info("开始分析页面...")
        
        try:
            # 提取页面基本信息
            basic_info = self._extract_basic_info(page)
            
            # 提取主要内容
            main_content = self._extract_main_content(page)
            
            # 提取功能特性
            features = self._extract_features(page)
            
            # 提取亮点
            highlights = self._extract_highlights(page)
            
            # 生成页面总结
            summary = self._generate_summary(basic_info, main_content, features, highlights)
            
            # 生成介绍文案
            introduction = self._generate_introduction(summary)
            
            result = {
                'basic_info': basic_info,
                'main_content': main_content,
                'features': features,
                'highlights': highlights,
                'summary': summary,
                'introduction': introduction
            }
            
            self.logger.info("页面分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"页面分析失败: {e}")
            return {}
    
    def _extract_basic_info(self, page: Page) -> Dict[str, str]:
        """
        提取页面基本信息
        
        Args:
            page: Playwright页面对象
        
        Returns:
            基本信息字典
        """
        try:
            info = page.evaluate("""
                () => {
                    return {
                        title: document.title || '',
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                        h1: document.querySelector('h1')?.textContent?.trim() || '',
                        url: window.location.href
                    };
                }
            """)
            
            self.logger.debug(f"基本信息: {info}")
            return info
            
        except Exception as e:
            self.logger.error(f"提取基本信息失败: {e}")
            return {}
    
    def _extract_main_content(self, page: Page) -> List[str]:
        """
        提取主要内容
        
        Args:
            page: Playwright页面对象
        
        Returns:
            内容列表
        """
        try:
            content = page.evaluate("""
                () => {
                    const contents = [];
                    
                    // 提取所有段落
                    document.querySelectorAll('p, article, section').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.length > 20 && text.length < 500) {
                            contents.push(text);
                        }
                    });
                    
                    // 提取标题
                    document.querySelectorAll('h2, h3, h4').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.length > 5) {
                            contents.push('【' + text + '】');
                        }
                    });
                    
                    // 去重并限制数量
                    return [...new Set(contents)].slice(0, 20);
                }
            """)
            
            self.logger.debug(f"提取到 {len(content)} 条内容")
            return content
            
        except Exception as e:
            self.logger.error(f"提取主要内容失败: {e}")
            return []
    
    def _extract_features(self, page: Page) -> List[str]:
        """
        提取功能特性
        
        Args:
            page: Playwright页面对象
        
        Returns:
            功能列表
        """
        try:
            features = page.evaluate("""
                () => {
                    const featureKeywords = [
                        '功能', '特性', '特点', '优势', '支持', '提供',
                        'feature', 'function', 'capability', 'support'
                    ];
                    
                    const features = [];
                    
                    // 查找包含功能关键词的元素
                    document.querySelectorAll('li, div, p, span').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.length > 10 && text.length < 200) {
                            const hasKeyword = featureKeywords.some(kw => 
                                text.toLowerCase().includes(kw.toLowerCase())
                            );
                            
                            if (hasKeyword) {
                                features.push(text);
                            }
                        }
                    });
                    
                    // 去重并限制数量
                    return [...new Set(features)].slice(0, 10);
                }
            """)
            
            self.logger.debug(f"提取到 {len(features)} 个功能特性")
            return features
            
        except Exception as e:
            self.logger.error(f"提取功能特性失败: {e}")
            return []
    
    def _extract_highlights(self, page: Page) -> List[str]:
        """
        提取亮点
        
        Args:
            page: Playwright页面对象
        
        Returns:
            亮点列表
        """
        try:
            highlights = page.evaluate("""
                () => {
                    const highlightKeywords = [
                        '亮点', '特色', '创新', '独家', '首创', '领先',
                        'highlight', 'unique', 'innovative', 'advanced'
                    ];
                    
                    const highlights = [];
                    
                    // 查找包含亮点关键词的元素
                    document.querySelectorAll('li, div, p, span, strong, b').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.length > 10 && text.length < 200) {
                            const hasKeyword = highlightKeywords.some(kw => 
                                text.toLowerCase().includes(kw.toLowerCase())
                            );
                            
                            if (hasKeyword) {
                                highlights.push(text);
                            }
                        }
                    });
                    
                    // 查找带特殊样式的元素（可能是亮点）
                    document.querySelectorAll('.highlight, .featured, .special, [class*="highlight"]').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.length > 10 && text.length < 200) {
                            highlights.push(text);
                        }
                    });
                    
                    // 去重并限制数量
                    return [...new Set(highlights)].slice(0, 10);
                }
            """)
            
            self.logger.debug(f"提取到 {len(highlights)} 个亮点")
            return highlights
            
        except Exception as e:
            self.logger.error(f"提取亮点失败: {e}")
            return []
    
    def _generate_summary(self, basic_info: Dict, main_content: List, 
                         features: List, highlights: List) -> Dict[str, Any]:
        """
        生成页面总结
        
        Args:
            basic_info: 基本信息
            main_content: 主要内容
            features: 功能特性
            highlights: 亮点
        
        Returns:
            总结字典
        """
        summary = {
            'title': basic_info.get('title', ''),
            'description': basic_info.get('description', ''),
            'main_topics': [],
            'key_features': [],
            'highlights': [],
            'content_summary': ''
        }
        
        # 提取主要主题
        if main_content:
            # 从内容中提取关键词
            all_text = ' '.join(main_content[:10])
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}', all_text)
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 取频率最高的词作为主题
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            summary['main_topics'] = [word for word, freq in sorted_words[:5]]
        
        # 提取关键功能
        summary['key_features'] = features[:5]
        
        # 提取亮点
        summary['highlights'] = highlights[:5]
        
        # 生成内容摘要
        if main_content:
            summary['content_summary'] = main_content[0] if main_content else ''
        
        return summary
    
    def _generate_introduction(self, summary: Dict) -> Dict[str, str]:
        """
        生成介绍文案
        
        Args:
            summary: 页面总结
        
        Returns:
            介绍文案字典
        """
        introduction = {
            'brief': '',
            'detailed': '',
            'highlights': ''
        }
        
        title = summary.get('title', '')
        description = summary.get('description', '')
        main_topics = summary.get('main_topics', [])
        key_features = summary.get('key_features', [])
        highlights = summary.get('highlights', [])
        
        # 生成简要介绍
        if title:
            introduction['brief'] = f"欢迎来到{title}。"
            if description:
                introduction['brief'] += f"{description}"
        
        # 生成详细介绍
        detailed_parts = []
        if title:
            detailed_parts.append(f"这是{title}的介绍页面。")
        
        if main_topics:
            topics_str = '、'.join(main_topics[:3])
            detailed_parts.append(f"页面主要涵盖了{topics_str}等内容。")
        
        if key_features:
            detailed_parts.append("主要功能包括：")
            for i, feature in enumerate(key_features[:3], 1):
                detailed_parts.append(f"{i}. {feature}")
        
        introduction['detailed'] = '\n'.join(detailed_parts)
        
        # 生成亮点介绍
        if highlights:
            highlight_parts = ["页面亮点："]
            for i, highlight in enumerate(highlights[:3], 1):
                highlight_parts.append(f"{i}. {highlight}")
            introduction['highlights'] = '\n'.join(highlight_parts)
        
        return introduction
    
    def generate_scene_texts(self, analysis: Dict[str, Any], 
                            scene_count: int = 5) -> List[Dict[str, str]]:
        """
        根据页面分析生成场景文本
        
        Args:
            analysis: 页面分析结果
            scene_count: 场景数量
        
        Returns:
            场景文本列表
        """
        scenes = []
        
        summary = analysis.get('summary', {})
        introduction = analysis.get('introduction', {})
        
        # 场景1: 开场介绍
        scenes.append({
            'name': 'intro',
            'type': 'hook',
            'text': introduction.get('brief', '欢迎观看本视频演示。'),
            'subtitle': summary.get('title', '视频演示')
        })
        
        # 场景2: 页面概述
        main_topics = summary.get('main_topics', [])
        if main_topics:
            topics_text = '、'.join(main_topics[:3])
            scenes.append({
                'name': 'overview',
                'type': 'feature',
                'text': f"这个页面主要涵盖了{topics_text}等核心内容。让我们一起探索这些精彩内容。",
                'subtitle': '页面概述'
            })
        
        # 场景3: 功能介绍
        key_features = summary.get('key_features', [])
        if key_features:
            features_text = '。'.join(key_features[:2])
            scenes.append({
                'name': 'features',
                'type': 'demo',
                'text': f"页面提供了丰富的功能。{features_text}。这些功能将帮助你更好地使用这个平台。",
                'subtitle': '功能介绍'
            })
        
        # 场景4: 亮点展示
        highlights = summary.get('highlights', [])
        if highlights:
            highlights_text = '。'.join(highlights[:2])
            scenes.append({
                'name': 'highlights',
                'type': 'benefit',
                'text': f"这个页面有很多亮点。{highlights_text}。这些特色让页面更加出色。",
                'subtitle': '亮点展示'
            })
        
        # 场景5: 总结号召
        scenes.append({
            'name': 'cta',
            'type': 'cta',
            'text': f"以上就是{summary.get('title', '这个页面')}的主要内容。希望这个介绍对你有帮助。欢迎继续探索！",
            'subtitle': '总结'
        })
        
        # 确保场景数量
        while len(scenes) < scene_count:
            scenes.append({
                'name': f'scene_{len(scenes) + 1}',
                'type': 'feature',
                'text': '让我们继续探索更多内容。',
                'subtitle': '继续探索'
            })
        
        return scenes[:scene_count]


if __name__ == "__main__":
    # 测试代码
    from playwright.sync_api import sync_playwright
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== 页面分析器测试 ===\n")
    
    analyzer = PageAnalyzer()
    
    print("✅ 页面分析器初始化成功")
    print("\n提示: 需要Playwright浏览器才能进行完整测试")
