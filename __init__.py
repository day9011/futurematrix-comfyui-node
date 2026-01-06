"""
ComfyUI Custom Node: Futurematrix ComfyUI
Futurematrix ComfyUI 自定义节点
"""

from .grsai import ChatAPI, NanoBanana


NODE_CLASS_MAPPINGS = {
    "ChatAPI": ChatAPI,
    "NanoBanana": NanoBanana,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ChatAPI": "Futurematrix/GRSAI Chat API",
    "NanoBanana": "Futurematrix/GRSAI NanoBanana",
}
# 这两个变量是 ComfyUI 加载节点所必需的
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("\033[32m[Futurematrix ComfyUI] 节点加载成功 ✓\033[0m")
