"""
ComfyUI Custom Node: Qwen Text Modifier
使用阿里云 Qwen 模型进行文本修改的 ComfyUI 自定义节点
"""

from .qwen_text_modifier import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 这两个变量是 ComfyUI 加载节点所必需的
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print('\033[32m[Qwen Text Modifier] 节点加载成功 ✓\033[0m')

