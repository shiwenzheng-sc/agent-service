from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def load_system_prompts():
    # 读主提示词：从配置拿路径 → 转绝对路径 → 读文件 → 返回字符串
    try:
        file_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as e:
        logger.error("[load_system_prompts]配置里没有 main_prompt_path")
        raise e
    try:
        return open(file_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]读提示词文件出错，{str(e)}")
        raise e

def load_rag_prompts():
    # 读主提示词：从配置拿路径 → 转绝对路径 → 读文件 → 返回字符串
    try:
        file_path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error("[load_rag_prompts]配置里没有 rag_summarize_prompt_path")
        raise e
    try:
        return open(file_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts]读提示词文件出错，{str(e)}")
        raise e 

def load_report_prompts():
    # 读主提示词：从配置拿路径 → 转绝对路径 → 读文件 → 返回字符串
    try:
        file_path = get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error("[load_report_prompts]配置里没有 report_prompt_path")
        raise e
    try:
        return open(file_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts]读提示词文件出错，{str(e)}")
        raise e 