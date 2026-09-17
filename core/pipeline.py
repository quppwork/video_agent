"""
流水线模块
采用pipeline模式，将整个流程分为多个步骤，每个步骤之间通过管道连接，实现数据流式处理
"""
import subprocess  # 子进程处理模块
from pathlib import Path  # 路径处理模块


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
    
    #提取音频
    audio_path = extract_audio(path, path.parent) # 提取音频
    return audio_path # 返回音频路径
    

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
        "ffmpeg",# 使用ffmpeg命令
        "-i", str(video),# 设置视频路径
        "-q:a", "0",# 设置音频质量为0
        "-map", "a",# 映射音频流
        str(audio_path),# 设置音频路径
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True) # 赋值result执行命令
    if result.returncode != 0: # 判断命令是否执行失败
        raise RuntimeError(f"提取音频失败: {result.stderr}") # 抛出提取音频失败异常
    return audio_path # 返回音频路径