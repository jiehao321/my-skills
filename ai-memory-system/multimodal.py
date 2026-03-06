"""
多模态模块 - 图片、语音处理
支持视觉模型自动下载
"""
import base64
import os
from pathlib import Path
from PIL import Image
import json

# 视觉模型 (自动下载)
VISION_MODEL = None


def get_vision_model():
    """获取视觉模型 (首次自动下载)"""
    global VISION_MODEL
    if VISION_MODEL is None:
        try:
            from transformers import pipeline
            VISION_MODEL = pipeline(
                "image-classification", 
                model="microsoft/resnet-50"
            )
            print("✅ 视觉模型已加载")
        except Exception as e:
            print(f"⚠️ 视觉模型加载失败: {e}")
            VISION_MODEL = False
    return VISION_MODEL


class ImageAnalyzer:
    """图片分析"""
    
    def describe_image(self, image_path: str) -> str:
        """描述图片内容"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            mode = img.mode
            
            info = f"图片尺寸: {width}x{height}, 模式: {mode}"
            
            # 尝试使用视觉模型
            model = get_vision_model()
            if model:
                results = model(img)
                if results:
                    top = results[0]
                    info += f"\n内容识别: {top['label']} ({top['score']:.2f})"
            
            return info
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def extract_colors(self, image_path: str) -> list:
        """提取图片主色调"""
        try:
            img = Image.open(image_path)
            img = img.convert('P', palette=Image.ADAPTIVE, colors=5)
            colors = img.getpalette()[:15]
            
            result = []
            for i in range(0, len(colors), 3):
                r, g, b = colors[i], colors[i+1], colors[i+2]
                result.append(f"#{r:02x}{g:02x}{b:02x}")
            
            return result
        except Exception as e:
            return [str(e)]
    
    def detect_faces(self, image_path: str) -> dict:
        """人脸检测"""
        try:
            from transformers import pipeline
            face_detector = pipeline(
                "image-classification", 
                model="valleykey/face-recognition"
            )
            img = Image.open(image_path)
            result = face_detector(img)
            return {"faces": len(result), "details": result}
        except Exception as e:
            return {"error": str(e)}


class ScreenshotAnalyzer:
    """截图分析"""
    
    def analyze_screenshot(self, image_path: str) -> dict:
        """分析截图内容"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            analysis = {
                "size": f"{width}x{height}",
                "aspect_ratio": round(width/height, 2),
                "format": img.format,
                "mode": img.mode
            }
            
            # 检测类型
            if any(keyword in image_path.lower() for keyword in ["web", "screen", "shot"]):
                analysis["type"] = "网页截图"
            else:
                analysis["type"] = "通用图片"
            
            return analysis
        except Exception as e:
            return {"error": str(e)}


class MultimodalInput:
    """多模态输入处理入口"""
    
    def __init__(self):
        self.image = ImageAnalyzer()
        self.screenshot = ScreenshotAnalyzer()
    
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
            return {"type": "document", "message": "PDF 分析需要额外依赖"}
        else:
            return {"type": "unknown", "message": f"不支持的文件类型: {suffix}"}


class VideoAnalyzer:
    """视频分析"""
    
    def get_info(self, video_path: str) -> dict:
        path = Path(video_path)
        return {
            "file": path.name,
            "size": f"{path.stat().st_size / 1024 / 1024:.2f} MB",
            "type": "video"
        }


class AudioAnalyzer:
    """音频分析"""
    
    def get_info(self, audio_path: str) -> dict:
        path = Path(audio_path)
        return {
            "file": path.name,
            "size": f"{path.stat().st_size / 1024:.2f} KB",
            "type": "audio"
        }


if __name__ == "__main__":
    print("=== 多模态模块 ===")
    print(f"PIL: ✅")
    
    # 测试视觉模型
    print("\n加载视觉模型...")
    model = get_vision_model()
    if model:
        print("✅ 视觉模型就绪")
    else:
        print("⚠️ 使用基础模式")
