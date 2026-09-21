"""
核心模块主函数
"""
import argparse  # 命令行参数解析模块
from pathlib import Path  # 导入Path类

from core.pipeline import run_pipeline  # 导入流水线模块


def main()->None:
    """
    主函数
    """
    DEFAULT_OUT_DIR = Path("tests_video/test_video_output")
    parser = argparse.ArgumentParser(description="视频摘要 CLI") # 创建一个解析命令行参数的解析器
    parser.add_argument( # 向解析器登记一项参数规则（本次注册的参数规则是：视频路径）
        "video_path", # 位置参数：视频路径
        help="本地视频文件路径" # 帮助文案。跑 python -m core.main -h 时会显示，方便自己和别人用
        )
    parser.add_argument(
        "--out-dir", # 选项参数：输出目录
        type=Path, # 类型：Path类
        default=DEFAULT_OUT_DIR, # 默认值：DEFAULT_OUT_DIR
        help="输出目录" # 帮助文案。跑 python -m core.main -h 时会显示，方便自己和别人用
    )
    args = parser.parse_args() # 从命令行读入
    result = run_pipeline(args.video_path, out_dir=args.out_dir) # 运行流水线
    print(result)

if __name__ == "__main__":
    main()