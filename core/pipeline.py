"""
业务层：流水线模块
采用pipeline模式，将整个流程分为多个步骤，每个步骤之间通过管道连接，实现数据流式处理
提取音频 -> 使用whisper转写音频 -> 保存时间戳文本 -> 使用LLM模型生成摘要 -> 保存摘要
"""
import os
import subprocess  # 子进程处理模块
from pathlib import Path  # 路径处理模块

import whisper
from dotenv import load_dotenv  # 环境变量处理模块
from openai import OpenAI  # OpenAI模块

# 全局变量,用于存储whisper模型
_whisper_model = None


# 流水线主函数
def run_pipeline(video_path: str,out_dir: Path)->str:
    """
    流水线主函数,处理视频文件
    Args:
        video_path: 视频路径
    Returns:
        str: 成功信息
    """
    path = Path(video_path) # 将视频路径转换为Path对象

    if not path.is_file(): # 判断文件是否存在
        raise FileNotFoundError(f"文件不存在: {path}")
    else:
        print(f"校验通过: {path}文件存在")
    
    # 提取音频
    audio_path = extract_audio(path, out_dir)

    # 使用whisper转写音频
    whisper_text = transcribe_with_whisper(audio_path)
    print(f"whisper_text: \n{whisper_text}") # 打印时间戳文本
    # 保存时间戳文本
    save_timestamp_text(whisper_text, out_dir, path)

    # 使用LLM模型生成摘要
    summary = summarize_with_llm(whisper_text)

    # 保存摘要
    save_summary(summary, out_dir, path)

    return summary # 返回摘要,测试通过



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



# 对whisper模型进行懒加载,只有在第一次使用时加载模型
def start_whisper_model():
    """
    启动whisper模型
    """
    global _whisper_model# 全局变量,用于存储whisper模型
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")
        print("whisper模型已加载")
    return _whisper_model



# 使用whisper提取音频函数
def transcribe_with_whisper(audio_path: Path)->str:
    """
    使用whisper提取音频函数,将音频转换为文本
    Args:
        audio_path: 音频路径
    Returns:
        str: 文本
    """
    model = start_whisper_model() # 创建whisper模型-base模型
    text_result = model.transcribe(str(audio_path), language="zh") # 音频转文字,语言为中文

    # 格式化时间函数
    def format_time(seconds: float)->str:
        """
        格式化时间函数,将时间转换为时间戳文本
        Args:
            seconds: 时间
        Returns:
            str: 时间戳文本
        """
        total_seconds = int(seconds) # 将时间转换为整数
        m,s = divmod(total_seconds, 60) # 将时间转换为分钟和秒
        return f"{m:02d}:{s:02d}" # 返回时间戳文本,格式为: 分钟:秒,不足2位补0
    
    text_lines = [] # 创建行列表,定义为text_lines列表
    for segment in text_result["segments"]:
        start_time = format_time(segment["start"])# 获取开始时间
        end_time = format_time(segment["end"])# 获取结束时间
        segment_text = segment["text"].strip()# 获取文本,并去除空格
        if not segment_text:
            continue
        text_lines.append(f"[{start_time} - {end_time}]: {segment_text}")# 添加行
    
    return "\n".join(text_lines) # 返回文本,将行列表转换为文本,使用换行符连接



# 保存时间戳文本函数
def save_timestamp_text(text_lines: str, out_dir: Path, path: Path)->None:
    """
    保存时间戳文本函数,将时间戳文本保存到文件
    Args:
        text_lines: 时间戳文本列表
        out_dir: 输出目录
        path: 视频路径
    """
    timestamp_path = out_dir / f"{path.stem}_timestamp.txt" # 创建时间戳路径
    timestamp_path.write_text(text_lines, encoding="utf-8") # 保存时间戳文本(写入文件,编码为utf-8)
    print(f"时间戳文本已保存到: {timestamp_path}") # 打印时间戳文本保存成功信息



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
    你是一个摘要生成器,请根据输入的文本生成摘要，需要包含时间戳，时间戳格式为: 开始时间 - 结束时间: 文本，时间必须来源于输入的文本。
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

