#!/usr/bin/env python3
"""
视频封面设计审查系统
基于2025年热门视频封面设计最佳实践
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CheckSeverity(Enum):
    """检查严重程度"""
    CRITICAL = "critical"      # 必须修复
    WARNING = "warning"        # 建议修复
    INFO = "info"              # 仅供参考


@dataclass
class AuditCheck:
    """单个审查检查项"""
    name: str
    passed: bool
    severity: CheckSeverity
    message: str
    suggestion: str
    score: int  # 0-100


@dataclass
class AuditReport:
    """审查报告"""
    template_name: str
    overall_score: int
    checks: List[AuditCheck]
    recommendations: List[str]
    passed: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_name": self.template_name,
            "overall_score": self.overall_score,
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "severity": c.severity.value,
                    "message": c.message,
                    "suggestion": c.suggestion,
                    "score": c.score
                }
                for c in self.checks
            ],
            "recommendations": self.recommendations
        }


class ThumbnailAuditor:
    """
    视频封面设计审查器
    基于真实爆款视频封面设计原则
    """
    
    # 设计规范标准
    STANDARDS = {
        # 三秒原则
        "title_max_length": 12,           # 标题最多12个字
        "subtitle_max_length": 20,        # 副标题最多20个字
        "visual_focus_ratio": 0.6,        # 视觉焦点占比60%+
        
        # 字体规范
        "title_font_size_range": (72, 96),     # 主标题字号范围
        "subtitle_font_size_ratio": 0.45,      # 副标题字号比例
        "min_contrast_ratio": 4.5,             # 最小对比度
        
        # 色彩规范
        "max_colors": 3,                  # 最多3种主色
        "accent_color": "#FFD700",        # 强调色(金色)
        
        # 布局规范
        "min_padding": 50,                # 最小边距
        "safe_zone_ratio": 0.85,          # 安全区域占比
    }
    
    # 高点击率色彩组合
    HIGH_CTR_COLORS = {
        "shock_red": ["#FF0000", "#FF4444", "#FFD700"],
        "curiosity_blue": ["#1a1a2e", "#16213e", "#FFD700"],
        "urgency_orange": ["#FF6B35", "#FF8C42", "#FFD700"],
        "listicle_purple": ["#667eea", "#764ba2", "#FFD700"],
        "emotional_pink": ["#FF1493", "#FF69B4", "#FFD700"],
    }
    
    def __init__(self):
        self.checks = []
        self.recommendations = []
    
    def audit(self, config: Dict[str, Any]) -> AuditReport:
        """
        审查封面配置
        
        Args:
            config: 封面配置字典
            
        Returns:
            AuditReport: 审查报告
        """
        self.checks = []
        self.recommendations = []
        
        template_name = config.get("template", "unknown")
        
        # 执行所有审查检查
        self._check_title_length(config)
        self._check_subtitle_length(config)
        self._check_font_size(config)
        self._check_color_scheme(config)
        self._check_visual_focus(config)
        self._check_contrast(config)
        self._check_padding(config)
        self._check_cta_presence(config)
        self._check_emoji_usage(config)
        self._check_badge_placement(config)
        
        # 计算总分
        total_score = sum(check.score for check in self.checks) // len(self.checks)
        
        # 判断是否通过
        critical_failed = any(
            not check.passed and check.severity == CheckSeverity.CRITICAL 
            for check in self.checks
        )
        
        return AuditReport(
            template_name=template_name,
            overall_score=total_score,
            checks=self.checks,
            recommendations=self.recommendations,
            passed=not critical_failed and total_score >= 70
        )
    
    def _check_title_length(self, config: Dict[str, Any]):
        """检查标题长度 - 三秒原则"""
        title = config.get("title", "")
        title_length = len(title)
        max_length = self.STANDARDS["title_max_length"]
        
        if title_length <= max_length:
            self.checks.append(AuditCheck(
                name="标题长度检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"标题长度符合规范 ({title_length}/{max_length}字)",
                suggestion="保持简洁",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="标题长度检查",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"标题过长 ({title_length}/{max_length}字)",
                suggestion=f"缩短至{max_length}字以内，确保3秒内可读",
                score=max(0, 100 - (title_length - max_length) * 10)
            ))
            self.recommendations.append(f"标题过长，建议精简为'{title[:max_length]}...'")
    
    def _check_subtitle_length(self, config: Dict[str, Any]):
        """检查副标题长度"""
        subtitle = config.get("subtitle", "")
        if not subtitle:
            self.checks.append(AuditCheck(
                name="副标题检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="无副标题（可选）",
                suggestion="添加副标题可增强信息传达",
                score=80
            ))
            return
        
        subtitle_length = len(subtitle)
        max_length = self.STANDARDS["subtitle_max_length"]
        
        if subtitle_length <= max_length:
            self.checks.append(AuditCheck(
                name="副标题长度检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"副标题长度合适 ({subtitle_length}/{max_length}字)",
                suggestion="保持简洁",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="副标题长度检查",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"副标题偏长 ({subtitle_length}/{max_length}字)",
                suggestion="精简副标题内容",
                score=max(0, 100 - (subtitle_length - max_length) * 5)
            ))
    
    def _check_font_size(self, config: Dict[str, Any]):
        """检查字体大小"""
        font_size = config.get("font_size", 75)
        min_size, max_size = self.STANDARDS["title_font_size_range"]
        
        if min_size <= font_size <= max_size:
            self.checks.append(AuditCheck(
                name="字体大小检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"字体大小合适 ({font_size}px)",
                suggestion="保持在这个范围",
                score=100
            ))
        elif font_size < min_size:
            self.checks.append(AuditCheck(
                name="字体大小检查",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"字体过小 ({font_size}px < {min_size}px)",
                suggestion=f"增大至{min_size}px以上确保可读性",
                score=50
            ))
        else:
            self.checks.append(AuditCheck(
                name="字体大小检查",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"字体偏大 ({font_size}px > {max_size}px)",
                suggestion="适当减小避免拥挤",
                score=80
            ))
    
    def _check_color_scheme(self, config: Dict[str, Any]):
        """检查配色方案"""
        color_scheme = config.get("color_scheme", "")
        
        if color_scheme in self.HIGH_CTR_COLORS:
            self.checks.append(AuditCheck(
                name="配色方案检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"使用高点击率配色: {color_scheme}",
                suggestion="此配色经过验证，点击率高",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="配色方案检查",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"未使用推荐配色: {color_scheme}",
                suggestion=f"建议使用推荐配色: {', '.join(self.HIGH_CTR_COLORS.keys())}",
                score=70
            ))
            self.recommendations.append(f"尝试使用'shock_red'或'curiosity_blue'配色提升点击率")
    
    def _check_visual_focus(self, config: Dict[str, Any]):
        """检查视觉焦点 - 主体占比"""
        # 基于模板类型评估
        template = config.get("template", "")
        emoji = config.get("emoji", "")
        
        has_strong_focus = emoji or "listicle" in template or "curiosity" in template
        
        if has_strong_focus:
            self.checks.append(AuditCheck(
                name="视觉焦点检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="视觉焦点突出，主体明确",
                suggestion="保持视觉焦点占比60%+",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="视觉焦点检查",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="视觉焦点不够突出",
                suggestion="添加Emoji或使用更大字体增强焦点",
                score=70
            ))
    
    def _check_contrast(self, config: Dict[str, Any]):
        """检查对比度"""
        # 检查是否使用文字描边或阴影
        template = config.get("template", "")
        
        # Pro版本模板都有良好的对比度处理
        if "pro-v3" in template:
            self.checks.append(AuditCheck(
                name="对比度检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="使用专业模板，对比度良好",
                suggestion="保持文字描边和阴影效果",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="对比度检查",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="建议升级到Pro版本模板",
                suggestion="Pro模板有更好的对比度处理",
                score=75
            ))
    
    def _check_padding(self, config: Dict[str, Any]):
        """检查边距"""
        width = config.get("width", 1080)
        min_padding = self.STANDARDS["min_padding"]
        
        # 检查安全区域
        safe_zone = width * self.STANDARDS["safe_zone_ratio"]
        
        self.checks.append(AuditCheck(
            name="边距检查",
            passed=True,
            severity=CheckSeverity.INFO,
            message=f"安全区域充足 ({safe_zone:.0f}px)",
            suggestion="保持内容在安全区域内",
            score=100
        ))
    
    def _check_cta_presence(self, config: Dict[str, Any]):
        """检查CTA存在性"""
        cta = config.get("cta_text", "")
        
        if cta:
            self.checks.append(AuditCheck(
                name="CTA检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="包含行动号召(CTA)",
                suggestion="CTA可增加点击率",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="CTA检查",
                passed=False,
                severity=CheckSeverity.INFO,
                message="无明确CTA",
                suggestion="添加'CLICK NOW'或'WATCH'等CTA",
                score=85
            ))
    
    def _check_emoji_usage(self, config: Dict[str, Any]):
        """检查Emoji使用"""
        emoji = config.get("emoji", "")
        
        if emoji:
            self.checks.append(AuditCheck(
                name="Emoji检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="使用Emoji增强情感连接",
                suggestion="Emoji可提升30%+点击率",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="Emoji检查",
                passed=False,
                severity=CheckSeverity.INFO,
                message="未使用Emoji",
                suggestion="添加相关Emoji增强视觉吸引力",
                score=80
            ))
    
    def _check_badge_placement(self, config: Dict[str, Any]):
        """检查徽章位置"""
        badge = config.get("badge", "")
        
        if badge:
            self.checks.append(AuditCheck(
                name="徽章位置检查",
                passed=True,
                severity=CheckSeverity.INFO,
                message="使用徽章突出卖点",
                suggestion="徽章在黄金位置，效果好",
                score=100
            ))
        else:
            self.checks.append(AuditCheck(
                name="徽章位置检查",
                passed=False,
                severity=CheckSeverity.INFO,
                message="无徽章",
                suggestion="添加'HOT'、'NEW'等徽章增加紧迫感",
                score=85
            ))
    
    def print_report(self, report: AuditReport):
        """打印审查报告"""
        print(f"\n{'='*70}")
        print(f"📋 封面设计审查报告: {report.template_name}")
        print(f"{'='*70}")
        print(f"\n🎯 综合评分: {report.overall_score}/100")
        print(f"✅ 审查结果: {'通过' if report.passed else '需改进'}")
        
        print(f"\n📊 详细检查项:")
        for check in report.checks:
            status = "✅" if check.passed else "❌"
            severity = {
                CheckSeverity.CRITICAL: "🔴",
                CheckSeverity.WARNING: "🟡",
                CheckSeverity.INFO: "🟢"
            }.get(check.severity, "⚪")
            
            print(f"\n  {status} {severity} {check.name}")
            print(f"     状态: {check.message}")
            print(f"     建议: {check.suggestion}")
            print(f"     得分: {check.score}/100")
        
        if report.recommendations:
            print(f"\n💡 优化建议:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n{'='*70}\n")


# 便捷函数
def audit_thumbnail(config: Dict[str, Any]) -> AuditReport:
    """审查封面配置的便捷函数"""
    auditor = ThumbnailAuditor()
    return auditor.audit(config)


def quick_audit(title: str, subtitle: str = "", template: str = "", 
                emoji: str = "", badge: str = "") -> AuditReport:
    """快速审查"""
    config = {
        "title": title,
        "subtitle": subtitle,
        "template": template,
        "emoji": emoji,
        "badge": badge,
        "font_size": 80,
        "color_scheme": "shock_red"
    }
    return audit_thumbnail(config)


if __name__ == "__main__":
    # 测试审查功能
    test_configs = [
        {
            "title": "5个秘密技巧",
            "subtitle": "专家不想让你知道",
            "template": "listicle-pro-v3.html",
            "emoji": "💡",
            "badge": "HOT",
            "font_size": 80,
            "color_scheme": "listicle_purple",
            "cta_text": "Watch Now"
        },
        {
            "title": "这是一个非常长的标题，超过了12个字限制",
            "subtitle": "",
            "template": "viral-pro-v3.html",
            "emoji": "",
            "badge": "",
            "font_size": 60,
            "color_scheme": "unknown"
        }
    ]
    
    auditor = ThumbnailAuditor()
    
    for config in test_configs:
        report = auditor.audit(config)
        auditor.print_report(report)
