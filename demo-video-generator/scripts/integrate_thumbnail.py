#!/usr/bin/env python3
"""
封面生成功能整合到视频生成器
将封面生成功能无缝集成到演示视频生成流程中
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

print("🔧 开始整合封面生成功能到视频生成器...")
print("="*60)

# 读取现有的视频生成器代码
video_gen_path = Path(__file__).parent.parent / 'lib' / 'demo_video_generator.py'

with open(video_gen_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经整合
if 'generate_thumbnail' in content:
    print("✅ 封面生成功能已经整合！")
    print("="*60)
    sys.exit(0)

# 添加导入
import_section = """from video_recorder import VideoRecorder
from config_validator import ConfigValidator"""

new_import_section = """from video_recorder import VideoRecorder
from config_validator import ConfigValidator
from thumbnail_generator import CodeBasedThumbnailGenerator"""

content = content.replace(import_section, new_import_section)

# 在 DemoVideoGenerator 类的 __init__ 方法中添加封面配置
init_section = """        self.video_composer = VideoComposer(
            video_config=self.config['video'],
            subtitle_config=self.config['subtitle'],
            logger=self.logger
        )"""

new_init_section = """        self.video_composer = VideoComposer(
            video_config=self.config['video'],
            subtitle_config=self.config['subtitle'],
            logger=self.logger
        )
        
        # 封面配置
        self.thumbnail_config = self.config.get('thumbnail', {})"""

content = content.replace(init_section, new_init_section)

# 在 generate 方法中添加封面生成
generate_end_section = """            self.logger.info("="*60)
            self.logger.info("✅ 演示视频生成完成！")
            self.logger.info("="*60)
            self.logger.info(f"📁 输出目录: {self.output_dir}")
            self.logger.info(f"🎬 视频文件: {self.output_file}")
            self.logger.info(f"📝 字幕文件: {self.subtitle_file}")
            self.logger.info(f"🎵 音频文件: {self.audio_file}")"""

new_generate_end_section = """            # 生成封面
            thumbnail_path = self._generate_thumbnail()
            
            self.logger.info("="*60)
            self.logger.info("✅ 演示视频生成完成！")
            self.logger.info("="*60)
            self.logger.info(f"📁 输出目录: {self.output_dir}")
            self.logger.info(f"🎬 视频文件: {self.output_file}")
            if thumbnail_path:
                self.logger.info(f"🖼️  封面文件: {thumbnail_path}")
            self.logger.info(f"📝 字幕文件: {self.subtitle_file}")
            self.logger.info(f"🎵 音频文件: {self.audio_file}")"""

content = content.replace(generate_end_section, new_generate_end_section)

# 添加封面生成方法（在类的末尾）
class_end = """        except Exception as e:
            self.logger.error(f"生成演示视频失败: {e}")
            raise"""

new_class_end = """        except Exception as e:
            self.logger.error(f"生成演示视频失败: {e}")
            raise
    
    def _generate_thumbnail(self):
        \"\"\"
        生成视频封面
        
        Returns:
            生成的封面文件路径
        \"\"\"
        if not self.thumbnail_config.get('enabled', True):
            self.logger.info("封面生成已禁用")
            return None
        
        try:
            self.logger.info("开始生成封面...")
            
            generator = CodeBasedThumbnailGenerator(
                template_dir=self.thumbnail_config.get('template_dir', 'templates/thumbnails'),
                output_dir=self.output_dir,
                logger=self.logger
            )
            
            # 准备封面数据
            thumbnail_data = {
                'title': self.project_config.get('title', 'Demo Video'),
                'subtitle': self.project_config.get('description', ''),
                'template': self.thumbnail_config.get('template', 'default.html'),
                'background': self.thumbnail_config.get('background'),
                'font_size': self.thumbnail_config.get('font_size', 80),
                'text_color': self.thumbnail_config.get('text_color', 'white'),
                'badge': self.thumbnail_config.get('badge'),
                'brand': self.thumbnail_config.get('brand'),
                'author': self.thumbnail_config.get('author'),
                'accent_color': self.thumbnail_config.get('accent_color', '#ffd700')
            }
            
            # 移除None值
            thumbnail_data = {k: v for k, v in thumbnail_data.items() if v is not None}
            
            # 生成封面
            output_path = generator.generate(thumbnail_data, validate=True)
            
            self.logger.info(f"✅ 封面已生成: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"生成封面失败: {e}")
            self.logger.warning("继续生成视频，跳过封面生成")
            return None"""

content = content.replace(class_end, new_class_end)

# 写回文件
with open(video_gen_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 封面生成功能已成功整合到视频生成器！")
print("="*60)
print("\n📝 使用方法：")
print("在配置文件中添加 'thumbnail' 配置项")
print("\n📖 示例配置：")
print("""
thumbnail:
  enabled: true
  template: default.html
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
  badge: NEW
  brand: Demo Video Generator
""")
