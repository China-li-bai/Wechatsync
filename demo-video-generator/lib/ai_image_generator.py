#!/usr/bin/env python3
"""
AI图像生成器 - 基于SiliconFlow Kolors API
用于生成高质量的YouTube缩略图
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import base64


class AIImageGenerator:
    """基于SiliconFlow Kolors的AI图像生成器"""
    
    MODELS = {
        'kolors': 'Kwai-Kolors/Kolors',
        'stable-diffusion': 'stabilityai/stable-diffusion-xl-base-1.0',
        'flux': 'black-forest-labs/FLUX.1-schnell'
    }
    
    IMAGE_SIZES = {
        'square': '1024x1024',
        'landscape': '1792x1024',
        'portrait': '1024x1792',
        'thumbnail': '1280x720'
    }
    
    YOUTUBESTYLES = {
        'shocking': 'shocked expression, dramatic lighting, vibrant colors, high contrast, eye-catching, YouTube thumbnail style',
        'happy': 'happy smiling face, bright colors, warm lighting, positive energy, YouTube thumbnail style',
        'tech': 'futuristic technology, neon lights, cyberpunk style, modern design, YouTube thumbnail style',
        'nature': 'beautiful nature landscape, golden hour lighting, vibrant colors, cinematic, YouTube thumbnail style',
        'food': 'delicious food photography, appetizing, warm lighting, close-up, YouTube thumbnail style',
        'gaming': 'gaming setup, RGB lighting, dynamic composition, exciting, YouTube thumbnail style',
        'tutorial': 'clean professional setup, good lighting, educational, friendly, YouTube thumbnail style',
        'review': 'product photography, professional lighting, clean background, YouTube thumbnail style'
    }
    
    def __init__(self, api_key: str, output_dir: str = "output/ai-images"):
        """
        初始化AI图像生成器
        
        Args:
            api_key: SiliconFlow API密钥
            output_dir: 输出目录
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.siliconflow.cn/v1/images/generations"
    
    def generate(self, prompt: str, model: str = 'kolors', 
                 image_size: str = '1024x1024', 
                 batch_size: int = 1,
                 num_inference_steps: int = 20,
                 guidance_scale: float = 7.5,
                 negative_prompt: Optional[str] = None) -> Dict:
        """
        生成AI图像
        
        Args:
            prompt: 图像描述提示词
            model: 模型名称
            image_size: 图像尺寸
            batch_size: 批量大小
            num_inference_steps: 推理步数
            guidance_scale: 引导比例
            negative_prompt: 负面提示词
        
        Returns:
            生成结果字典
        """
        model_name = self.MODELS.get(model, model)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_name,
            'prompt': prompt,
            'image_size': image_size,
            'batch_size': batch_size,
            'num_inference_steps': num_inference_steps,
            'guidance_scale': guidance_scale
        }
        
        if negative_prompt:
            data['negative_prompt'] = negative_prompt
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            timeout=60
        )
        
        response.raise_for_status()
        return response.json()
    
    def generate_and_save(self, prompt: str, filename: Optional[str] = None,
                          model: str = 'kolors', 
                          image_size: str = '1024x1024',
                          **kwargs) -> Path:
        """
        生成AI图像并保存
        
        Args:
            prompt: 图像描述提示词
            filename: 文件名（可选）
            model: 模型名称
            image_size: 图像尺寸
            **kwargs: 其他参数
        
        Returns:
            保存的文件路径
        """
        result = self.generate(prompt, model, image_size, **kwargs)
        
        if 'images' not in result or len(result['images']) == 0:
            raise ValueError("No images generated")
        
        image_data = result['images'][0]
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_image_{timestamp}.png"
        
        output_path = self.output_dir / filename
        
        if image_data.get('url'):
            image_response = requests.get(image_data['url'], timeout=30)
            image_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
        elif image_data.get('b64_json'):
            image_bytes = base64.b64decode(image_data['b64_json'])
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
        else:
            raise ValueError("No image data found in response")
        
        return output_path
    
    def generate_youtube_thumbnail(self, style: str, custom_prompt: Optional[str] = None,
                                    title: Optional[str] = None,
                                    **kwargs) -> Path:
        """
        生成YouTube缩略图
        
        Args:
            style: 风格名称（shocking, happy, tech等）
            custom_prompt: 自定义提示词（可选）
            title: 标题（可选，会添加到提示词中）
            **kwargs: 其他参数
        
        Returns:
            生成的缩略图路径
        """
        style_prompt = self.YOUTUBESTYLES.get(style, self.YOUTUBESTYLES['shocking'])
        
        if custom_prompt:
            prompt = f"{custom_prompt}, {style_prompt}"
        else:
            prompt = style_prompt
        
        if title:
            prompt = f"{prompt}, text overlay saying '{title}'"
        
        filename = f"thumbnail_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        return self.generate_and_save(
            prompt=prompt,
            filename=filename,
            image_size='1280x720',
            **kwargs
        )
    
    def generate_batch(self, prompts: List[str], **kwargs) -> List[Path]:
        """
        批量生成图像
        
        Args:
            prompts: 提示词列表
            **kwargs: 其他参数
        
        Returns:
            生成的文件路径列表
        """
        results = []
        for i, prompt in enumerate(prompts, 1):
            try:
                filename = f"batch_{i:03d}.png"
                path = self.generate_and_save(prompt, filename=filename, **kwargs)
                results.append(path)
                print(f"✅ 生成成功 {i}/{len(prompts)}: {path}")
            except Exception as e:
                print(f"❌ 生成失败 {i}/{len(prompts)}: {e}")
        return results
    
    def list_models(self) -> Dict[str, str]:
        """列出所有可用模型"""
        return self.MODELS
    
    def list_styles(self) -> Dict[str, str]:
        """列出所有YouTube风格"""
        return self.YOUTUBESTYLES
    
    def list_sizes(self) -> Dict[str, str]:
        """列出所有图像尺寸"""
        return self.IMAGE_SIZES


if __name__ == "__main__":
    import os
    
    print("="*60)
    print("🎨 AI图像生成器测试 - SiliconFlow Kolors")
    print("="*60)
    
    api_key = os.environ.get('SILICONFLOW_API_KEY', 'sk-bslkcslwfoyghkuahkrzzsrvphyrcjgegrjmonnzaxxanvmb')
    
    generator = AIImageGenerator(api_key=api_key, output_dir="output/ai-images")
    
    print("\n📋 可用模型:")
    for model, desc in generator.list_models().items():
        print(f"  - {model}: {desc}")
    
    print("\n🎨 YouTube风格:")
    for style, desc in generator.list_styles().items():
        print(f"  - {style}: {desc[:50]}...")
    
    print("\n📐 图像尺寸:")
    for size, desc in generator.list_sizes().items():
        print(f"  - {size}: {desc}")
    
    print("\n🧪 测试生成:")
    print("-"*60)
    
    try:
        print("\n测试1: 简单提示词")
        path = generator.generate_and_save(
            prompt="a beautiful sunset over the ocean with seagulls",
            filename="test_sunset.png"
        )
        print(f"✅ 生成成功: {path}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    try:
        print("\n测试2: YouTube缩略图风格")
        path = generator.generate_youtube_thumbnail(
            style='shocking',
            title='Amazing Discovery'
        )
        print(f"✅ 生成成功: {path}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
