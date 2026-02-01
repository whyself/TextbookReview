import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 使用 LangGraph 的现代 Agent 构建器，抛弃老旧且充满 Bug 的 AgentExecutor
from langgraph.prebuilt import create_react_agent

# 导入我们可以使用的工具
from src.tools.textin_tool import extract_field, parse_text
from src.tools.excel_tool import append_to_excel
from src.tools.update_task import update_task

def get_review_agent():
    load_dotenv()
    
    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "qwen-max"), 
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
    )

    # 2. 定义工具集
    tools = [extract_field, parse_text, append_to_excel, update_task]

    # 3. 定义 System Message (Prompt)
    # LangGraph 的 create_react_agent 接受一个 state_modifier 或者 messages_modifier 作为 System Prompt
    system_message = """
你是一个专业的教材申报审核助手。
你的任务是：
1. 读取给定的每一个教材申报文件夹。
2. 根据用户要求，使用 TextIn 工具解析文件夹中的内容。
3. 根据用户要求，审核材料并调用update_task工具进行反馈。
4. 根据用户要求，将审核结果写入Excel工具。
         
请一步步思考，确保每一个文件都被处理。如果在解析过程中遇到错误，请记录错误信息但不要停止整个任务。
"""

    # 4. 创建 Modern Agent (LangGraph)
    # 这会返回一个 CompiledGraph，它的用法和 AgentExecutor 类似，也有 .invoke() 方法
    # 4. 创建 Modern Agent (LangGraph)
    # 不传 system prompt 参数，改为在 invoke 时手动传入
    agent = create_react_agent(llm, tools)
    
    return agent, system_message
