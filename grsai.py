import requests
import re
import json
import time
import torch
from PIL import Image
from io import BytesIO


class ChatAPI:

    CATEGORY = "Futurematrix/GRSAI/Chat API"

    """
    节点左边输入
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING",),
                "host": (
                    "STRING",
                    {"default": "https://grsaiapi.com"},
                ),
                "model": ("STRING", {"default": "gemini-3-pro"}),
                "prompt": ("STRING",),
            },
            "optional": {
                "delete_think": ("BOOLEAN", {"default": False}),
            },
        }

    """
    节点右边输出
    """
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "chat"

    def chat(self, api_key, host, model, prompt, delete_think):
        messages = [{"role": "user", "content": prompt}]
        response = requests.post(
            f"{host.rstrip('/')}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "stream": False,
            },
        )
        content = response.json()["choices"][0]["message"]["content"]
        if delete_think:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        content = content.strip()
        return (content,)


class NanoBanana:

    CATEGORY = "Futurematrix/GRSAI/NanoBanana"
    """
    节点左边输入
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "host": (
                    "STRING",
                    {"default": "https://grsaiapi.com"},
                ),
                "model": ("STRING", {"default": "nano-banana-pro"}),
                "prompt": ("STRING",),
            },
            "optional": {
                "urls": ("STRING", {"default": ""}),  # 为json dumps后的list
                "aspect_ratio": (
                    ["auto"]
                    + [
                        "1:1",
                        "16:9",
                        "9:16",
                        "4:3",
                        "3:4",
                        "2:3",
                        "3:2",
                        "5:4",
                        "4:5",
                        "21:9",
                    ],
                ),
                "image_size": (["1K"] + ["2K", "4K"],),
            },
        }

    """
    节点右边输出
    """
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"

    def generate_image(
        self,
        api_key,
        host,
        model,
        prompt,
        urls=None,
        aspect_ratio=None,
        image_size=None,
    ):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {"model": model, "prompt": prompt, "webHook": "-1", "shutProgress": True}
        if urls is not None:
            if isinstance(urls, str):
                if urls.strip() == "":
                    urls = None
                else:
                    urls = json.loads(urls)
        if urls is not None:
            data["urls"] = urls
        if aspect_ratio is not None:
            data["aspectRatio"] = aspect_ratio
        if image_size is not None:
            data["imageSize"] = image_size
        response = requests.post(
            f"{host.rstrip('/')}/v1/draw/nano-banana",
            headers=headers,
            json=data,
        )
        res_json = response.json()
        if res_json["code"] != 0:
            raise Exception(res_json["msg"])
        task_id = res_json["data"]["id"]
        image_urls = None
        while True:
            time.sleep(1)
            data = {"id": task_id}
            response = requests.post(
                f"{host.rstrip('/')}/v1/draw/result", headers=headers, json=data
            )
            res_json = response.json()
            if res_json["code"] != 0:
                raise Exception(res_json["msg"])
            data = res_json["data"]
            if data["status"] == "running":
                continue
            if data["status"] == "succeeded":
                results = data["results"]
                if len(results) > 0:
                    image_urls = [result["url"] for result in results]
                break
            if data["failure_reason"].strip() != "":
                raise Exception(data["failure_reason"])
        if len(image_urls) == 0:
            raise Exception("生成失败")

        # 下载多张图片转成tensor
        imgs = []
        for image_url in image_urls:
            resp = requests.get(image_url)
            if resp.status_code != 200:
                raise Exception("图片下载失败")
            img_pil = Image.open(BytesIO(resp.content)).convert("RGB")
            img = torch.from_numpy(
                (
                    torch.ByteTensor(torch.ByteStorage.from_buffer(img_pil.tobytes()))
                    .float()
                    .reshape(img_pil.size[1], img_pil.size[0], 3)
                )
                / 255.0
            )
            # img: [H, W, C]
            img = img.unsqueeze(0)  # [1, H, W, C]
            imgs.append(img)
        # Concatenate images along batch dimension
        if len(imgs) == 0:
            raise Exception("生成失败")
        imgs_tensor = torch.cat(imgs, dim=0)
        return (imgs_tensor,)
