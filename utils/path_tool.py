import os

def get_project_root() -> str:
    """获取项目根目录（path_tool.py固定放在utils文件夹）"""
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path: str) -> str:
    """
    根据项目根目录，把相对路径转为绝对路径
    :param relative_path: 相对于项目根目录的路径，如 "config/rag.yml"
    :return: 规范化后的绝对路径
    """
    project_root = get_project_root()
    raw_path = os.path.join(project_root, relative_path)
    abs_path = os.path.normpath(raw_path)
    return abs_path
