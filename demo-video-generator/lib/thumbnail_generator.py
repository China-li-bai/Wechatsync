"""
编码封面生成器 - 基于HTML/CSS + Playwright

特性:
- 完全可控: 精确控制每个元素
- 可验证: 配置验证和输出验证
- 吸引眼球: 基于CTR优化原则
- 统一风格: 模板系统保证一致性
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
    
    VALID_STYLES = ['tutorial', 'review', 'news', 'entertainment', 'tech', 'minimal']
    
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
