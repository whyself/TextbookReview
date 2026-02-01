import pandas as pd
import os
from langchain.tools import tool
from typing import List, Dict

@tool
def append_to_excel(data: List[Dict[str, str]], output_file: str = "review_results.xlsx") -> str:
    """
    将审核结果添加到 Excel 文件中。
    参数:
    - data: 包含审核信息的字典列表，例如 [{"文件夹名": "运筹学", "申报单位": "南京大学", "ISBN": "9787112311347","审核状态": "通过","备注":"..." }]
    - output_file: 输出的 Excel 文件名，默认为 review_results.xlsx
    
    返回: 操作结果消息
    """
    try:
        df_new = pd.DataFrame(data)
        
        if os.path.exists(output_file):
            # 如果文件存在，读取原有数据并追加
            # 注意：这里简单的追加，如果需要更复杂的格式可能需要 openpyxl
            with pd.ExcelWriter(output_file, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                # 获取现有行数以追加
                try:
                    reader = pd.read_excel(output_file)
                    existing_columns = set(reader.columns)
                    new_columns = set(df_new.columns)
                    
                    # 检查新数据是否缺少现有列（这可能导致数据错位或看起来奇怪）
                    # 或者是检查新数据是否有额外的列？用户需求是“列上有缺失字段”，通常指新数据缺了某些表头
                    missing_columns = existing_columns - new_columns
                    if missing_columns:
                        return f"Error: Input data is missing columns existing in {output_file}: {missing_columns}. Please ensure data structure matches."

                    start_row = len(reader) + 1
                    header = False
                except pd.errors.EmptyDataError:
                    start_row = 0
                    header = True
                
                df_new.to_excel(writer, index=False, header=header, startrow=start_row)
        else:
            # 如果文件不存在，创建新文件
            df_new.to_excel(output_file, index=False)
            
        return f"Successfully wrote {len(data)} records to {output_file}"
    except Exception as e:
        return f"Error writing to Excel: {str(e)}"
