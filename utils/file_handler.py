import os,hashlib
from utils.logger_handler import logger
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_core.documents import Document

# 获取文件md5哈希字符串，用于判断文件是否变更
def get_file_md5_hex(filepath:str):
    # 文件不存在，打日志并返回None
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return 
    # 路径存在，但不是文件（是文件夹）
    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]{filepath} 不是有效文件，是文件夹")
        return
    
    md5_obj = hashlib.md5()  # 创建md5哈希对象
    chunk_size = 8192       # 文件读取缓冲区大小，单位字节
    with open(filepath,"rb") as f:  # 以二进制模式打开文件
        # 循环读取文件块，海象运算符赋值，更新md5对象
        while chunk := f.read(chunk_size):
            md5_obj.update(chunk)
    return md5_obj.hexdigest()  # 计算并返回md5十六进制字符串


def listdir_with_allowed_type(filepath:str, allowed_end) -> tuple:
    """遍历目录，筛选指定后缀的文件，返回绝对路径元组"""
    file_list = []
    if not os.path.exists(filepath):
        logger.error(f"{filepath}文件夹不存在")
        return tuple(file_list)
    # 遍历文件夹，筛选后缀匹配的文件，拼接成绝对路径存入列表
    for filename in os.listdir(filepath):
        if filename.endswith(allowed_end):
            abs_path = os.path.join(filepath,filename)
            file_list.append(abs_path)
    return tuple(file_list)  # 返回元组，不可变，避免外部修改


def pdf_loader(filename, passwd=None) -> list[Document]:
    # 加载PDF文档，返回Document对象列表
    return PyPDFLoader(filename, passwd).load()


def txt_loader(filename) -> list[Document]:
    # 加载txt文本文件，返回Document对象列表
    return TextLoader(filename, encoding="utf-8").load()
