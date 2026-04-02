#!/usr/bin/env python3
"""
表情模板自动生成系统
自动生成20+种CSS表情的HTML模板
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmotionConfig:
    """表情配置"""
    name: str
    emoji: str
    name_en: str
    eyebrow_angle: int  # 眉毛角度
    eye_shape: str  # 眼睛形状
    mouth_shape: str  # 嘴巴形状
    has_tears: bool = False
    has_blush: bool = False
    has_sweat: bool = False
    has_veins: bool = False
    face_color: str = "#FFD700"
    animations: List[str] = None
    description: str = ""


class EmotionTemplateGenerator:
    """表情模板生成器"""
    
    def __init__(self):
        self.emotions = self._define_emotions()
        self.output_dir = Path("templates/thumbnails/emotions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _define_emotions(self) -> Dict[str, EmotionConfig]:
        """定义所有表情配置"""
        return {
            # 基础情绪
            "happy": EmotionConfig(
                name="开心",
                emoji="😄",
                name_en="happy",
                eyebrow_angle=-20,
                eye_shape="crescent",
                mouth_shape="big_smile",
                has_blush=True,
                face_color="#FFD700",
                animations=["bounce", "shake"],
                description="大笑，眼睛弯成月牙，腮红"
            ),
            "sad": EmotionConfig(
                name="悲伤",
                emoji="😢",
                name_en="sad",
                eyebrow_angle=25,
                eye_shape="downward",
                mouth_shape="frown",
                has_tears=True,
                face_color="#87CEEB",
                animations=["tear_drop", "tremble"],
                description="八字眉，眼角下垂，流泪"
            ),
            "angry": EmotionConfig(
                name="愤怒",
                emoji="😡",
                name_en="angry",
                eyebrow_angle=-40,
                eye_shape="narrow",
                mouth_shape="grit",
                has_veins=True,
                face_color="#FF6B6B",
                animations=["pulse", "shake"],
                description="倒八眉，怒视，咬牙切齿"
            ),
            "surprised": EmotionConfig(
                name="震惊",
                emoji="😱",
                name_en="surprised",
                eyebrow_angle=-30,
                eye_shape="wide",
                mouth_shape="o_shape",
                has_sweat=True,
                face_color="#FFD700",
                animations=["eye_pop", "mouth_open"],
                description="挑眉，大眼，O型嘴，汗珠"
            ),
            "fear": EmotionConfig(
                name="恐惧",
                emoji="😨",
                name_en="fear",
                eyebrow_angle=20,
                eye_shape="wide_scared",
                mouth_shape="wavy",
                has_sweat=True,
                face_color="#E0FFFF",
                animations=["tremble", "shake"],
                description="恐惧眼神，颤抖，冷汗"
            ),
            "disgust": EmotionConfig(
                name="厌恶",
                emoji="🤢",
                name_en="disgust",
                eyebrow_angle=-10,
                eye_shape="squint",
                mouth_shape="nausea",
                face_color="#90EE90",
                animations=["wobble"],
                description="眯眼，恶心表情"
            ),
            
            # 复杂情绪
            "anxious": EmotionConfig(
                name="焦虑",
                emoji="😰",
                name_en="anxious",
                eyebrow_angle=15,
                eye_shape="worried",
                mouth_shape="worry_line",
                has_sweat=True,
                face_color="#F0E68C",
                animations=["sweat_drop", "eyebrow_twitch"],
                description="担忧眉，汗珠，不安"
            ),
            "confused": EmotionConfig(
                name="困惑",
                emoji="😕",
                name_en="confused",
                eyebrow_angle=0,
                eye_shape="question",
                mouth_shape="confused",
                face_color="#FFDAB9",
                animations=["head_tilt"],
                description="歪头，问号眼，迷茫"
            ),
            "embarrassed": EmotionConfig(
                name="尴尬",
                emoji="😅",
                name_en="embarrassed",
                eyebrow_angle=-15,
                eye_shape="nervous",
                mouth_shape="awkward_smile",
                has_sweat=True,
                has_blush=True,
                face_color="#FFB6C1",
                animations=["sweat_drop", "blush_pulse"],
                description="尬笑，流汗，脸红"
            ),
            "disappointed": EmotionConfig(
                name="失望",
                emoji="😞",
                name_en="disappointed",
                eyebrow_angle=30,
                eye_shape="sad",
                mouth_shape="small_frown",
                face_color="#D3D3D3",
                animations=["sigh"],
                description="极度失望，叹气"
            ),
            "tired": EmotionConfig(
                name="疲惫",
                emoji="😫",
                name_en="tired",
                eyebrow_angle=10,
                eye_shape="droopy",
                mouth_shape="exhausted",
                face_color="#DDA0DD",
                animations=["heavy_blink"],
                description="眼皮沉重，困倦"
            ),
            "excited": EmotionConfig(
                name="兴奋",
                emoji="🤩",
                name_en="excited",
                eyebrow_angle=-25,
                eye_shape="star",
                mouth_shape="big_grin",
                has_blush=True,
                face_color="#FF69B4",
                animations=["star_shine", "bounce"],
                description="星星眼，大笑，激动"
            ),
            "suspicious": EmotionConfig(
                name="怀疑",
                emoji="🤨",
                name_en="suspicious",
                eyebrow_angle=-35,
                eye_shape="squint_one",
                mouth_shape="flat",
                face_color="#F4A460",
                animations=["eyebrow_raise"],
                description="挑眉，眯眼，警惕"
            ),
            "proud": EmotionConfig(
                name="得意",
                emoji="😏",
                name_en="proud",
                eyebrow_angle=-15,
                eye_shape="confident",
                mouth_shape="smirk",
                face_color="#FFA07A",
                animations=["smirk_tilt"],
                description="自信眼神，得意笑"
            ),
            "shy": EmotionConfig(
                name="害羞",
                emoji="😳",
                name_en="shy",
                eyebrow_angle=5,
                eye_shape="averted",
                mouth_shape="small_smile",
                has_blush=True,
                face_color="#FFB6C1",
                animations=["blush_intensify"],
                description="脸红，眼神躲闪"
            ),
            "pain": EmotionConfig(
                name="痛苦",
                emoji="😣",
                name_en="pain",
                eyebrow_angle=35,
                eye_shape="squeezed",
                mouth_shape="grimace",
                has_veins=True,
                face_color="#FF6347",
                animations=["wince", "shake"],
                description="痛苦表情，青筋"
            ),
            
            # 极端情绪
            "crazy": EmotionConfig(
                name="疯狂",
                emoji="🤪",
                name_en="crazy",
                eyebrow_angle=-45,
                eye_shape="mismatched",
                mouth_shape="tongue_out",
                face_color="#98FB98",
                animations=["wobble", "spin"],
                description="疯癫，大小眼，吐舌"
            ),
            "desperate": EmotionConfig(
                name="绝望",
                emoji="😩",
                name_en="desperate",
                eyebrow_angle=40,
                eye_shape="pleading",
                mouth_shape="cry",
                has_tears=True,
                face_color="#B0C4DE",
                animations=["cry_heavy", "shake"],
                description="绝望哭泣，恳求"
            ),
            "ecstatic": EmotionConfig(
                name="狂喜",
                emoji="🥳",
                name_en="ecstatic",
                eyebrow_angle=-30,
                eye_shape="closed_joy",
                mouth_shape="laughing",
                has_blush=True,
                face_color="#FFD700",
                animations=["bounce_fast", "sparkle"],
                description="极致快乐，闭眼大笑"
            ),
            "terrified": EmotionConfig(
                name="恐怖",
                emoji="😱",
                name_en="terrified",
                eyebrow_angle=25,
                eye_shape="huge",
                mouth_shape="scream",
                has_sweat=True,
                face_color="#F0F8FF",
                animations=["scream_shake", "sweat_pour"],
                description="极度恐惧，尖叫"
            ),
            "furious": EmotionConfig(
                name="暴怒",
                emoji="🤬",
                name_en="furious",
                eyebrow_angle=-50,
                eye_shape="slit",
                mouth_shape="censored",
                has_veins=True,
                face_color="#DC143C",
                animations=["rage_shake", "steam"],
                description="极度愤怒，青筋暴起"
            ),
            
            # 特殊风格
            "pixel": EmotionConfig(
                name="像素",
                emoji="👾",
                name_en="pixel",
                eyebrow_angle=0,
                eye_shape="pixel",
                mouth_shape="pixel",
                face_color="#FFD700",
                animations=["pixel_bounce"],
                description="8-bit像素风格"
            ),
            "comic": EmotionConfig(
                name="漫画",
                emoji="💥",
                name_en="comic",
                eyebrow_angle=-20,
                eye_shape="comic",
                mouth_shape="comic_shout",
                face_color="#FFA500",
                animations=[["comic_pop"]],
                description="美漫风格，爆炸效果"
            ),
            "minimal": EmotionConfig(
                name="极简",
                emoji="○",
                name_en="minimal",
                eyebrow_angle=0,
                eye_shape="dot",
                mouth_shape="line",
                face_color="#FFFFFF",
                animations=["fade"],
                description="极简线条风格"
            )
        }
    
    def generate_all_templates(self):
        """生成所有表情模板"""
        logger.info(f"开始生成 {len(self.emotions)} 个表情模板...")
        
        generated_files = []
        
        for emotion_id, config in self.emotions.items():
            try:
                html_content = self._generate_emotion_html(emotion_id, config)
                output_file = self.output_dir / f"emotion-{emotion_id}.html"
                output_file.write_text(html_content, encoding='utf-8')
                generated_files.append(output_file)
                logger.info(f"✅ 生成表情: {config.name} ({emotion_id})")
            except Exception as e:
                logger.error(f"❌ 生成失败 {emotion_id}: {e}")
        
        # 生成预览页面
        self._generate_preview_page()
        
        logger.info(f"\n🎉 共生成 {len(generated_files)} 个表情模板")
        return generated_files
    
    def _generate_emotion_html(self, emotion_id: str, config: EmotionConfig) -> str:
        """生成单个表情的HTML"""
        css = self._generate_emotion_css(emotion_id, config)
        html_structure = self._generate_html_structure(emotion_id, config)
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>表情 - {config.name} {config.emoji}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: 1080px;
            height: 1920px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }}

        .container {{
            text-align: center;
        }}

        {css}

        .emotion-label {{
            margin-top: 60px;
            font-size: 72px;
            color: white;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        }}

        .emotion-emoji {{
            font-size: 120px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emotion-emoji">{config.emoji}</div>
        {html_structure}
        <div class="emotion-label">{config.name} - {config.name_en}</div>
    </div>
</body>
</html>"""
    
    def _generate_emotion_css(self, emotion_id: str, config: EmotionConfig) -> str:
        """生成表情CSS"""
        css_parts = []
        
        # 基础容器
        css_parts.append(f"""
        .face-{emotion_id} {{
            width: 400px;
            height: 400px;
            background: {config.face_color};
            border-radius: 50%;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: {emotion_id}-bounce 1s ease-in-out infinite;
        }}

        @keyframes {emotion_id}-bounce {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        """)
        
        # 眉毛
        css_parts.append(f"""
        .face-{emotion_id} .eyebrow {{
            position: absolute;
            width: 80px;
            height: 12px;
            background: #000;
            border-radius: 6px;
            top: 100px;
        }}

        .face-{emotion_id} .eyebrow.left {{
            left: 80px;
            transform: rotate({config.eyebrow_angle}deg);
        }}

        .face-{emotion_id} .eyebrow.right {{
            right: 80px;
            transform: rotate(-{config.eyebrow_angle}deg);
        }}
        """)
        
        # 眼睛
        eye_css = self._get_eye_css(emotion_id, config.eye_shape)
        css_parts.append(eye_css)
        
        # 嘴巴
        mouth_css = self._get_mouth_css(emotion_id, config.mouth_shape)
        css_parts.append(mouth_css)
        
        # 特效
        if config.has_tears:
            css_parts.append(self._get_tear_css(emotion_id))
        if config.has_blush:
            css_parts.append(self._get_blush_css(emotion_id))
        if config.has_sweat:
            css_parts.append(self._get_sweat_css(emotion_id))
        if config.has_veins:
            css_parts.append(self._get_vein_css(emotion_id))
        
        return "\n".join(css_parts)
    
    def _get_eye_css(self, emotion_id: str, eye_shape: str) -> str:
        """获取眼睛CSS"""
        eye_styles = {
            "crescent": "border-radius: 50%; background: transparent; border-top: 8px solid #000;",
            "wide": "border-radius: 50%; width: 70px; height: 80px;",
            "narrow": "border-radius: 50%; width: 60px; height: 30px;",
            "downward": "border-radius: 50% 50% 45% 45%;",
            "star": "clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); background: #FFD700;",
            "pixel": "width: 40px; height: 40px; border-radius: 0;",
            "dot": "width: 20px; height: 20px; border-radius: 50%; background: #000;",
        }
        
        eye_style = eye_styles.get(eye_shape, eye_styles["wide"])
        
        return f"""
        .face-{emotion_id} .eye {{
            position: absolute;
            width: 60px;
            height: 70px;
            background: #FFF;
            border: 5px solid #000;
            top: 140px;
            {eye_style}
        }}

        .face-{emotion_id} .eye.left {{ left: 90px; }}
        .face-{emotion_id} .eye.right {{ right: 90px; }}
        """
    
    def _get_mouth_css(self, emotion_id: str, mouth_shape: str) -> str:
        """获取嘴巴CSS"""
        mouth_styles = {
            "big_smile": "width: 120px; height: 60px; border-radius: 0 0 60px 60px; background: #000;",
            "frown": "width: 80px; height: 40px; border-top: 6px solid #000; border-radius: 50% 50% 0 0;",
            "o_shape": "width: 60px; height: 80px; border-radius: 50%; background: #000;",
            "grit": "width: 100px; height: 30px; background: #FFF; border: 4px solid #000;",
            "line": "width: 60px; height: 4px; background: #000;",
        }
        
        mouth_style = mouth_styles.get(mouth_shape, mouth_styles["big_smile"])
        
        return f"""
        .face-{emotion_id} .mouth {{
            position: absolute;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            {mouth_style}
        }}
        """
    
    def _get_tear_css(self, emotion_id: str) -> str:
        return f"""
        .face-{emotion_id} .tear {{
            position: absolute;
            width: 15px;
            height: 25px;
            background: linear-gradient(to bottom, #87CEEB, #4169E1);
            border-radius: 50%;
            top: 200px;
            animation: tear-fall 1.5s ease-in infinite;
        }}

        .face-{emotion_id} .tear.left {{ left: 100px; }}
        .face-{emotion_id} .tear.right {{ right: 100px; animation-delay: 0.5s; }}

        @keyframes tear-fall {{
            0% {{ transform: translateY(0); opacity: 1; }}
            100% {{ transform: translateY(50px); opacity: 0; }}
        }}
        """
    
    def _get_blush_css(self, emotion_id: str) -> str:
        return f"""
        .face-{emotion_id} .blush {{
            position: absolute;
            width: 60px;
            height: 40px;
            background: rgba(255, 182, 193, 0.6);
            border-radius: 50%;
            top: 200px;
        }}

        .face-{emotion_id} .blush.left {{ left: 60px; }}
        .face-{emotion_id} .blush.right {{ right: 60px; }}
        """
    
    def _get_sweat_css(self, emotion_id: str) -> str:
        return f"""
        .face-{emotion_id} .sweat {{
            position: absolute;
            width: 20px;
            height: 30px;
            background: linear-gradient(to bottom, #E0FFFF, #87CEEB);
            border-radius: 50%;
            top: 80px;
            right: 60px;
            animation: sweat-drop 1s ease-in infinite;
        }}

        @keyframes sweat-drop {{
            0% {{ transform: translateY(0); opacity: 1; }}
            100% {{ transform: translateY(40px); opacity: 0; }}
        }}
        """
    
    def _get_vein_css(self, emotion_id: str) -> str:
        return f"""
        .face-{emotion_id} .vein {{
            position: absolute;
            width: 40px;
            height: 8px;
            background: rgba(139, 0, 0, 0.5);
            border-radius: 4px;
            top: 60px;
        }}

        .face-{emotion_id} .vein.left {{ left: 50px; transform: rotate(-30deg); }}
        .face-{emotion_id} .vein.right {{ right: 50px; transform: rotate(30deg); }}
        """
    
    def _generate_html_structure(self, emotion_id: str, config: EmotionConfig) -> str:
        """生成HTML结构"""
        parts = [f'<div class="face-{emotion_id}">']
        
        # 眉毛
        parts.append('        <div class="eyebrow left"></div>')
        parts.append('        <div class="eyebrow right"></div>')
        
        # 青筋
        if config.has_veins:
            parts.append('        <div class="vein left"></div>')
            parts.append('        <div class="vein right"></div>')
        
        # 眼睛
        parts.append('        <div class="eye left"></div>')
        parts.append('        <div class="eye right"></div>')
        
        # 腮红
        if config.has_blush:
            parts.append('        <div class="blush left"></div>')
            parts.append('        <div class="blush right"></div>')
        
        # 泪珠
        if config.has_tears:
            parts.append('        <div class="tear left"></div>')
            parts.append('        <div class="tear right"></div>')
        
        # 嘴巴
        parts.append('        <div class="mouth"></div>')
        
        # 汗珠
        if config.has_sweat:
            parts.append('        <div class="sweat"></div>')
        
        parts.append('    </div>')
        
        return '\n'.join(parts)
    
    def _generate_preview_page(self):
        """生成预览页面"""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"zh-CN\">",
            "<head>",
            "    <meta charset=\"UTF-8\">",
            "    <title>表情模板库 - Emotion Template Library</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }",
            "        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }",
            "        .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }",
            "        .card h3 { margin: 0 0 10px 0; }",
            "        .card iframe { width: 100%; height: 200px; border: none; border-radius: 5px; }",
            "        .card a { display: block; margin-top: 10px; color: #667eea; text-decoration: none; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>🎭 表情模板库 - Emotion Template Library</h1>",
            "    <p>共 {} 个表情模板</p>".format(len(self.emotions)),
            "    <div class=\"grid\">"
        ]
        
        for emotion_id, config in self.emotions.items():
            html_parts.append(f"""
        <div class="card">
            <h3>{config.emoji} {config.name} ({config.name_en})</h3>
            <iframe src="emotion-{emotion_id}.html"></iframe>
            <a href="emotion-{emotion_id}.html" target="_blank">查看完整模板 →</a>
        </div>""")
        
        html_parts.extend([
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        preview_file = self.output_dir / "index.html"
        preview_file.write_text('\n'.join(html_parts), encoding='utf-8')
        logger.info(f"✅ 生成预览页面: {preview_file}")


# 设置日志
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    generator = EmotionTemplateGenerator()
    generator.generate_all_templates()
