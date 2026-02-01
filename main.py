import os
import glob
from dotenv import load_dotenv
from src.agents.review_agent import get_review_agent
from datetime import datetime

def main():
    # 加载环境变量
    load_dotenv()
    
    # 配置你的数据目录
    data_dir = os.path.join(os.getcwd(), "data") 
    # 如果 data 目录不存在作为演示创建它
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory at {data_dir}. Please put your textbook folders here.")

    print(f"Start scanning directory: {data_dir}")

    # 获取所有子文件夹或文件
    # 假设每个子文件夹代表一本教材的申报材料
    # 或者如果文件直接散落在 data_dir，也可以调整 glob 模式
    # 这里假设 data 目录下有许多子文件夹
    items = [f for f in glob.glob(os.path.join(data_dir, "*"))]

    if not items:
        print("No files or directories found in data directory.")
        return

    agent, system_prompt = get_review_agent()

    # 批量处理或者单个处理
    # 建议将任务描述为一次性处理多个，或者并在循环中逐个调用 Agent
    # 为了稳定性，这里演示遍历列表，逐个送入 Agent 处理，防止 Context Window 超限
    
    for item_path in items:
        print(f"Processing: {item_path}")
        
        # 构建给 Agent 的指令
        # 获取该目录下的所有文件名，辅助 Agent 决策
        try:
             files_in_dir = os.listdir(item_path)
             files_list_str = "\n".join([f"- {f}" for f in files_in_dir])
        except Exception as e:
             files_list_str = f"无法读取目录: {e}"

        query = f"""

        当前时间是：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        请处理以下路径的教材申报材料: {item_path}
        
        该文件夹下包含以下文件：
        {files_list_str}
        
        请先判断文件夹中哪个文件是申报书，哪个是附件1，哪个是附件2，注意它们完全没有规范命名

        1、使用 TextIn 工具(extract_field)提取申报书中以下字段的内容：
        - 申报单位
        - 申报类型
        - 申报教材名称
        - ISBN
        - 第一主编/作者
        - 其他编写人员（前5人，不含主编）
        - 主要语种类型
        - 出版单位
        - 初版时间（XXXX-XX）
        - 载体形式
        - 本版出版时间（XXXX-XX）
        - 版次
        - "最新印次时间（XXXX-XX）"
        - "总印次（各版累计）"
        - 初版以来合计印数（万）
        - 是否为重点立项教材
        - 其他省部级以上项目获奖

        2、使用 TextIn 工具(parse_text)提取除申报书文件外两个文件(附件)的全文内容，并从中查找以下字段的信息：
        - 申报教材名称
        - ISBN
        - 第一主编/作者
        - 主要语种类型
        - 出版单位
        - 初版时间（XXXX-XX）
        - 载体形式
        - 本版出版时间（XXXX-XX）
        - 版次
        - 最新印次时间（XXXX-XX）
        
        3、请依据第二步其他文件提取出来的字段内容，对第一步申报表中提取出的相应字段进行核对,请注意字段不一定完全匹配才算一致，格式可能不一样但意思一致的也算一致，并调用 update_task tool 进行反馈：
        - 如果一致，返回通过
        - 如果不一致，返回不通过，并附带不通过的内容作为备注

        4、将文件夹名与第一步申报表中提取出的字段内容以及审核状态与备注全部发送给 Excel 工具，将结果写入 'review_results.xlsx'。
        """
        
        try:
            # LangGraph 接受的输入格式是 messages 列表
            # 我们手动把 System Prompt 插在最前面
            result = agent.invoke({"messages": [("system", system_prompt), ("user", query)]})
            
            # LangGraph 的返回也是一个 State 字典，最终回复在 messages 的最后一条
            last_message = result["messages"][-1]
            print(f"Agent Reply: {last_message.content}")
            
            print(f"Completed {item_path}")
        except Exception as e:
            print(f"Failed to process {item_path}: {e}")

if __name__ == "__main__":
    main()
