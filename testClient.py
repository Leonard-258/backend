import requests
import os
import time

# 后端地址
BASE_URL = "http://localhost:8000"

# 模拟一个 Session ID (就像是某个用户打开了网页)
SESSION_ID = "user_test_001"


def create_dummy_image(filename):
    """创建一个假的图片文件用于测试"""
    if not os.path.exists(filename):
        with open(filename, "wb") as f:
            # 写入一些随机字节，模拟图片内容
            f.write(os.urandom(1024))
    return filename


def test_workflow():
    print(f"=== 开始测试工作流 (Session: {SESSION_ID}) ===")

    # 1. 模拟 ESP32 上传 4 张图片
    print("\n[Step 1] 模拟 ESP32 上传图片...")
    image_files = ["cam_1.jpg", "cam_2.jpg", "cam_3.jpg", "cam_4.jpg"]

    for img_name in image_files:
        create_dummy_image(img_name)  # 确保本地有这个文件

        # 构造上传请求
        with open(img_name, "rb") as f:
            files = {"file": (img_name, f, "image/jpeg")}
            data = {"session_id": SESSION_ID}

            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)

            if response.status_code == 200:
                print(f"  -> 上传 {img_name} 成功! 当前服务器已收图: {response.json()['count']} 张")
            else:
                print(f"  -> 上传失败: {response.text}")

        # 模拟传输间隔
        time.sleep(0.5)

    # 2. 模拟前端：请求生成初步 3D 模型
    print("\n[Step 2] 模拟前端：请求生成初步模型...")
    response = requests.post(f"{BASE_URL}/generate_initial", data={"session_id": SESSION_ID})

    if response.status_code == 200:
        result = response.json()
        print("  -> AI 响应成功！")
        print(f"  -> 模型下载地址: {BASE_URL}/static/{result['model_url']}")
        print(f"  -> 预览图片列表: {result['images']}")
    else:
        print(f"  -> 请求失败: {response.text}")
        return

    # 3. 模拟用户编辑：比如“给它加个红帽子”
    print("\n[Step 3] 模拟用户编辑：输入指令 'Add a red hat'...")
    edit_data = {
        "session_id": SESSION_ID,
        "prompt": "Add a red hat"
    }

    # 注意：我们的 Mock AI 设定了 sleep(3) + sleep(2)，所以这里会卡顿几秒，是正常的
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/edit_model", data=edit_data)
    duration = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print(f"  -> 编辑成功！(耗时 {duration:.2f} 秒)")
        print(f"  -> 新模型下载地址: {BASE_URL}/static/{result['model_url']}")
        print(f"  -> 使用的提示词: {result['prompt']}")
    else:
        print(f"  -> 编辑失败: {response.text}")

    # 清理测试生成的临时图片
    for img in image_files:
        if os.path.exists(img):
            os.remove(img)
    print("\n=== 测试结束，流程跑通！ ===")


if __name__ == "__main__":
    # 确保后端已经运行了再运行这个脚本
    try:
        test_workflow()
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到后端。请确保你已经运行了 'python main.py'")