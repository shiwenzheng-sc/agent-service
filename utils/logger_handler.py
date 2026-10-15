from datetime import datetime
import logging
from utils.path_tool import get_abs_path
import os

# 日志根目录，获取项目下logs文件夹绝对路径
LOG_ROOT = get_abs_path("logs")
# 创建日志文件夹，已存在则不报错
os.makedirs(LOG_ROOT, exist_ok=True)

# 定义默认日志输出格式
# 时间 - 日志器名称 - 日志级别 - 文件名:行号 - 日志信息
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    """
    获取自定义日志器，同时输出控制台日志 + 文件日志
    :param name: logger名称，默认agent，用于区分不同模块日志
    :param console_level: 控制台输出日志级别，默认INFO，低于该级别的日志控制台不打印
    :param file_level: 文件输出日志级别，默认DEBUG，低于该级别的日志不写入文件
    :param log_file: 日志文件完整路径，不传则默认 logs/agent.log
    :return: 配置好的Logger实例
    """
    # 获取指定名称的logger对象
    logger = logging.getLogger(name)
    # logger全局最低级别，必须设置为DEBUG，保证handler可以独立过滤级别
    logger.setLevel(logging.DEBUG)

    # 防止重复添加handler：如果logger已有处理器，直接返回，避免重复打印日志
    if logger.handlers:
        return logger

    # 【控制台处理器】输出日志到终端
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # 日志文件路径，未传入则使用默认路径
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%y%m%d')}.log")
    # 【文件处理器】将日志写入文件，编码UTF-8防止中文乱码
    file_handler = logging.FileHandler(log_file, encoding="UTF-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger

logger = get_logger()