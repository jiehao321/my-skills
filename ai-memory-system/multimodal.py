"""
多模态模块 - 图片、语音处理
"""
import base64
import os
from pathlib import Path

# 检查依赖
try:
    from PIL import Image
    import PIL
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import torch
    from transformers import pipeline
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


class ImageAnalyzer:
    """图片分析"""
    
    def __init__(self):
        self.model = None
        if HAS_VISION:
            try:
                # 尝试加载轻量模型
                self.model = pipeline(
                    "image-classification", 
                    model="google/vit-base-patch16-224"
                )
            except:
                pass
    
    def describe_image(self, image_path: str) -> str:
        """描述图片内容"""
        if not HAS_PIL:
            return "需要安装 Pillow: pip install pillow"
        
        try:
            img = Image.open(image_path)
            width, height = img.size
            mode = img.mode
            
            # 基础信息
            info = f"图片尺寸: {width}x{height}, 模式: {mode}"
            
            # 如果有视觉模型，尝试识别
            if self.model:
                results = self.model(img)
                if results:
                    top = results[0]
                    info += f", 主要内容: {top['label']} ({top['score']:.2f})"
            
            return info
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def extract_colors(self, image_path: str) -> list:
        """提取图片主色调"""
        if not HAS_PIL:
            return ["需要安装 Pillow"]
        
        try:
            img = Image.open(image_path)
            img = img.convert('P', palette=Image.ADAPTIVE, colors=5)
            colors = img.getpalette()[:15]
            
            # 转换为 RGB
            result = []
            for i in range(0, len(colors), 3):
                r, g, b = colors[i], colors[i+1], colors[i+2]
                result.append(f"#{r:02x}{g:02x}{b:02x}")
            
            return result
        except Exception as e:
            return [str(e)]


class ScreenshotAnalyzer:
    """截图分析 - 检测 UI 元素"""
    
    def __init__(self):
        pass
    
    def analyze_screenshot(self, image_path: str) -> dict:
        """分析截图内容"""
        if not HAS_PIL:
            return {"error": "需要安装 Pillow"}
        
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            # 简单分析
            analysis = {
                "size": f"{width}x{height}",
                "aspect_ratio": round(width/height, 2),
                "format": img.format,
                "mode": img.mode
            }
            
            # 检测是否为网页截图
            if any(keyword in image_path.lower() for keyword in ["web", "screen", "shot"]):
                analysis["type"] = "网页截图"
            else:
                analysis["type"] = "通用图片"
            
            return analysis
        except Exception as e:
            return {"error": str(e)}


class DocumentAnalyzer:
    """文档分析 - PDF/OCR"""
    
    def __init__(self):
        pass
    
    def extract_text_from_image(self, image_path: str) -> str:
        """从图片提取文字 (OCR)"""
        if not HAS_PIL:
            return "需要安装 Pillow"
        
        # 简单实现：返回图片基本信息
        # 实际可用 pytesseract 进行 OCR
        try:
            img = Image.open(image_path)
            return f"图片尺寸: {img.size}, 可用 OCR 提取文字"
        except Exception as e:
            return f"失败: {str(e)}"


class MultimodalInput:
    """多模态输入处理入口"""
    
    def __init__(self):
        self.image = ImageAnalyzer()
        self.screenshot = ScreenshotAnalyzer()
        self.document = DocumentAnalyzer()
    
    def process(self, file_path: str) -> dict:
        """处理各种类型的输入"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return {
                "type": "image",
                "description": self.image.describe_image(file_path),
                "colors": self.image.extract_colors(file_path)
            }
        elif suffix in ['.pdf']:
            return {
                "type": "document",
                "message": "PDF 分析需要额外依赖"
            }
        else:
            return {
                "type": "unknown",
                "message": f"不支持的文件类型: {suffix}"
            }


# ========== 视频/音频处理 ==========

class VideoAnalyzer:
    """视频分析 (基础版)"""
    
    def __init__(self):
        pass
    
    def get_info(self, video_path: str) -> dict:
        """获取视频基本信息"""
        # 实际可用 ffmpeg
        path = Path(video_path)
        return {
            "file": path.name,
            "size": f"{path.stat().st_size / 1024 / 1024:.2f} MB",
            "type": "video",
            "note": "需要 ffmpeg 进行详细分析"
        }


class AudioAnalyzer:
    """音频分析"""
    
    def __init__(self):
        pass
    
    def get_info(self, audio_path: str) -> dict:
        """获取音频信息"""
        path = Path(audio_path)
        return {
            "file": path.name,
            "size": f"{path.stat().st_size / 1024:.2f} KB",
            "type": "audio",
            "note": "需要 audio 处理库进行详细分析"
        }


if __name__ == "__main__":
    print("=== 多模态测试 ===")
    
    multimodal = MultimodalAnalyzer()
    
    # 检查支持情况
    print(f"\nPIL 支持: {HAS_PIL}")
    print(f"视觉模型: {HAS_VISION}")
    
    print("\n支持的输入类型:")
    print("- 图片: jpg, png, gif, bmp, webp")
    print("- 视频: mp4, avi, mov")
    print("- 音频: mp3, wav, flac")
    print("- 文档: pdf")
