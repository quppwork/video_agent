"""
fastapi 应用
使用fastapi创建一个API应用,接收视频文件,调用核心业务模块,返回摘要
"""

import shutil  # 把上传流复制到磁盘文件,因为fastapi的UploadFile只提供流式访问
from pathlib import Path  # 拼接上传/输出路径

from fastapi import FastAPI, File, HTTPException, UploadFile

from core.pipeline import run_pipeline  # 导入流水线函数

# 全局变量
app = FastAPI() # 创建fastapi应用
UPLOAD_DIR = Path("tests_video/upload") # 上传文件目录
OUT_DIR = Path("tests_video/test_video_output") # 输出文件目录

@app.post("/summarize") # 注册POST请求路由:地址是/summarize,请求体是file
def summarize(file: UploadFile = File(...)):  # 请求体是file,文件名不能为空  # noqa: B008
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")# 抛出HTTP异常,状态码是400,详情是"文件名不能为空"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True) # 创建上传文件目录
    dest = UPLOAD_DIR / Path(file.filename).name # 拼接上传文件路径
    with dest.open("wb") as f: # 打开上传文件
        shutil.copyfileobj(file.file, f) # 把上传内容写到dest

    summary = run_pipeline(str(dest),out_dir=OUT_DIR) # 调用核心业务模块,跑流水线
    return {"summary": summary,"saved_to":str(OUT_DIR)} # 变成JSON格式返回
    """
    {
        "summary": "摘要",
        "saved_to": "保存路径"
    }
    """
