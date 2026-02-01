from langchain_core.tools import tool

@tool
def update_task(task_id: str, status: str, feedback: str = "") -> str:
    """
    向终端输出任务状态
    
    Args:
        task_id: 任务或文件标识符 (例如文件名)
        status: 状态 ("通过" 或 "不通过")
        feedback: 如果不通过，提供具体原因或差异内容
    
    Returns:
        Confirmation message.
    """
    # 直接在终端打印大模型传入的内容
    print(f"\n[任务更新] ID: {task_id}")
    print(f"  状态: {status}")
    if feedback:
        print(f"  反馈: {feedback}")
    print("-" * 30 + "\n")
    
    return f"Task {task_id} updated: Status={status}, Feedback={feedback}"
