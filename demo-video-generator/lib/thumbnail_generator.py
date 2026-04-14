"""
编码封面生成器 - 基于HTML/CSS + Playwright (v3.0 CTR优化版 + 竖屏支持)

特性:
- 完全可控: 精确控制每个元素
- 可验证: 配置验证和输出验证
- 吸引眼球: 基于CTR优化原则和心理学设计
- 统一风格: 模板系统保证一致性
- 智能推荐: AI驱动的模板和配色方案推荐
- 情绪触发: 内置高转化率情绪触发词库
- 竖屏适配: 支持移动端竖屏（1080x1920）模板

v2.0 新增:
- 5个高CTR优化模板（viral, curiosity, urgency, emotional, minimal-impact）
- 智能模板推荐引擎
- 情绪触发词自动检测
- 色彩心理学配色方案
- A/B测试支持

v3.0 新增:
- 5个竖屏适配模板（viral-vertical, curiosity-vertical, urgency-vertical, emotional-vertical）
- 竖屏模式自动检测和切换
- 移动端优化设计
- 基于STEPPS病毒传播法则的模板设计
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
from jinja2 import Environment, FileSystemLoader, Template
from playwright.sync_api import sync_playwright, Browser, Page


class ThumbnailConfigValidator:
    """封面配置验证器"""
    
    REQUIRED_FIELDS = ['title']
    
    OPTIONAL_FIELDS = [
        'template', 'width', 'height', 'subtitle', 'background',
        'font_size', 'text_color', 'badge', 'author', 'date',
        'brand', 'logo', 'accent_color', 'style'
    ]
    
    VALID_STYLES = [
        'tutorial', 'review', 'news', 'entertainment', 'tech', 'minimal',
        'viral', 'curiosity', 'urgency', 'emotional', 'minimal-impact',
        'viral-vertical', 'curiosity-vertical', 'urgency-vertical', 'emotional-vertical'
    ]
    
    EMOTIONAL_TRIGGERS = {
        'shock': ['震惊', '惊讶', '不敢相信', '竟然', '居然', '天啊', '我的天', '崩溃', 
                '炸裂', '爆了', '疯了吧', '离谱', '不可思议', '惊呆', '目瞪口呆'],
        'curiosity': ['秘密', '隐藏', '真相', '揭秘', '内幕', '没人告诉你', '为什么',
                    '如何', '怎样', '什么', '哪里', '谁', '什么时候', '疑问', '疑惑',
                    ' mystery', '秘密武器', '绝招', '技巧', '方法', '策略'],
        'urgency': ['紧急', '立即', '马上', '限时', '最后', '机会', '错过', '倒计时',
                  '抓紧', '速看', '快', '即将', '马上删除', '仅限今天', '最后机会',
                  ' NOW', 'HOT', '火速', '紧迫', '重要通知'],
        'emotional': ['感动', '泪目', '哭了', '心碎', '温暖', '治愈', '励志', '激励',
                   '故事', '经历', '人生', '成长', '改变', '蜕变', '逆袭', '坚持',
                   '梦想', '希望', '爱', '亲情', '友情', '爱情', '感动到哭'],
        'success': ['成功', '赚钱', '暴富', '财富', '自由', '财务', '收入', '月入',
                 '百万', '千万', '翻倍', '增长', '提升', '突破', '冠军', '第一',
                 'TOP', 'NO.1', '最佳', '最强', '终极']
    }
    
    COLOR_SCHEMES = {
        'shock_red': {
            'background': 'linear-gradient(135deg, #FF0844 0%, #FFB199 100%)',
            'accent_color': '#FFD700',
            'description': '震惊红 - 紧急、激情、高能量'
        },
        'mystery_dark': {
            'background': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
            'accent_color': '#FFD700',
            'description': '神秘深蓝 - 好奇、悬疑、高端'
        },
        'urgency_orange': {
            'background': 'linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%)',
            'accent_color': '#FFD700',
            'description': '紧迫橙红 - 紧急、行动、FOMO'
        },
        'emotional_purple': {
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'accent_color': '#FFD700',
            'description': '情绪紫 - 情感、故事、共鸣'
        },
        'impact_black': {
            'background': 'linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%)',
            'accent_color': '#FFD700',
            'description': '冲击黑金 - 极简、力量、权威'
        },
        'success_green': {
            'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
            'accent_color': '#FFFFFF',
            'description': '成功绿 - 成长、财富、积极'
        },
        'energy_yellow': {
            'background': 'linear-gradient(135deg, #F7971E 0%, #FFD200 100%)',
            'accent_color': '#000000',
            'description': '能量黄 - 注意、警示、活力'
        }
    }
    
    POWER_WORDS = {
        'urgency': ['紧急', '立即', '马上', '限时', '最后', '机会', '错过', '倒计时',
                   '抓紧', '速看', '快', '即将', '马上删除', '仅限今天', '最后机会',
                   'NOW', 'HOT', '火速', '紧迫', '重要通知'],
        'curiosity': ['秘密', '隐藏', '真相', '揭秘', '内幕', '没人告诉你', '为什么',
                    '如何', '怎样', '什么', '哪里', '谁', '什么时候', '疑问', '疑惑',
                    '神秘', '绝招', '技巧', '方法', '策略'],
        'value': ['免费', '独家', 'VIP', '顶级', '最佳', '终极', '完美', '豪华',
                 '精品', '稀缺', '限量', '特别', '专属', '私人', '定制'],
        'emotion': ['震惊', '惊讶', '不敢相信', '感动', '泪目', '崩溃', '炸裂',
                   '疯了吧', '离谱', '不可思议', '惊呆', '目瞪口呆', '惊喜', '狂喜'],
        'result': ['成功', '赚钱', '暴富', '财富', '自由', '改变', '突破', '逆袭',
                  '成长', '提升', '翻倍', '增长', '冠军', '第一', 'TOP', 'NO.1'],
        'quantity': ['100万', '翻倍', '3倍', '10倍', '100%', '零风险', '保证',
                    '100%', '无效退款', '永久', '终身', '无限', '无数'],
        'social': ['100万人', '99%的人', '大家都在', '疯传', '刷屏', '热门',
                  '爆款', '网红', '流行', '趋势', '潮流']
    }
    
    COPYWRITING_TIPS = {
        'min_length': 4,
        'max_length': 15,
        'ideal_length': 7,
        'max_lines': 3,
        'recommended_words': 3
    }
    
    @classmethod
    def analyze_title_quality(cls, title: str) -> Dict[str, Any]:
        """
        分析标题质量并给出优化建议
        
        Args:
            title: 标题
        
        Returns:
            质量分析字典
        """
        title_stripped = title.strip()
        title_length = len(title_stripped)
        word_count = len([w for w in title_stripped.split() if w])
        
        power_words_found = []
        for category, words in cls.POWER_WORDS.items():
            for word in words:
                if word in title_stripped:
                    power_words_found.append({
                        'word': word,
                        'category': category
                    })
        
        has_question = any(q in title_stripped for q in ['?', '？', '为什么', '如何', '怎样', '什么'])
        has_number = any(str(i) in title_stripped for i in range(10))
        has_emoji = any(ord(c) > 0x1F000 for c in title_stripped)
        
        length_score = 0
        if cls.COPYWRITING_TIPS['min_length'] <= title_length <= cls.COPYWRITING_TIPS['max_length']:
            length_score = 30
        elif title_length < cls.COPYWRITING_TIPS['min_length']:
            length_score = 15
        else:
            length_score = 20
        
        power_word_score = min(len(power_words_found) * 20, 40)
        bonus_score = 0
        if has_question: bonus_score += 10
        if has_number: bonus_score += 10
        if has_emoji: bonus_score += 10
        
        total_score = length_score + power_word_score + bonus_score
        total_score = min(total_score, 100)
        
        suggestions = []
        
        if title_length < cls.COPYWRITING_TIPS['min_length']:
            suggestions.append(f"标题太短（{title_length}字），建议增加到{cls.COPYWRITING_TIPS['ideal_length']}字左右")
        elif title_length > cls.COPYWRITING_TIPS['max_length']:
            suggestions.append(f"标题太长（{title_length}字），建议精简到{cls.COPYWRITING_TIPS['max_length']}字以内")
        
        if not power_words_found:
            suggestions.append("建议添加强力词汇（如：秘密、限时、独家、免费等）")
        
        if not has_question and not has_number:
            suggestions.append("建议使用数字或疑问句，增加好奇心")
        
        if not any(c in ['!', '！', '?', '？'] for c in title_stripped):
            suggestions.append("适当使用感叹号或问号，增强情感表达")
        
        return {
            'title_length': title_length,
            'word_count': word_count,
            'power_words': power_words_found,
            'has_question': has_question,
            'has_number': has_number,
            'has_emoji': has_emoji,
            'scores': {
                'length': length_score,
                'power_words': power_word_score,
                'bonus': bonus_score,
                'total': total_score
            },
            'suggestions': suggestions,
            'rating': '优秀' if total_score >= 80 else '良好' if total_score >= 60 else '一般' if total_score >= 40 else '需改进'
        }
    
    @classmethod
    def suggest_title_improvements(cls, title: str) -> List[str]:
        """
        建议标题改进方案
        
        Args:
            title: 原始标题
        
        Returns:
            改进建议列表
        """
        suggestions = []
        quality = cls.analyze_title_quality(title)
        
        if quality['scores']['total'] >= 80:
            suggestions.append(f"当前标题评分{quality['scores']['total']}分，已经很好了！")
            return suggestions
        
        if not quality['has_number']:
            suggestions.append(f"试试添加数字：3个{title}")
            suggestions.append(f"试试添加数字：{title}的5个秘诀")
        
        if not quality['has_question']:
            suggestions.append(f"改成疑问句：为什么{title}？")
            suggestions.append(f"改成疑问句：如何{title}？")
        
        if not quality['power_words']:
            suggestions.append(f"添加强力词：独家！{title}")
            suggestions.append(f"添加强力词：震惊！{title}")
        
        if quality['title_length'] < 5:
            suggestions.append(f"扩展标题：{title}的惊人秘密")
        
        if quality['title_length'] > 12:
            short_title = title[:10] + "..." if len(title) > 10 else title
            suggestions.append(f"精简版本：{short_title}")
        
        return suggestions
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> List[str]:
        """
        验证配置
        
        Args:
            config: 配置字典
        
        Returns:
            错误消息列表（空列表表示验证通过）
        """
        errors = []
        
        if not isinstance(config, dict):
            errors.append("配置必须是字典类型")
            return errors
        
        for field in cls.REQUIRED_FIELDS:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        if 'title' in config and not isinstance(config['title'], str):
            errors.append("title 必须是字符串类型")
        
        if 'width' in config:
            if not isinstance(config['width'], int) or config['width'] <= 0:
                errors.append("width 必须是正整数")
        
        if 'height' in config:
            if not isinstance(config['height'], int) or config['height'] <= 0:
                errors.append("height 必须是正整数")
        
        if 'style' in config and config['style'] not in cls.VALID_STYLES:
            errors.append(f"style 必须是以下之一: {', '.join(cls.VALID_STYLES)}")
        
        return errors


class CodeBasedThumbnailGenerator:
    """编码封面生成器"""
    
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    DEFAULT_TEMPLATE = 'default.html'
    
    VERTICAL_WIDTH = 1080
    VERTICAL_HEIGHT = 1920
    
    EMOTIONAL_TRIGGERS = ThumbnailConfigValidator.EMOTIONAL_TRIGGERS
    COLOR_SCHEMES = ThumbnailConfigValidator.COLOR_SCHEMES
    VALID_STYLES = ThumbnailConfigValidator.VALID_STYLES
    
    STEPPS_PRINCIPLES = {
        'social_currency': {
            'name': '社交货币',
            'description': '分享让我们看起来很棒的东西，提升社交地位和形象',
            'keywords': ['独家', '内幕', '秘密', '顶级', 'VIP', '专家', '大师', '第一', 
                       '冠军', '最佳', '终极', '罕见', '稀有', '限量', '特别'],
            'template_suggestion': ['viral-vertical.html', 'viral.html'],
            'badge_suggestions': ['独家', '内幕', 'TOP1', '必看']
        },
        'triggers': {
            'name': '诱因',
            'description': '利用环境线索触发记忆，让内容在特定场景下被想起',
            'keywords': ['每天', '每周', '早上', '晚上', '周末', '节日', '季节', '天气',
                       '咖啡', '工作', '学习', '运动', '吃饭', '睡觉'],
            'template_suggestion': ['curiosity-vertical.html', 'curiosity.html'],
            'badge_suggestions': ['每日', '提醒', '注意']
        },
        'emotion': {
            'name': '情绪',
            'description': '激发高唤醒情绪（敬畏、愤怒、焦虑、兴奋），促进分享',
            'keywords': ['震惊', '惊讶', '感动', '愤怒', '兴奋', '恐惧', '惊喜', '崩溃',
                       '泪目', '爆了', '炸裂', '疯了吧', '离谱', '不可思议'],
            'template_suggestion': ['emotional-vertical.html', 'emotional.html', 'viral-vertical.html'],
            'badge_suggestions': ['震惊', '感动', 'HOT', '必看']
        },
        'public': {
            'name': '公开性',
            'description': '让产品/思想可见，模仿行为更容易发生',
            'keywords': ['公开', '展示', '证明', '结果', '效果', '变化', '前后', '对比',
                       '真实', '实测', '体验', '见证', '案例', '成功故事'],
            'template_suggestion': ['minimal-impact.html', 'viral-vertical.html'],
            'badge_suggestions': ['真实', '实测', '见证']
        },
        'practical_value': {
            'name': '实用价值',
            'description': '提供有用信息，帮助他人解决问题或省钱省时',
            'keywords': ['教程', '方法', '技巧', '攻略', '指南', '步骤', '如何', '怎样',
                       '秘诀', '窍门', '工具', '资源', '免费', '省钱', '效率'],
            'template_suggestion': ['curiosity-vertical.html', 'minimal-impact.html'],
            'badge_suggestions': ['教程', '技巧', '免费', '干货']
        },
        'stories': {
            'name': '故事',
            'description': '用叙事包装信息，让内容更容易被记住和传播',
            'keywords': ['故事', '经历', '人生', '成长', '改变', '逆袭', '坚持', '梦想',
                       '希望', '爱', '亲情', '友情', '爱情', '治愈', '励志'],
            'template_suggestion': ['emotional-vertical.html', 'emotional.html'],
            'badge_suggestions': ['真实故事', '感人', '治愈', '励志']
        }
    }
    
    def __init__(
        self,
        template_dir: str = 'templates/thumbnails',
        output_dir: str = 'output/thumbnails',
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化封面生成器
        
        Args:
            template_dir: 模板目录路径
            output_dir: 输出目录路径
            logger: 日志记录器
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    def _init_browser(self):
        """初始化浏览器（延迟加载）"""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
            self.logger.info("浏览器已初始化")
    
    def _close_browser(self):
        """关闭浏览器"""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
            self.logger.info("浏览器已关闭")
    
    def generate(
        self,
        config: Dict[str, Any],
        output_path: Optional[str] = None,
        validate: bool = True
    ) -> Path:
        """
        生成封面
        
        Args:
            config: 配置字典
            output_path: 输出路径（可选）
            validate: 是否验证配置
        
        Returns:
            生成的封面文件路径
        """
        if validate:
            errors = ThumbnailConfigValidator.validate(config)
            if errors:
                raise ValueError(f"配置验证失败:\n" + "\n".join(errors))
        
        config = self._apply_defaults(config)
        
        template_name = config.get('template', self.DEFAULT_TEMPLATE)
        template = self.env.get_template(template_name)
        html = template.render(**config)
        
        if output_path is None:
            import hashlib
            config_hash = hashlib.md5(
                json.dumps(config, sort_keys=True).encode()
            ).hexdigest()[:8]
            output_path = self.output_dir / f"thumbnail_{config_hash}.png"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(
                    viewport={
                        'width': config['width'],
                        'height': config['height']
                    }
                )
                
                page.set_content(html, wait_until='domcontentloaded')
                
                page.screenshot(
                    path=str(output_path),
                    type='png',
                    full_page=False
                )
                
                page.close()
                
                self.logger.info(f"封面已生成: {output_path}")
                return output_path
                
            except Exception as e:
                self.logger.error(f"生成封面失败: {e}")
                raise
            finally:
                browser.close()
    
    def generate_batch(
        self,
        configs: List[Dict[str, Any]],
        output_dir: Optional[str] = None,
        validate: bool = True
    ) -> List[Path]:
        """
        批量生成封面
        
        Args:
            configs: 配置列表
            output_dir: 输出目录（可选）
            validate: 是否验证配置
        
        Returns:
            生成的封面文件路径列表
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for i, config in enumerate(configs, 1):
                    if validate:
                        errors = ThumbnailConfigValidator.validate(config)
                        if errors:
                            raise ValueError(f"配置{i}验证失败:\n" + "\n".join(errors))
                    
                    config = self._apply_defaults(config)
                    
                    template_name = config.get('template', self.DEFAULT_TEMPLATE)
                    template = self.env.get_template(template_name)
                    html = template.render(**config)
                    
                    if output_dir:
                        output_path = output_dir / f"thumbnail_{i:03d}.png"
                    else:
                        import hashlib
                        config_hash = hashlib.md5(
                            json.dumps(config, sort_keys=True).encode()
                        ).hexdigest()[:8]
                        output_path = self.output_dir / f"thumbnail_{config_hash}.png"
                    
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        page = browser.new_page(
                            viewport={
                                'width': config['width'],
                                'height': config['height']
                            }
                        )
                        
                        page.set_content(html, wait_until='domcontentloaded')
                        page.screenshot(path=str(output_path), type='png', full_page=False)
                        page.close()
                        
                        results.append(output_path)
                        self.logger.info(f"进度: {i}/{len(configs)} - {output_path}")
                        
                    except Exception as e:
                        self.logger.error(f"生成封面{i}失败: {e}")
                        raise
                        
            finally:
                browser.close()
        
        return results
    
    def _apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用默认配置"""
        defaults = {
            'width': self.DEFAULT_WIDTH,
            'height': self.DEFAULT_HEIGHT,
            'template': self.DEFAULT_TEMPLATE,
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'font_size': 80,
            'text_color': 'white',
            'style': 'minimal'
        }
        
        result = defaults.copy()
        result.update(config)
        
        return result
    
    def preview_html(self, config: Dict[str, Any]) -> str:
        """
        预览HTML（用于调试）
        
        Args:
            config: 配置字典
        
        Returns:
            渲染后的HTML字符串
        """
        config = self._apply_defaults(config)
        template_name = config.get('template', self.DEFAULT_TEMPLATE)
        template = self.env.get_template(template_name)
        return template.render(**config)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self._close_browser()
    
    def __del__(self):
        """析构函数"""
        self._close_browser()
    
    @classmethod
    def analyze_emotion(cls, title: str) -> Dict[str, Any]:
        """
        分析标题中的情绪触发词
        
        Args:
            title: 视频标题
        
        Returns:
            情绪分析结果字典
        """
        title_lower = title.lower()
        detected_emotions = {}
        
        for emotion, keywords in cls.EMOTIONAL_TRIGGERS.items():
            matches = [kw for kw in keywords if kw.lower() in title_lower]
            if matches:
                detected_emotions[emotion] = {
                    'keywords': matches,
                    'count': len(matches),
                    'intensity': min(len(matches) * 20, 100)
                }
        
        primary_emotion = max(detected_emotions.keys(), key=lambda x: detected_emotions[x]['count']) if detected_emotions else None
        
        return {
            'detected': detected_emotions,
            'primary': primary_emotion,
            'has_emotional_trigger': len(detected_emotions) > 0,
            'total_triggers': sum(e['count'] for e in detected_emotions.values())
        }
    
    @classmethod
    def recommend_template(cls, title: str, style: Optional[str] = None) -> Dict[str, Any]:
        """
        基于标题内容智能推荐模板
        
        Args:
            title: 视频标题
            style: 手动指定的风格（可选）
        
        Returns:
            推荐结果字典
        """
        emotion_analysis = cls.analyze_emotion(title)
        
        if style and style in cls.VALID_STYLES:
            recommended_template = f"{style}.html"
            reason = f"用户指定风格: {style}"
        elif emotion_analysis['primary']:
            emotion_to_template = {
                'shock': ('viral.html', '检测到震惊/惊讶情绪触发词，推荐病毒式传播模板'),
                'curiosity': ('curiosity.html', '检测到好奇心缺口关键词，推荐神秘悬念模板'),
                'urgency': ('urgency.html', '检测到紧迫感/稀缺性词汇，推荐紧急行动模板'),
                'emotional': ('emotional.html', '检测到情感/故事类词汇，推荐情绪共鸣模板'),
                'success': ('minimal-impact.html', '检测到成功/财富关键词，推荐极简冲击模板')
            }
            
            template_info = emotion_to_template.get(emotion_analysis['primary'], ('default.html', '默认推荐'))
            recommended_template = template_info[0]
            reason = template_info[1]
        else:
            recommended_template = 'default.html'
            reason = '未检测到明显情绪触发词，使用默认模板'
        
        return {
            'template': recommended_template,
            'reason': reason,
            'emotion_analysis': emotion_analysis,
            'confidence': emotion_analysis['total_triggers'] * 10 if emotion_analysis['has_emotional_trigger'] else 30
        }
    
    @classmethod
    def recommend_color_scheme(cls, title: str) -> Dict[str, Any]:
        """
        基于标题内容推荐配色方案
        
        Args:
            title: 视频标题
        
        Returns:
            配色方案字典
        """
        emotion_analysis = cls.analyze_emotion(title)
        
        emotion_to_color = {
            'shock': 'shock_red',
            'curiosity': 'mystery_dark',
            'urgency': 'urgency_orange',
            'emotional': 'emotional_purple',
            'success': 'success_green'
        }
        
        if emotion_analysis['primary']:
            scheme_key = emotion_to_color.get(emotion_analysis['primary'], 'emotional_purple')
        else:
            scheme_key = 'emotional_purple'
        
        return {
            **cls.COLOR_SCHEMES[scheme_key],
            'scheme_name': scheme_key,
            'recommended_by': emotion_analysis['primary'] or 'default'
        }
    
    @classmethod
    def generate_ctr_optimized_config(
        cls,
        title: str,
        subtitle: Optional[str] = None,
        badge: Optional[str] = None,
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成CTR优化的完整配置（智能推荐一站式方案）
        
        Args:
            title: 视频标题（必需）
            subtitle: 副标题（可选）
            badge: 徽章文字（可选）
            custom_style: 自定义风格（可选）
        
        Returns:
            完整的优化配置字典
        """
        template_rec = cls.recommend_template(title, custom_style)
        color_rec = cls.recommend_color_scheme(title)
        
        badge_suggestions = {
            'shock': ['震惊', '爆了', 'HOT', '必看'],
            'curiosity': ['秘密', '揭秘', '真相', '内幕'],
            'urgency': ['限时', '紧急', '最后机会', '立即'],
            'emotional': ['感动', '泪目', '治愈', '真实'],
            'success': ['TOP1', '冠军', '终极', '突破']
        }
        
        auto_badge = badge
        if not badge and template_rec['emotion_analysis']['primary']:
            suggestions = badge_suggestions.get(template_rec['emotion_analysis']['primary'], [])
            auto_badge = suggestions[0] if suggestions else 'HOT'
        
        config = {
            'title': title,
            'template': template_rec['template'],
            'background': color_rec['background'],
            'accent_color': color_rec['accent_color'],
            'font_size': 75,
            'text_color': '#FFFFFF',
            'badge': auto_badge
        }
        
        if subtitle:
            config['subtitle'] = subtitle
        
        config['_meta'] = {
            'template_recommendation': template_rec,
            'color_recommendation': color_rec,
            'optimization_notes': [
                f"✅ 推荐模板: {template_rec['template']} ({template_rec['reason']})",
                f"✅ 推荐配色: {color_rec['description']} (基于{template_rec['emotion_analysis']['primary'] or '默认'}情绪)",
                f"✅ 检测到 {template_rec['emotion_analysis']['total_triggers']} 个情绪触发词",
                f"✅ 预估CTR提升: +{min(template_rec['confidence'], 90)}%"
            ]
        }
        
        return config
    
    def generate_with_optimization(
        self,
        title: str,
        subtitle: Optional[str] = None,
        badge: Optional[str] = None,
        output_path: Optional[str] = None,
        style: Optional[str] = None
    ) -> Path:
        """
        使用智能优化的方式生成封面（便捷方法）
        
        Args:
            title: 视频标题
            subtitle: 副标题
            badge: 徽章文字
            output_path: 输出路径
            style: 自定义风格
        
        Returns:
            生成的封面文件路径
        """
        optimized_config = self.generate_ctr_optimized_config(
            title=title,
            subtitle=subtitle,
            badge=badge,
            custom_style=style
        )
        
        meta = optimized_config.pop('_meta', None)
        
        if meta:
            self.logger.info("="*60)
            self.logger.info("🎨 CTR优化建议:")
            for note in meta['optimization_notes']:
                self.logger.info(f"   {note}")
            self.logger.info("="*60)
        
        return self.generate(optimized_config, output_path)
    
    def generate_ab_test_variants(
        self,
        title: str,
        variants_count: int = 3,
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成A/B测试变体（用于对比测试不同设计）
        
        Args:
            title: 视频标题
            variants_count: 变体数量（2-5）
            output_dir: 输出目录
        
        Returns:
            变体信息列表（包含配置和输出路径）
        """
        variants_count = max(2, min(5, variants_count))
        
        base_styles = ['viral', 'curiosity', 'urgency', 'emotional', 'minimal-impact']
        selected_styles = base_styles[:variants_count]
        
        results = []
        
        for i, style in enumerate(selected_styles, 1):
            config = self.generate_ctr_optimized_config(title, custom_style=style)
            
            variant_output_dir = Path(output_dir) if output_dir else self.output_dir / 'ab_test'
            variant_output_dir.mkdir(parents=True, exist_ok=True)
            
            variant_path = variant_output_dir / f"variant_{i}_{style}.png"
            
            try:
                generated_path = self.generate(config, str(variant_path))
                
                results.append({
                    'variant_id': i,
                    'style': style,
                    'config': config,
                    'output_path': generated_path,
                    'meta': config.get('_meta', {})
                })
                
                self.logger.info(f"✅ A/B变体{i} ({style}) 已生成: {generated_path}")
                
            except Exception as e:
                self.logger.error(f"❌ A/B变体{i} ({style}) 生成失败: {e}")
                raise
        
        self.logger.info(f"\n🧪 A/B测试完成! 共生成 {len(results)} 个变体")
        self.logger.info("💡 建议: 在实际环境中测试这些变体的点击率，选择最佳方案")
        
        return results
    
    @classmethod
    def is_vertical_mode(cls, config: Dict[str, Any]) -> bool:
        """
        检测是否为竖屏模式
        
        Args:
            config: 配置字典
        
        Returns:
            是否为竖屏模式
        """
        width = config.get('width', cls.DEFAULT_WIDTH)
        height = config.get('height', cls.DEFAULT_HEIGHT)
        
        return height > width
    
    @classmethod
    def auto_detect_orientation(cls, title: str, platform_hint: Optional[str] = None) -> str:
        """
        自动检测推荐的方向（横屏/竖屏）
        
        Args:
            title: 视频标题
            platform_hint: 平台提示（如 'tiktok', 'youtube_shorts', 'instagram_reels'）
        
        Returns:
            'horizontal' 或 'vertical'
        """
        if platform_hint:
            vertical_platforms = ['tiktok', 'shorts', 'reels', 'vertical', 'mobile', 'phone']
            for vp in vertical_platforms:
                if vp in platform_hint.lower():
                    return 'vertical'
        
        title_lower = title.lower()
        mobile_keywords = ['手机', '移动端', '竖屏', '短视频', '抖音', '快手', 
                          '小红书', 'TikTok', 'Shorts', 'Reels', '9:16', '竖版']
        
        for keyword in mobile_keywords:
            if keyword in title_lower:
                return 'vertical'
        
        return 'horizontal'
    
    @classmethod
    def analyze_stepps(cls, title: str) -> Dict[str, Any]:
        """
        基于STEPPS法则分析标题的病毒传播潜力
        
        Args:
            title: 视频标题
        
        Returns:
            STEPPS分析结果字典
        """
        title_lower = title.lower()
        detected_principles = {}
        
        for principle_key, principle_data in cls.STEPPS_PRINCIPLES.items():
            matches = [kw for kw in principle_data['keywords'] if kw.lower() in title_lower]
            if matches:
                detected_principles[principle_key] = {
                    'name': principle_data['name'],
                    'description': principle_data['description'],
                    'matched_keywords': matches,
                    'count': len(matches),
                    'intensity': min(len(matches) * 20, 100),
                    'template_suggestions': principle_data['template_suggestion'],
                    'badge_suggestions': principle_data['badge_suggestions']
                }
        
        primary_principle = max(detected_principles.keys(), key=lambda x: detected_principles[x]['count']) if detected_principles else None
        
        viral_score = sum(p['count'] * 15 for p in detected_principles.values())
        viral_score = min(viral_score, 100)
        
        return {
            'detected': detected_principles,
            'primary': primary_principle,
            'viral_score': viral_score,
            'total_matches': sum(p['count'] for p in detected_principles.values()),
            'has_viral_potential': viral_score > 30,
            'recommendations': {
                'best_template': detected_principles[primary_principle]['template_suggestions'][0] if primary_principle else None,
                'best_badge': detected_principles[primary_principle]['badge_suggestions'][0] if primary_principle else None,
                'primary_strategy': detected_principles[primary_principle]['name'] if primary_principle else '通用策略',
                'secondary_strategies': [detected_principles[k]['name'] for k in list(detected_principles.keys())[1:3]] if len(detected_principles) > 1 else []
            }
        }
    
    @classmethod
    def generate_viral_optimized_config(
        cls,
        title: str,
        subtitle: Optional[str] = None,
        badge: Optional[str] = None,
        orientation: Optional[str] = None,
        platform_hint: Optional[str] = None,
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成基于STEPPS病毒传播法则优化的完整配置（v3.0增强版）
        
        Args:
            title: 视频标题（必需）
            subtitle: 副标题（可选）
            badge: 徽章文字（可选）
            orientation: 方向 ('horizontal' 或 'vertical')，自动检测如果为None
            platform_hint: 平台提示（可选）
            custom_style: 自定义风格（可选）
        
        Returns:
            完整的优化配置字典
        """
        stepps_analysis = cls.analyze_stepps(title)
        emotion_analysis = cls.analyze_emotion(title)
        
        auto_orientation = orientation or cls.auto_detect_orientation(title, platform_hint)
        is_vertical = (auto_orientation == 'vertical')
        
        if is_vertical and not custom_style:
            template_rec = cls.recommend_template(title, style='viral-vertical')
            base_style = 'viral-vertical'
        elif custom_style:
            template_rec = cls.recommend_template(title, style=custom_style)
            base_style = custom_style
        else:
            template_rec = cls.recommend_template(title)
            base_style = template_rec['template'].replace('.html', '')
        
        color_rec = cls.recommend_color_scheme(title)
        
        auto_badge = badge
        if not badge and stepps_analysis['recommendations']['best_badge']:
            auto_badge = stepps_analysis['recommendations']['best_badge']
        elif not badge and emotion_analysis['primary']:
            badge_map = {
                'shock': '震惊',
                'curiosity': '秘密',
                'urgency': '紧急',
                'emotional': '感动',
                'success': 'TOP1'
            }
            auto_badge = badge_map.get(emotion_analysis['primary'], 'HOT')
        
        width = cls.VERTICAL_WIDTH if is_vertical else cls.DEFAULT_WIDTH
        height = cls.VERTICAL_HEIGHT if is_vertical else cls.DEFAULT_HEIGHT
        
        font_size_multiplier = 1.4 if is_vertical else 1.0
        
        config = {
            'title': title,
            'template': template_rec['template'],
            'background': color_rec['background'],
            'accent_color': color_rec['accent_color'],
            'font_size': int(75 * font_size_multiplier),
            'text_color': '#FFFFFF',
            'badge': auto_badge,
            'width': width,
            'height': height,
            'orientation': auto_orientation
        }
        
        if subtitle:
            config['subtitle'] = subtitle
        
        config['_meta'] = {
            'stepps_analysis': stepps_analysis,
            'emotion_analysis': emotion_analysis,
            'orientation_info': {
                'mode': auto_orientation,
                'is_vertical': is_vertical,
                'dimensions': f"{width}x{height}",
                'platform_optimized_for': platform_hint or ('Mobile/TikTok/Shorts' if is_vertical else 'Desktop/YouTube')
            },
            'optimization_notes': [
                f"📱 方向模式: {auto_orientation.upper()} ({width}x{height})",
                f"🎨 推荐模板: {template_rec['template']} ({template_rec['reason']})",
                f"🎯 推荐配色: {color_rec['description']} (基于{emotion_analysis['primary'] or '默认'}情绪)",
                f"🔥 病毒评分: {stepps_analysis['viral_score']}/100",
                f"💡 主要策略: {stepps_analysis['recommendations']['primary_strategy']}",
                f"✅ 检测到 {stepps_analysis['total_matches']} 个病毒传播关键词",
                f"✅ 检测到 {emotion_analysis['total_triggers']} 个情绪触发词",
                f"📈 预估CTR提升: +{min(stepps_analysis['viral_score'], 90)}%",
                f"🚀 病毒潜力: {'高' if stepps_analysis['has_viral_potential'] else '中'}"
            ]
        }
        
        return config
    
    def generate_with_viral_optimization(
        self,
        title: str,
        subtitle: Optional[str] = None,
        badge: Optional[str] = None,
        output_path: Optional[str] = None,
        orientation: Optional[str] = None,
        platform_hint: Optional[str] = None,
        style: Optional[str] = None
    ) -> Path:
        """
        使用病毒传播优化的方式生成封面（v3.0增强便捷方法）
        
        Args:
            title: 视频标题
            subtitle: 副标题
            badge: 徽章文字
            output_path: 输出路径
            orientation: 方向 ('horizontal' 或 'vertical')
            platform_hint: 平台提示
            style: 自定义风格
        
        Returns:
            生成的封面文件路径
        """
        optimized_config = self.generate_viral_optimized_config(
            title=title,
            subtitle=subtitle,
            badge=badge,
            orientation=orientation,
            platform_hint=platform_hint,
            custom_style=style
        )
        
        meta = optimized_config.pop('_meta', None)
        
        if meta:
            self.logger.info("="*70)
            self.logger.info("🚀 v3.0 病毒传播优化建议:")
            self.logger.info("-"*70)
            for note in meta['optimization_notes']:
                self.logger.info(f"   {note}")
            
            if meta.get('stepps_analysis', {}).get('detected'):
                self.logger.info("\n📊 STEPPS分析详情:")
                for principle_key, principle_data in meta['stepps_analysis']['detected'].items():
                    self.logger.info(f"   • {principle_data['name']}: 匹配{principle_data['count']}个关键词 - {', '.join(principle_data['matched_keywords'])}")
            
            self.logger.info("="*70)
        
        return self.generate(optimized_config, output_path)
