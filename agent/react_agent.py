# import：create_agent / chat_model / load_system_prompts
#         7个工具（点名导入！）/ 3个中间件
from utils.prompt_loader import load_system_prompts 
from model.factory import chat_model
from agent.tools.agent_tools import get_current_month,get_user_id,get_user_location,get_weather,fetch_external_data,fill_context_for_report,rag_summarize
from langchain.agents import create_agent
from agent.tools.middleware import log_before_model,monitor_tool,report_prompt_switch
# class ReactAgent
#     __init__: self.agent = create_agent(model=, system_prompt=, tools=[7个], middleware=[3个])
#     execute_stream(query):
#         input_dict = {"messages": [{"role":"user","content":query}]}
#         for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
#             最后一条消息有内容 → yield 内容+"\n"   ← 生成器（订正1）
# __main__: agent = ReactAgent()，for 循环打印 execute_stream("给我生成我的使用报告")

class ReactAgent():
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt= load_system_prompts(),
            tools=[get_current_month,get_user_id,get_user_location,get_weather,fetch_external_data,fill_context_for_report,rag_summarize],
            middleware=[log_before_model,monitor_tool,report_prompt_switch]
        )
    def execute_stream(self,query:str):
        input_dict={
            "messages":[
                {"role":"user","content":query}
            ]
        }
        for chunk in self.agent.stream(input_dict,stream_mode="values",context={"report":False}):
            lastmessage = chunk["messages"][-1]
            if lastmessage.content:
                yield lastmessage.content.strip()+"\n"

if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk,end="",flush=True)
    