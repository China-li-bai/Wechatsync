#!/usr/bin/env python3
"""
智能文案引擎 v2.0
基于AIDA模型和营销心理学的专业文案生成系统

核心功能:
- AIDA框架集成 (Attention-Interest-Desire-Action)
- 多种钩子生成 (痛点/结果/好奇/身份)
- 深度页面分析 (价值主张/痛点/目标用户)
- 场景化脚本生成
- 情感触发词优化

参考来源:
- [AIDA Framework for SaaS](https://blogsthatsell.com/blog/aida-framework-for-saas/)
- [21 ad hooks for SaaS](https://productkit.ai/blog/ad-hooks-for-saas-from-experts)
- [Video Hook Strategy](https://scriptstorm.ai/blog/video-hook-strategy-first-3-seconds)
"""

import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PageInsight:
    """页面深度洞察"""
    value_proposition: str = ""
    pain_points: List[str] = field(default_factory=list)
    target_audience: str = ""
    use_cases: List[str] = field(default_factory=list)
    social_proof: List[str] = field(default_factory=list)
    unique_selling_points: List[str] = field(default_factory=list)
    emotional_triggers: List[str] = field(default_factory=list)
    key_benefits: List[str] = field(default_factory=list)


@dataclass
class SceneScript:
    """场景脚本"""
    scene_type: str = ""
    hook: str = ""
    narrative: str = ""
    benefit: str = ""
    visual_cue: str = ""
    duration: float = 0.0


class HookGenerator:
    """钩子生成器 - 基于真实SaaS案例的模板库"""
    
    TEMPLATES = {
        'pain_point': [
            "你是否还在为{pain_point}而烦恼？",
            "受够了{pain_point}吗？今天给你介绍一个神器！",
            "还在手动{pain_point}？你out了！",
            "{pain_point}？99%的人都在浪费时间做这件事...",
            "别再为{pain_point}头疼了，这个工具能帮你解决",
        ],
        'result_first': [
            "用这个工具，我只花了{time}就完成了{task}",
            "不可思议！用这个方法，我的{metric}提升了{percentage}",
            "原来{task}可以这么简单！",
            "用了这个工具后，我的效率直接翻倍！",
            "从{old_state}到{new_state}，我只用了{time}",
        ],
        'curiosity': [
            "你绝对想不到，{topic}竟然可以这么简单",
            "揭秘：为什么{number}个用户都选择{product}",
            "今天才知道，原来{feature}这么强大",
            "90%的人都不知道的{topic}秘密...",
            "如果我说{bold_claim}，你信吗？",
        ],
        'identity': [
            "刷到这条视频的{role}，恭喜你！找对地方了",
            "作为{role}，这个工具你必须知道",
            "如果你是{role}，千万别划走！这可能是你今年最重要的发现",
            "所有{role}请注意，这个工具专为你打造",
        ],
        'shock_value': [
            "我被震惊了！{shocking_fact}",
            "不敢相信！{unbelievable_result}",
            "这是我用过最{adjective}的工具，没有之一",
            "说真的，如果你还在{old_way}，你真的亏大了",
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, hook_type: str, **kwargs) -> str:
        """
        生成钩子
        
        Args:
            hook_type: 钩子类型 (pain_point/result_first/curiosity/identity/shock_value)
            **kwargs: 模板变量
        
        Returns:
            生成的钩子文本
        """
        templates = self.TEMPLATES.get(hook_type, self.TEMPLATES['pain_point'])
        
        if not templates:
            return ""
        
        import random
        template = random.choice(templates)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.warning(f"缺少模板变量: {e}")
            return template.format(pain_point="这个问题", **{k: v for k, v in kwargs.items() if k != 'pain_point'})


class DeepPageAnalyzer:
    """深度页面分析器 - 超越DOM提取的语义理解"""
    
    PAIN_POINT_PATTERNS = [
        r' tired of (.+?)[.?]',
        r' struggling with (.+?)[.?]',
        r' frustrated by (.+?)[.?]',
        r' stop wasting (.+?)[.?]',
        r' no more (.+?)[.?]',
        r' say goodbye to (.+?)[.?]',
        r' 受够了(.+)',
        r' 不再需要(.+)',
        r' 告别(.+)',
        r' 拒绝(.+)',
    ]
    
    VALUE_PROP_PATTERNS = [
        r'(?:the|an?)\s+(.+?)\s+(?:for|that)\s+(?:helps?|lets?|allows?|enables?)\s+(?:you\s+to\s+)?(.+)',
        r'(.+?)\s+(?:so you can|so that you can)\s+(.+)',
        r'(.+?)\s+for\s+(.+?)\s+(?:teams?|businesses?|companies?)',
        r'让(.+?)(?:可以|能够)(.+)',
        r'帮助(.+?)(?:实现|完成|解决)(.+)',
    ]
    
    AUDIENCE_PATTERNS = [
        r' for (.+?)(?:\s|,|\.|$)',
        r'(.+?)(?:teams?|businesses?|professionals?|developers?|marketers?|creators?)',
        r'专为(.+?)设计',
        r'面向(.+?)的',
    ]
    
    SOCIAL_PROOF_INDICATORS = [
        'trusted by', 'used by', 'customers', 'users', 'reviews',
        'rating', 'testimonials', 'case studies', 'clients',
        '信任', '用户', '客户', '评价', '推荐'
    ]
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze(self, page_analysis: Dict) -> PageInsight:
        """
        深度分析页面
        
        Args:
            page_analysis: 基础页面分析结果
        
        Returns:
            页面深度洞察
        """
        insight = PageInsight()
        
        try:
            basic_info = page_analysis.get('basic_info', {})
            main_content = page_analysis.get('main_content', [])
            features = page_analysis.get('features', [])
            
            all_text = ' '.join(main_content + features)
            all_text += f" {basic_info.get('description', '')}"
            all_text += f" {basic_info.get('h1', '')}"
            
            insight.value_proposition = self._extract_value_proposition(all_text, basic_info)
            insight.pain_points = self._identify_pain_points(all_text)
            insight.target_audience = self._infer_target_audience(all_text, basic_info)
            insight.use_cases = self._extract_use_cases(features, main_content)
            insight.social_proof = self._extract_social_proof(all_text)
            insight.unique_selling_points = self._extract_usp(features, main_content)
            insight.key_benefits = self._extract_benefits(all_text, features)
            
            self.logger.info(f"深度分析完成: VP={insight.value_proposition[:50]}...")
            
        except Exception as e:
            self.logger.error(f"深度分析失败: {e}")
        
        return insight
    
    def _extract_value_proposition(self, text: str, basic_info: Dict) -> str:
        """提取价值主张"""
        h1 = basic_info.get('h1', '')
        description = basic_info.get('description', '')
        
        if h1 and len(h1) > 10:
            return h1
        
        if description and len(description) > 20:
            return description[:100]
        
        for pattern in self.VALUE_PROP_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    return f"{groups[0].strip()} - {groups[1].strip()}"
                elif len(groups) == 1:
                    return groups[0].strip()
        
        sentences = re.split(r'[。！？.!?\n]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 150:
                return sentence
        
        return text[:100] if text else "未知产品"
    
    def _identify_pain_points(self, text: str) -> List[str]:
        """识别用户痛点"""
        pain_points = []
        
        for pattern in self.PAIN_POINT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            pain_points.extend(matches)
        
        seen = set()
        unique_pains = []
        for pain in pain_points:
            pain = pain.strip()
            if pain not in seen and len(pain) > 5:
                seen.add(pain)
                unique_pains.append(pain)
        
        if not unique_pains:
            default_pains = self._infer_default_pains(text)
            unique_pains.extend(default_pains[:2])
        
        return unique_pains[:5]
    
    def _infer_default_pains(self, text: str) -> List[str]:
        """推断默认痛点"""
        default_pains = []
        
        if any(word in text.lower() for word in ['time', '时间', '快速', 'fast']):
            default_pains.append("花费大量时间在重复性工作上")
        
        if any(word in text.lower() for word in ['cost', '费用', '成本', 'money']):
            default_pains.append("运营成本居高不下")
        
        if any(word in text.lower() for word in ['complex', '复杂', 'difficult']):
            default_pains.append("流程复杂难以管理")
        
        if any(word in text.lower() for word in ['manual', '手动', '手工']):
            default_pains.append("依赖手动操作容易出错")
        
        return default_pains
    
    def _infer_target_audience(self, text: str, basic_info: Dict) -> str:
        """推断目标用户"""
        for pattern in self.AUDIENCE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                audience = match.group(1).strip()
                if len(audience) > 2 and len(audience) < 50:
                    return audience
        
        title = basic_info.get('title', '')
        if title:
            keywords = {
                'developer': '开发者',
                'business': '企业',
                'marketing': '营销人员',
                'creator': '创作者',
                'team': '团队',
                'startup': '创业公司',
                'enterprise': '大型企业',
            }
            for eng, cn in keywords.items():
                if eng in title.lower():
                    return cn
        
        return "用户"
    
    def _extract_use_cases(self, features: List, content: List) -> List[str]:
        """提取使用场景"""
        use_cases = []
        
        use_case_patterns = [
            r'(?:用于|可以|能够|支持)(.{10,50})',
            r'(?:when you|for|to)(.{10,50})',
        ]
        
        all_text = ' '.join(features + content)
        
        for pattern in use_case_patterns:
            matches = re.findall(pattern, all_text)
            use_cases.extend(matches)
        
        return list(set(use_cases))[:5]
    
    def _extract_social_proof(self, text: str) -> List[str]:
        """提取社会证明"""
        proofs = []
        
        number_pattern = r'(\d+[,\d]*(?:\s*(?:users?|customers?|clients?|companies?|用户|客户)))'
        matches = re.findall(number_pattern, text, re.IGNORECASE)
        proofs.extend(matches)
        
        brand_pattern = r'(?:trusted by|used by|包括|服务过)(.{10,100})'
        matches = re.findall(brand_pattern, text, re.IGNORECASE)
        proofs.extend(matches)
        
        return list(set(proofs))[:3]
    
    def _extract_usp(self, features: List, content: List) -> List[str]:
        """提取独特卖点"""
        usp_keywords = [
            ('first', '首创'), ('only', '唯一'), ('best', '最好'),
            ('unique', '独特'), ('advanced', '领先'), ('AI', '智能'),
            ('auto', '自动'), ('instant', '即时'), ('real-time', '实时'),
        ]
        
        usps = []
        all_features = ' '.join(features)
        
        for eng, cn in usp_keywords:
            if eng.lower() in all_features.lower():
                for feature in features:
                    if eng.lower() in feature.lower():
                        usps.append(feature)
                        break
        
        return usps[:5]
    
    def _extract_benefits(self, text: str, features: List) -> List[str]:
        """提取用户利益"""
        benefit_patterns = [
            r'(?:save|节省|降低)(.{5,30})',
            r'(?:increase|提高|提升|增长)(.{5,30})',
            r'(?:faster|更快|easier|更简单|better)(.{5,30})',
            r'(?:help|帮助|enable|让你)(.{5,40})',
        ]
        
        benefits = []
        for pattern in benefit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            benefits.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return list(set(benefits))[:5]


class AIDAFramework:
    """AIDA营销框架实现"""
    
    def __init__(self, hook_generator: HookGenerator):
        self.hook_generator = hook_generator
        self.logger = logging.getLogger(__name__)
    
    def generate_attention(self, insight: PageInsight, product_name: str = "") -> str:
        """生成Attention（吸引注意）阶段文案"""
        if insight.pain_points:
            pain = insight.pain_points[0]
            return self.hook_generator.generate(
                'pain_point',
                pain_point=pain
            )
        
        if insight.value_proposition:
            return self.hook_generator.generate(
                'curiosity',
                topic=insight.value_proposition[:30],
                product=product_name or "这个工具"
            )
        
        return f"今天给你介绍一个超好用的工具：{product_name or '它'}"
    
    def generate_interest(self, insight: PageInsight) -> str:
        """生成Interest（引发兴趣）阶段文案"""
        parts = []
        
        if insight.target_audience:
            parts.append(f"作为{insight.target_audience}，你是不是经常遇到这些问题？")
        
        if insight.pain_points:
            parts.append("\n".join([f"• {pain}" for pain in insight.pain_points[:3]]))
        
        if insight.use_cases:
            parts.append(f"\n特别是在{insight.use_cases[0]}的时候，这些问题尤其突出。")
        
        if not parts:
            return "让我来告诉你为什么这个工具值得你关注。"
        
        return "\n".join(parts)
    
    def generate_desire(self, insight: PageInsight, product_name: str = "") -> str:
        """生成Desire（刺激欲望）阶段文案"""
        parts = []
        
        if insight.value_proposition:
            parts.append(f"\n✨ 核心价值：{insight.value_proposition}")
        
        if insight.key_benefits:
            parts.append("\n🎯 主要功能：")
            for i, benefit in enumerate(insight.key_benefits[:3], 1):
                parts.append(f"  {i}. {benefit}")
        
        if insight.unique_selling_points:
            parts.append("\n💡 独特优势：")
            for usp in insight.unique_selling_points[:2]:
                parts.append(f"  • {usp}")
        
        if insight.social_proof:
            parts.append(f"\n📊 {insight.social_proof[0]}")
        
        if not parts:
            return f"\n{product_name or '这个工具'}能帮助你大幅提升工作效率，简化工作流程。"
        
        return "\n".join(parts)
    
    def generate_action(self, insight: PageInsight, product_name: str = "", url: str = "") -> str:
        """生成Action（促成行动）阶段文案"""
        actions = [
            f"🚀 立即体验{product_name or '这个工具'}，开启高效工作新模式！",
            f"💪 别再犹豫了，{product_name or '它'}值得你拥有！",
            f"✨ 点击链接，亲自感受{product_name or '它的强大功能'}！",
        ]
        
        if url:
            actions.append(f"🔗 访问 {url} 了解更多")
        
        import random
        return random.choice(actions)


class CopywritingEngine:
    """智能文案引擎 - 整合所有组件的主类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.hook_generator = HookGenerator()
        self.deep_analyzer = DeepPageAnalyzer(logger)
        self.aida_framework = AIDAFramework(self.hook_generator)
    
    def generate_compelling_copy(self, page_analysis: Dict, 
                                product_name: str = "",
                                url: str = "") -> Dict[str, Any]:
        """
        生成有吸引力的完整文案
        
        Args:
            page_analysis: 基础页面分析结果
            product_name: 产品名称
            url: 产品URL
        
        Returns:
            包含完整文案的字典
        """
        self.logger.info("开始生成智能文案...")
        
        try:
            insight = self.deep_analyzer.analyze(page_analysis)
            
            attention = self.aida_framework.generate_attention(insight, product_name)
            interest = self.aida_framework.generate_interest(insight)
            desire = self.aida_framework.generate_desire(insight, product_name)
            action = self.aida_framework.generate_action(insight, product_name, url)
            
            full_script = self._assemble_full_script(
                attention, interest, desire, action
            )
            
            scenes = self._generate_scene_scripts(
                insight, attention, interest, desire, action
            )
            
            result = {
                'insight': {
                    'value_proposition': insight.value_proposition,
                    'pain_points': insight.pain_points,
                    'target_audience': insight.target_audience,
                    'key_benefits': insight.key_benefits,
                    'social_proof': insight.social_proof,
                },
                'copy': {
                    'hook': attention,
                    'problem': interest,
                    'solution': desire,
                    'cta': action,
                    'full_script': full_script,
                },
                'scenes': scenes,
            }
            
            self.logger.info(f"✅ 文案生成完成: {len(scenes)} 个场景")
            return result
            
        except Exception as e:
            self.logger.error(f"文案生成失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}
    
    def _assemble_full_script(self, attention: str, interest: str, 
                             desire: str, action: str) -> str:
        """组装完整脚本"""
        sections = [
            f"【开场钩子】\n{attention}\n",
            f"【问题共鸣】\n{interest}\n",
            f"【价值展示】\n{desire}\n",
            f"【行动号召】\n{action}"
        ]
        
        return "\n".join(sections)
    
    def _generate_scene_scripts(self, insight: PageInsight, 
                               attention: str, interest: str,
                               desire: str, action: str) -> List[Dict]:
        """生成场景脚本列表"""
        scenes = [
            {
                'name': 'hook',
                'type': 'hook',
                'text': attention,
                'subtitle': '开场',
                'action': 'screenshot',
                'duration_weight': 1.0
            },
            {
                'name': 'problem',
                'type': 'feature',
                'text': interest[:150] if len(interest) > 150 else interest,
                'subtitle': '痛点',
                'action': 'scroll',
                'scroll_distance': 300,
                'duration_weight': 1.3
            },
            {
                'name': 'solution',
                'type': 'demo',
                'text': desire[:200] if len(desire) > 200 else desire,
                'subtitle': '解决方案',
                'action': 'scroll',
                'scroll_distance': 400,
                'duration_weight': 1.5
            },
            {
                'name': 'benefit',
                'type': 'benefit',
                'text': self._extract_key_benefit_text(insight),
                'subtitle': '核心优势',
                'action': 'interact',
                'selector': '',
                'duration_weight': 1.2
            },
            {
                'name': 'cta',
                'type': 'cta',
                'text': action,
                'subtitle': '行动号召',
                'action': 'scroll_to_top',
                'duration_weight': 1.0
            }
        ]
        
        return scenes
    
    def _extract_key_benefit_text(self, insight: PageInsight) -> str:
        """提取关键利益文本"""
        if insight.key_benefits:
            return f"核心优势：{insight.key_benefits[0]}"
        
        if insight.value_proposition:
            return insight.value_proposition
        
        if insight.unique_selling_points:
            return f"独特之处：{insight.unique_selling_points[0]}"
        
        return "这个工具将彻底改变你的工作效率！"
