from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import uuid

# 引入我们刚才写的假 AI 服务
from services.ai_engine import ai_service

app = FastAPI()

# 1. 配置跨域（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 挂载静态目录 (让前端能通过 URL 访问图片和模型)
# 访问 http://localhost:8000/static/models/xxx.glb 就能下载
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/models", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 简单内存数据库，存一下当前的 session 状态
# 结构: {"session_id": {"images": [], "history": []}}
db = {}


# --- 接口 1: ESP32 上传图片 ---
# ESP32 每次拍一张图就 POST 到这里，带上 session_id 就能归类
@app.post("/upload")
async def upload_image(session_id: str = Form(...), file: UploadFile = File(...)):
    # 为图片生成保存路径
    file_location = f"static/images/{session_id}_{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 存入“数据库”
    if session_id not in db:
        db[session_id] = {"images": [], "history": []}

    # 存的是相对路径，方便前端访问
    img_url = f"images/{session_id}_{file.filename}"
    db[session_id]["images"].append(img_url)

    return {"status": "success", "image_url": img_url, "count": len(db[session_id]["images"])}


# --- 接口 2: 开始生成初步模型 (Step 1) ---
# 前端检测到 4 张图齐了，调用这个接口
@app.post("/generate_initial")
async def generate_initial(session_id: str = Form(...)):
    if session_id not in db or len(db[session_id]["images"]) == 0:
        raise HTTPException(status_code=400, detail="没有找到图片，请先上传")

    images = db[session_id]["images"]

    # 调用 AI 引擎 (这里是 Mock 的，会等 3 秒)
    model_path = await ai_service.generate_initial_model(images)

    # 记录历史
    record = {
        "step": 0,
        "type": "initial",
        "model_url": model_path,
        "images": images
    }
    db[session_id]["history"].append(record)

    return record


# --- 接口 3: 编辑模型 (Step 2 - Edit Flow) ---
@app.post("/edit_model")
async def edit_model(session_id: str = Form(...), prompt: str = Form(...)):
    if session_id not in db:
        raise HTTPException(status_code=404, detail="Session not found")

    current_data = db[session_id]
    current_step = len(current_data["history"])

    # 调用 AI 引擎进行“编辑”
    # 注意：这里我们传入当前的图片，AI 应该返回新的图片和新的模型
    result = await ai_service.edit_and_regenerate(
        current_data["images"],
        prompt,
        current_step
    )

    # 记录新的历史
    record = {
        "step": current_step,
        "type": "edit",
        "prompt": prompt,
        "model_url": result["model_url"],
        "images": result["edited_images"]  # 如果编辑改变了图片，这里更新
    }
    db[session_id]["history"].append(record)

    return record


# --- 接口 4: 获取历史记录 ---
@app.get("/history/{session_id}")
async def get_history(session_id: str):
    return db.get(session_id, {"history": []})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)