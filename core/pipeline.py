"""
流水线模块
采用pipeline模式，将整个流程分为多个步骤，每个步骤之间通过管道连接，实现数据流式处理
"""



def run_pipeline(video_path: str)->str:
    """
    流水线主函数
    """
    return f"success: {video_path}"