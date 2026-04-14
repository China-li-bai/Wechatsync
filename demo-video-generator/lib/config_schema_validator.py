#!/usr/bin/env python3
"""
JSON Schema配置验证器 v1.0.0
使用JSON Schema进行严格的配置验证

参考项目:
- jsonschema: https://python-jsonschema.readthedocs.io/
- pytest-schema: https://github.com/codedawi/pytest-schema

技术要点:
- 严格类型检查
- 枚举值验证
- 范围验证
- 默认值填充
- 详细错误提示
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("⚠️  提示: 安装 jsonschema 可以启用配置验证 (pip install jsonschema)")


class ConfigSchemaValidator:
    """JSON Schema配置验证器"""
    
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Demo Video Generator Configuration",
        "description": "演示视频生成器配置文件Schema",
        "type": "object",
        "required": ["project", "voice", "scenes"],
        "properties": {
            "project": {
                "type": "object",
                "description": "项目基础配置",
                "required": ["name", "url"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "项目名称"
                    },
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "目标网站URL"
                    },
                    "output_dir": {
                        "type": "string",
                        "default": "./output",
                        "description": "输出目录"
                    },
                    "output_name": {
                        "type": "string",
                        "default": "demo-video",
                        "description": "输出文件名（不含扩展名）"
                    }
                },
                "additionalProperties": False
            },
            "voice": {
                "type": "object",
                "description": "语音配置",
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["zh-CN", "zh-TW", "zh-HK", "en-US", "ja-JP", "ko-KR"],
                        "default": "zh-CN",
                        "description": "语言"
                    },
                    "voice_name": {
                        "type": "string",
                        "default": "XiaoxiaoNeural",
                        "description": "语音名称"
                    },
                    "speed": {
                        "type": "number",
                        "minimum": 0.5,
                        "maximum": 2.0,
                        "default": 1.0,
                        "description": "语速 (0.5-2.0)"
                    }
                },
                "additionalProperties": True
            },
            "scenes": {
                "type": "array",
                "description": "场景配置列表",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "type", "text"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                            "description": "场景名称"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["hook", "feature", "demo", "benefit", "cta"],
                            "description": "场景类型"
                        },
                        "text": {
                            "type": "string",
                            "minLength": 1,
                            "description": "语音文本"
                        },
                        "subtitle": {
                            "type": "string",
                            "description": "字幕文本（可选）"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["screenshot", "scroll", "interact", "scroll_to_top"],
                            "default": "screenshot",
                            "description": "动作类型"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS选择器（用于interact动作）"
                        },
                        "scroll_distance": {
                            "type": "number",
                            "minimum": 0,
                            "default": 300,
                            "description": "滚动距离（像素）"
                        },
                        "wait_after": {
                            "type": "number",
                            "minimum": 0,
                            "default": 3,
                            "description": "动作后等待时间（秒）"
                        }
                    },
                    "additionalProperties": True
                }
            },
            "recording": {
                "type": "object",
                "description": "录制配置",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用自动录制"
                    },
                    "auto_scroll": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否自动滚动"
                    },
                    "scroll_distance": {
                        "type": "number",
                        "minimum": 0,
                        "default": 300,
                        "description": "默认滚动距离（像素）"
                    },
                    "wait_after_action": {
                        "type": "number",
                        "minimum": 0,
                        "default": 2,
                        "description": "动作后等待时间（秒）"
                    }
                },
                "additionalProperties": True
            },
            "video": {
                "type": "object",
                "description": "视频配置",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["mp4", "webm", "mov"],
                        "default": "mp4",
                        "description": "输出格式"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "high",
                        "description": "质量等级"
                    },
                    "resolution": {
                        "type": "string",
                        "pattern": "^\\d+x\\d+$",
                        "default": "1280x720",
                        "description": "分辨率"
                    },
                    "fps": {
                        "type": "integer",
                        "minimum": 15,
                        "maximum": 60,
                        "default": 30,
                        "description": "帧率"
                    },
                    "codec": {
                        "type": "string",
                        "default": "libx264",
                        "description": "视频编码器"
                    }
                },
                "additionalProperties": True
            },
            "audio": {
                "type": "object",
                "description": "音频配置",
                "properties": {
                    "codec": {
                        "type": "string",
                        "default": "aac",
                        "description": "音频编码器"
                    },
                    "bitrate": {
                        "type": "string",
                        "pattern": "^\\d+k$",
                        "default": "128k",
                        "description": "比特率"
                    }
                },
                "additionalProperties": True
            },
            "subtitle": {
                "type": "object",
                "description": "字幕配置",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用字幕"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["srt", "ass"],
                        "default": "srt",
                        "description": "字幕格式"
                    },
                    "font": {
                        "type": "string",
                        "default": "PingFang SC",
                        "description": "字体"
                    },
                    "font_size": {
                        "type": "integer",
                        "minimum": 12,
                        "maximum": 48,
                        "default": 24,
                        "description": "字号"
                    },
                    "color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{6}$",
                        "default": "#FFFFFF",
                        "description": "颜色"
                    },
                    "outline_color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{6}$",
                        "default": "#000000",
                        "description": "描边颜色"
                    },
                    "background_color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{8}$",
                        "default": "#80000000",
                        "description": "背景色（带透明度）"
                    },
                    "outline": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 5,
                        "default": 2,
                        "description": "描边宽度"
                    },
                    "shadow": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 5,
                        "default": 1,
                        "description": "阴影"
                    }
                },
                "additionalProperties": True
            },
            "thumbnail": {
                "type": "object",
                "description": "封面配置",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用封面生成"
                    },
                    "template": {
                        "type": "string",
                        "default": "default.html",
                        "description": "模板文件名"
                    },
                    "template_dir": {
                        "type": "string",
                        "default": "templates/thumbnails",
                        "description": "模板目录"
                    },
                    "background": {
                        "type": "string",
                        "default": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "description": "背景渐变"
                    },
                    "font_size": {
                        "type": "integer",
                        "minimum": 40,
                        "maximum": 120,
                        "default": 80,
                        "description": "标题字号"
                    },
                    "text_color": {
                        "type": "string",
                        "default": "white",
                        "description": "文字颜色"
                    },
                    "badge": {
                        "type": "string",
                        "description": "徽章文字（可选）"
                    },
                    "brand": {
                        "type": "string",
                        "description": "品牌名称（可选）"
                    },
                    "author": {
                        "type": "string",
                        "description": "作者名称（可选）"
                    },
                    "accent_color": {
                        "type": "string",
                        "default": "#ffd700",
                        "description": "强调色"
                    }
                },
                "additionalProperties": True
            },
            "advanced": {
                "type": "object",
                "description": "高级配置",
                "properties": {
                    "browser": {
                        "type": "object",
                        "properties": {
                            "headless": {
                                "type": "boolean",
                                "default": False,
                                "description": "是否无头模式"
                            },
                            "timeout": {
                                "type": "integer",
                                "minimum": 5000,
                                "maximum": 60000,
                                "default": 30000,
                                "description": "超时时间（毫秒）"
                            }
                        }
                    },
                    "validation": {
                        "type": "object",
                        "properties": {
                            "check_sync": {
                                "type": "boolean",
                                "default": True,
                                "description": "检查音视频同步"
                            },
                            "check_quality": {
                                "type": "boolean",
                                "default": True,
                                "description": "检查视频质量"
                            },
                            "max_file_size": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 10,
                                "description": "最大文件大小（MB）"
                            }
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "parallel_voice": {
                                "type": "boolean",
                                "default": True,
                                "description": "并行生成语音"
                            },
                            "skip_existing": {
                                "type": "boolean",
                                "default": True,
                                "description": "跳过已存在的文件"
                            }
                        }
                    }
                },
                "additionalProperties": True
            }
        },
        "additionalProperties": True
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化配置验证器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        
        if not HAS_JSONSCHEMA:
            self.logger.warning("jsonschema未安装，配置验证功能受限")
    
    def validate(self, config: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        验证配置
        
        Args:
            config: 配置字典
        
        Returns:
            (是否成功, 错误列表)
        """
        if not HAS_JSONSCHEMA:
            self.logger.warning("jsonschema未安装，跳过验证")
            return True, []
        
        try:
            # 使用Draft7Validator进行验证
            validator = Draft7Validator(self.SCHEMA)
            errors = list(validator.iter_errors(config))
            
            if errors:
                error_list = []
                for error in errors:
                    error_info = {
                        'path': ' -> '.join(str(p) for p in error.path),
                        'message': error.message,
                        'validator': error.validator,
                        'schema_path': ' -> '.join(str(p) for p in error.schema_path)
                    }
                    
                    # 添加期望值
                    if error.validator == 'enum':
                        error_info['expected'] = error.schema['enum']
                    elif error.validator == 'minimum':
                        error_info['expected'] = f">= {error.schema['minimum']}"
                    elif error.validator == 'maximum':
                        error_info['expected'] = f"<= {error.schema['maximum']}"
                    elif error.validator == 'type':
                        error_info['expected'] = error.schema['type']
                    
                    error_list.append(error_info)
                
                return False, error_list
            
            return True, []
            
        except Exception as e:
            self.logger.error(f"配置验证异常: {e}")
            return False, [{'message': str(e)}]
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用默认值
        
        Args:
            config: 配置字典
        
        Returns:
            填充默认值后的配置
        """
        if not HAS_JSONSCHEMA:
            self.logger.warning("jsonschema未安装，无法应用默认值")
            return config
        
        result = config.copy()
        
        # 递归应用默认值
        self._apply_defaults_recursive(result, self.SCHEMA)
        
        return result
    
    def _apply_defaults_recursive(self, config: Dict[str, Any], schema: Dict[str, Any]):
        """
        递归应用默认值
        
        Args:
            config: 配置字典
            schema: Schema字典
        """
        if 'properties' not in schema:
            return
        
        for key, prop_schema in schema['properties'].items():
            # 如果配置中没有该字段，且有默认值，则添加
            if key not in config and 'default' in prop_schema:
                config[key] = prop_schema['default']
                self.logger.debug(f"应用默认值: {key} = {prop_schema['default']}")
            
            # 如果是对象类型，递归处理
            if prop_schema.get('type') == 'object' and key in config:
                self._apply_defaults_recursive(config[key], prop_schema)
            
            # 如果是数组类型，递归处理每个元素
            if prop_schema.get('type') == 'array' and key in config:
                items_schema = prop_schema.get('items', {})
                for item in config[key]:
                    if isinstance(item, dict):
                        self._apply_defaults_recursive(item, items_schema)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        获取Schema信息
        
        Returns:
            Schema信息字典
        """
        return {
            'title': self.SCHEMA.get('title'),
            'description': self.SCHEMA.get('description'),
            'required_fields': self.SCHEMA.get('required', []),
            'properties': list(self.SCHEMA.get('properties', {}).keys())
        }
    
    def generate_template(self) -> Dict[str, Any]:
        """
        生成配置模板
        
        Returns:
            配置模板字典
        """
        template = {}
        self._apply_defaults_recursive(template, self.SCHEMA)
        return template
    
    def validate_file(self, config_file: Path) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        验证配置文件
        
        Args:
            config_file: 配置文件路径
        
        Returns:
            (是否成功, 错误列表)
        """
        import yaml
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            return self.validate(config)
            
        except Exception as e:
            self.logger.error(f"配置文件读取失败: {e}")
            return False, [{'message': str(e)}]


if __name__ == "__main__":
    # 测试代码
    import yaml
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    validator = ConfigSchemaValidator()
    
    # 显示Schema信息
    print("\n=== Schema信息 ===")
    info = validator.get_schema_info()
    print(f"标题: {info['title']}")
    print(f"描述: {info['description']}")
    print(f"必需字段: {', '.join(info['required_fields'])}")
    print(f"属性: {', '.join(info['properties'])}")
    
    # 生成配置模板
    print("\n=== 配置模板 ===")
    template = validator.generate_template()
    print(yaml.dump(template, allow_unicode=True, default_flow_style=False))
    
    # 测试验证
    if len(sys.argv) > 1:
        config_file = Path(sys.argv[1])
        print(f"\n=== 验证配置文件: {config_file} ===")
        
        success, errors = validator.validate_file(config_file)
        
        if success:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - 路径: {error.get('path', 'N/A')}")
                print(f"    消息: {error.get('message', 'N/A')}")
                if 'expected' in error:
                    print(f"    期望: {error['expected']}")
