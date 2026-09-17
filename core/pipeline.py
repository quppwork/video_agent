"""
流水线模块
采用pipeline模式，将整个流程分为多个步骤，每个步骤之间通过管道连接，实现数据流式处理
"""
import os  # os模块
import subprocess  # 子进程处理模块
from pathlib import Path  # 路径处理模块

import whisper  # whisper模块
from dotenv import load_dotenv  # 环境变量处理模块
from openai import OpenAI  # OpenAI模块


# 流水线主函数
def run_pipeline(video_path: str)->str:
    """
    流水线主函数,处理视频文件
    Args:
        video_path: 视频路径
    Returns:
        str: 成功信息
    """
    path = Path(video_path) # 将视频路径转换为Path对象

    if not path.is_file(): # 判断文件是否存在
        raise FileNotFoundError(f"文件不存在: {path}") # 抛出文件不存在异常
    else:
        print(f"校验通过: {path}文件存在") # 打印成功信息
    
    # 提取音频
    out_dir = Path("tests_video/test_video_output")
    audio_path = extract_audio(path, out_dir) # 提取音频

    # 使用whisper转写音频
    whisper_text = transcribe_with_whisper(audio_path) # 使用whisper转写音频

    # 使用LLM模型生成摘要
    summary = summarize_with_llm(whisper_text) # 使用LLM模型生成摘要(返回摘要)
    save_choice = input("是否保存摘要? (y/n): ") # 询问是否保存摘要
    if save_choice == "y": # 如果选择保存摘要(输入y)
        save_summary(summary, out_dir, path) # 保存摘要
    else: # 如果选择不保存摘要(输入n)
        print("摘要未保存") # 打印摘要未保存信息
    return summary # 返回摘要



# 提取音频函数
def extract_audio(video: Path, out_dir: Path)->Path:
    """
    提取音频函数,将视频转换为音频
    Args:
        video: 视频路径
        out_dir: 输出目录
    Returns:
        Path: 音频路径
    """
    out_dir.mkdir(parents=True, exist_ok=True) # 创建输出目录
    audio_path = out_dir / f"{video.stem}.wav" # 创建音频路径
    cmd = [
        "ffmpeg","-y",# 使用ffmpeg命令,强制覆盖输出文件
        "-i", str(video),# 设置视频路径
        "-q:a", "0",# 设置音频质量为0
        "-map", "a",# 映射音频流
        str(audio_path),# 设置音频路径
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True) # 赋值result执行命令
    if result.returncode != 0: # 判断命令是否执行失败
        raise RuntimeError(f"提取音频失败: {result.stderr}") # 抛出提取音频失败异常
    return audio_path # 返回音频路径



# 使用whisper提取音频函数
def transcribe_with_whisper(audio_path: Path)->str:
    """
    使用whisper提取音频函数,将音频转换为文本
    Args:
        audio_path: 音频路径
    Returns:
        str: 文本
    """
    model = whisper.load_model("base") # 创建whisper模型-base模型
    result = model.transcribe(str(audio_path), language="zh") # 音频转文字,语言为中文
    return result["text"] # 返回文本



# 使用LLM模型生成摘要
def summarize_with_llm(text: str)->str:
    """
    使用LLM模型生成摘要
    Args:
        text: 文本
    Returns:
        str: 摘要
    """
    load_dotenv() # 加载环境变量.env文件

    # 判断环境变量是否设置
    if not os.getenv("AI_LLM_API_KEY") or not os.getenv("AI_LLM_BASE_URL") or not os.getenv("AI_LLM_MODEL"):
        raise ValueError("环境变量未设置,请检查.env文件") # 抛出环境变量未设置异常
    else:
        print("AI模型已加载") # 打印环境变量设置成功信息
    
    # 创建OpenAI客户端
    llm_client = OpenAI(
        api_key=os.getenv("AI_LLM_API_KEY"),# API密钥
        base_url=os.getenv("AI_LLM_BASE_URL"),# API地址
        )
    promote_text = """
    你是一个摘要生成器,请根据输入的文本生成摘要。
    """
    response = llm_client.chat.completions.create(# 创建聊天完成,使用环境变量中的模型和API密钥
        model=os.getenv("AI_LLM_MODEL"),
        messages=[# 消息列表
            {"role": "system", "content": promote_text},# 系统消息
            {"role": "user", "content": text},# 用户消息
        ],
    )
    return response.choices[0].message.content # 返回摘要,取第一个消息的回答



# 保存摘要函数
def save_summary(summary: str, out_dir: Path, path: Path)->None:
    """
    保存摘要函数,将摘要保存到文件
    Args:
        summary: 摘要
        out_dir: 输出目录
        path: 视频路径
    """
    summary_path = out_dir / f"{path.stem}_summary.txt" # 创建摘要路径
    summary_path.write_text(summary, encoding="utf-8") # 保存摘要(写入文件,编码为utf-8)
    print(f"摘要已保存到: {summary_path}") # 打印摘要保存成功信息


# 测试函数
if __name__ == "__main__":
    test_text = "你好,世界"
    test_summary = summarize_with_llm(test_text)
    print(test_summary)