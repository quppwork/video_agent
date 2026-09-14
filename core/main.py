"""
核心模块主函数
"""
import argparse

from core.pipeline import run_pipeline



def main()->None:
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="视频摘要 CLI") # 创建一个解析命令行参数的解析器
    parser.add_argument( # 向解析器登记一项参数规则（本次注册的参数规则是：视频路径）
        "video_path", # 位置参数：视频路径
        help="本地视频文件路径" # 帮助文案。跑 python -m core.main -h 时会显示，方便自己和别人用
        )
    args = parser.parse_args() # 从命令行读入

    result = run_pipeline(args.video_path) # 运行流水线
    print(result)


if __name__ == "__main__":
    main()