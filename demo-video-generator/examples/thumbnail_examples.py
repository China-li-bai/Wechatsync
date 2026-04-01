"""
编码封面生成器 - 完整示例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def example_basic():
    """基础示例"""
    print("\n=== 基础示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    config = {
        'title': '5步吃透CTR',
        'subtitle': 'YouTube封面优化指南',
        'badge': 'HOT',
        'brand': 'Demo Video Generator',
        'author': 'AI Assistant'
    }
    
    output_path = generator.generate(config)
    print(f"✅ 封面已生成: {output_path}")


def example_tutorial():
    """教程模板示例"""
    print("\n=== 教程模板示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    config = {
        'template': 'tutorial.html',
        'title': 'Python入门教程',
        'subtitle': '从零开始学编程',
        'badge': 'NEW',
        'brand': 'Demo Video Generator',
        'steps': 5,
        'author': 'AI Assistant',
        'background': 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)',
        'accent_color': '#ffd700'
    }
    
    output_path = generator.generate(config)
    print(f"✅ 教程封面已生成: {output_path}")


def example_review():
    """评测模板示例"""
    print("\n=== 评测模板示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    config = {
        'template': 'review.html',
        'title': 'iPhone 15 Pro',
        'subtitle': '深度评测',
        'rating': 5,
        'badge': '推荐',
        'brand': 'Tech Review',
        'background': 'linear-gradient(135deg, #2ec4b6 0%, #e71d36 100%)',
        'accent_color': '#ffd700'
    }
    
    output_path = generator.generate(config)
    print(f"✅ 评测封面已生成: {output_path}")


def example_batch():
    """批量生成示例"""
    print("\n=== 批量生成示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    configs = [
        {
            'title': f'教程第{i}集',
            'subtitle': f'学习Python的第{i}天',
            'badge': 'NEW' if i == 1 else None,
            'brand': 'Python教程'
        }
        for i in range(1, 6)
    ]
    
    output_paths = generator.generate_batch(configs, output_dir='output/batch')
    print(f"✅ 批量生成了 {len(output_paths)} 个封面")
    
    for i, path in enumerate(output_paths, 1):
        print(f"  {i}. {path.name}")


def example_custom_style():
    """自定义样式示例"""
    print("\n=== 自定义样式示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    config = {
        'title': '自定义封面',
        'subtitle': '完全自定义样式',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'font_size': 100,
        'text_color': 'white',
        'badge': 'CUSTOM',
        'accent_color': '#00d9ff',
        'brand': 'My Brand',
        'author': 'Custom Author'
    }
    
    output_path = generator.generate(config)
    print(f"✅ 自定义封面已生成: {output_path}")


def example_tech_style():
    """技术风格示例"""
    print("\n=== 技术风格示例 ===")
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    config = {
        'template': 'tutorial.html',
        'title': 'React Hooks详解',
        'subtitle': '从入门到精通',
        'badge': 'TECH',
        'brand': '前端开发',
        'steps': 10,
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'accent_color': '#00d9ff',
        'style': 'tech'
    }
    
    output_path = generator.generate(config)
    print(f"✅ 技术风格封面已生成: {output_path}")


def example_context_manager():
    """上下文管理器示例"""
    print("\n=== 上下文管理器示例 ===")
    
    with CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    ) as generator:
        config = {
            'title': '上下文管理器',
            'subtitle': '自动资源管理'
        }
        
        output_path = generator.generate(config)
        print(f"✅ 封面已生成: {output_path}")
    
    print("✅ 资源已自动清理")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "="*60)
    print("🎨 编码封面生成器 - 完整示例")
    print("="*60)
    
    examples = [
        example_basic,
        example_tutorial,
        example_review,
        example_batch,
        example_custom_style,
        example_tech_style,
        example_context_manager
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ 示例失败: {example.__name__}")
            print(f"   错误: {e}")
    
    print("\n" + "="*60)
    print("✅ 所有示例运行完成！")
    print("="*60)


if __name__ == '__main__':
    run_all_examples()
