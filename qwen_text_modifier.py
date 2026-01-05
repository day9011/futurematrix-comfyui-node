"""
ComfyUI 自定义节点：使用 Qwen Chat 模型修改文本
"""

import os
from typing import Tuple, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    print("\033[91m[Qwen Text Modifier] 错误: 未安装 openai 库\033[0m")
    print("\033[93m[Qwen Text Modifier] 请运行: pip install openai>=1.0.0\033[0m")
    raise


class QwenTextModifier:
    """
    使用阿里云 Qwen 模型进行文本修改的 ComfyUI 自定义节点
    """

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("modified_text", "original_text", "debug_info")
    FUNCTION = "modify_text"
    CATEGORY = "🤖 Qwen/Text Processing"
    OUTPUT_NODE = True

    DESCRIPTION = "使用阿里云 Qwen 大模型对文本进行智能修改和优化"

    def __init__(self):
        self.type = "QwenTextModifier"
        self.output_node = True

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        定义节点的输入类型
        """
        return {
            "required": {
                # API Key 配置
                "api_key": (
                    "STRING",
                    {
                        "default": "sk-your-api-key-here",
                        "multiline": False,
                        "tooltip": "阿里云 DashScope API Key",
                    },
                ),
                # 输入文本
                "input_text": (
                    "STRING",
                    {
                        "default": "这是一段需要修改的文本",
                        "multiline": True,
                        "tooltip": "需要处理的原始文本",
                    },
                ),
                # 修改指令
                "instruction": (
                    "STRING",
                    {
                        "default": "请优化以下文本，使其更加通顺流畅",
                        "multiline": True,
                        "tooltip": "告诉模型如何修改文本的指令",
                    },
                ),
                # 模型选择
                "model": (
                    [
                        "qwen-max-latest",
                        "qwen-plus-latest",
                        "qwen-turbo-latest",
                        "qwen-long",
                    ],
                    {
                        "default": "qwen-max-latest",
                        "tooltip": "选择使用的 Qwen 模型版本",
                    },
                ),
                # Temperature 参数
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.7,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "tooltip": "控制生成文本的随机性，值越高越随机",
                    },
                ),
            },
            "optional": {
                # 系统提示词（可选）
                "system_prompt": (
                    "STRING",
                    {
                        "default": "你是一个专业的文本编辑助手，擅长根据用户需求修改和优化文本。",
                        "multiline": True,
                        "tooltip": "系统级提示词，用于设定模型的角色和行为",
                    },
                ),
            },
        }

    def modify_text(
        self,
        api_key: str,
        input_text: str,
        instruction: str,
        model: str,
        temperature: float,
        system_prompt: str = None,
    ) -> Tuple[str, str, str]:
        """
        使用 Qwen 模型修改文本

        Args:
            api_key: 阿里云 API Key
            input_text: 输入文本
            instruction: 修改指令
            model: 模型名称
            temperature: 温度参数
            system_prompt: 系统提示词（可选）

        Returns:
            Tuple[str, str, str]: (修改后的文本, 原始文本, 调试信息)
        """
        try:
            # 验证 API Key
            if (
                not api_key
                or api_key.strip() == ""
                or api_key == "sk-your-api-key-here"
            ):
                error_msg = "错误: 请提供有效的阿里云 API Key"
                print(f"\033[91m[QwenTextModifier] {error_msg}\033[0m")
                print(
                    "\033[93m提示: 在 https://dashscope.console.aliyun.com/ 获取 API Key\033[0m"
                )
                return (error_msg, input_text, error_msg)

            # 初始化 OpenAI 兼容客户端
            client = OpenAI(
                api_key=api_key.strip(),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            # 构建消息列表
            messages = []

            # 添加系统提示词
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})

            # 构建用户消息
            user_content = f"{instruction}\n\n原文：\n{input_text}"
            messages.append({"role": "user", "content": user_content})

            # 调用 Qwen API
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )

            # 提取修改后的文本
            modified_text = completion.choices[0].message.content

            # 构建调试信息
            debug_info = f"""
=== Qwen 模型调用信息 ===
模型: {model}
Temperature: {temperature}
Prompt Tokens: {completion.usage.prompt_tokens}
Completion Tokens: {completion.usage.completion_tokens}
Total Tokens: {completion.usage.total_tokens}
Finish Reason: {completion.choices[0].finish_reason}
=========================
"""

            print(f"[QwenTextModifier] 文本修改成功")
            print(f"[QwenTextModifier] 使用的模型: {model}")
            print(
                f"[QwenTextModifier] Token 使用情况: {completion.usage.total_tokens} tokens"
            )

            return (modified_text, input_text, debug_info)

        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[QwenTextModifier] 调用失败: {error_msg}")
            return (error_msg, input_text, error_msg)


class QwenTextModifierStream:
    """
    使用阿里云 Qwen 模型进行文本修改的 ComfyUI 自定义节点（流式版本）
    """

    def __init__(self):
        self.type = "QwenTextModifierStream"
        self.output_node = True

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        定义节点的输入类型
        """
        return {
            "required": {
                "api_key": (
                    "STRING",
                    {
                        "default": "sk-your-api-key-here",
                        "multiline": False,
                        "tooltip": "阿里云 DashScope API Key",
                    },
                ),
                "input_text": (
                    "STRING",
                    {
                        "default": "这是一段需要修改的文本",
                        "multiline": True,
                        "tooltip": "需要处理的原始文本",
                    },
                ),
                "instruction": (
                    "STRING",
                    {
                        "default": "请优化以下文本，使其更加通顺流畅",
                        "multiline": True,
                        "tooltip": "告诉模型如何修改文本的指令",
                    },
                ),
                "model": (
                    ["qwen-max-latest", "qwen-plus-latest", "qwen-turbo-latest"],
                    {
                        "default": "qwen-max-latest",
                        "tooltip": "选择使用的 Qwen 模型版本",
                    },
                ),
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.7,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "tooltip": "控制生成文本的随机性",
                    },
                ),
            },
            "optional": {
                "system_prompt": (
                    "STRING",
                    {
                        "default": "你是一个专业的文本编辑助手。",
                        "multiline": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("modified_text", "original_text")
    FUNCTION = "modify_text_stream"
    CATEGORY = "🤖 Qwen/Text Processing"
    OUTPUT_NODE = True

    DESCRIPTION = "使用阿里云 Qwen 大模型对文本进行智能修改（流式输出）"

    def modify_text_stream(
        self,
        api_key: str,
        input_text: str,
        instruction: str,
        model: str,
        temperature: float,
        system_prompt: str = None,
    ) -> Tuple[str, str]:
        """
        使用 Qwen 模型修改文本（流式输出）
        """
        try:
            # 验证 API Key
            if (
                not api_key
                or api_key.strip() == ""
                or api_key == "sk-your-api-key-here"
            ):
                error_msg = "错误: 请提供有效的阿里云 API Key"
                print(f"\033[91m[QwenTextModifierStream] {error_msg}\033[0m")
                return (error_msg, input_text)

            client = OpenAI(
                api_key=api_key.strip(),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})

            user_content = f"{instruction}\n\n原文：\n{input_text}"
            messages.append({"role": "user", "content": user_content})

            # 流式调用
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            # 收集流式输出
            modified_text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    modified_text += content
                    print(content, end="", flush=True)

            print()  # 换行
            print(f"[QwenTextModifierStream] 流式文本修改完成")

            return (modified_text, input_text)

        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[QwenTextModifierStream] 调用失败: {error_msg}")
            return (error_msg, input_text)


# ComfyUI 节点注册
NODE_CLASS_MAPPINGS = {
    "QwenTextModifier": QwenTextModifier,
    "QwenTextModifierStream": QwenTextModifierStream,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenTextModifier": "Qwen Text Modifier 📝",
    "QwenTextModifierStream": "Qwen Text Modifier (Stream) 🌊",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
