import asyncio
import shutil
import os
from typing import List


class MockAIService:
    def __init__(self, static_dir: str):
        self.static_dir = static_dir

    # 模拟：第一步，图生 3D
    async def generate_initial_model(self, image_paths: List[str]) -> str:
        print(f">>> [AI 引擎] 收到 {len(image_paths)} 张图片，准备生成初步模型...")
        print(f"    图片路径: {image_paths}")

        # 模拟 AI 思考时间 (比如 3 秒)
        await asyncio.sleep(3)

        # 模拟：直接复制一个现成的“假模型”到目标位置
        # 注意：你需要先自己在 static/models 里放一个叫 demo_base.glb 的文件做测试
        output_path = f"{self.static_dir}/models/result_initial.glb"
        # 实际代码这里会调用 API 下载文件，现在我们假装生成了
        if not os.path.exists(output_path):
            # 为了防止报错，如果没有假文件，创建一个空文件占位
            with open(output_path, "wb") as f:
                f.write(b"dummy 3d model content")

        print(f">>> [AI 引擎] 初步模型生成完毕: {output_path}")
        return "models/result_initial.glb"  # 返回相对路径给前端

    # 模拟：第二步，语言编辑图片 -> 再生 3D
    async def edit_and_regenerate(self, current_images: List[str], prompt: str,
                                  step_count: int) -> dict:
        print(f">>> [AI 引擎] 收到编辑指令: '{prompt}'")

        # 1. 模拟调用 GPT/DALL-E 修改图片
        print("    正在使用 AI 编辑 4 张视图...")
        await asyncio.sleep(2)
        # 这里逻辑上应该生成 4 张新图，我们简化，假设图片路径不变或生成了新图
        # 实际开发时，这里会返回 new_image_01.jpg 等

        # 2. 模拟调用图生 3D API
        print("    正在根据新图重新生成 3D 模型...")
        await asyncio.sleep(3)

        new_model_name = f"result_step_{step_count}.glb"
        output_path = f"{self.static_dir}/models/{new_model_name}"

        # 创建假文件用于测试
        with open(output_path, "wb") as f:
            f.write(b"dummy edited 3d model content")

        print(f">>> [AI 引擎] 编辑完成，新模型: {new_model_name}")

        return {
            "model_url": f"models/{new_model_name}",
            "edited_images": current_images,  # 暂时返回旧图，以后替换为新图
            "prompt_used": prompt
        }


# 单例模式，方便调用
ai_service = MockAIService("static")