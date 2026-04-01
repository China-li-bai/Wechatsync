"""
编码封面生成器测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from thumbnail_generator import CodeBasedThumbnailGenerator, ThumbnailConfigValidator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_config_validation():
    """测试配置验证"""
    print("\n=== 测试配置验证 ===")
    
    valid_config = {
        'title': '测试标题',
        'subtitle': '测试副标题',
        'width': 1280,
        'height': 720
    }
    
    errors = ThumbnailConfigValidator.validate(valid_config)
    print(f"✅ 有效配置验证: {len(errors)} 个错误")
    
    invalid_config = {
        'width': -100,
        'style': 'invalid_style'
    }
    
    errors = ThumbnailConfigValidator.validate(invalid_config)
    print(f"✅ 无效配置验证: {len(errors)} 个错误")
    for error in errors:
        print(f"  - {error}")


def test_default_template():
    """测试默认模板"""
    print("\n=== 测试默认模板 ===")
    
    config = {
        'title': '5步吃透CTR',
        'subtitle': 'YouTube封面优化指南',
        'badge': 'HOT',
        'brand': 'Demo Video Generator',
        'author': 'AI Assistant'
    }
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    output_path = generator.generate(config)
    print(f"✅ 默认模板生成成功: {output_path}")
    
    assert output_path.exists(), "封面文件不存在"
    assert output_path.stat().st_size > 0, "封面文件为空"
    
    print(f"✅ 文件大小: {output_path.stat().st_size / 1024:.2f} KB")


def test_tutorial_template():
    """测试教程模板"""
    print("\n=== 测试教程模板 ===")
    
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
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    output_path = generator.generate(config)
    print(f"✅ 教程模板生成成功: {output_path}")
    
    assert output_path.exists(), "封面文件不存在"
    assert output_path.stat().st_size > 0, "封面文件为空"


def test_review_template():
    """测试评测模板"""
    print("\n=== 测试评测模板 ===")
    
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
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    output_path = generator.generate(config)
    print(f"✅ 评测模板生成成功: {output_path}")
    
    assert output_path.exists(), "封面文件不存在"
    assert output_path.stat().st_size > 0, "封面文件为空"


def test_batch_generation():
    """测试批量生成"""
    print("\n=== 测试批量生成 ===")
    
    configs = [
        {
            'title': f'测试标题 {i}',
            'subtitle': f'测试副标题 {i}',
            'badge': 'HOT' if i % 2 == 0 else None,
            'brand': 'Demo Video Generator'
        }
        for i in range(1, 4)
    ]
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    output_paths = generator.generate_batch(configs)
    
    print(f"✅ 批量生成成功: {len(output_paths)} 个封面")
    
    for i, path in enumerate(output_paths, 1):
        print(f"  {i}. {path.name} ({path.stat().st_size / 1024:.2f} KB)")


def test_preview_html():
    """测试HTML预览"""
    print("\n=== 测试HTML预览 ===")
    
    config = {
        'title': 'HTML预览测试',
        'subtitle': '这是一个测试'
    }
    
    generator = CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    )
    
    html = generator.preview_html(config)
    
    print(f"✅ HTML预览成功: {len(html)} 字符")
    print(f"✅ 包含title: {'title' in html.lower()}")
    print(f"✅ 包含subtitle: {'subtitle' in html.lower()}")


def test_context_manager():
    """测试上下文管理器"""
    print("\n=== 测试上下文管理器 ===")
    
    config = {
        'title': '上下文管理器测试',
        'subtitle': '自动资源管理'
    }
    
    with CodeBasedThumbnailGenerator(
        template_dir='templates/thumbnails',
        output_dir='output/thumbnails'
    ) as generator:
        output_path = generator.generate(config)
        print(f"✅ 上下文管理器生成成功: {output_path}")
    
    print("✅ 资源已自动清理")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 编码封面生成器测试套件")
    print("="*60)
    
    tests = [
        test_config_validation,
        test_default_template,
        test_tutorial_template,
        test_review_template,
        test_batch_generation,
        test_preview_html,
        test_context_manager
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
